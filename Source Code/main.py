import tkinter as tk
from interface import RealTimeSIEM

def main():
    root = tk.Tk()
    app = RealTimeSIEM(root)
    root.state("zoomed")
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
