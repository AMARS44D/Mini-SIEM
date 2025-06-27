import win32evtlog
import win32api
import win32security
import logging
import time

LEVELS = {
    1: "Critical",
    2: "Error",
    3: "Warning",
    4: "Information",
    5: "Verbose"
}

def adjust_privileges():

#    Adjust process privileges to read security logs.

    try:
        privilege = win32security.SE_SECURITY_NAME
        h_token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        )
        win32security.AdjustTokenPrivileges(
            h_token,
            False,
            [(win32security.LookupPrivilegeValue(None, privilege), win32security.SE_PRIVILEGE_ENABLED)]
        )
    except Exception as e:
        logging.warning(f"Adjusting privileges failed: {str(e)}")

def read_logs_loop(callback_insert_event, callback_update_status, running_flag, last_event_ids, level_counts):
    """
    Loop reading Windows Event Logs in the background.
    Calls callback_insert_event for each new event.
    Calls callback_update_status after processing logs.
    """
    adjust_privileges()
    server = 'localhost'
    log_types = ['System', 'Application', 'Security', 'Installation', 'Network']

    while running_flag():
        for log_type in log_types:
            handle = None
            try:
                handle = win32evtlog.OpenEventLog(server, log_type)
            except Exception as e:
                print(f"Error opening log {log_type}: {e}")
                continue

            if not handle:
                print(f"Invalid handle for {log_type}, skipping.")
                continue

            try:
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events:
                    continue

                for event in reversed(events):
                    record_id = event.RecordNumber
                    last_id = last_event_ids.get(log_type, 0)
                    if record_id <= last_id:
                        continue
                    last_event_ids[log_type] = record_id

                    level = LEVELS.get(event.EventType, "Unknown")
                    level_counts[level] += 1
                    time_str = event.TimeGenerated.Format()
                    msg = " ".join(event.StringInserts) if event.StringInserts else "No message"
                    source = str(event.SourceName)
                    event_id = str(event.EventID)

                    # Call insert event callback
                    callback_insert_event(time_str, log_type, event_id, level, source, msg)

                # Update status label callback
                callback_update_status()

            except Exception as e:
                print(f"Error reading log {log_type}: {e}")
            finally:
                if handle:
                    try:
                        win32evtlog.CloseEventLog(handle)
                    except Exception as e:
                        print(f"Error closing log {log_type}: {e}")

        time.sleep(1)
