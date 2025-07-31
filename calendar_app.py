import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import calendar
import datetime
import json
import os
import csv

REMINDER_FILE = "reminders.json"
OCCASION_FILE = "occasions.json"

# ---------------------- Data Storage ----------------------
def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

def load_occasions():
    if os.path.exists(OCCASION_FILE):
        with open(OCCASION_FILE, "r") as f:
            return json.load(f)
    return {}

# ---------------------- Main Application ----------------------
class CalendarReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar Reminder App")
        self.reminders = load_reminders()
        self.occasions = load_occasions()
        self.current_date = datetime.date.today()
        self.dark_mode = False
        self.build_ui()
        self.check_today_reminders()

    def build_ui(self):
        self.style = ttk.Style()

        self.header = tk.Label(self.root, text="", font=("Arial", 16))
        self.header.pack(pady=10)

        # Dropdowns for month/year selection
        dropdown_frame = tk.Frame(self.root)
        dropdown_frame.pack(pady=5)

        tk.Label(dropdown_frame, text="Month:").pack(side=tk.LEFT)
        self.month_var = tk.StringVar(value=str(self.current_date.month))
        month_list = [str(i) for i in range(1, 13)]
        self.month_box = ttk.Combobox(dropdown_frame, values=month_list, textvariable=self.month_var, width=5)
        self.month_box.pack(side=tk.LEFT, padx=5)

        tk.Label(dropdown_frame, text="Year:").pack(side=tk.LEFT)
        self.year_var = tk.StringVar(value=str(self.current_date.year))
        year_list = [str(y) for y in range(1900, 2101)]
        self.year_box = ttk.Combobox(dropdown_frame, values=year_list, textvariable=self.year_var, width=7)
        self.year_box.pack(side=tk.LEFT, padx=5)

        jump_button = tk.Button(dropdown_frame, text="Jump", command=self.jump_to_selected_date)
        jump_button.pack(side=tk.LEFT, padx=10)

        export_button = tk.Button(dropdown_frame, text="Export Reminders", command=self.export_reminders)
        export_button.pack(side=tk.LEFT, padx=10)

        theme_button = tk.Button(dropdown_frame, text="Toggle Dark Mode", command=self.toggle_theme)
        theme_button.pack(side=tk.LEFT, padx=10)

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Previous Month", command=self.prev_month).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Next Month", command=self.next_month).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Go to Date", command=self.goto_date).pack(side=tk.LEFT, padx=10)

        self.show_calendar()

    def show_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        year = self.current_date.year
        month = self.current_date.month
        self.header.config(text=f"{calendar.month_name[month]} {year}")

        cal = calendar.monthcalendar(year, month)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold")).grid(row=0, column=i)

        for row_idx, week in enumerate(cal, 1):
            for col_idx, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(self.calendar_frame, text=str(day), width=5,
                                    command=lambda d=day: self.show_reminder_popup(year, month, d))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

    def show_reminder_popup(self, year, month, day):
        date_str = f"{year}-{month:02d}-{day:02d}"
        existing = self.reminders.get(date_str, [])
        occasion = self.occasions.get(date_str, "No occasion recorded.")
        note = simpledialog.askstring("Reminder", f"Occasion: {occasion}\n\nReminders on {date_str}:\n" +
                                      "\n".join(f"{i+1}. {r}" for i, r in enumerate(existing)) +
                                      "\n\nAdd new reminder (or leave empty to cancel):")
        if note:
            self.reminders.setdefault(date_str, []).append(note)
            save_reminders(self.reminders)
            messagebox.showinfo("Saved", "Reminder added!")

    def next_month(self):
        month = self.current_date.month + 1
        year = self.current_date.year
        if month > 12:
            month = 1
            year += 1
        self.current_date = datetime.date(year, month, 1)
        self.month_var.set(str(month))
        self.year_var.set(str(year))
        self.show_calendar()

    def prev_month(self):
        month = self.current_date.month - 1
        year = self.current_date.year
        if month < 1:
            month = 12
            year -= 1
        self.current_date = datetime.date(year, month, 1)
        self.month_var.set(str(month))
        self.year_var.set(str(year))
        self.show_calendar()

    def goto_date(self):
        try:
            year = simpledialog.askinteger("Go to Date", "Enter Year (e.g., 2025):")
            month = simpledialog.askinteger("Go to Date", "Enter Month (1-12):")
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                self.current_date = datetime.date(year, month, 1)
                self.month_var.set(str(month))
                self.year_var.set(str(year))
                self.show_calendar()
            else:
                messagebox.showerror("Invalid Input", "Enter a valid year and month (1–12).")
        except Exception:
            messagebox.showerror("Error", "Could not parse the date.")

    def jump_to_selected_date(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                self.current_date = datetime.date(year, month, 1)
                self.show_calendar()
            else:
                messagebox.showerror("Invalid Input", "Month must be 1–12 and year 1900–2100.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric month and year.")

    def check_today_reminders(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        if today in self.reminders:
            notes = "\n".join(f"- {n}" for n in self.reminders[today])
            messagebox.showinfo("Today's Reminders", f"Reminders for today ({today}):\n\n{notes}")

    def export_reminders(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Reminder"])
            for date, notes in self.reminders.items():
                for note in notes:
                    writer.writerow([date, note])
        messagebox.showinfo("Exported", "Reminders exported successfully!")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#2e2e2e" if self.dark_mode else "SystemButtonFace"
        fg_color = "white" if self.dark_mode else "black"

        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            self.apply_theme(widget, bg_color, fg_color)

    def apply_theme(self, widget, bg, fg):
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass
        for child in widget.winfo_children():
            self.apply_theme(child, bg, fg)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarReminderApp(root)
    root.mainloop()
