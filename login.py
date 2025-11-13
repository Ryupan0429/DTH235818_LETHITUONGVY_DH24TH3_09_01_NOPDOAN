import tkinter as tk
from tkinter import messagebox
from db import get_connection
import configparser 
import os

try:
    from styles.ui_style import (
        BG_MAIN, BTN_PRIMARY_BG, BTN_DANGER_BG, 
        FONT_NORMAL, FONT_TITLE, center
    )
except ImportError:
    # Fallback
    BG_MAIN = "#e8f8e9"
    BTN_PRIMARY_BG = "#b9e89b"
    BTN_DANGER_BG = "#f7c6c6"
    FONT_NORMAL = ("Segoe UI", 10)
    FONT_TITLE = ("Segoe UI", 11, "bold")
    def center(win, w, h):
        win.update_idletasks()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        x, y = (sw - w)//2, (sh - h)//2
        win.geometry(f"{w}x{h}+{x}+{y}")

CONFIG_FILE = 'config.ini'

def load_remembered_user():
    """Tải username nếu có lưu."""
    if not os.path.exists(CONFIG_FILE):
        return ""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Remember' in config and 'username' in config['Remember']:
        return config['Remember']['username']
    return ""

def save_remembered_user(username):
    """Lưu username."""
    config = configparser.ConfigParser()
    config['Remember'] = {'username': username}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def clear_remembered_user():
    """Xóa username đã lưu."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

def login_screen():
    """Hiển thị cửa sổ đăng nhập."""
    root = tk.Tk()
    root.title("Đăng nhập hệ thống")
    root.configure(bg=BG_MAIN)
    center(root, 400, 280)
    root.resizable(False, False)

    frame = tk.Frame(root, bg="white", bd=1, relief="sunken", padx=20, pady=20)
    frame.pack(pady=20)

    tk.Label(frame, text="ĐĂNG NHẬP HỆ THỐNG", font=("Segoe UI", 14, "bold"),
             fg="#2c3e50", bg="white").grid(row=0, column=0, columnspan=2, pady=(0,15))

    tk.Label(frame, text="Username:", font=FONT_NORMAL, bg="white").grid(row=1, column=0, sticky="w", pady=5)
    username_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
    username_entry.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Password:", font=FONT_NORMAL, bg="white").grid(row=2, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(frame, width=30, show="*", font=FONT_NORMAL)
    password_entry.grid(row=2, column=1, pady=5)
    
    remember_var = tk.BooleanVar()
    remember_check = tk.Checkbutton(frame, text="Ghi nhớ đăng nhập", font=FONT_NORMAL, 
                                    bg="white", variable=remember_var)
    remember_check.grid(row=3, column=1, sticky="w", pady=5)
    
    saved_user = load_remembered_user()
    if saved_user:
        username_entry.insert(0, saved_user)
        remember_var.set(True)
        password_entry.focus()
    else:
        username_entry.focus()


    def handle_login():
        user, pw = username_entry.get().strip(), password_entry.get().strip()
        if not user or not pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ Username và Password")
            return
        
        if remember_var.get():
            save_remembered_user(user)
        else:
            clear_remembered_user()
            
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT Role, Password FROM Users WHERE Username=?", (user,))
            row = cur.fetchone()
            conn.close()
            
            if not row or pw != row[1]:
                messagebox.showerror("Sai thông tin", "Sai tên đăng nhập hoặc mật khẩu!")
                return
            
            from main_app import open_main_admin
            from customer_app import open_main_customer
            
            role = row[0]
            root.destroy() 
            
            if role.lower() == 'customer':
                open_main_customer(role=role, username=user)
            else:
                open_main_admin(role=role, username=user)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def handle_exit():
        root.destroy()

    btn_frame = tk.Frame(frame, bg="white")
    btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

    tk.Button(btn_frame, text="Đăng nhập", width=12, bg=BTN_PRIMARY_BG, fg="black",
              font=FONT_NORMAL, command=handle_login).grid(row=0,column=0,padx=8)
    tk.Button(btn_frame, text="Thoát", width=12, bg=BTN_DANGER_BG, fg="black",
              font=FONT_NORMAL, command=handle_exit).grid(row=0,column=1,padx=8)

    root.bind('<Return>', lambda event=None: handle_login())
    root.mainloop()

if __name__ == "__main__":
    login_screen()