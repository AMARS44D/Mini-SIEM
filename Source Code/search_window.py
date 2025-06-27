import tkinter as tk
from tkinter import ttk
from utils import is_int

class SearchWindow:
    def __init__(self, parent, all_events, tree):

        self.parent = parent
        self.all_events = all_events
        self.tree = tree
        self.search_widgets = {}

        self.win = tk.Toplevel(parent)
        self.win.title("Advanced Search")
        self.win.configure(bg="black")

        self.build_widgets()

    def build_widgets(self):
        # Extract and sort IDs (including negatives)
        id_values = sorted(set(int(x) for x in (str(self.tree.set(child, "ID")) for child in self.tree.get_children()) if is_int(x)))
        id_values = [str(x) for x in id_values]

        event_id_values = sorted(set(int(event["Event ID"]) for event in self.all_events if is_int(event["Event ID"])))
        event_id_values = [str(x) for x in event_id_values]

        log_type_values = sorted(set(event["Log Type"] for event in self.all_events))
        level_values = sorted(set(event["Level"] for event in self.all_events))

        # ID
        tk.Label(self.win, text="ID", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        cb_id = ttk.Combobox(self.win, values=[""] + id_values, state="readonly", width=37)
        cb_id.grid(row=0, column=1, padx=10, pady=5)
        cb_id.set("")
        self.search_widgets["ID"] = cb_id

        # Event ID
        tk.Label(self.win, text="Event ID", bg="black", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        cb_event_id = ttk.Combobox(self.win, values=[""] + event_id_values, state="readonly", width=37)
        cb_event_id.grid(row=1, column=1, padx=10, pady=5)
        cb_event_id.set("")
        self.search_widgets["Event ID"] = cb_event_id

        # Log Type
        tk.Label(self.win, text="Log Type", bg="black", fg="white").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        cb_log_type = ttk.Combobox(self.win, values=[""] + log_type_values, state="readonly", width=37)
        cb_log_type.grid(row=2, column=1, padx=10, pady=5)
        cb_log_type.set("")
        self.search_widgets["Log Type"] = cb_log_type

        # Level
        tk.Label(self.win, text="Level", bg="black", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        cb_level = ttk.Combobox(self.win, values=[""] + level_values, state="readonly", width=37)
        cb_level.grid(row=3, column=1, padx=10, pady=5)
        cb_level.set("")
        self.search_widgets["Level"] = cb_level

        # Contains word (Message)
        tk.Label(self.win, text="Contains word (Message)", bg="black", fg="white").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_msg = tk.Entry(self.win, width=40)
        entry_msg.grid(row=4, column=1, padx=10, pady=5)
        self.search_widgets["Contains word (Message)"] = entry_msg

        tk.Button(self.win, text="Search", command=self.perform_search, font=('Helvetica', 11)).grid(row=5, column=0, columnspan=2, pady=10)

    def perform_search(self):
        criteria = {key: widget.get().strip() for key, widget in self.search_widgets.items()}

        filtered_events = []
        for event in self.all_events:
            if criteria["ID"] and str(event["ID"]) != criteria["ID"]:
                continue
            if criteria["Event ID"] and str(event["Event ID"]) != criteria["Event ID"]:
                continue
            if criteria["Log Type"] and event["Log Type"] != criteria["Log Type"]:
                continue
            if criteria["Level"] and event["Level"] != criteria["Level"]:
                continue
            if criteria["Contains word (Message)"] and criteria["Contains word (Message)"].lower() not in event["Message"].lower():
                continue
            filtered_events.append(event)

        self.show_results(filtered_events)

    def show_results(self, filtered_events):
        result_win = tk.Toplevel(self.parent)
        result_win.title("Search Results")
        result_win.configure(bg="black")

        columns = ("ID", "Time", "Log Type", "Event ID", "Level", "Source", "Message")
        tree = ttk.Treeview(result_win, columns=columns, show='headings', height=20)
        for col in columns:
            tree.heading(col, text=col)

        tree.column("ID", width=60, anchor="center")
        tree.column("Time", width=150, anchor="w")
        tree.column("Log Type", width=90, anchor="w")
        tree.column("Event ID", width=80, anchor="w")
        tree.column("Level", width=90, anchor="w")
        tree.column("Source", width=250, anchor="w")
        tree.column("Message", width=650, anchor="w")

        tree.pack(fill='both', expand=True)

        # Color tags
        tree.tag_configure("Critical", foreground="red")
        tree.tag_configure("Error", foreground="red")
        tree.tag_configure("Warning", foreground="yellow")
        tree.tag_configure("Information", foreground="white")
        tree.tag_configure("Verbose", foreground="gray")
        tree.tag_configure("Unknown", foreground="green")

        for event in filtered_events:
            tree.insert("", "end",
                        values=(event["ID"], event["Time"], event["Log Type"], event["Event ID"], event["Level"], event["Source"], event["Message"]),
                        tags=(event["Level"],))

        def on_double_click_result(event):
            item_id = tree.focus()
            if not item_id:
                return
            item = tree.item(item_id)
            values = item.get('values', [])
            if not values:
                return

            details_win = tk.Toplevel(result_win)
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

            close_btn = tk.Button(details_win, text="Close", command=details_win.destroy, font=('Helvetica', 11))
            close_btn.grid(row=len(labels_text), column=0, columnspan=2, pady=10)

        tree.bind("<Double-1>", on_double_click_result)

        self.win.destroy()
