import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys


def enable_windows_dpi_awareness():
    """Prevent Windows from bitmap-scaling the window, which can blur text."""
    if not sys.platform.startswith("win"):
        return
    try:
        import ctypes
        # Per-monitor DPI awareness v2 gives Tk crisp native text on scaled displays.
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError, TypeError):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError, TypeError):
            pass


enable_windows_dpi_awareness()

# ============================================================
# MediCampus - Stitch-inspired Campus Clinic UI
# Mobile-style desktop prototype based on the supplied Stitch
# reference: teal/navy healthcare cards, bottom navigation,
# profile/settings, appointments, schedules, records, staff.
# ============================================================

BG = "#F3F5F8"
NAVY = "#102744"
NAVY_2 = "#1B385D"
TEAL = "#6AAFC0"
TEAL_DARK = "#326F8B"
MINT = "#E5EFFB"
MINT_2 = "#F0F5FC"
WHITE = "#FFFFFF"
TEXT = "#1E2D42"
MUTED = "#788494"
BORDER = "#E1E7EF"
RED = "#E35B61"
RED_BG = "#FFE9EA"
YELLOW = "#F3B74F"
BLUE_BG = "#E8F1FF"
GREEN = "#20A77A"

class Card(tk.Frame):
    def __init__(self, parent, bg=WHITE, **kwargs):
        super().__init__(
            parent, bg=bg, highlightbackground=BORDER,
            highlightthickness=1, bd=0, **kwargs
        )

class MediCampusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediCampus — Campus Clinic Appointment & Health Record System")
        self.geometry("480x900")
        self.minsize(420, 700)
        self.configure(bg=BG)

        # Use Windows' native UI font and avoid tiny default text.
        for font_name in ("TkDefaultFont", "TkTextFont", "TkMenuFont",
                          "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont",
                          "TkIconFont", "TkTooltipFont"):
            try:
                tkfont = __import__("tkinter.font", fromlist=["nametofont"]).nametofont(font_name)
                tkfont.configure(family="Segoe UI", size=10)
            except (tk.TclError, RuntimeError):
                pass

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TEntry", padding=(10, 9), fieldbackground=WHITE,
                        foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER,
                        darkcolor=BORDER)
        style.map("TEntry", bordercolor=[("focus", TEAL)])

        self.student_id = "MC-2024-1048"
        self.student_name = "Maria Santos"
        self.department = "Department of Information Technology"
        self.email = "maria.santos@campus.edu.ph"
        self.phone = "+63 917 382 9014"

        self.logged_in = False
        self.staff_logged_in = False

        self.appointment = {
            "id": "APT-2026-1048",
            "clinic": "University Campus Health Center",
            "doctor": "Dr. Andrea Reyes, MD",
            "specialty": "General Medical Consultation",
            "date": "Fri, Oct 16, 2026",
            "time": "10:30 AM",
            "room": "Room 204",
            "status": "Confirmed",
        }

        self.records = [
            {
                "date": "Sep 18, 2026",
                "type": "Wellness Checkup",
                "doctor": "Dr. Andrea Reyes, MD",
                "notes": "Routine physical examination and wellness consultation.",
                "status": "COMPLETED",
            },
            {
                "date": "Aug 22, 2026",
                "type": "General Consultation",
                "doctor": "Dr. Miguel Santos, MD",
                "notes": "Clinic consultation recorded by campus health staff.",
                "status": "COMPLETED",
            },
            {
                "date": "Feb 10, 2026",
                "type": "Flu Vaccination",
                "doctor": "Nurse Ana Cruz, RN",
                "notes": "Campus influenza vaccination record.",
                "status": "VERIFIED RECORD",
            },
        ]

        self.schedules = [
            ("Today", "10:30 AM", "Open"),
            ("Today", "11:15 AM", "Open"),
            ("Today", "2:00 PM", "Booked"),
            ("Tomorrow", "9:00 AM", "Open"),
            ("Tomorrow", "1:00 PM", "Open"),
            ("Sat 26", "2:30 PM", "Open"),
            ("Sun 27", "3:45 PM", "Open"),
        ]

        self.current = "welcome"
        self.history = []

        # Fixed navigation dock stays visible while the page content scrolls.
        self.nav_dock = tk.Frame(self, bg=WHITE, highlightbackground=BORDER,
                                 highlightthickness=1)
        self.nav_visible = False

        # Scrollable mobile-style content area
        self.scroll_area = tk.Frame(self, bg=BG)
        self.scroll_area.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.scroll_area, bg=BG, highlightthickness=0, bd=0
        )
        self.scrollbar = tk.Scrollbar(
            self.scroll_area, orient="vertical",
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.canvas_window, width=e.width
            )
        )

        # Mouse-wheel scrolling on Windows/macOS and Linux.
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._scroll_up)
        self.canvas.bind_all("<Button-5>", self._scroll_down)

        self.show_welcome()

    # -------------------- scrolling --------------------
    def _on_mousewheel(self, event):
        # Windows/macOS send a signed delta; normalize it for Tk.
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_up(self, event):
        self.canvas.yview_scroll(-3, "units")

    def _scroll_down(self, event):
        self.canvas.yview_scroll(3, "units")

    # -------------------- helpers --------------------
    def clear(self):
        # Hide and clear the dock before each screen is rebuilt. Screens that
        # use bottom navigation call bottom_nav() after their content is ready.
        self.nav_dock.pack_forget()
        self.nav_visible = False
        for w in self.nav_dock.winfo_children():
            w.destroy()
        for w in self.content.winfo_children():
            w.destroy()
        self.after_idle(lambda: self.canvas.yview_moveto(0))

    def label(self, parent, text, size=10, color=TEXT, bold=False,
              bg=None, anchor="w", **kwargs):
        return tk.Label(
            parent, text=text, bg=bg or parent.cget("bg"),
            fg=color, anchor=anchor,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            **kwargs
        )

    def button(self, parent, text, command, primary=True, small=False):
        bg = NAVY if primary else WHITE
        fg = WHITE if primary else NAVY
        active = NAVY_2 if primary else MINT
        widget = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=active,
            activeforeground=fg, relief="flat", bd=0,
            highlightbackground=BORDER, highlightthickness=1 if not primary else 0,
            cursor="hand2", takefocus=True,
            font=("Segoe UI", 10 if small else 11, "bold"),
            padx=14 if small else 18, pady=9 if small else 12
        )
        widget.bind("<Enter>", lambda event, w=widget, color=active: w.configure(bg=color))
        widget.bind("<Leave>", lambda event, w=widget, color=bg: w.configure(bg=color))
        return widget

    def pill(self, parent, text, bg=MINT, fg=TEAL_DARK):
        return tk.Label(
            parent, text=text, bg=bg, fg=fg,
            font=("Segoe UI", 9, "bold"), padx=8, pady=4
        )

    def top_brand(self, title=None, profile=True):
        bar = tk.Frame(self.content, bg=BG)
        bar.pack(fill="x", padx=18, pady=(12, 4))

        brand = tk.Frame(bar, bg=BG)
        brand.pack(side="left")
        logo = tk.Canvas(brand, width=28, height=28, bg=BG, highlightthickness=0)
        logo.pack(side="left")
        logo.create_oval(2, 2, 26, 26, fill=TEAL, outline="")
        logo.create_text(14, 14, text="+", fill=WHITE,
                         font=("Segoe UI", 15, "bold"))
        txt = tk.Frame(brand, bg=BG)
        txt.pack(side="left", padx=6)
        self.label(txt, "CAMPUS HEALTH", 7, TEAL_DARK, True).pack(anchor="w")
        self.label(txt, "MediCampus", 12, NAVY, True).pack(anchor="w")

        right = tk.Frame(bar, bg=BG)
        right.pack(side="right")
        if profile:
            tk.Button(
                right, text="◔", command=self.show_profile,
                bg=BG, fg=NAVY, activebackground=BG,
                relief="flat", bd=0, font=("Segoe UI", 14, "bold"),
                cursor="hand2"
            ).pack(side="right", padx=(7, 0))
        tk.Button(
            right, text="♧", command=lambda: messagebox.showinfo(
                "Notifications", "No new clinic notifications."
            ),
            bg=BG, fg=MUTED, activebackground=BG,
            relief="flat", bd=0, font=("Segoe UI", 13),
            cursor="hand2"
        ).pack(side="right")

        if title:
            self.label(self.content, title, 18, NAVY, True).pack(
                anchor="w", padx=20, pady=(10, 4)
            )

    def back_header(self, title, subtitle=None):
        bar = tk.Frame(self.content, bg=BG)
        bar.pack(fill="x", padx=18, pady=(12, 4))
        tk.Button(
            bar, text="‹", command=self.go_back,
            bg=BG, fg=NAVY, activebackground=BG,
            relief="flat", bd=0, font=("Segoe UI", 24, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=(0, 5))
        box = tk.Frame(bar, bg=BG)
        box.pack(side="left", fill="x", expand=True)
        self.label(box, title, 18, NAVY, True).pack(anchor="w")
        if subtitle:
            self.label(box, subtitle, 8, MUTED).pack(anchor="w", pady=(2, 0))

    def bottom_nav(self, active="Home"):
        for w in self.nav_dock.winfo_children():
            w.destroy()
        items = [
            ("⌂", "Home", self.show_dashboard),
            ("▦", "Schedules", self.show_schedules),
            ("▤", "Records", self.show_history),
            ("●", "Profile", self.show_profile),
        ]
        for icon, name, cmd in items:
            selected = name == active
            color = TEAL if selected else MUTED
            cell = tk.Frame(self.nav_dock, bg=MINT_2 if selected else WHITE)
            cell.pack(side="left", expand=True, fill="both", padx=3, pady=4)
            tk.Button(
                cell, text=f"{icon}  {name}", command=cmd,
                bg=MINT_2 if selected else WHITE, fg=color,
                activebackground=MINT, activeforeground=TEAL_DARK,
                relief="flat", bd=0, font=("Segoe UI", 9, "bold"),
                cursor="hand2", padx=4, pady=10
            ).pack(fill="both", expand=True)
        self.nav_dock.pack(side="bottom", fill="x", padx=10, pady=(0, 6))
        self.nav_visible = True

    def go_back(self):
        if self.current in ("schedules", "history", "profile"):
            self.show_dashboard()
        elif self.current in ("booking", "details"):
            self.show_schedules()
        elif self.current == "login":
            self.show_welcome()
        elif self.current == "record_visit":
            self.show_staff()
        else:
            self.show_dashboard()

    # -------------------- welcome/login --------------------
    def show_welcome(self):
        self.current = "welcome"
        self.clear()

        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", padx=22, pady=(22, 0))
        self.pill(top, "OFFICIAL UNIVERSITY HEALTH NETWORK").pack(anchor="w")

        hero = tk.Frame(self.content, bg=BG)
        hero.pack(fill="both", expand=True, padx=22)

        logo = tk.Canvas(hero, width=82, height=82, bg=BG, highlightthickness=0)
        logo.pack(pady=(36, 12))
        logo.create_oval(4, 4, 78, 78, fill=TEAL, outline="")
        logo.create_text(41, 41, text="+", fill=WHITE,
                         font=("Segoe UI", 38, "bold"))

        self.label(hero, "MediCampus", 28, NAVY, True, anchor="center").pack()
        self.label(
            hero, "Campus Clinic Appointment &\nHealth Record System",
            12, TEXT, True, anchor="center", justify="center"
        ).pack(pady=(4, 8))
        self.label(
            hero,
            "Your health, wellness, and campus care in one tap.\n"
            "Dedicated support for students, faculty, and clinical visitors.",
            8, MUTED, anchor="center", justify="center"
        ).pack()

        features = [
            ("＋", "Instant Clinic Booking", "Same-day triage, checkups & campus care"),
            ("▣", "Digital Health Records", "Appointments, visit notes & clinic history"),
            ("◷", "Campus Doctor Schedules", "Real-time room status & physician availability"),
        ]
        for icon, title, desc in features:
            c = Card(hero)
            c.pack(fill="x", pady=4)
            tk.Label(c, text=icon, bg=MINT, fg=TEAL_DARK,
                     font=("Segoe UI", 16, "bold"), width=3, pady=6).pack(
                         side="left", padx=10, pady=10
                     )
            info = tk.Frame(c, bg=WHITE)
            info.pack(side="left", fill="x", expand=True, pady=8, padx=(0, 8))
            self.label(info, title, 9, NAVY, True).pack(anchor="w")
            self.label(info, desc, 7, MUTED, wraplength=285).pack(anchor="w")

        self.button(hero, "Get Started  →", self.show_login).pack(fill="x", pady=(8, 5))
        tk.Button(
            hero, text="Are you clinic staff?  Staff Portal Login",
            command=self.show_staff_login, bg=BG, fg=TEAL_DARK,
            activebackground=BG, relief="flat", bd=0,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack()

        self.label(self.content, "v2.5  •  Campus Health Services", 7, MUTED,
                   anchor="center").pack(pady=(0, 8))

    def show_login(self):
        self.current = "login"
        self.clear()
        self.back_header("Welcome Back", "Sign in to access your student health portal")

        box = tk.Frame(self.content, bg=BG)
        box.pack(fill="both", expand=True, padx=24, pady=18)

        switch = tk.Frame(box, bg=WHITE, highlightbackground=BORDER,
                           highlightthickness=1)
        switch.pack(fill="x", pady=(0, 14))
        tk.Button(switch, text="Student / Faculty", command=self.show_login,
                  bg=MINT, fg=NAVY, activebackground=BLUE_BG, relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=8
                  ).pack(side="left", fill="x", expand=True, padx=3, pady=3)
        tk.Button(switch, text="Clinic Staff", command=self.show_staff_login,
                  bg=WHITE, fg=TEAL_DARK, activebackground=BLUE_BG, relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=8
                  ).pack(side="left", fill="x", expand=True, padx=3, pady=3)

        info = tk.Frame(box, bg=BLUE_BG)
        info.pack(fill="x", pady=(0, 18))
        self.label(
            info,
            "Campus SSO enabled. Use your official @campus.edu credentials.",
            7, NAVY, wraplength=350, justify="left"
        ).pack(anchor="w", padx=12, pady=9)

        self.label(box, "Student ID or Campus Email", 8, TEXT, True).pack(anchor="w")
        sid = ttk.Entry(box, font=("Segoe UI", 11))
        sid.insert(0, "MC-2024-1048")
        sid.pack(fill="x", ipady=7, pady=(5, 13))

        self.label(box, "Password", 8, TEXT, True).pack(anchor="w")
        pwd = ttk.Entry(box, show="•", font=("Segoe UI", 11))
        pwd.insert(0, "1234")
        pwd.pack(fill="x", ipady=7, pady=(5, 13))

        keep = tk.BooleanVar(value=True)
        tk.Checkbutton(
            box, text="Keep me securely signed in on this device",
            variable=keep, bg=BG, fg=MUTED, activebackground=BG,
            font=("Segoe UI", 9), relief="flat"
        ).pack(anchor="w", pady=(0, 12))

        def login():
            if sid.get().strip() in ("MC-2024-1048", "maria.santos@campus.edu.ph") and pwd.get() == "1234":
                self.logged_in = True
                self.show_dashboard()
            else:
                messagebox.showerror("Login failed", "Use the demo student account: MC-2024-1048 / 1234")

        self.button(box, "Sign In  →", login).pack(fill="x")
        def fill_demo_account():
            sid.delete(0, "end")
            sid.insert(0, "MC-2024-1048")
            pwd.delete(0, "end")
            pwd.insert(0, "1234")
            messagebox.showinfo("Demo account", "Demo credentials filled in. Select Sign In to continue.")
        self.label(box, "DEMO ACCESS", 7, MUTED, anchor="center").pack(pady=10)
        self.button(box, "Fill Demo Credentials", fill_demo_account,
                    primary=False).pack(fill="x")

        tk.Button(
            box, text="New student on campus?  Create an account / Register",
            command=lambda: messagebox.showinfo(
                "Student Registration",
                "Registration is not connected to a real university account system in this demo.\n\n"
                "For this prototype, use the demo student account to explore the screens."
            ),
            bg=BG, fg=TEAL_DARK, activebackground=BG, activeforeground=NAVY,
            relief="flat", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack(pady=13)

        care = tk.Frame(box, bg=BG)
        care.pack(fill="x")
        for title, value in [("Urgent Care", "8 min wait"), ("Mental Health", "Drop-ins Open")]:
            c = Card(care)
            c.pack(side="left", fill="x", expand=True, padx=3)
            self.label(c, title, 7, NAVY, True, anchor="center").pack(pady=(8, 0))
            self.label(c, value, 7, TEAL_DARK, True, anchor="center").pack(pady=(2, 8))
            action = (lambda: messagebox.showinfo("Urgent Care", "For emergencies, contact local emergency services or campus clinic staff.")) if title == "Urgent Care" else (lambda: messagebox.showinfo("Mental Health Support", "Please contact the campus counseling service or clinic for current drop-in availability."))
            for widget in (c, *c.winfo_children()):
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda event, callback=action: callback())

    # -------------------- student dashboard --------------------
    def show_dashboard(self):
        self.current = "dashboard"
        self.clear()
        self.top_brand()

        # Navy hero panel inspired by the supplied mobile-app reference.
        hero = tk.Frame(self.content, bg=NAVY)
        hero.pack(fill="x", padx=14, pady=(5, 10))
        hero_inner = tk.Frame(hero, bg=NAVY)
        hero_inner.pack(fill="x", padx=15, pady=13)
        self.label(hero_inner, "CAMPUS HEALTH • STUDENT SERVICES", 8, "#B9D8F3", True, bg=NAVY).pack(anchor="w")
        hero_row = tk.Frame(hero_inner, bg=NAVY)
        hero_row.pack(fill="x", pady=(5, 1))
        hero_copy = tk.Frame(hero_row, bg=NAVY)
        hero_copy.pack(side="left", fill="x", expand=True)
        self.label(hero_copy, "Your health,\nour priority.", 19, WHITE, True, bg=NAVY, justify="left").pack(anchor="w")
        self.label(hero_copy, "Appointments made simple.", 9, "#DCE8F7", bg=NAVY).pack(anchor="w", pady=(4, 0))
        icon = tk.Canvas(hero_row, width=68, height=68, bg=NAVY, highlightthickness=0)
        icon.pack(side="right", padx=(6, 0))
        icon.create_oval(5, 5, 63, 63, fill=NAVY_2, outline="#3D7185", width=2)
        icon.create_text(34, 34, text="+", fill="#B9D8F3", font=("Segoe UI", 37, "bold"))

        welcome = tk.Frame(self.content, bg=BG)
        welcome.pack(fill="x", padx=20, pady=(4, 7))
        self.label(welcome, f"Good morning, {self.student_name.split()[0]}! 👋",
                   16, NAVY, True).pack(anchor="w")
        self.label(welcome, f"{self.student_id}  •  {self.department}",
                   8, MUTED).pack(anchor="w")

        notice = tk.Frame(self.content, bg=MINT, highlightbackground="#D1E0F2", highlightthickness=1)
        notice.pack(fill="x", padx=18, pady=5)
        self.label(notice, "CAMPUS HEALTH NOTICE", 7, TEAL_DARK, True).pack(
            anchor="w", padx=12, pady=(9, 2)
        )
        self.label(
            notice,
            "Annual flu shots and wellness checkups are available at the University Campus Clinic.",
            8, TEXT, wraplength=345
        ).pack(anchor="w", padx=12, pady=(0, 5))
        self.label(notice, "Walk-ins welcome  •  Open Now", 7, TEAL_DARK, True).pack(
            anchor="w", padx=12, pady=(0, 9)
        )

        head = tk.Frame(self.content, bg=BG)
        head.pack(fill="x", padx=20, pady=(8, 2))
        self.label(head, "Quick actions", 14, NAVY, True).pack(side="left")
        self.label(head, "Tap to launch", 7, MUTED).pack(side="right")

        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="x", padx=16)
        items = [
            ("＋", "Book Visit", "Find available slots", self.show_schedules),
            ("◷", "Schedules", "Doctors & hours", self.show_schedules),
            ("▣", "Appointments", "1 Upcoming slot", self.show_details),
            ("♥", "Visit History", "Lab & Rx records", self.show_history),
        ]
        for i, (icon, title, sub, cmd) in enumerate(items):
            c = tk.Button(
                actions, text=f"{icon}\n{title}\n{sub}", command=cmd,
                bg="#FFFFFF", fg=NAVY, activebackground=MINT,
                activeforeground=NAVY, relief="flat", bd=0,
                highlightbackground=BORDER, highlightthickness=1,
                cursor="hand2", font=("Segoe UI", 10, "bold"),
                width=15, height=4, justify="left", anchor="nw",
                padx=12, pady=9
            )
            c.grid(row=i//2, column=i%2, sticky="nsew", padx=4, pady=4)
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        head2 = tk.Frame(self.content, bg=BG)
        head2.pack(fill="x", padx=20, pady=(9, 3))
        self.label(head2, "Next appointment", 14, NAVY, True).pack(side="left")
        self.label(head2, "View All", 7, TEAL_DARK, True).pack(side="right")

        c = tk.Frame(self.content, bg=NAVY, highlightbackground=NAVY, highlightthickness=1)
        c.pack(fill="x", padx=18, pady=4)
        row = tk.Frame(c, bg=NAVY)
        row.pack(fill="x", padx=14, pady=(11, 4))
        self.pill(row, "CONFIRMED", "#DDEAF8", NAVY).pack(side="right")
        self.label(row, f"{self.appointment['date']} • {self.appointment['time']}", 8, "#BFD3EA", True, bg=NAVY).pack(side="left")
        self.label(c, self.appointment["doctor"], 12, WHITE, True, bg=NAVY).pack(anchor="w", padx=14)
        self.label(c, self.appointment["specialty"], 9, "#DCE7F5", bg=NAVY).pack(anchor="w", padx=14, pady=2)
        self.label(c, f"{self.appointment['clinic']} • {self.appointment['room']}", 8, "#BFD0E4", bg=NAVY, wraplength=330).pack(
            anchor="w", padx=14, pady=(1, 9)
        )
        rr = tk.Frame(c, bg=NAVY)
        rr.pack(fill="x", padx=14, pady=(0, 12))
        self.button(rr, "View Details →", self.show_details).pack(side="left")
        self.button(rr, "Reschedule", self.show_schedules, primary=False, small=True).pack(
            side="right"
        )

        self.bottom_nav("Home")

    # -------------------- schedules/booking --------------------
    def show_schedules(self):
        """Interactive Stitch-inspired clinic schedule with date, clinic, and slot selection."""
        self.current = "schedules"
        self.clear()
        self.top_brand(profile=False)

        self.label(self.content, "LIVE AVAILABILITY FEED  •  Updated just now",
                   8, TEAL_DARK, True).pack(anchor="w", padx=20, pady=(4, 2))
        self.label(self.content, "Campus Clinic Schedules", 20, NAVY, True).pack(
            anchor="w", padx=18, pady=(2, 2))
        self.label(self.content, "Check provider availability and walk-in consultation hours",
                   9, MUTED, wraplength=380, justify="left").pack(
            anchor="w", padx=18, pady=(0, 10))

        self.schedule_filter = getattr(self, "schedule_filter", "All Campus Clinics")
        self.schedule_day = getattr(self, "schedule_day", "Tue 24")
        self.schedule_time = getattr(self, "schedule_time", None)

        filters = tk.Frame(self.content, bg=BG)
        filters.pack(fill="x", padx=14, pady=(0, 9))
        for name in ("All Campus Clinics", "Main Student Infirmary", "Sports"):
            selected = self.schedule_filter == name
            tk.Button(filters, text=name, command=lambda n=name: self._set_schedule_filter(n),
                      bg=NAVY if selected else BLUE_BG, fg=WHITE if selected else NAVY,
                      activebackground=TEAL, activeforeground=WHITE,
                      relief="flat", bd=0, font=("Segoe UI", 8, "bold"),
                      padx=8, pady=7, cursor="hand2").pack(side="left", padx=2)

        monthrow = tk.Frame(self.content, bg=BG)
        monthrow.pack(fill="x", padx=18, pady=(0, 4))
        self.label(monthrow, "▦  October 2026", 9, NAVY, True).pack(side="left")
        self.label(monthrow, "Week 4 • Campus hours", 8, TEAL_DARK, True).pack(side="right")

        days = tk.Frame(self.content, bg=BLUE_BG)
        days.pack(fill="x", padx=18, pady=(0, 11))
        for day, date in [("Mon", "23"), ("Tue", "24"), ("Wed", "25"),
                          ("Thu", "26"), ("Fri", "27"), ("Sat", "28")]:
            key = f"{day} {date}"
            chosen = self.schedule_day == key
            cell = tk.Button(days, text=f"{day}\\n{date}",
                             command=lambda d=key: self._set_schedule_day(d),
                             bg=NAVY if chosen else WHITE,
                             fg=WHITE if chosen else NAVY,
                             activebackground=TEAL, activeforeground=WHITE,
                             relief="flat", bd=0, font=("Segoe UI", 9, "bold"),
                             padx=4, pady=5, cursor="hand2")
            cell.pack(side="left", expand=True, fill="both", padx=2, pady=4)

        heading = tk.Frame(self.content, bg=BG)
        heading.pack(fill="x", padx=18, pady=(0, 5))
        self.label(heading, f"{self.schedule_day.split()[0]} Schedules", 12, NAVY, True).pack(side="left")
        self.pill(heading, "3 providers", BLUE_BG, TEAL_DARK).pack(side="left", padx=6)
        tk.Button(heading, text="Map View ›", command=self._show_clinic_map,
                  bg=BG, fg=TEAL_DARK, activebackground=BG, relief="flat",
                  bd=0, font=("Segoe UI", 8, "bold"), cursor="hand2").pack(side="right")

        providers = [
            ("Dr. Evelyn Vance, MD", "General Medicine", "Main Student Infirmary • Room 204",
             "08:30 AM – 12:00 PM  |  01:30 PM – 04:30 PM",
             ["09:30 AM", "10:30 AM", "11:15 AM", "02:00 PM", "03:30 PM"], "Available today"),
            ("Dr. Marcus Reyes, MD", "Family Medicine", "Main Student Infirmary • Room 208",
             "09:00 AM – 12:00 PM  |  01:00 PM – 03:00 PM",
             ["09:00 AM", "10:00 AM", "01:30 PM"], "Few slots left"),
            ("Nurse Sarah Cruz, RN", "Immunization & Triage", "West Pavilion • Triage Desk",
             "08:00 AM – 05:00 PM • Continuous",
             [], "Walk-ins welcome"),
        ]
        if self.schedule_filter == "Main Student Infirmary":
            providers = providers[:2]
        elif self.schedule_filter == "Sports":
            providers = [("Nurse Sarah Cruz, RN", "Sports Physiotherapy & Triage",
                          "Sports Pavilion • Treatment Room", "10:00 AM – 04:00 PM",
                          ["10:30 AM", "11:30 AM", "02:30 PM"], "Available today")]

        for name, specialty, location, hours, times, status in providers:
            c = Card(self.content)
            c.pack(fill="x", padx=18, pady=4)
            head = tk.Frame(c, bg=WHITE)
            head.pack(fill="x", padx=10, pady=(9, 3))
            avatar = tk.Label(head, text="✚", bg=MINT, fg=TEAL_DARK,
                              font=("Segoe UI", 15, "bold"), width=3, pady=5)
            avatar.pack(side="left", padx=(0, 8))
            details = tk.Frame(head, bg=WHITE)
            details.pack(side="left", fill="x", expand=True)
            self.label(details, name, 10, NAVY, True).pack(anchor="w")
            self.label(details, specialty, 8, MUTED).pack(anchor="w")
            self.pill(head, status, MINT, TEAL_DARK).pack(side="right", anchor="n")
            self.label(c, "♧  " + location, 8, MUTED, wraplength=350).pack(
                anchor="w", padx=12, pady=(1, 5))
            self.label(c, "◷  " + hours, 8, TEXT).pack(anchor="w", padx=12, pady=2)
            if times:
                self.label(c, "SELECT AVAILABLE TIME", 7, TEAL_DARK, True).pack(
                    anchor="w", padx=12, pady=(8, 3))
                time_row = tk.Frame(c, bg=WHITE)
                time_row.pack(fill="x", padx=8, pady=(0, 7))
                for t in times:
                    selected = self.schedule_time == t
                    tk.Button(time_row, text=t, command=lambda tt=t: self._select_schedule_time(tt),
                              bg=TEAL if selected else BLUE_BG,
                              fg=WHITE if selected else NAVY,
                              activebackground=TEAL, activeforeground=WHITE,
                              relief="flat", bd=0, font=("Segoe UI", 8, "bold"),
                              padx=7, pady=5, cursor="hand2").pack(side="left", padx=3, pady=2)
                bottom = tk.Frame(c, bg=WHITE)
                bottom.pack(fill="x", padx=10, pady=(0, 9))
                tk.Button(bottom, text="ⓘ  Doctor Bio", command=lambda n=name, s=specialty:
                          messagebox.showinfo("Provider information", f"{n}\\n{s}\\nCampus Clinic staff (demo profile)."),
                          bg=WHITE, fg=TEAL_DARK, activebackground=BLUE_BG,
                          relief="flat", bd=0, font=("Segoe UI", 8, "bold"),
                          cursor="hand2").pack(side="left")
                self.button(bottom, "Select & Book  →",
                            lambda ts=times: self._book_selected_schedule(ts),
                            small=True).pack(side="right")
            else:
                note = tk.Frame(c, bg=BLUE_BG)
                note.pack(fill="x", padx=10, pady=5)
                self.label(note, "Fast-track student digital queue\\nNo prior slot needed for routine triage or vaccination.",
                           8, NAVY, wraplength=300).pack(anchor="w", padx=8, pady=7)
                self.button(c, "Join Queue  →", self._join_clinic_queue,
                            small=True).pack(anchor="e", padx=10, pady=(0, 9))

        if self.schedule_time:
            dock = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            dock.pack(fill="x", padx=18, pady=(8, 10))
            self.label(dock, f"ACTIVE CHOICE  •  {self.schedule_day} at {self.schedule_time}",
                       8, MUTED, True).pack(side="left", padx=9, pady=10)
            self.button(dock, "Proceed to Book  →",
                        lambda: self.show_booking(self.schedule_day, self.schedule_time),
                        small=True).pack(side="right", padx=7, pady=5)

        self.bottom_nav("Schedules")

    def _set_schedule_filter(self, value):
        self.schedule_filter = value
        self.schedule_time = None
        self.show_schedules()

    def _set_schedule_day(self, value):
        self.schedule_day = value
        self.schedule_time = None
        self.show_schedules()

    def _select_schedule_time(self, value):
        self.schedule_time = value
        self.show_schedules()

    def _book_selected_schedule(self, times):
        if self.schedule_time not in times:
            self.schedule_time = times[0]
        self.show_booking(self.schedule_day, self.schedule_time)

    def _join_clinic_queue(self):
        messagebox.showinfo("Demo queue", "You have been added to the sample walk-in queue. Please check in at the clinic desk.")
    def _show_clinic_map(self):
        messagebox.showinfo(
            "Campus clinic locations",
            "MAIN STUDENT INFIRMARY\\n2nd Floor • Main Campus Center\\n\\n"
            "SPORTS PAVILION\\nWest campus • Physiotherapy and triage\\n\\n"
            "This is a sample location guide; it does not use live maps."
        )

    def show_booking(self, selected_date="Tomorrow", selected_time="10:30 AM"):
        self.current = "booking"
        self.clear()
        self.back_header("Book a Clinic Visit", "Review your appointment before confirming")

        c = Card(self.content)
        c.pack(fill="x", padx=18, pady=7)
        self.label(c, "OPEN FOR APPOINTMENTS", 7, TEAL_DARK, True).pack(
            anchor="w", padx=12, pady=(10, 2)
        )
        self.label(c, "University Campus Clinic", 14, NAVY, True).pack(anchor="w", padx=12)
        self.label(c, "Main Campus • 2nd Floor • Campus Health Center",
                   7, MUTED).pack(anchor="w", padx=12, pady=(1, 8))

        self.label(c, "✓  General Medical Consultation", 9, NAVY, True).pack(
            anchor="w", padx=12, pady=6
        )
        self.label(c, "Standard consultation • approximately 20 min",
                   7, MUTED).pack(anchor="w", padx=28)

        self.label(c, "ATTENDING CLINICIAN", 7, TEAL_DARK, True).pack(
            anchor="w", padx=12, pady=(12, 2)
        )
        self.label(c, self.appointment["doctor"], 9, NAVY, True).pack(anchor="w", padx=12)
        self.label(c, "Campus Certified Clinician", 7, MUTED).pack(anchor="w", padx=12, pady=(1, 9))

        rows = [
            ("Appointment Date", f"{selected_date}, 2026"),
            ("Time", selected_time),
            ("Reason for Visit", "Mild flu symptoms and throat irritation for 2 days"),
        ]
        for name, value in rows:
            r = tk.Frame(c, bg=WHITE)
            r.pack(fill="x", padx=12, pady=5)
            self.label(r, name, 7, MUTED).pack(anchor="w")
            self.label(r, value, 8, NAVY, True).pack(anchor="w", pady=(1, 0))

        warning = tk.Frame(self.content, bg=RED_BG)
        warning.pack(fill="x", padx=18, pady=6)
        self.label(
            warning, "URGENT CLINIC TRIAGE NOTICE\n"
            "If you experience severe or urgent symptoms, seek emergency care.",
            7, RED, True, wraplength=350, justify="left"
        ).pack(anchor="w", padx=11, pady=8)

        self.button(
            self.content, "Confirm Appointment  →",
            lambda: self.confirm_booking(selected_date, selected_time)
        ).pack(fill="x", padx=18, pady=4)
        self.button(self.content, "Cancel and return to schedules",
                    self.show_schedules, primary=False).pack(fill="x", padx=18, pady=4)

    def confirm_booking(self, d, t):
        self.appointment["date"] = f"{d}, 2026"
        self.appointment["time"] = t
        self.appointment["status"] = "Confirmed"
        messagebox.showinfo("Appointment confirmed",
                            "Your MediCampus appointment has been booked.")
        self.show_details()

    # -------------------- appointment details --------------------
    def show_details(self):
        self.current = "details"
        self.clear()
        self.top_brand(profile=False)
        self.back_header("Appointment Details", "Your upcoming campus clinic visit")

        c = Card(self.content)
        c.pack(fill="x", padx=18, pady=7)
        status = self.appointment.get("status", "Confirmed")
        status_bg, status_fg = (RED_BG, RED) if status in ("Cancelled", "Completed") else (MINT, TEAL_DARK)
        self.pill(c, f"BOOKING STATUS  •  {status}", status_bg, status_fg).pack(anchor="w", padx=12, pady=(10, 4))
        self.label(c, self.appointment["doctor"], 10, NAVY, True).pack(anchor="w", padx=12)
        self.label(c, self.appointment["specialty"], 7, MUTED).pack(anchor="w", padx=12)
        self.label(c, "Campus Certified Clinician", 7, TEAL_DARK, True).pack(
            anchor="w", padx=12, pady=(1, 8)
        )

        for title, value in [
            ("SCHEDULED TIME", f"{self.appointment['date']} • {self.appointment['time']}"),
            ("CLINIC DESTINATION", f"{self.appointment['clinic']} • {self.appointment['room']}"),
            ("STUDENT INFORMATION", f"{self.student_name} • {self.student_id}"),
        ]:
            r = tk.Frame(c, bg=WHITE)
            r.pack(fill="x", padx=12, pady=6)
            self.label(r, title, 7, TEAL_DARK, True).pack(anchor="w")
            self.label(r, value, 8, NAVY, True).pack(anchor="w", pady=(2, 0))

        note = tk.Frame(self.content, bg=BLUE_BG)
        note.pack(fill="x", padx=18, pady=6)
        self.label(
            note,
            "Before your visit\nPlease arrive 10 minutes early and bring your campus ID.",
            7, NAVY, wraplength=350, justify="left"
        ).pack(anchor="w", padx=11, pady=9)

        self.button(self.content, "Back to Dashboard  →",
                    self.show_dashboard).pack(fill="x", padx=18, pady=5)
        if self.appointment.get("status") == "Confirmed":
            self.button(self.content, "Cancel Appointment",
                        self.cancel_appointment, primary=False).pack(fill="x", padx=18, pady=4)

    def cancel_appointment(self):
        if not messagebox.askyesno("Cancel appointment", "Cancel this clinic appointment?"):
            return
        self.appointment["status"] = "Cancelled"
        messagebox.showinfo("Appointment cancelled",
                            "Your appointment has been cancelled.")
        self.show_details()

    # -------------------- records/history --------------------
    def show_history(self):
        self.current = "history"
        self.clear()
        self.top_brand(profile=False)
        self.back_header("Visit History", "Clinic visits and health record entries")

        pass_info = tk.Frame(self.content, bg=MINT)
        pass_info.pack(fill="x", padx=18, pady=5)
        self.label(pass_info, "STUDENT HEALTH PASS", 7, TEAL_DARK, True).pack(
            anchor="w", padx=11, pady=(9, 2)
        )
        self.label(pass_info, "4 Completed", 9, NAVY, True).pack(anchor="w", padx=11)
        self.label(pass_info, f"{self.student_name} • {self.student_id}",
                   7, MUTED).pack(anchor="w", padx=11, pady=(1, 8))

        tabs = tk.Frame(self.content, bg=BG)
        tabs.pack(fill="x", padx=18, pady=5)
        self.history_filter = getattr(self, "history_filter", "All Visits")
        filter_specs = [("All Visits", "All Visits (4)"), ("Consultations", "Consultations"),
                        ("Immunizations", "Immunizations")]
        for key, caption in filter_specs:
            selected = self.history_filter == key
            tk.Button(tabs, text=caption, command=lambda value=key: self.set_history_filter(value),
                      bg=TEAL if selected else WHITE, fg=WHITE if selected else NAVY,
                      activebackground=BLUE_BG, activeforeground=NAVY,
                      font=("Segoe UI", 9, "bold"), padx=8, pady=6,
                      relief="flat", bd=0, highlightbackground=BORDER,
                      highlightthickness=1, cursor="hand2").pack(side="left", padx=2)

        filtered = self.records
        if self.history_filter == "Consultations":
            filtered = [r for r in self.records if any(word in r["type"].lower()
                       for word in ("consult", "wellness", "checkup"))]
        elif self.history_filter == "Immunizations":
            filtered = [r for r in self.records if any(word in r["type"].lower()
                       for word in ("vaccin", "immuniz"))]
        if not filtered:
            self.label(self.content, f"No {self.history_filter.lower()} records found.",
                       9, MUTED, anchor="center").pack(fill="x", padx=18, pady=28)
        for rec in filtered:
            c = Card(self.content)
            c.pack(fill="x", padx=18, pady=4)
            row = tk.Frame(c, bg=WHITE)
            row.pack(fill="x", padx=11, pady=(8, 2))
            self.label(row, rec["date"], 7, MUTED).pack(side="left")
            self.pill(row, rec["status"], MINT, TEAL_DARK).pack(side="right")
            self.label(c, rec["type"], 10, NAVY, True).pack(anchor="w", padx=11)
            self.label(c, rec["doctor"], 7, MUTED).pack(anchor="w", padx=11, pady=1)
            self.label(c, "CLINICAL NOTES", 7, TEAL_DARK, True).pack(
                anchor="w", padx=11, pady=(6, 1)
            )
            self.label(c, rec["notes"], 7, TEXT, wraplength=350,
                       justify="left").pack(anchor="w", padx=11, pady=(0, 8))
            def show_record_details(record=rec):
                messagebox.showinfo(
                    "Visit Record",
                    f"Date: {record['date']}\nVisit: {record['type']}\n"
                    f"Clinician: {record['doctor']}\nStatus: {record['status']}\n\n"
                    f"Clinical notes: {record['notes']}\n\n"
                    "Demo data only — this prototype is not a secure medical record system."
                )
            stack = [c]
            while stack:
                widget = stack.pop()
                stack.extend(widget.winfo_children())
                if isinstance(widget, (tk.Frame, tk.Label)):
                    widget.configure(cursor="hand2")
                    widget.bind("<Button-1>", lambda event, callback=show_record_details: callback())

        self.bottom_nav("Records")

    def set_history_filter(self, value):
        self.history_filter = value
        self.show_history()

    # -------------------- profile/settings --------------------
    def show_profile(self):
        self.current = "profile"
        self.clear()
        self.top_brand(profile=False)
        self.back_header("Profile", "Manage your student health account")

        c = Card(self.content)
        c.pack(fill="x", padx=18, pady=7)
        avatar = tk.Canvas(c, width=66, height=66, bg=WHITE, highlightthickness=0)
        avatar.pack(pady=(12, 4))
        avatar.create_oval(5, 5, 61, 61, fill=MINT, outline="")
        avatar.create_text(33, 33, text="MS", fill=TEAL_DARK,
                           font=("Segoe UI", 17, "bold"))
        self.label(c, self.student_name, 13, NAVY, True, anchor="center").pack()
        self.label(c, "Undergraduate Student • Junior Year", 7, MUTED,
                   anchor="center").pack()
        self.pill(c, f"ID  {self.student_id}", MINT, TEAL_DARK).pack(pady=(5, 12))

        self.label(self.content, "Clinical & Student Record", 12, NAVY, True).pack(
            anchor="w", padx=20, pady=(8, 4)
        )
        for title, value in [
            ("Academic Department", self.department),
            ("Campus SSO Email", self.email),
            ("Phone Number", self.phone),
            ("Campus Residence", "Mabini Hall • Room 312"),
            ("Primary Clinic", "University Campus Health Center"),
        ]:
            r = Card(self.content)
            r.pack(fill="x", padx=18, pady=2)
            self.label(r, title, 7, MUTED).pack(anchor="w", padx=10, pady=(6, 0))
            self.label(r, value, 8, NAVY, True).pack(anchor="w", padx=10, pady=(1, 6))

        self.label(self.content, "Settings & Consent", 12, NAVY, True).pack(
            anchor="w", padx=20, pady=(8, 4)
        )
        settings = [
            ("Notification Preferences", "SMS alerts & appointment reminders", self.open_notification_preferences),
            ("Health Insurance & Coverage", "Campus Shield Active (Tier 1)", self.open_insurance_details),
            ("Biometric Sign-In", "FaceID / campus biometric data", self.open_biometric_settings),
        ]
        for title, desc, action in settings:
            r = Card(self.content)
            r.pack(fill="x", padx=18, pady=2)
            r.configure(cursor="hand2")
            heading = self.label(r, title, 8, NAVY, True)
            heading.pack(anchor="w", padx=10, pady=(7, 0))
            detail = self.label(r, desc, 7, MUTED)
            detail.pack(anchor="w", padx=10, pady=(1, 6))
            for widget in (r, heading, detail):
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda event, callback=action: callback())

        self.button(self.content, "Sign Out of MediCampus", self.sign_out,
                    primary=False).pack(fill="x", padx=18, pady=9)
        self.label(self.content, "24/7 CAMPUS CRISIS LINE  •  911 / Campus Police",
                   7, RED, True, anchor="center").pack(pady=(0, 7))
        self.bottom_nav("Profile")

    def open_notification_preferences(self):
        enabled = messagebox.askyesno(
            "Notification Preferences",
            "Would you like to enable SMS alerts and appointment reminders?\n\n"
            "Choose Yes to enable or No to keep them disabled."
        )
        self.notifications_enabled = enabled
        status = "enabled" if enabled else "disabled"
        messagebox.showinfo("Notification Preferences", f"SMS alerts and appointment reminders are {status} in this demo.")

    def open_insurance_details(self):
        messagebox.showinfo(
            "Health Insurance & Coverage",
            "Plan: Campus Shield\nStatus: Active (demo data)\nTier: 1\n\n"
            "This is sample information for the MediCampus prototype. Contact the campus clinic to verify actual coverage."
        )

    def open_biometric_settings(self):
        messagebox.showinfo(
            "Biometric Sign-In",
            "Biometric sign-in is a design placeholder in this prototype.\n\n"
            "No face scan or biometric data is collected or stored."
        )

    def sign_out(self):
        if not messagebox.askyesno("Sign out", "Are you sure you want to sign out of MediCampus?"):
            return
        self.logged_in = False
        self.staff_logged_in = False
        self.show_welcome()

    # -------------------- staff portal --------------------
    def show_staff_login(self):
        self.current = "staff_login"
        self.clear()
        self.back_header("Clinic Staff Console", "Manage appointments and basic visit records")

        box = tk.Frame(self.content, bg=BG)
        box.pack(fill="both", expand=True, padx=24, pady=16)

        switch = tk.Frame(box, bg=WHITE, highlightbackground=BORDER,
                           highlightthickness=1)
        switch.pack(fill="x", pady=(0, 14))
        tk.Button(switch, text="Student / Faculty", command=self.show_login,
                  bg=WHITE, fg=NAVY, activebackground=BLUE_BG, relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=8
                  ).pack(side="left", fill="x", expand=True, padx=3, pady=3)
        tk.Button(switch, text="Clinic Staff", command=self.show_staff_login,
                  bg=NAVY, fg=WHITE, activebackground=NAVY_2, relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=8
                  ).pack(side="left", fill="x", expand=True, padx=3, pady=3)

        info = tk.Frame(box, bg=MINT)
        info.pack(fill="x", pady=(0, 15))
        self.label(info, "Restricted Access: Authorized University Medical Personnel Only",
                   7, TEAL_DARK, True, wraplength=350).pack(anchor="w", padx=10, pady=8)

        self.label(box, "Staff ID or Clinical Email", 8, TEXT, True).pack(anchor="w")
        sid = ttk.Entry(box, font=("Segoe UI", 11))
        sid.insert(0, "STAFF001")
        sid.pack(fill="x", ipady=7, pady=(5, 12))

        self.label(box, "Password", 8, TEXT, True).pack(anchor="w")
        pwd = ttk.Entry(box, show="•", font=("Segoe UI", 11))
        pwd.insert(0, "admin123")
        pwd.pack(fill="x", ipady=7, pady=(5, 16))

        def login():
            if sid.get().strip() == "STAFF001" and pwd.get() == "admin123":
                self.staff_logged_in = True
                self.show_staff()
            else:
                messagebox.showerror("Login failed",
                                     "Demo staff: STAFF001 / admin123")

        self.button(box, "Staff Sign In  →", login).pack(fill="x")
        self.label(box, "Today's Roster", 7, MUTED, anchor="center").pack(pady=9)
        self.label(box, "Urgent Triage  •  3 waiting", 7, RED, True,
                   anchor="center").pack()

    def show_staff(self):
        self.current = "staff"
        self.clear()
        self.top_brand(profile=False)
        self.back_header("Clinic Staff Console", "Manage appointments and visit records")

        # Hero panel
        banner = tk.Frame(self.content, bg=NAVY, highlightthickness=0)
        banner.pack(fill="x", padx=18, pady=(8, 12))
        self.label(banner, "STAFF PORTAL  •  TODAY", 8, "#BFD7F2", True).pack(
            anchor="w", padx=16, pady=(13, 3)
        )
        self.label(banner, "Today's Clinic Roster", 16, WHITE, True).pack(
            anchor="w", padx=16
        )
        self.label(banner, "University Campus Clinic  ·  Room 204", 8, "#D9E7F8").pack(
            anchor="w", padx=16, pady=(3, 13)
        )

        # Roster summary
        stats = tk.Frame(self.content, bg=BG)
        stats.pack(fill="x", padx=18, pady=(0, 8))
        for title, value, detail in [
            ("UPCOMING", "1", "appointment"),
            ("OPEN SLOTS", "2", "available today"),
        ]:
            tile = tk.Frame(stats, bg="#E7EFFB", highlightbackground=BORDER,
                            highlightthickness=1)
            tile.pack(side="left", fill="both", expand=True,
                      padx=(0, 6) if title == "UPCOMING" else (6, 0))
            self.label(tile, title, 7, MUTED, True).pack(anchor="w", padx=12, pady=(9, 1))
            self.label(tile, value, 17, NAVY, True).pack(anchor="w", padx=12)
            self.label(tile, detail, 8, "#386A9B").pack(anchor="w", padx=12, pady=(0, 9))

        self.label(self.content, "NEXT APPOINTMENT", 8, "#386A9B", True).pack(
            anchor="w", padx=20, pady=(8, 4)
        )
        c = Card(self.content)
        c.pack(fill="x", padx=18, pady=(0, 10))
        head = tk.Frame(c, bg=WHITE)
        head.pack(fill="x", padx=12, pady=(11, 4))
        self.pill(head, "10:30 AM  ·  CONFIRMED", bg="#E4EEFC", fg="#245E96").pack(side="left")
        self.label(c, self.student_name, 12, NAVY, True).pack(anchor="w", padx=12, pady=(3, 1))
        self.label(c, f"{self.student_id}  ·  General Medical Consultation",
                   8, MUTED, wraplength=350).pack(anchor="w", padx=12, pady=(0, 9))
        self.button(c, "Record Visit  →", self.record_visit).pack(
            fill="x", padx=12, pady=(0, 12)
        )

        self.label(self.content, "QUICK ACCESS", 8, "#386A9B", True).pack(
            anchor="w", padx=20, pady=(5, 4)
        )
        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="x", padx=18, pady=(0, 5))
        self.button(actions, "View Student Health Records  →",
                    self.show_history, primary=False).pack(fill="x", pady=(0, 7))
        self.button(actions, "View Appointment History  →",
                    self.show_history, primary=False).pack(fill="x", pady=(0, 4))

        self.label(self.content, "Demo roster · sample data only", 8, MUTED,
                   anchor="center").pack(pady=(7, 12))
    def record_visit(self):
        self.appointment["status"] = "Completed"
        self.records.insert(0, {
            "date": datetime.now().strftime("%b %d, %Y"),
            "type": "General Medical Consultation",
            "doctor": "Clinic Staff",
            "notes": "Visit recorded by clinic staff. Basic consultation completed.",
            "status": "COMPLETED",
        })
        messagebox.showinfo("Visit recorded",
                            "The visit was recorded and the appointment is now completed.")
        self.show_staff()

if __name__ == "__main__":
    app = MediCampusApp()
    app.mainloop()
