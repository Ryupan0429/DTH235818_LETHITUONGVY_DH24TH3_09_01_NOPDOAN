import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import (
    style_ttk, create_button, BG_MAIN, BG_TOOLBAR, 
    center, FONT_TITLE, FONT_NORMAL, FONT_H1
)
from Modules.utils import create_treeview_frame
from Features.chi_tiet import InvoiceDetailWindow
from datetime import datetime, date
from Features.doi_mat_khau import ChangePasswordDialog
from tkcalendar import DateEntry
from Customer.customer_mua_hang import ShopTab
from Customer.customer_san_pham import CustomerSanPhamTab
from Features.khach_hang_dialog import TINH_THANH_VN

# ===================================================================
# TAB HỒ SƠ (PROFILE)
# ===================================================================
class ProfileTab(tk.Frame):
    def __init__(self, parent, username, main_app):
        super().__init__(parent, bg=BG_MAIN)
        self.username = username
        self.main_app = main_app
        self.conn = get_connection()
        self.user_data = {}
        
        self._build_ui()
        self.load_profile()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        center_frame = tk.Frame(self, bg="white", bd=1, relief="sunken")
        center_frame.pack(pady=30, padx=50, fill="both")
        
        header_frame = tk.Frame(center_frame, bg="white")
        header_frame.pack(pady=10)

        self.welcome_label = tk.Label(header_frame, text="Hồ sơ cá nhân", font=FONT_H1, bg="white")
        self.welcome_label.pack(side="left")

        form_frame = tk.Frame(center_frame, bg="white")
        form_frame.pack(pady=10, padx=20, fill="x")

        fields = [("Mã KH:", "MaKH"), ("Họ Tên:", "TenKH"), ("SĐT:", "SDT"), 
                  ("Giới tính:", "GioiTinh"), ("Quê quán:", "QueQuan"), ("Tổng chi tiêu:", "TongChiTieu")]
        self.entries = {}

        for i, (text, key) in enumerate(fields):
            tk.Label(form_frame, text=text, font=FONT_NORMAL, bg="white").grid(row=i, column=0, sticky="e", padx=5, pady=8)
            
            if key == "QueQuan":
                entry = ttk.Combobox(form_frame, width=38, values=TINH_THANH_VN, font=FONT_NORMAL) 
            elif key == "GioiTinh":
                entry = ttk.Combobox(form_frame, width=38, values=['Nam', 'Nữ', 'Khác'], font=FONT_NORMAL)
            else:
                entry = tk.Entry(form_frame, width=40, relief="solid", bd=1,
                                 disabledbackground="#f0f0f0", 
                                 disabledforeground="black") 
                
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=8)
            entry.config(state="disabled")
            self.entries[key] = entry

        btn_frame = tk.Frame(center_frame, bg="white")
        btn_frame.pack(pady=20)
        
        self.edit_button = create_button(btn_frame, "Sửa thông tin", command=self._toggle_edit, kind="secondary")
        self.edit_button.pack(side="left", padx=10)
        
        self.pw_button = create_button(btn_frame, "Đổi mật khẩu", command=self._open_change_password_dialog, kind="accent")
        self.pw_button.pack(side="left", padx=10)
        
        self.save_button = create_button(btn_frame, "Lưu thay đổi", command=self._save_profile, kind="primary")
        
        create_button(btn_frame, "Tải lại", command=self.load_profile, kind="accent").pack(side="left", padx=10)
        
    def load_profile(self):
        """Tải thông tin hồ sơ từ CSDL."""
        try:
            cur = self.conn.cursor()
            
            cur.execute("SELECT * FROM dbo.KhachHang WHERE MaKH = ?", (self.username,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin người dùng.", parent=self)
                return

            cols = [col[0] for col in cur.description]
            self.user_data = dict(zip(cols, row))
            
            # Đảm bảo TongChiTieu là mới nhất (mặc dù trigger đã chạy)
            cur.execute("SELECT SUM(TongGT) FROM dbo.HoaDon WHERE MaKH = ?", (self.username,))
            calculated_tct_row = cur.fetchone()
            tct = calculated_tct_row[0] if calculated_tct_row and calculated_tct_row[0] is not None else 0
            self.user_data["TongChiTieu"] = tct 

            for key, entry in self.entries.items():
                value = self.user_data.get(key)
                entry.config(state="normal")
                
                if key == "QueQuan" or key == "GioiTinh":
                    entry.set(value or "")
                else:
                    entry.delete(0, "end")
                    if key == "TongChiTieu":
                        entry.insert(0, f"{tct or 0:,.0f} đồng")
                    else:
                        entry.insert(0, value or "")
                entry.config(state="disabled") 

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hồ sơ:\n{e}", parent=self)

    def _toggle_edit(self):
        """Cho phép sửa các trường."""
        self.edit_button.pack_forget()
        self.save_button.pack(side="left", padx=10)
        self.pw_button.pack_forget()

        self.entries["TenKH"].config(state="normal")
        self.entries["SDT"].config(state="normal")
        self.entries["GioiTinh"].config(state="readonly")
        self.entries["QueQuan"].config(state="readonly")
        
        self.entries["TenKH"].focus_set()

    def _save_profile(self):
        """Lưu thông tin đã sửa vào CSDL."""
        try:
            hoten = self.entries["TenKH"].get().strip()
            sdt = self.entries["SDT"].get().strip()
            gioitinh = self.entries["GioiTinh"].get().strip()
            quequan = self.entries["QueQuan"].get().strip()

            if not hoten or not (sdt.isdigit() and len(sdt) == 10):
                messagebox.showwarning("Thiếu", "Họ tên không được trống và SĐT phải là 10 chữ số.", parent=self)
                return

            cur = self.conn.cursor()
            cur.execute(
                "UPDATE dbo.KhachHang SET TenKH = ?, SDT = ?, GioiTinh = ?, QueQuan = ? WHERE MaKH = ?",
                (hoten, sdt, gioitinh, quequan, self.username)
            )
            self.conn.commit()

            self.save_button.pack_forget()
            self.edit_button.pack(side="left", padx=10)
            self.pw_button.pack(side="left", padx=10)

            # Trả về trạng thái vô hiệu hóa
            for key in ["TenKH", "SDT", "GioiTinh", "QueQuan"]:
                self.entries[key].config(state="disabled")

            messagebox.showinfo("Thành công", "Đã cập nhật thông tin hồ sơ.", parent=self)
            self.load_profile()
            self.main_app.update_welcome_title() # Cập nhật tiêu đề cửa sổ

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu hồ sơ:\n{e}", parent=self)

    def _open_change_password_dialog(self):
        ChangePasswordDialog(self, self.username)

# ===================================================================
# TAB LỊCH SỬ GIAO DỊCH (HISTORY)
# ===================================================================
class HistoryTab(tk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent, bg=BG_MAIN)
        self.username = username
        self.conn = get_connection()
        self.tree = None
        self._sort_state = {}
        
        self._build_ui()
        self.load_history()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        toolbar = tk.Frame(self, bg=BG_TOOLBAR)
        toolbar.pack(fill="x", padx=10, pady=(8,4))

        tk.Label(toolbar, text="Tìm Mã HĐ:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(toolbar, width=15)
        self.search.pack(side="left", padx=(0, 8))

        tk.Label(toolbar, text="Từ ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_from = DateEntry(toolbar, width=10, date_pattern='dd/MM/yyyy')
        self.date_from.delete(0, "end")
        self.date_from.pack(side="left")

        tk.Label(toolbar, text="Đến ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_to = DateEntry(toolbar, width=10, date_pattern='dd/MM/yyyy')
        self.date_to.delete(0, "end")
        self.date_to.pack(side="left", padx=(0, 8))

        create_button(toolbar, "Lọc", command=self.load_history, kind="secondary").pack(side="left", padx=6)
        create_button(toolbar, "X", command=self._clear_filters, kind="danger", width=3).pack(side="left", padx=(0,4))
        create_button(toolbar, "Tải lại", command=self.load_history, kind="accent").pack(side="left", padx=(4,0))
        
        tk.Label(self, text="Nháy đúp vào một hóa đơn để xem chi tiết.", font=FONT_NORMAL, bg=BG_MAIN).pack(padx=10, pady=5, anchor="w")
        self.area, self.tree = create_treeview_frame(self)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Dùng logic sort chung
        self.columns_info = {"MaHD": "Mã HĐ", "NgayGD": "Ngày Giao Dịch", "TongGT": "Tổng Giá Trị"}
        from Modules.utils import setup_sortable_treeview, reset_sort_headings
        setup_sortable_treeview(self.tree, self.columns_info, self._sort_state)

    def _clear_filters(self):
        self.search.delete(0, "end")
        self.date_from.delete(0, "end")
        self.date_to.delete(0, "end")
        self._sort_state.clear()
        self.load_history()

    def load_history(self):
        """Tải lịch sử hóa đơn của khách hàng."""
        try:
            for i in self.tree.get_children(): self.tree.delete(i)

            cur = self.conn.cursor()
            
            where = ["MaKH = ?"]
            params = [self.username]

            kw = self.search.get().strip()
            if kw:
                where.append("MaHD LIKE ?")
                params.append(f"%{kw}%")

            df_str = self.date_from.get()
            dt_str = self.date_to.get()
            try:
                if df_str:
                    df = datetime.strptime(df_str, '%d/%m/%Y').date()
                    where.append("CAST(NgayGD AS DATE) >= ?") 
                    params.append(df)
                if dt_str:
                    dt = datetime.strptime(dt_str, '%d/%m/%Y').date()
                    where.append("CAST(NgayGD AS DATE) <= ?")
                    params.append(dt)
            except ValueError:
                if df_str or dt_str:
                    messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ (dd/MM/yyyy).", parent=self)
                    return
            
            where_sql = " AND ".join(where)
            # Dùng bảng Hóa Đơn
            sql = f"SELECT MaHD, NgayGD, TongGT FROM dbo.HoaDon WHERE {where_sql} ORDER BY NgayGD DESC"
            
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            
            for r in rows:
                vals = list(r)
                if isinstance(vals[1], (datetime, date)):
                    vals[1] = vals[1].strftime('%d/%m/%Y') # Format dd/MM/yyyy
                vals[2] = f"{vals[2]:,.0f} đồng"
                self.tree.insert("", "end", values=tuple(vals))
            
            from Modules.utils import reset_sort_headings
            reset_sort_headings(self.tree, self.columns_info, self._sort_state)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lịch sử:\n{e}", parent=self)

    def _on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading": return
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        if not vals: return
        
        mahd = vals[0]
        InvoiceDetailWindow(self, mahd) # Tái sử dụng dialog chi tiết HĐ

# ===================================================================
# CỬA SỔ CHÍNH CỦA KHÁCH HÀNG
# ===================================================================
class CustomerApp(tk.Tk):
    def __init__(self, role, username):
        super().__init__()
        
        style_ttk(self)
        
        self.role = role
        self.username = username
        self.user_data = self._load_user_data()

        self.title(f"Chào mừng {self.user_data.get('TenKH', username)}!")
        self.geometry("1100x700")
        center(self, 1100, 700)
        self.configure(bg=BG_MAIN)
        
        self._create_header()
        self._create_notebook()
        
        self.protocol("WM_DELETE_WINDOW", self._handle_logout)

    def update_welcome_title(self):
        """Hàm public để ProfileTab gọi khi Tên thay đổi."""
        self.user_data = self._load_user_data()
        self.title(f"Chào mừng {self.user_data.get('TenKH', self.username)}!")
        self.welcome_label.config(text=f"{self.user_data.get('TenKH', self.username)} ({self.role})")


    def _load_user_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            # Dùng bảng KhachHang
            cur.execute("SELECT * FROM dbo.KhachHang WHERE MaKH = ?", (self.username,))
            row = cur.fetchone()
            conn.close()
            if row:
                cols = [col[0] for col in cur.description]
                return dict(zip(cols, row))
            return {}
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu người dùng:\n{e}")
            return {}

    def _create_header(self):
        header_frame = tk.Frame(self, bg=BG_TOOLBAR, height=40)
        header_frame.pack(fill="x")
        
        logout_btn = ttk.Button(header_frame, text="Đăng xuất", 
                               command=self._handle_logout, 
                               style="Danger.TButton")
        logout_btn.pack(side="right", padx=10, pady=5)

        self.welcome_label = tk.Label(header_frame, text=f"{self.user_data.get('TenKH', self.username)} ({self.role})", 
                 font=FONT_TITLE, bg=BG_TOOLBAR)
        self.welcome_label.pack(side="right", padx=10, pady=5)

    def _create_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.profile_tab = ProfileTab(notebook, self.username, self)
        self.shop_tab = ShopTab(notebook, self.username, self.user_data) 
        self.history_tab = HistoryTab(notebook, self.username)
        self.san_pham_tab = CustomerSanPhamTab(notebook, self.username, self.shop_tab) # Dùng shop_tab

        notebook.add(self.profile_tab, text="👤 Hồ sơ cá nhân")
        notebook.add(self.shop_tab, text="🛒 Mua hàng")
        notebook.add(self.history_tab, text="🧾 Lịch sử giao dịch")
        notebook.add(self.san_pham_tab, text="💊 Tra cứu sản phẩm") 
        
        def on_tab_changed(event):
            """Cập nhật dữ liệu khi chuyển tab."""
            try:
                selected_tab_text = notebook.tab(notebook.select(), "text")
                
                if selected_tab_text == "👤 Hồ sơ cá nhân":
                    self.profile_tab.load_profile() 
                elif selected_tab_text == "🧾 Lịch sử giao dịch":
                    self.history_tab.load_history()
            
            except tk.TclError:
                pass 
            except Exception as e:
                print(f"Lỗi khi chuyển tab: {e}")

        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    def _handle_logout(self):
        self.destroy()
        from login import login_screen
        login_screen()

def open_main_customer(role, username):
    app = CustomerApp(role, username)
    app.mainloop()