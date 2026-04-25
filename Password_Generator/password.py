#PASSWORD GENERATOR

import tkinter as tk
from tkinter import messagebox
import random
import string

BG_MAIN  = "#0d1117"
BG_CARD  = "#161b22"
BORDER   = "#30363d"
TEXT_PRI = "#e6edf3"
TEXT_MUT = "#8b949e"
BLUE     = "#58a6ff"
GREEN    = "#238636"
RED      = "#da3633"
YELLOW   = "#d29922"
BTN_COPY = "#1f6feb"

def get_strength(password, num_types):
    score = 0
    if len(password) >= 8:  score += 1
    if len(password) >= 12: score += 1
    if len(password) >= 16: score += 1
    if num_types >= 2: score += 1
    if num_types >= 3: score += 1
    if num_types >= 4: score += 1

    pct = int((score / 6) * 100)

    if pct <= 33:   return "Weak", RED
    elif pct <= 66: return "Medium", YELLOW
    else:           return "Strong", GREEN

def generate_password():
    raw = length_var.get().strip()

    if not raw:
        messagebox.showwarning("Oops!", "Enter password length")
        return

    try:
        length = int(raw)
    except:
        messagebox.showerror("Invalid", "Length must be a number")
        return

    if length < 4:
        messagebox.showerror("Too Short", "Minimum length is 4")
        return

    if length > 32:
        messagebox.showerror("Too Long", "Maximum length is 32")
        return

    sets = []
    if var_upper.get():   sets.append(string.ascii_uppercase)
    if var_lower.get():   sets.append(string.ascii_lowercase)
    if var_digits.get():  sets.append(string.digits)
    if var_symbols.get(): sets.append(string.punctuation)

    if not sets:
        messagebox.showerror("Select Option", "Choose at least one type")
        return

    pwd = [random.choice(s) for s in sets]
    all_chars = "".join(sets)

    while len(pwd) < length:
        pwd.append(random.choice(all_chars))

    random.shuffle(pwd)
    final = "".join(pwd)

    result_var.set(final)
    result_entry.config(fg=BLUE)

    label, color = get_strength(final, len(sets))
    strength_label.config(text=f"Strength: {label}", fg=color)

    strength_canvas.delete("bar")
    width = {"Weak":120, "Medium":240, "Strong":350}[label]
    strength_canvas.create_rectangle(0, 0, width, 8,
                                     fill=color, outline="", tags="bar")
    
def copy_password():
    pwd = result_var.get()

    if pwd == "—":
        messagebox.showwarning("Empty", "Generate password first")
        return

    root.clipboard_clear()
    root.clipboard_append(pwd)

    copy_btn.config(text="Copied ✓", bg=GREEN)
    root.after(1500, lambda: copy_btn.config(text="Copy", bg=BTN_COPY))

def clear_all():
    length_var.set("")
    result_var.set("—")
    result_entry.config(fg=TEXT_MUT)

    var_upper.set(0)
    var_lower.set(0)
    var_digits.set(0)
    var_symbols.set(0)

    strength_label.config(text="Strength: —", fg=TEXT_MUT)
    strength_canvas.delete("bar")

root = tk.Tk()
root.title("Password Generator")
root.geometry("420x520")
root.configure(bg=BG_MAIN)
root.resizable(False, False)

tk.Label(root, text="Password Generator",
         bg=BG_MAIN, fg=BLUE,
         font=("Helvetica", 20, "bold")).pack(pady=(20,5))

tk.Label(root, text="Create secure passwords easily",
         bg=BG_MAIN, fg=TEXT_MUT,
         font=("Arial", 9)).pack(pady=(0,15))


card = tk.Frame(root, bg=BG_CARD,
                highlightbackground=BORDER,
                highlightthickness=1)
card.pack(fill="x", padx=20, pady=10)

tk.Label(card, text="Password Length",
         bg=BG_CARD, fg=TEXT_MUT).pack(anchor="w", padx=16, pady=(12,5))

length_var = tk.StringVar()

length_entry = tk.Entry(card, textvariable=length_var,
                        justify="center",
                        font=("Arial", 14),
                        bg=BG_MAIN, fg=TEXT_PRI,
                        insertbackground=TEXT_PRI,
                        relief="flat",
                        highlightbackground=BORDER,
                        highlightthickness=1)
length_entry.pack(fill="x", padx=16, pady=(0,10), ipady=6)

var_upper = tk.IntVar(value=0)
var_lower = tk.IntVar(value=0)
var_digits = tk.IntVar(value=0)
var_symbols = tk.IntVar(value=0)

options = [
    ("Uppercase (A-Z)", var_upper),
    ("Lowercase (a-z)", var_lower),
    ("Digits (0-9)", var_digits),
    ("Symbols (!@#$)", var_symbols)
]

for text, var in options:
    tk.Checkbutton(card, text=text, variable=var,
                   bg=BG_CARD, fg=TEXT_PRI,
                   selectcolor=BG_MAIN).pack(anchor="w", padx=16)

result_var = tk.StringVar(value="—")

result_entry = tk.Entry(root, textvariable=result_var,
                        justify="center",
                        font=("Courier", 14),
                        fg=TEXT_MUT, bg=BG_MAIN,
                        state="readonly")
result_entry.pack(fill="x", padx=20, pady=10, ipady=8)


strength_label = tk.Label(root, text="Strength: —",
                         bg=BG_MAIN, fg=TEXT_MUT)
strength_label.pack()

strength_canvas = tk.Canvas(root, height=8,
                            bg=BORDER, highlightthickness=0)
strength_canvas.pack(fill="x", padx=20, pady=5)

btn_frame = tk.Frame(root, bg=BG_MAIN)
btn_frame.pack(fill="x", padx=20, pady=10)

btn_style = dict(font=("Arial", 11, "bold"),
                 relief="flat", pady=8)

tk.Button(btn_frame, text="Generate",
          bg=GREEN, fg="white",
          command=generate_password,
          **btn_style).grid(row=0, column=0, sticky="ew", padx=5)

copy_btn = tk.Button(btn_frame, text="Copy",
                     bg=BTN_COPY, fg="white",
                     command=copy_password,
                     **btn_style)
copy_btn.grid(row=0, column=1, sticky="ew", padx=5)

tk.Button(btn_frame, text="Clear",
          bg=RED, fg="white",
          command=clear_all,
          **btn_style).grid(row=0, column=2, sticky="ew", padx=5)

for i in range(3):
    btn_frame.columnconfigure(i, weight=1)

root.mainloop()
