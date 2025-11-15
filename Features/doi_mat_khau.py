import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import center, FONT_NORMAL, create_button

class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.title("Đổi Mật khẩu")
        self.username = username
        
        self.geometry("400x250")
        center(self, 400, 250)
        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Mật khẩu cũ:", font=FONT_NORMAL).grid(row=0, column=0, sticky="w", pady=5)
        self.old_pw = tk.Entry(frame, width=30, font=FONT_NORMAL, show="*")
        self.old_pw.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frame, text="Mật khẩu mới:", font=FONT_NORMAL).grid(row=1, column=0, sticky="w", pady=5)
        self.new_pw = tk.Entry(frame, width=30, font=FONT_NORMAL, show="*")
        self.new_pw.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frame, text="Xác nhận MK mới:", font=FONT_NORMAL).grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_pw = tk.Entry(frame, width=30, font=FONT_NORMAL, show="*")
        self.confirm_pw.grid(row=2, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        create_button(btn_frame, "Lưu thay đổi", command=self._save, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)

        self.old_pw.focus_set()
        self.wait_window(self)

    def _save(self):
        old = self.old_pw.get()
        new = self.new_pw.get()
        confirm = self.confirm_pw.get()

        if not old or not new or not confirm:
            messagebox.showwarning("Thiếu", "Vui lòng nhập đầy đủ thông tin.", parent=self)
            return

        if new != confirm:
            messagebox.showwarning("Lỗi", "Mật khẩu mới và xác nhận không khớp.", parent=self)
            self.new_pw.focus_set()
            return
        
        if len(new) < 3:
            messagebox.showwarning("Lỗi", "Mật khẩu mới phải có ít nhất 3 ký tự.", parent=self)
            return

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # 1. Kiểm tra mật khẩu cũ
            cur.execute("SELECT Password FROM Users WHERE Username = ?", (self.username,))
            row = cur.fetchone()
            if not row or row[0] != old:
                messagebox.showerror("Sai", "Mật khẩu cũ không chính xác.", parent=self)
                return
                
            # 2. Cập nhật mật khẩu mới
            cur.execute("UPDATE Users SET Password = ? WHERE Username = ?", (new, self.username))
            conn.commit()
            
            messagebox.showinfo("Thành công", "Đã đổi mật khẩu thành công.", parent=self)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể đổi mật khẩu:\n{e}", parent=self)
        finally:
            if conn:
                conn.close()