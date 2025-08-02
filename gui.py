import tkinter as tk
from tkinter import messagebox
from analyzer import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import threading
import sys, os, urllib, io
import datetime
from mailer import send_alert_email
from PIL import Image, ImageTk
from voice_recorder import voice_recorder

def check_and_alert():
    try:
        with open("user_settings.json", "r") as f:
            settings = json.load(f)
        guardian_email = settings.get("guardian_email")
        if not guardian_email:
            return

        count, latest_line = count_below_threshold()
        if count > ALERT_LIMIT:
            send_alert_email(guardian_email, count)
            # Set alert status to latest line to avoid re-checking same lines
            set_alert_status(latest_line)
            messagebox.showinfo(
                "Guardian Alert Sent",
                f"An alert was sent to the guardian ({guardian_email}) because mood dropped below {THRESHOLD} more than {ALERT_LIMIT} times."
            )
    except Exception as e:
        print("Error during guardian alert check:", e)
        
        
def check_and_add_guardian_alert(alert_limit=10):
    ALERTS_LOG_FILE = "alerts_log.json"
    count, latest_line, neg_lines = count_below_threshold(return_lines=True)
    if count > alert_limit:
        alert_record = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "negative_count": count,
            "status": "Sent",
            "reason_lines": neg_lines
        }
        logs = []
        if os.path.exists(ALERTS_LOG_FILE):
            with open(ALERTS_LOG_FILE, "r") as f:
                loaded_data = json.load(f)
                # Ensure logs is always a list
                if isinstance(loaded_data, list):
                    logs = loaded_data
                else:
                    logs = []  # Reset to empty list if file contains invalid format
        logs.insert(0, alert_record)
        with open(ALERTS_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        # Set alert status to latest line to avoid re-checking same lines
        set_alert_status(latest_line)
        

def launch_gui(user_info):
    check_and_add_guardian_alert()
    root = tk.Tk()
    root.title("MindTrackAI")
    root.geometry("900x600")
    root.configure(bg="#1e1e1e")

    def on_close():
        print("Exiting MindTrackAI...")
        # Stop voice recording if active
        if voice_recorder.is_recording:
            voice_recorder.stop_recording()
        
        # Clear keystrokes for user privacy
        try:
            if os.path.exists("keystrokes.txt"):
                with open("keystrokes.txt", "w") as f: 
                    f.write("")
                print("🔒 Keystrokes cleared for privacy")
        except Exception as e:
            print(f"Warning: Could not clear keystrokes file: {e}")
        
        # Reset alert status to 0 when app closes
        reset_alert_status()
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

     # Top Bar
    top_bar = tk.Frame(root, bg="#1e1e1e", height=50)
    top_bar.pack(side="top", fill="x")
    title_label = tk.Label(
        top_bar, text="MINDTRACKAI", fg="#cccccc", bg="#1e1e1e",
        font=("Segoe UI", 14, "bold")
    )
    title_label.pack(side="left", padx=20, pady=10)
    user_text = user_info if isinstance(user_info, str) else user_info["name"]
    user_icon = tk.Label(
        top_bar, text=f"\U0001F7E2 {user_text}", bg="#1e1e1e", fg="white", cursor="hand2"
    )
    user_icon.pack(side="right", padx=10)
    settings_icon = tk.Label(top_bar, text="\u2699\ufe0f", bg="#1e1e1e", fg="white", cursor="hand2")
    settings_icon.pack(side="right", padx=(0, 10))

    # Sidebar
    sidebar = tk.Frame(root, bg="#111111", width=150)
    sidebar.pack(side="left", fill="y")
    def create_sidebar_btn(text, icon="\U0001F4CA"):
        return tk.Button(
            sidebar, text=f"{icon} {text}", bg="#111111", fg="white",
            relief="flat", font=("Segoe UI", 10), anchor="w",
            activebackground="#1e1e1e", activeforeground="cyan", padx=10
        )

    def show_live_graph():
        check_and_add_guardian_alert()
        graph_window = tk.Toplevel()
        graph_window.title("Live Mood Trend")
        graph_window.geometry("600x400")

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def animate(i):
            history = get_day_analysis()
            ax.clear()
            if history:
                trimmed = history[-50:]
                x_data = list(range(len(trimmed)))
                y_data = [score for (_, score) in trimmed]
                ax.plot(x_data, y_data, color='cyan', linestyle='-', marker='o')
            ax.set_title("Mood Trend (Live)")
            ax.set_xlabel("Entry")
            ax.set_ylabel("Mood Score")
            ax.set_ylim(-1, 1)
            ax.grid(color='#444444')
            
            check_and_alert()

        ani = FuncAnimation(fig, animate, interval=1000)
        canvas.draw()

    def show_analysis():
        check_and_add_guardian_alert()
        mood_score = get_latest_mood()
        if mood_score >= 0.3:
            mood_color = "lime green"
            mood_emoji = "😊"
            mood_text = "Positive"
            comment = "You're doing great today!"
        elif mood_score <= -0.3:
            mood_color = "red"
            mood_emoji = "😞"
            mood_text = "Negative"
            comment = "It might be a tough day. Hang in there!"
        else:
            mood_color = "orange"
            mood_emoji = "😐"
            mood_text = "Neutral"
            comment = "A balanced day. Keep going!"

        popup = tk.Toplevel()
        popup.title("Sentiment Analysis Result")
        popup.geometry("370x260")
        popup.configure(bg="#23272A")
        popup.resizable(False, False)
        tk.Label(
            popup, text=f"Sentiment Score: {mood_score:.4f}",
            fg=mood_color, bg="#23272A", font=("Segoe UI", 16, "bold")
        ).pack(pady=(18, 5))
        tk.Label(
            popup, text=mood_emoji, font=("Segoe UI", 48), bg="#23272A"
        ).pack()
        tk.Label(
            popup, text=f"Your mood is: {mood_text}", fg=mood_color,
            bg="#23272A", font=("Segoe UI", 14)
        ).pack(pady=(5, 1))
        tk.Label(
            popup, text=comment, fg="white",
            bg="#23272A", font=("Segoe UI", 10, "italic")
        ).pack(pady=(0, 18))
        tk.Button(
            popup, text="OK", command=popup.destroy,
            bg="#3968C9", fg="white", font=("Segoe UI", 11, "bold"),
            activebackground="#27438B", activeforeground="white", relief="flat", bd=0,
            padx=20, pady=2
        ).pack(pady=10)

    def show_guardian():
        check_and_add_guardian_alert()
        popup = tk.Toplevel()
        popup.title("Guardian Dashboard")
        popup.geometry("700x450")
        popup.configure(bg="#23272A")
        popup.resizable(False, False)
        def get_current_alert_state():
            count, _, _ = count_below_threshold(return_lines=True)
            if count > 10:
                return "Armed", count
            else:
                return "Waiting", count

        state, since_last = get_current_alert_state()
        state_color = "red" if state == "Armed" else "lime green"
        tk.Label(
            popup,
            text=f"Current Alert State: {state}",
            fg=state_color,
            bg="#23272A",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(20, 5))
        tk.Label(
            popup,
            text=f"Negative entries since last alert: {since_last}",
            fg="#fff",
            bg="#23272A",
            font=("Segoe UI", 11)
        ).pack(pady=(0, 15))

        ALERTS_LOG_FILE = "alerts_log.json"
        def load_alert_history():
            if not os.path.exists(ALERTS_LOG_FILE):
                return []
            with open(ALERTS_LOG_FILE, "r") as f:
                return json.load(f)
        logs = load_alert_history()
        table_frame = tk.Frame(popup, bg="#23272A")
        table_frame.pack(pady=(10, 0), padx=8, fill="x")
        headers = ["Date/Time", "Neg. Count", "Status", "Reason Excerpt"]
        for col, title in enumerate(headers):
            tk.Label(
                table_frame, text=title, fg="#FFBD39", bg="#23272A",
                font=("Segoe UI", 10, "bold"), padx=10, pady=7
            ).grid(row=0, column=col, sticky="nsew")
        if logs:
            for i, alert in enumerate(logs[:12], start=1):
                excerpt = " | ".join(alert["reason_lines"][:2]) + ("..." if len(alert["reason_lines"]) > 2 else "")
                row_bg = "#262d34" if i % 2 else "#23272A"
                for col, val in enumerate([alert["date"], str(alert["negative_count"]), alert["status"], excerpt]):
                    col_fg = "#7cffc0" if col==2 and val=="Sent" else "#fff"
                    lbl = tk.Label(
                        table_frame, text=val, fg=col_fg,
                        bg=row_bg, font=("Segoe UI", 10), padx=8, pady=5, anchor="w", justify="left"
                    )
                    lbl.grid(row=i, column=col, sticky="nsew")
                def make_popup(idx=i-1):
                    def cb(event):
                        detail = logs[idx]
                        dtl = tk.Toplevel(popup)
                        dtl.title("Alert Details")
                        dtl.geometry("420x280")
                        dtl.configure(bg="#21252c")
                        tk.Label(dtl, text=f"Date: {detail['date']}", fg="#FFBD39", bg="#21252c",
                              font=("Segoe UI", 11, "bold")).pack(pady=(13,5))
                        tk.Label(dtl, text="Negative entries triggering the alert:",
                              fg="#fff", bg="#21252c", font=("Segoe UI", 10, "bold")).pack()
                        t = tk.Text(dtl, wrap="word", width=48, height=10, bg="#252930", fg="#fff", font=("Segoe UI",10))
                        t.insert("end", "\n".join(detail["reason_lines"]))
                        t.config(state="disabled")
                        t.pack(padx=12, pady=10)
                    return cb
                table_frame.grid_slaves(row=i, column=3)[0].bind("<Button-1>", make_popup())
        else:
            tk.Label(table_frame, text="No guardian alerts yet.", fg="#888", bg="#23272A", font=("Segoe UI", 11, "italic")).grid(row=1, column=0, columnspan=4, pady=30)
        tk.Label(
            popup, text="Tip: Click 'Reason Excerpt' to view full alert details.", fg="#85e1fa",
            bg="#23272A", font=("Segoe UI", 11, "italic")
        ).pack(pady=17)
        
    main_area = tk.Frame(root, bg="#1e1e1e")
    main_area.pack(expand=True, fill="both", padx=20, pady=20)
    app_name_label = tk.Label(
        main_area,
        text="MindTrack.AI",
        font=("Segoe UI", 36, "bold"),
        bg="#1e1e1e",
        fg="#2966e3"
    )
    app_name_label.pack(pady=(70, 10))
    quote = (
        '"The greatest weapon against stress is our ability to choose one thought over another."'
        "\n– William James"
    )
    quote_label = tk.Label(
        main_area,
        text=quote,
        font=("Segoe UI", 15, "italic"),
        bg="#1e1e1e",
        fg="#ffaa00",
        wraplength=650,
        justify="center"
    )
    quote_label.pack(pady=(8, 30))

    def open_settings(event=None):
        SettingsWindow(root, user_info, main_area, top_bar, sidebar, app_name_label, quote_label)
    settings_icon.bind("<Button-1>", open_settings)

    btn_live = create_sidebar_btn("Live Graph", "\U0001F4C8")
    btn_live.config(command=show_live_graph)
    btn_live.pack(fill="x", pady=(20, 5))

    btn_analysis = create_sidebar_btn("Analysis", "\U0001F4C9")
    btn_analysis.config(command=show_analysis)
    btn_analysis.pack(fill="x", pady=5)

    # Voice Recording Button
    voice_btn_text = tk.StringVar(value="🎤 Start Voice")
    voice_btn_color = tk.StringVar(value="#28a745")  # Green
    
    def toggle_voice_recording():
        if voice_recorder.is_recording:
            # Stop recording
            voice_recorder.stop_recording()
            voice_btn_text.set("🎤 Start Voice")
            voice_btn_color.set("#28a745")  # Green
            btn_voice.config(bg="#28a745", activebackground="#218838")
        else:
            # Start recording
            voice_recorder.start_recording()
            voice_btn_text.set("⏹️ Stop Voice")
            voice_btn_color.set("#dc3545")  # Red
            btn_voice.config(bg="#dc3545", activebackground="#c82333")
    
    btn_voice = tk.Button(
        sidebar, textvariable=voice_btn_text, bg="#28a745", fg="white",
        relief="flat", font=("Segoe UI", 10, "bold"), 
        activebackground="#218838", activeforeground="white",
        command=toggle_voice_recording, padx=10, pady=8
    )
    btn_voice.pack(fill="x", pady=5)

    # btn_guardian = create_sidebar_btn("Guardian", "\U0001F9D1\u200D\U0001F4BB")
    # btn_guardian.config(command=show_guardian)
    # btn_guardian.pack(fill="x", pady=5)
    root.mainloop()

    # # ========== Main Area ==========
    # main_area = tk.Frame(root, bg="#1e1e1e")
    # main_area.pack(expand=True, fill="both", padx=20, pady=20)

    # card_style = {
    #     "bg": "#2a2a2a",
    #     "fg": "#ffffff",
    #     "font": ("Segoe UI", 12, "bold"),
    #     "width": 25,
    #     "height": 5,
    #     "bd": 0,
    #     "relief": "flat"
    # }

    # graph_card = tk.Label(main_area, text="Last mood trend (work in progress)", **card_style)
    # graph_card.grid(row=0, column=0, padx=10, pady=10)

    # analysis_card = tk.Label(main_area, text="Analysis", **card_style)
    # analysis_card.grid(row=0, column=1, padx=10, pady=10)

    # guardian_card = tk.Label(main_area, text="Guardian Dashboard", **card_style)
    # guardian_card.grid(row=1, column=0, padx=10, pady=10)

    # root.mainloop()

# ====== SETTINGS PANEL FOR MINDTRACKAI - Interactive/Colorful Version ======
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, user_info, main_area, top_bar, sidebar, app_name_label, quote_label):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("440x580")
        self.configure(bg="#23272A")
        self.resizable(False, False)
        self.parent = parent
        self.dark_mode = True

        self.main_area = main_area
        self.top_bar = top_bar
        self.sidebar = sidebar
        self.app_name_label = app_name_label
        self.quote_label = quote_label

        # --- Modern, colorful tab row ---
        tab_frame = tk.Frame(self, bg="#23272A")
        tab_frame.pack(fill="x", pady=(18, 9))
        self.tabs = {}
        self.panels = {}

        # Configure the tab_frame to center the buttons
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(1, weight=0)
        tab_frame.grid_columnconfigure(2, weight=0)
        tab_frame.grid_columnconfigure(3, weight=0)
        tab_frame.grid_columnconfigure(4, weight=1)

        for i, tab_name in enumerate(("Preferences", "Account", "About")):
            btn = tk.Button(
                tab_frame, text=tab_name,
                bg="#f0f0f0" if i != 0 else "#2966e3",
                fg="#333" if i != 0 else "white",
                font=("Segoe UI", 12, "bold"), bd=0, padx=26, pady=13,
                activebackground="#2966e3", activeforeground="white",
                relief="flat",
                command=lambda n=tab_name: self.show_panel(n)
            )
            btn.grid(row=0, column=i+1, padx=(0 if i == 0 else 8, 0))
            self.tabs[tab_name] = btn

        container = tk.Frame(self, bg="#23272A")
        container.pack(fill="both", expand=True)
        self.panel_container = container

        self.create_preferences_panel()
        self.create_account_panel(user_info)
        self.create_about_panel()
        self.show_panel("Preferences")

    def show_panel(self, tab_name):
        for name, panel in self.panels.items():
            panel.forget()
        for name, btn in self.tabs.items():
            if name == tab_name:
                btn.config(bg="#2966e3", fg="white")
            else:
                btn.config(bg="#f0f0f0", fg="#333")
        self.panels[tab_name].pack(fill="both", expand=True)

    def create_preferences_panel(self):
        frame = tk.Frame(self.panel_container, bg="#23272A")
        tk.Label(
            frame, text="Theme Selection", bg="#23272A", fg="#fff",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=32, pady=(38, 14))

        self.theme = tk.StringVar(value="Dark")
        btn_light = tk.Button(
            frame, text="Light Mode", bg="#f0f0f0", fg="#333",
            font=("Segoe UI", 12, "bold"), bd=0, relief="flat", padx=34, pady=13,
            activebackground="#2966e3", activeforeground="white",
            command=lambda: self.set_theme("Light")
        )
        btn_dark = tk.Button(
            frame, text="Dark Mode", bg="#2966e3", fg="white",
            font=("Segoe UI", 12, "bold"), bd=0, relief="flat", padx=34, pady=13,
            activebackground="#2966e3", activeforeground="white",
            command=lambda: self.set_theme("Dark")
        )
        btn_light.place(x=40, y=78, width=145)
        btn_dark.place(x=200, y=78, width=145)
        self.btn_light = btn_light
        self.btn_dark = btn_dark
        frame.pack_propagate(False)

        def update_buttons():
            current = self.theme.get()
            if current == "Light":
                self.btn_light.config(bg="#2966e3", fg="white")
                self.btn_dark.config(bg="#f0f0f0", fg="#333")
            else:
                self.btn_dark.config(bg="#2966e3", fg="white")
                self.btn_light.config(bg="#f0f0f0", fg="#333")

        self.update_buttons = update_buttons

        self.set_theme = self._set_theme  # bind with full context
        self.update_buttons()
        self.panels["Preferences"] = frame

    def _set_theme(self, theme):
        self.theme.set(theme)
        self.update_buttons()
        if theme == "Light":
            bg = "#f2f2f2"
            fg = "#23272A"
            brand_fg = "#2966e3"
            quote_fg = "#e08000"
            sidebar_bg = "#eaeaea"
            topbar_bg = "#eaeaea"
            sidebar_fg = "#23272A"
        else:
            bg = "#1e1e1e"
            fg = "#cccccc"
            brand_fg = "#2966e3"
            quote_fg = "#ffaa00"
            sidebar_bg = "#111111"
            topbar_bg = "#1e1e1e"
            sidebar_fg = "white"

        # Main window background
        try:
            self.parent.configure(bg=bg)
        except Exception:
            pass

        # Sidebar
        try:
            self.sidebar.configure(bg=sidebar_bg)
            for w in self.sidebar.winfo_children():
                w.configure(bg=sidebar_bg, fg=sidebar_fg)
        except Exception:
            pass

        # Top bar
        try:
            self.top_bar.configure(bg=topbar_bg)
            for w in self.top_bar.winfo_children():
                w.configure(bg=topbar_bg, fg=fg)
        except Exception:
            pass

        # Main area and widgets
        try:
            self.main_area.configure(bg=bg)
            self.app_name_label.configure(bg=bg, fg=brand_fg)
            self.quote_label.configure(bg=bg, fg=quote_fg)
        except Exception:
            pass

    def create_account_panel(self, user_info):
        frame = tk.Frame(self.panel_container, bg="#23272A")
        with urllib.request.urlopen(user_info["picture"]) as u:
            raw_data = u.read()
        #self.image = tk.PhotoImage(data=base64.encodebytes(raw_data))
        image = ImageTk.PhotoImage(Image.open(io.BytesIO(raw_data)))
        name = user_info.get("name", "User") if hasattr(user_info, "get") else getattr(user_info, "name", "User")
        label = tk.Label(frame, image=image)
        label.image = image
        label.pack(pady=(50, 10))
        tk.Label(frame, text=f"Name: {name}", bg="#23272A", fg="#fff", font=("Segoe UI", 12)).pack(pady=3)
        self.panels["Account"] = frame

    def create_about_panel(self):
        frame = tk.Frame(self.panel_container, bg="#23272A")
        desc = (
            "MindTrackAI is an innovative AI-powered desktop companion designed\n"
            "to passively monitor typing behavior for early signs of emotional distress.\n\n"
            "Our goal is to provide a real-time, privacy-first solution that\n"
            "supports mental well-being, especially for students and remote workers,\n"
            "by offering insights and alerting guardians for timely intervention."
        )
        tk.Label(frame, text=desc, bg="#23272A", fg="#fff",
                 font=("Segoe UI", 11), justify="left", wraplength=380
                 ).pack(pady=(52, 8), padx=18)
        tk.Label(frame, text="Developed by: xEN coders", bg="#23272A",
                 fg="#aad6ff", font=("Segoe UI", 12, "italic")).pack(pady=(12, 8), padx=18)
        self.panels["About"] = frame
