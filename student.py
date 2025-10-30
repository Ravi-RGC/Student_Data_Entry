import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import mysql.connector
from datetime import datetime
import csv

# ==============================
# MySQL CONNECTION
# ==============================
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="college_ravi"
    )
    cur = conn.cursor()
except mysql.connector.Error as e:
    messagebox.showerror("DB Error", f"MySQL Connection Failed:\n{e}")
    exit()

cur.execute("CREATE DATABASE IF NOT EXISTS college_ravi")
cur.execute("USE college_ravi")

cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(50) NOT NULL
    )
''')
cur.execute("INSERT IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")

cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        roll VARCHAR(20) UNIQUE NOT NULL,
        course VARCHAR(50) NOT NULL,
        semester INT NOT NULL,
        fees INT NOT NULL,
        date VARCHAR(20) NOT NULL
    )
''')
conn.commit()

# ==============================
# MAIN APP
# ==============================
def open_main_app():
    root = tk.Tk()
    root.title("Ravi Ranjan Kumar (25MCA20310)")
    root.geometry("900x680")
    root.configure(bg="#f0f4f8")

    # Header
    header = tk.Frame(root, bg="#2980b9", height=80)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="COLLEGE STUDENT MANAGEMENT", bg="#2980b9", fg="white", font=("Arial", 18, "bold")).pack(pady=15)
    tk.Label(header, text="Ravi Ranjan Kumar | UID: 25MCA20310", bg="#2980b9", fg="#ecf0f1", font=("Arial", 10)).pack()

    content = tk.Frame(root, bg="#f0f4f8")
    content.pack(fill="both", expand=True, padx=25, pady=20)

    # Form
    insert_frame = tk.LabelFrame(content, text=" ADD / UPDATE STUDENT ", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#2c3e50")
    insert_frame.pack(fill="x", pady=10)

    form = tk.Frame(insert_frame, bg="#f0f4f8")
    form.pack(pady=15, padx=20)

    labels = ["Name", "Roll No", "Course", "Semester", "Fees Paid"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(form, text=label + ":", bg="#f0f4f8", fg="#2c3e50", font=("Arial", 11)).grid(row=i, column=0, sticky="w", pady=6)
        entry = tk.Entry(form, width=35, font=("Arial", 11), relief="solid", bd=1)
        entry.grid(row=i, column=1, pady=6, padx=10)
        entries.append(entry)

    def clear_form():
        for e in entries: e.delete(0, "end")
        update_btn.pack_forget()
        insert_btn.pack(pady=12)

    def insert_student():
        name = entries[0].get().strip()
        roll = entries[1].get().strip().upper()
        course = entries[2].get().strip()
        sem = entries[3].get().strip()
        fees = entries[4].get().strip()
        date = datetime.now().strftime("%d-%m-%Y")
        if not all([name, roll, course, sem, fees]):
            messagebox.showwarning("Error", "All fields are required!")
            return
        try:
            sem = int(sem)
            fees = int(fees)
            if sem < 1 or sem > 8 or fees < 0:
                raise ValueError
        except:
            messagebox.showwarning("Error", "Semester (1-8) & Fees must be valid numbers!")
            return
        try:
            cur.execute("INSERT INTO students (name,roll,course,semester,fees,date) VALUES (%s,%s,%s,%s,%s,%s)",
                        (name, roll, course, sem, fees, date))
            conn.commit()
            messagebox.showinfo("Success", f"Student {name} added!")
            clear_form()
            refresh_all()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Roll No already exists!")

    def update_student():
        name = entries[0].get().strip()
        roll = entries[1].get().strip().upper()
        course = entries[2].get().strip()
        sem = entries[3].get().strip()
        fees = entries[4].get().strip()
        sid = selected_id.get()
        if not all([name, roll, course, sem, fees, sid]):
            return
        try:
            sem = int(sem)
            fees = int(fees)
        except:
            return
        cur.execute("UPDATE students SET name=%s,roll=%s,course=%s,semester=%s,fees=%s WHERE id=%s",
                    (name, roll, course, sem, fees, sid))
        conn.commit()
        messagebox.showinfo("Updated", f"Student {name} updated!")
        clear_form()
        refresh_all()

    insert_btn = tk.Button(insert_frame, text="INSERT STUDENT", bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                           command=insert_student, width=20, relief="flat")
    insert_btn.pack(pady=12)

    update_btn = tk.Button(insert_frame, text="UPDATE STUDENT", bg="#2980b9", fg="white", font=("Arial", 11, "bold"),
                           command=update_student, width=20, relief="flat")

    # Table Frame
    view_frame = tk.LabelFrame(content, text=" ALL STUDENTS ", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#2c3e50")
    view_frame.pack(fill="both", expand=True, pady=15)

    # SEARCH BAR
    search_frame = tk.Frame(view_frame, bg="#f0f4f8")
    search_frame.pack(fill="x", padx=15, pady=8)

    tk.Label(search_frame, text="SEARCH:", bg="#f0f4f8", fg="#e74c3c", font=("Arial", 11, "bold")).pack(side="left")
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30, font=("Arial", 11), relief="solid")
    search_entry.pack(side="left", padx=8)

    # TREEVIEW + SCROLLBAR FRAME
    tree_frame = tk.Frame(view_frame)
    tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    cols = ("ID", "Name", "Roll", "Course", "Sem", "Fees", "Date")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

    # Configure columns
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    # SCROLLBAR
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # PACK TREEVIEW AND SCROLLBAR PROPERLY
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")  # This is the key!

    # STYLE
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="white", foreground="#2c3e50", fieldbackground="white", font=("Arial", 10))
    style.configure("Treeview.Heading", background="#3498db", foreground="white", font=("Arial", 10, "bold"))

    selected_id = tk.StringVar()

    def load_for_update():
        sel = tree.selection()
        if not sel: 
            messagebox.showwarning("Select", "Select a row!")
            return
        vals = tree.item(sel[0])['values']
        clear_form()
        for i, v in enumerate(vals[1:6]): entries[i].insert(0, str(v))
        selected_id.set(vals[0])
        insert_btn.pack_forget()
        update_btn.pack(pady=12)

    def delete_student():
        sel = tree.selection()
        if not sel: return
        if messagebox.askyesno("Delete", "Remove?"):
            sid = tree.item(sel[0])['values'][0]
            cur.execute("DELETE FROM students WHERE id=%s", (sid,))
            conn.commit()
            refresh_all()

    def export_csv():
        cur.execute("SELECT * FROM students")
        rows = cur.fetchall()
        if not rows: return
        file = filedialog.asksaveasfilename(defaultextension=".csv")
        if file:
            with open(file, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(rows)
            messagebox.showinfo("Success", "Exported!")

    def update_stats():
        cur.execute("SELECT COUNT(*), SUM(fees) FROM students")
        c, t = cur.fetchone()
        stats_label.config(text=f"Students: {c or 0} | Fees: ₹{t or 0}")

    def view_students():
        for i in tree.get_children(): tree.delete(i)
        cur.execute("SELECT * FROM students ORDER BY id DESC")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)

    def search_student():
        query = search_var.get().strip()
        for i in tree.get_children(): tree.delete(i)
        if query:
            cur.execute("SELECT * FROM students WHERE name LIKE %s OR roll LIKE %s OR course LIKE %s",
                        (f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cur.execute("SELECT * FROM students ORDER BY id DESC")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        update_stats()

    # LIVE SEARCH ON KEY RELEASE
    search_entry.bind("<KeyRelease>", lambda e: search_student())

    # SEARCH BUTTON
    tk.Button(search_frame, text="GO", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
              command=search_student, width=8).pack(side="left", padx=3)

    # Buttons
    btn_frame = tk.Frame(view_frame, bg="#f0f4f8")
    btn_frame.pack(fill="x", padx=15, pady=5)
    tk.Button(btn_frame, text="Refresh", bg="#34495e", fg="white", command=lambda: refresh_all(), width=8).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Update", bg="#2980b9", fg="white", command=load_for_update, width=8).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Delete", bg="#e74c3c", fg="white", command=delete_student, width=8).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Export", bg="#9b59b6", fg="white", command=export_csv, width=8).pack(side="left", padx=2)

    stats_label = tk.Label(view_frame, text="", bg="#f0f4f8", fg="#27ae60", font=("Arial", 10, "bold"))
    stats_label.pack(pady=5)

    def refresh_all():
        search_var.set("")
        view_students()
        update_stats()

    # Footer
    footer = tk.Frame(root, bg="#ecf0f1", height=40)
    footer.pack(fill="x")
    footer.pack_propagate(False)
    tk.Label(footer, text="Scrollbar Fixed | Live Search Working", bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 9)).pack(pady=10)

    refresh_all()
    root.mainloop()

# ==============================
# LOGIN
# ==============================
login_root = tk.Tk()
login_root.title("Login")
login_root.geometry("400x300")
login_root.configure(bg="#f0f4f8")

tk.Label(login_root, text="LOGIN", bg="#f0f4f8", fg="#2c3e50", font=("Arial", 18, "bold")).pack(pady=30)
frame = tk.Frame(login_root, bg="#f0f4f8")
frame.pack(pady=20)

tk.Label(frame, text="Username:", bg="#f0f4f8", fg="#2c3e50", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
user_entry = tk.Entry(frame, width=30, font=("Arial", 11))
user_entry.grid(row=0, column=1, pady=8, padx=10)

tk.Label(frame, text="Password:", bg="#f0f4f8", fg="#2c3e50", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
pass_entry = tk.Entry(frame, width=30, font=("Arial", 11), show="*")
pass_entry.grid(row=1, column=1, pady=8, padx=10)

def check_login():
    u = user_entry.get().strip()
    p = pass_entry.get().strip()
    if not u or not p:
        messagebox.showwarning("Error", "Fill both!")
        return
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
    if cur.fetchone():
        login_root.destroy()
        open_main_app()
    else:
        messagebox.showerror("Failed", "Wrong credentials!")

tk.Button(frame, text="LOGIN", bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
          command=check_login, width=15).grid(row=2, column=0, columnspan=2, pady=15)

login_root.mainloop()
conn.close()