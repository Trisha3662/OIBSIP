import tkinter as tk
import requests
import threading
import time

# Weather App (Tkinter GUI)
# 
# How to run:
# 1. Go to https://openweathermap.org/
# 2. Create free account
# 3. Generate API key
# 4. Replace "YOUR_API_KEY_HERE" with your key

API_KEY = "YOUR_API_KEY_HERE"

# ─ weather icon mapper ─ 
def get_icon(wid, code):
    night = code.endswith("n")
    if 200 <= wid < 300: return "⛈"   
    if 300 <= wid < 400: return "🌦"   
    if wid == 511:       return "🌨"  
    if 500 <= wid < 600: return "🌧" 
    if 600 <= wid < 700: return "❄"    
    if 700 <= wid < 800: return "🌫" 
    if wid == 800:       return "🌙" if night else "☀"   
    if wid == 801:       return "🌤"   
    if wid == 802:       return "⛅"   
    return "☁"                         

def validate(city):
    city = city.strip()
    if not city:
        return False, "Please enter a city name."
    if len(city) < 2:
        return False, "City name is too short (min 2 characters)."
    if len(city) > 85:
        return False, "City name is too long."
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '-,.")
    bad = [c for c in city if c not in allowed]
    if bad:
        return False, f"Invalid character '{bad[0]}'. Use letters only."
    return True, ""

BG      = "#0f1621"   
SURFACE = "#172032"  
LINE    = "#1f2e45"   
BLUE    = "#4d87d6"   
BLUE2   = "#6fa3e8"   
TEXT    = "#dce8f5"   
SUB     = "#5a7a9a"   
RED     = "#b05b5b"
AMBER   = "#a07840"  
GREEN   = "#3d8f72" 

# ── main application class ───
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App ")
        self.root.geometry("440x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"440x700+{(sw-440)//2}+{(sh-700)//2}")

        self.unit       = tk.StringVar(value="metric")
        self._busy      = False
        self._dots      = 0
        self._last_city = None   

        self._build_ui()

        if API_KEY == "YOUR_API_KEY_HERE":
            self._toast(
                "API key not set. Open weather_app.py and paste your key.",
                kind="warn"
            )
    def _build_ui(self):
        """Build all UI sections."""
        self._build_header()
        self._build_search()
        self._build_message_area()
        self._build_result_area()

    def _build_header(self):
        tk.Frame(self.root, bg=BG, height=28).pack(fill="x")

        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28)

        tk.Label(row, text="Weather App",
                 font=("Segoe UI", 24, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # °C / °F toggle 
        tog = tk.Frame(row, bg=BG)
        tog.pack(side="right", pady=(8, 0))
        self._unit_btns = {}
        for lbl, val in [("°C", "metric"), ("°F", "imperial")]:
            b = tk.Button(tog, text=lbl,
                          font=("Segoe UI", 10, "bold"),
                          relief="flat", bd=0,
                          padx=12, pady=5,
                          cursor="hand2",
                          command=lambda v=val: self._set_unit(v))
            b.pack(side="left", padx=2)
            self._unit_btns[val] = b
        self._set_unit("metric")

        tk.Label(self.root,
                 text="Enter a city name to get current weather",
                 font=("Segoe UI", 9),
                 bg=BG, fg=SUB).pack(anchor="w", padx=28, pady=(2, 18))

    # ── search bar ────────
    def _build_search(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28)

        self.city_var = tk.StringVar()
        self.entry = tk.Entry(
            row, textvariable=self.city_var,
            font=("Segoe UI", 13),
            bg=SURFACE, fg=TEXT,
            insertbackground=TEXT,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=BLUE
        )
        self.entry.pack(side="left", fill="x", expand=True,
                        ipady=10, ipadx=12)
        self.entry.bind("<Return>",   lambda e: self._go())
        self.entry.bind("<FocusIn>",  lambda e: self.entry.config(
            highlightbackground=BLUE))
        self.entry.bind("<FocusOut>", lambda e: self.entry.config(
            highlightbackground=LINE))
        self.entry.focus()

        self.btn = tk.Button(
            row, text="Search",
            font=("Segoe UI", 10, "bold"),
            bg=BLUE, fg="#ffffff",
            activebackground=BLUE2, activeforeground="#ffffff",
            relief="flat", bd=0,
            padx=18, pady=10,
            cursor="hand2",
            command=self._go
        )
        self.btn.pack(side="left", padx=(8, 0))

    # ── message area ───
    def _build_message_area(self):
        self.msg_var = tk.StringVar()
        self.msg_lbl = tk.Label(
            self.root, textvariable=self.msg_var,
            font=("Segoe UI", 9),
            bg=BG, fg=RED,
            wraplength=384, justify="left", anchor="w"
        )
        self.msg_lbl.pack(fill="x", padx=28, pady=(8, 0))

    # ── result area ─────
    def _build_result_area(self):
        self.result = tk.Frame(self.root, bg=BG)
        self.result.pack(fill="both", expand=True, padx=28, pady=(10, 24))

    def _set_unit(self, val):
        if self.unit.get() == val:
            return
        self.unit.set(val)
        for v, b in self._unit_btns.items():
            b.config(bg=BLUE if v == val else SURFACE,
                     fg="#ffffff" if v == val else SUB)
        if self._last_city:
            self._refetch(self._last_city)

    def _toast(self, msg, kind="error", ttl=6000):
        colours = {"error": RED, "warn": AMBER, "ok": GREEN, "info": SUB}
        self.msg_var.set(msg)
        self.msg_lbl.config(fg=colours.get(kind, RED))
        if ttl:
            self.root.after(ttl, lambda: self.msg_var.set(""))

    def _clear_msg(self):
        self.msg_var.set("")

    # ── search triggered by user ─────
    def _go(self):
        """Called when Search button clicked or Enter pressed."""
        if self._busy:
            return

        city = self.city_var.get().strip()
        ok, err = validate(city)
        if not ok:
            self._toast(err, "error")
            return
        if API_KEY == "YOUR_API_KEY_HERE":
            self._toast(
                "No API key found. Open weather_app.py and paste your key.",
                "warn"
            )
            return

        self._start_fetch(city)
    def _refetch(self, city):
        
        if self._busy:
            return
        self._start_fetch(city)

    def _start_fetch(self, city):
        self._clear_msg()
        self._busy = True
        self.btn.config(state="disabled", bg=LINE)
        self._clear_result()
        self._dots = 0
        self._spin()
        threading.Thread(
            target=self._fetch, args=(city,), daemon=True
        ).start()

    def _spin(self):
        if not self._busy:
            self.msg_var.set("")
            return
        frames = ["Fetching   ", "Fetching .  ", "Fetching .. ", "Fetching ..."]
        self.msg_var.set(frames[self._dots % 4])
        self.msg_lbl.config(fg=SUB)
        self._dots += 1
        self.root.after(350, self._spin)


    def _fetch(self, city):
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={requests.utils.quote(city)}"
            f"&appid={API_KEY}"
            f"&units={self.unit.get()}"
        )
        try:
            r = requests.get(url, timeout=9)
            d = r.json()
        except requests.exceptions.ConnectionError:
            self.root.after(0, self._err,
                "No internet connection. Check your network.")
            return
        except requests.exceptions.Timeout:
            self.root.after(0, self._err,
                "Request timed out. Please try again.")
            return
        except Exception:
            self.root.after(0, self._err,
                "Unexpected error. Please try again.")
            return

        if   r.status_code == 200:
            self.root.after(0, self._show, d)
        elif r.status_code == 401:
            self.root.after(0, self._err,
                "Invalid API key. Check weather_app.py.")
        elif r.status_code == 404:
            self.root.after(0, self._err,
                f'City "{city}" not found. Check the spelling.')
        elif r.status_code == 429:
            self.root.after(0, self._err,
                "Too many requests. Wait a minute and try again.")
        else:
            self.root.after(0, self._err,
                f"API error {r.status_code}: {d.get('message','Unknown')}")

    def _err(self, msg):
        self._busy = False
        self.btn.config(state="normal", bg=BLUE)
        self._toast(msg, "error")

    def _clear_result(self):

        for w in self.result.winfo_children():
            w.destroy()

    def _show(self, d):
        self._busy = False
        self._last_city = d["name"]   
        self.btn.config(state="normal", bg=BLUE)
        self._clear_msg()
        self._clear_result()

        unit = self.unit.get()
        u    = "°C" if unit == "metric" else "°F"
        ws   = "m/s" if unit == "metric" else "mph"

        city    = d["name"]
        country = d["sys"]["country"]
        desc    = d["weather"][0]["description"].title()
        icon    = get_icon(d["weather"][0]["id"], d["weather"][0]["icon"])
        temp    = round(d["main"]["temp"])
        feels   = round(d["main"]["feels_like"])
        lo      = round(d["main"]["temp_min"])
        hi      = round(d["main"]["temp_max"])
        hum     = d["main"]["humidity"]
        pres    = d["main"]["pressure"]
        wind    = d["wind"]["speed"]
        vis_r   = d.get("visibility")
        vis     = f"{vis_r / 1000:.1f} km" if vis_r else "N/A"

        self._divider()

        hero = tk.Frame(self.result, bg=BG)
        hero.pack(fill="x", pady=(0, 4))

        lf = tk.Frame(hero, bg=BG)
        lf.pack(side="left", fill="both", expand=True)

        tk.Label(lf, text=city,
                 font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=TEXT, anchor="w").pack(fill="x")
        tk.Label(lf, text=country,
                 font=("Segoe UI", 9),
                 bg=BG, fg=SUB, anchor="w").pack(fill="x")
        tk.Label(lf, text=desc,
                 font=("Segoe UI", 10),
                 bg=BG, fg=BLUE2, anchor="w").pack(fill="x", pady=(6, 0))

        rf = tk.Frame(hero, bg=BG)
        rf.pack(side="right")

        tk.Label(rf, text=icon,
                 font=("Segoe UI Emoji", 36),
                 bg=BG).pack()
        tk.Label(rf, text=f"{temp}{u}",
                 font=("Segoe UI", 32, "bold"),
                 bg=BG, fg=TEXT).pack()
        tk.Label(rf, text=f"feels like {feels}{u}",
                 font=("Segoe UI", 9),
                 bg=BG, fg=SUB).pack()

        # ── temperature range bar ──
        self._divider()
        bar = tk.Frame(self.result, bg=SURFACE, height=4)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        pct = min(max((temp + 10) / 55, 0.04), 1.0)
        tk.Frame(bar, bg=BLUE, height=4,
                 width=int(384 * pct)).pack(side="left")
        self._divider()

        # ── high / low strip ──
        hl = tk.Frame(self.result, bg=BG)
        hl.pack(fill="x", pady=(4, 10))
        tk.Label(hl, text=f"H  {hi}{u}",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hl, text="  /  ",
                 font=("Segoe UI", 10),
                 bg=BG, fg=SUB).pack(side="left")
        tk.Label(hl, text=f"L  {lo}{u}",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # ── stat grid  ──
        stats = [
            ("Humidity",   f"{hum}%"),
            ("Wind Speed", f"{wind} {ws}"),
            ("Pressure",   f"{pres} hPa"),
            ("Visibility", vis),
        ]

        grid = tk.Frame(self.result, bg=BG)
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for i, (lbl, val) in enumerate(stats):
            cell = tk.Frame(grid, bg=SURFACE,
                            highlightbackground=LINE,
                            highlightthickness=1)
            cell.grid(row=i // 2, column=i % 2,
                      sticky="nsew",
                      padx=(0, 4) if i % 2 == 0 else (0, 0),
                      pady=3)

            # blue left accent bar
            tk.Frame(cell, bg=BLUE, width=3).pack(
                side="left", fill="y")

            inner = tk.Frame(cell, bg=SURFACE)
            inner.pack(side="left", fill="x", expand=True,
                       padx=10, pady=10)

            tk.Label(inner, text=lbl,
                     font=("Segoe UI", 8),
                     bg=SURFACE, fg=SUB,
                     anchor="w").pack(fill="x")
            tk.Label(inner, text=val,
                     font=("Segoe UI", 14, "bold"),
                     bg=SURFACE, fg=TEXT,
                     anchor="w").pack(fill="x", pady=(2, 0))

        # ── timestamp ──
        now = time.strftime("%d %b %Y  —  %I:%M %p")
        tk.Label(self.result,
                 text=f"Last updated: {now}",
                 font=("Segoe UI", 9),
                 bg=BG, fg=SUB).pack(anchor="e", pady=(10, 0))

    def _divider(self):
        tk.Frame(self.result, bg=LINE, height=1).pack(fill="x", pady=4)


# ── entry point ──────
if __name__ == "__main__":
    root = tk.Tk()
    app  = WeatherApp(root)
    root.mainloop()