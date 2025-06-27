from reportlab.pdfgen import canvas
from datetime import datetime, timezone
import time
import os
import tkinter as tk
from tkinter import messagebox

def generate_report_pdf(treeview, level_counts, start_time):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    base_filename = "SIEM_Report"
    extension = ".pdf"

    i = 1
    while True:
        filename = os.path.join(desktop_path, f"{base_filename}_{i}{extension}")
        if not os.path.isfile(filename):
            break
        i += 1

    c = canvas.Canvas(filename)
    now = datetime.now(timezone.utc)  # UTC / GMT time

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Mini-SIEM Report")

    y = 780
    c.setFont("Helvetica", 12)
    for level, count in level_counts.items():
        c.drawString(50, y, f"{level} : {count}")
        y -= 20

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 10, "Displayed Events:")
    y -= 40

    c.setFont("Helvetica", 10)
    for item_id in treeview.get_children():
        values = treeview.item(item_id)['values']
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 800
        c.drawString(50, y, str(values))
        y -= 15

    uptime = time.time() - start_time
    minutes = int(uptime // 60)
    c.drawString(50, y - 20, f"Uptime: {minutes} minutes")

    c.setFont("Helvetica", 9)
    c.drawString(450, 10, f"Date (GMT): {now.strftime('%Y-%m-%d %H:%M:%S')}")

    c.save()

    # Popup info window using tkinter
    root = tk.Tk()
    root.withdraw()  # Hide main window
    messagebox.showinfo("Report Created", f"Report successfully saved on Desktop:\n{filename}")
    root.destroy()

    print(f"Report saved on Desktop: {filename}")
