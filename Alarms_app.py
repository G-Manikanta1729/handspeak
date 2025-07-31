import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from threading import Thread
import time
import os
import platform

try:
    from playsound import playsound
except ImportError:
    playsound = None

try:
    from plyer import notification
except ImportError:
    notification = None

class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Alarm Clock + Stopwatch + Timer")
        self.alarms = []
        self.stopwatch_running = False
        self.stopwatch_start_time = None
        self.timer_running = False
        self.timer_seconds = 0

        self.build_ui()
        Thread(target=self.update_clock, daemon=True).start()
        Thread(target=self.check_alarms, daemon=True).start()

    def build_ui(self):
        self.clock_label = tk.Label(self.root, text="", font=("Arial", 20), fg="blue")
        self.clock_label.pack(pady=10)

        tk.Label(self.root, text="Set Alarm (HH:MM 24hr):", font=("Arial", 12)).pack()
        self.time_entry = tk.Entry(self.root, font=("Arial", 12), width=10)
        self.time_entry.pack(pady=5)

        self.snooze_minutes = tk.IntVar(value=5)
        tk.Label(self.root, text="Snooze (mins):").pack()
        tk.Entry(self.root, textvariable=self.snooze_minutes, width=5).pack(pady=5)

        self.tone_path = tk.StringVar()
        tk.Button(self.root, text="Select Alarm Tone", command=self.select_tone).pack(pady=5)
        tk.Label(self.root, textvariable=self.tone_path, fg="gray").pack()

        tk.Button(self.root, text="Set Daily Alarm", command=lambda: self.set_alarm(daily=True), bg="#00c853", fg="white").pack(pady=5)
        tk.Button(self.root, text="Set One-Time Alarm", command=lambda: self.set_alarm(daily=False), bg="#0091ea", fg="white").pack(pady=5)

        self.alarms_frame = tk.LabelFrame(self.root, text="Active Alarms")
        self.alarms_frame.pack(pady=10, fill="both", expand=True)

        # Stopwatch
        tk.Label(self.root, text="Stopwatch", font=("Arial", 14)).pack(pady=(10, 0))
        self.stopwatch_label = tk.Label(self.root, text="00:00:00", font=("Arial", 20), fg="darkred")
        self.stopwatch_label.pack()
        stopwatch_frame = tk.Frame(self.root)
        stopwatch_frame.pack()
        tk.Button(stopwatch_frame, text="Start", command=self.start_stopwatch).pack(side=tk.LEFT, padx=5)
        tk.Button(stopwatch_frame, text="Stop", command=self.stop_stopwatch).pack(side=tk.LEFT, padx=5)
        tk.Button(stopwatch_frame, text="Reset", command=self.reset_stopwatch).pack(side=tk.LEFT, padx=5)

        # Countdown Timer
        tk.Label(self.root, text="Countdown Timer (sec):", font=("Arial", 12)).pack(pady=(10, 0))
        self.timer_entry = tk.Entry(self.root, font=("Arial", 12), width=10)
        self.timer_entry.pack()
        tk.Button(self.root, text="Start Timer", command=self.start_timer).pack(pady=5)
        self.timer_label = tk.Label(self.root, text="00:00", font=("Arial", 20), fg="green")
        self.timer_label.pack()

    def update_clock(self):
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            self.clock_label.config(text=now)
            if self.stopwatch_running:
                elapsed = datetime.now() - self.stopwatch_start_time
                self.stopwatch_label.config(text=str(elapsed).split('.')[0])
            if self.timer_running:
                if self.timer_seconds > 0:
                    self.timer_seconds -= 1
                    mins, secs = divmod(self.timer_seconds, 60)
                    self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
                else:
                    self.timer_running = False
                    self.timer_label.config(text="00:00")
                    self.notify_user("Timer", "Countdown finished!")
                    self.vibrate_simulation()
            time.sleep(1)

    def select_tone(self):
        path = filedialog.askopenfilename(title="Select Alarm Tone", filetypes=[("Audio Files", "*.mp3 *.wav")])
        if path:
            self.tone_path.set(path)

    def set_alarm(self, daily=True):
        alarm_time = self.time_entry.get()
        tone = self.tone_path.get()

        try:
            alarm_dt = datetime.strptime(alarm_time, "%H:%M").time()
            self.alarms.append({"time": alarm_dt, "tone": tone, "daily": daily})
            self.refresh_alarms_list()
            msg = "daily" if daily else "once"
            messagebox.showinfo("Alarm Set", f"Alarm set for {alarm_dt.strftime('%H:%M')} ({msg})")
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter time in HH:MM format (24-hour).")

    def refresh_alarms_list(self):
        for widget in self.alarms_frame.winfo_children():
            widget.destroy()

        for idx, alarm in enumerate(self.alarms):
            frame = tk.Frame(self.alarms_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"{alarm['time'].strftime('%H:%M')} ({'Daily' if alarm['daily'] else 'Once'})", width=25).pack(side=tk.LEFT)
            tk.Button(frame, text="Delete", command=lambda i=idx: self.delete_alarm(i)).pack(side=tk.RIGHT)

    def delete_alarm(self, index):
        del self.alarms[index]
        self.refresh_alarms_list()

    def check_alarms(self):
        while True:
            now = datetime.now().time().replace(second=0, microsecond=0)
            for alarm in self.alarms[:]:
                if now == alarm["time"]:
                    Thread(target=self.trigger_alarm, args=(alarm,), daemon=True).start()
                    if not alarm["daily"]:
                        self.alarms.remove(alarm)
                        self.refresh_alarms_list()
                    time.sleep(60)
            time.sleep(1)

    def trigger_alarm(self, alarm):
        self.notify_user("Alarm!", f"It's {alarm['time'].strftime('%H:%M')}! Wake up!")
        self.vibrate_simulation()
        if playsound and os.path.exists(alarm["tone"]):
            playsound(alarm["tone"])
        if messagebox.askyesno("Snooze", "Snooze this alarm?"):
            snooze_dt = (datetime.now() + timedelta(minutes=self.snooze_minutes.get())).time().replace(second=0, microsecond=0)
            self.alarms.append({"time": snooze_dt, "tone": alarm["tone"], "daily": False})
            self.refresh_alarms_list()

    def notify_user(self, title, message):
        if notification:
            notification.notify(title=title, message=message, timeout=5)
        else:
            print(f"NOTIFY: {title} - {message}")

    def vibrate_simulation(self):
        for _ in range(3):
            if platform.system() == "Windows":
                os.system("echo \a")
            time.sleep(0.5)

    # Stopwatch Functions
    def start_stopwatch(self):
        if not self.stopwatch_running:
            self.stopwatch_start_time = datetime.now() - timedelta(seconds=self.get_stopwatch_seconds())
            self.stopwatch_running = True

    def stop_stopwatch(self):
        self.stopwatch_running = False

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_label.config(text="00:00:00")

    def get_stopwatch_seconds(self):
        try:
            h, m, s = map(int, self.stopwatch_label.cget("text").split(":"))
            return h * 3600 + m * 60 + s
        except:
            return 0

    # Countdown Timer
    def start_timer(self):
        try:
            seconds = int(self.timer_entry.get())
            self.timer_seconds = seconds
            self.timer_running = True
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter countdown in seconds.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("360x720")
    app = AlarmClock(root)
    root.mainloop()