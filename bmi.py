#BMI CALCULATOR

import tkinter as tk
from tkinter import messagebox

history = []

def calculate_bmi():
    w = weight_entry.get()
    h = height_entry.get()

    if w == "" or h == "":
        messagebox.showwarning("Missing Input", "Please fill all fields")
        return

    try:
        weight = float(w)
        height = float(h)
    except:
        messagebox.showerror("Invalid Input", "Enter numeric values only")
        return

    if weight <= 0 or height <= 0:
        messagebox.showerror("Invalid Value", "Values must be greater than 0")
        return

    if weight > 300:
        messagebox.showerror("Invalid Weight", "Weight seems unrealistic")
        return

    if height > 3:
        messagebox.showerror("Invalid Height", "Enter height in meters (e.g. 1.7)")
        return

    bmi = weight / (height ** 2)

    if bmi < 18.5:
        category = "Underweight 😕"
        color = "#ff9800"
    elif bmi < 25:
        category = "Normal 😊"
        color = "#4caf50"
    elif bmi < 30:
        category = "Overweight 😐"
        color = "#ff9800"
    else:
        category = "Obese 😟"
        color = "#f44336"

    result = f"BMI: {bmi:.2f} ({category})"
    result_label.config(text=result, fg=color)

    history.append(result)
    update_history()


def update_history():
    history_box.delete(0, tk.END)
    for item in history:
        history_box.insert(tk.END, item)


def clear_inputs():
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    result_label.config(text="")


def clear_history():
    history.clear()
    history_box.delete(0, tk.END)

root = tk.Tk()
root.title("Smart BMI Calculator - Python GUI Project")
root.geometry("430x540")
root.configure(bg="#1e1e2f")

tk.Label(root, text="BMI Calculator",
         font=("Helvetica", 18, "bold"),
         bg="#1e1e2f", fg="white").pack(pady=15)

frame = tk.Frame(root, bg="#2c2c3e", bd=2, relief="ridge")
frame.pack(pady=10, padx=20, fill="both")

tk.Label(frame, text="Weight (kg)",
         bg="#2c2c3e", fg="white").pack(pady=5)
weight_entry = tk.Entry(frame, bg="#ffffff", fg="black", justify="center")
weight_entry.pack(pady=5)

tk.Label(frame, text="Height (m)",
         bg="#2c2c3e", fg="white").pack(pady=5)
height_entry = tk.Entry(frame, bg="#ffffff", fg="black", justify="center")
height_entry.pack(pady=5)

btn_frame = tk.Frame(frame, bg="#2c2c3e")
btn_frame.pack(pady=12)

tk.Button(btn_frame, text="Calculate",
          bg="#4caf50", fg="white",
          width=10, command=calculate_bmi).grid(row=0, column=0, padx=5)

tk.Button(btn_frame, text="Clear",
          bg="#f44336", fg="white",
          width=10, command=clear_inputs).grid(row=0, column=1, padx=5)

tk.Button(btn_frame, text="Clear History",
          bg="#2196f3", fg="white",
          width=12, command=clear_history).grid(row=0, column=2, padx=5)

result_label = tk.Label(root, text="",
                        font=("Arial", 13, "bold"),
                        bg="#1e1e2f", fg="white")
result_label.pack(pady=15)

tk.Label(root, text="History",
         font=("Arial", 12, "bold"),
         bg="#1e1e2f", fg="white").pack()


history_box = tk.Listbox(root, width=45, height=6,
                         bg="#ffffff", fg="black",
                         bd=2, relief="solid")
history_box.pack(pady=10)

tk.Label(root, text="Developed by Trisha",
         font=("Arial", 9),
         bg="#1e1e2f", fg="gray").pack(pady=5)

root.mainloop()