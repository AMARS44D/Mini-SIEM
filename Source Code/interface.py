import tkinter as tk
from tkinter import ttk
import threading
import os
import time
from log_reader import read_logs_loop
from report_pdf import generate_report_pdf
from search_window import SearchWindow

class RealTimeSIEM:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini-SIEM Localhost")
        self.root.configure(bg="black")

        self.last_event_ids = {}
        self.running_flag = True
        self.event_counter = 0
        self.all_events = []
        self.level_counts = {lvl: 0 for lvl in ["Critical", "Error", "Warning", "Information", "Verbose", "Unknown"]}
        self.start_time = time.time()

        self.setup_gui()
        threading.Thread(target=self.logs_thread, daemon=True).start()

    def logs_thread(self):
        def callback_insert_event(time_str, log_type, event_id, level, source, msg):
            self.event_counter += 1
            event_dict = {
                "ID": self.event_counter,
                "Time": time_str,
                "Log Type": log_type,
                "Event ID": event_id,
                "Level": level,
                "Source": source,
                "Message": msg
            }
            self.all_events.append(event_dict)

            # Insert into Treeview in main thread
            self.root.after(0, lambda: self.tree.insert("", "end",
                                                       values=(self.event_counter, time_str, log_type, event_id, level, source, msg),
                                                       tags=(level,)))
            self.root.after(0, lambda: self.tree.see(self.tree.get_children()[-1]))

        def callback_update_status():
            self.root.after(0, self.update_status_label)

        read_logs_loop(callback_insert_event, callback_update_status, lambda: self.running_flag, self.last_event_ids, self.level_counts)

    def setup_gui(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="black",
                        foreground="white",
                        fieldbackground="black",
                        font=('Helvetica', 11))
        style.configure("Treeview.Heading",
                        background="black",
                        foreground="white",
                        font=('Helvetica', 12, 'bold'))

        columns = ("ID", "Time", "Log Type", "Event ID", "Level", "Source", "Message")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=20)
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Time", width=150, anchor="w")
        self.tree.column("Log Type", width=90, anchor="w")
        self.tree.column("Event ID", width=80, anchor="w")
        self.tree.column("Level", width=90, anchor="w")
        self.tree.column("Source", width=250, anchor="w")
        self.tree.column("Message", width=650, anchor="w")

        self.tree.pack(fill='both', expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Status bar frame with counts
        self.status_frame = tk.Frame(self.root, bg="black")
        self.status_frame.pack(pady=10)
        self.update_status_label()

        # Color tags per level
        self.tree.tag_configure("Critical", foreground="red")
        self.tree.tag_configure("Error", foreground="red")
        self.tree.tag_configure("Warning", foreground="yellow")
        self.tree.tag_configure("Information", foreground="white")
        self.tree.tag_configure("Verbose", foreground="gray")
        self.tree.tag_configure("Unknown", foreground="green")

        # Footer frame with buttons
        footer_frame = tk.Frame(self.root, bg="black")
        footer_frame.pack(pady=10)

        tk.Button(footer_frame, text="Search Event", command=self.open_search_window, font=('Helvetica', 11)).pack(side="left", padx=10)
        tk.Button(footer_frame, text="Generate PDF Report", command=self.generate_report_pdf, font=('Helvetica', 11)).pack(side="left", padx=10)

    def update_status_label(self):
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        for lvl in self.level_counts:
            color = "white"
            if lvl in ["Critical", "Error"]:
                color = "red"
            elif lvl == "Warning":
                color = "yellow"
            elif lvl == "Unknown":
                color = "green"

            count = self.level_counts[lvl]
            text = f"{lvl}: {count}"
            tk.Label(self.status_frame, text=text, fg=color, bg="black", font=('Courier', 11, 'bold')).pack(side="left", padx=10)

    def on_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        item = self.tree.item(item_id)
        values = item.get('values', [])
        if not values:
            return

        details_win = tk.Toplevel(self.root)
        details_win.title("Event Details")
        details_win.configure(bg="black")

        labels_text = ["ID:", "Time:", "Log Type:", "Event ID:", "Level:", "Source:", "Message:"]
        for i, (label_text, val) in enumerate(zip(labels_text, values)):
            lbl = tk.Label(details_win, text=label_text, fg="white", bg="black", font=('Helvetica', 11, 'bold'))
            lbl.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            val_lbl = tk.Label(details_win,
                               text=val,
                               fg="green" if label_text == "Message:" else "white",
                               bg="black",
                               wraplength=700,
                               justify="left",
                               font=('Helvetica', 11))
            val_lbl.grid(row=i, column=1, sticky="w", padx=10, pady=5)

        tk.Button(details_win, text="Close", command=details_win.destroy, font=('Helvetica', 11)).grid(row=len(labels_text), column=0, columnspan=2, pady=10)

    def generate_report_pdf(self):
        filename = os.path.join(os.path.expanduser("~"), "Desktop", "report_SIEM.pdf")
        generate_report_pdf(self.tree, self.level_counts, self.start_time)

    def open_search_window(self):
        SearchWindow(self.root, self.all_events, self.tree)

    def stop(self):
        self.running_flag = False
