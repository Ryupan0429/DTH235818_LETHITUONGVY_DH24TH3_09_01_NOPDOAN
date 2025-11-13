import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import (
    style_ttk, create_button, BG_MAIN, BG_TOOLBAR, BTN_DANGER_BG, 
    center, FONT_TITLE, FONT_NORMAL, FONT_H1, FONT_ICON 
)
from styles.treeview_utils import create_treeview_frame, auto_fit_columns
from services.finance import get_discount_rate, get_next_rank_info
from features.invoice_detail_window import InvoiceDetailWindow
from datetime import datetime, date
from features.change_password_dialog import ChangePasswordDialog
from views.customer_thuoc import CustomerThuocTab
from tkcalendar import DateEntry
from features.customer_dialog import TINH_THANH_VN
from views.customer_shop import ShopTab

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

        self.rank_icon = tk.Label(header_frame, text="👑", font=("Segoe UI", 30), bg="white")
        self.rank_icon.pack(side="left", padx=(0, 10))
        self.rank_label = tk.Label(header_frame, text="Hạng: ...", font=FONT_H1, bg="white")
        self.rank_label.pack(side="left")

        progress_frame = tk.Frame(center_frame, bg="white")
        progress_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        self.progress_label = tk.Label(progress_frame, text="Tiến trình lên hạng:", font=FONT_NORMAL, bg="white")
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(fill="x", pady=2)
        
        self.progress_text = tk.Label(progress_frame, text=".../... VNĐ", font=FONT_NORMAL, bg="white")
        self.progress_text.pack(anchor="e")

        self.discount_label = tk.Label(center_frame, text="Giảm giá hiện tại: 0%", font=FONT_TITLE, fg="green", bg="white")
        self.discount_label.pack(pady=10)

        form_frame = tk.Frame(center_frame, bg="white")
        form_frame.pack(pady=10, padx=20, fill="x")

        fields = [("Mã KH:", "MaKH"), ("Họ Tên:", "HoTenKH"), ("SĐT:", "SDT"), ("Địa chỉ:", "DiaChi"), ("Tổng chi tiêu:", "TongChiTieu")]
        self.entries = {}

        for i, (text, key) in enumerate(fields):
            tk.Label(form_frame, text=text, font=FONT_NORMAL, bg="white").grid(row=i, column=0, sticky="e", padx=5, pady=8)
            
            if key == "DiaChi":
                entry = ttk.Combobox(form_frame, width=38, values=TINH_THANH_VN) 
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=8)
            else:
                # Thêm màu nền khi bị vô hiệu hóa
                entry = tk.Entry(form_frame, width=40, relief="solid", bd=1,
                                 disabledbackground="#f0f0f0", 
                                 disabledforeground="black") 
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=8)
                
            entry.config(state="disabled") # Bắt đầu ở trạng thái disabled
            self.entries[key] = entry

        btn_frame = tk.Frame(center_frame, bg="white")
        btn_frame.pack(pady=20)
        self.edit_button = create_button(btn_frame, "Sửa thông tin", command=self._toggle_edit, kind="secondary")
        self.edit_button.pack(side="left", padx=10)
        
        self.pw_button = create_button(btn_frame, "Đổi mật khẩu", command=self._open_change_password_dialog, kind="accent")
        self.pw_button.pack(side="left", padx=10)
        
        self.save_button = create_button(btn_frame, "Lưu thay đổi", command=self._save_profile, kind="primary")
        
        create_button(btn_frame, "⟳", command=self.load_profile, kind="accent", font=FONT_ICON).pack(side="left", padx=10)
        
    def load_profile(self):
        """Tải thông tin hồ sơ từ CSDL."""
        try:
            cur = self.conn.cursor()
            
            cur.execute("SELECT * FROM dbo.ThongTinKhachHang WHERE MaKH = ?", (self.username,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin người dùng.")
                return

            cols = [col[0] for col in cur.description]
            self.user_data = dict(zip(cols, row))
            rank_from_db = self.user_data.get("ThuHang", "Đồng") 

            cur.execute("SELECT SUM(TongGT) FROM dbo.HoaDonNongDuoc WHERE MaKH = ?", (self.username,))
            calculated_tct_row = cur.fetchone()
            tct = calculated_tct_row[0] if calculated_tct_row and calculated_tct_row[0] is not None else 0
            
            self.user_data["TongChiTieu"] = tct 

            (current_rank, next_rank, value, max_val) = get_next_rank_info(tct)
            
            if current_rank != rank_from_db:
                try:
                    cur.execute(
                        "UPDATE dbo.ThongTinKhachHang SET ThuHang = ? WHERE MaKH = ?",
                        (current_rank, self.username)
                    )
                    self.conn.commit()
                    self.user_data["ThuHang"] = current_rank 
                except Exception as e:
                    print(f"Lỗi khi cập nhật hạng: {e}")
            
            for key, entry in self.entries.items():
                value = self.user_data.get(key)
                entry.config(state="normal") # Chuyển sang normal để xóa/ghi
                if key == "DiaChi":
                    entry.set(value or "")
                else:
                    entry.delete(0, "end")
                    if key == "TongChiTieu":
                        entry.insert(0, f"{tct or 0:,.0f} đồng")
                    else:
                        entry.insert(0, value or "")
                entry.config(state="disabled") # Trả về state disabled (màu xám)
            
            rank_color = {"Đồng": "#B87333", "Bạc": "#A9A9A9", "Vàng": "#FFD700", "Bạch Kim": "#E5E4E2", "Kim Cương": "#B9F2FF"}
            self.rank_label.config(text=f"Hạng: {current_rank}")
            self.rank_icon.config(fg=rank_color.get(current_rank, "#B9F2FF"))

            discount_rate = get_discount_rate(current_rank)
            self.discount_label.config(text=f"Giảm giá hiện tại: {discount_rate * 100:,.0f}%")

            if next_rank:
                self.progress_label.config(text="Tiến trình lên hạng:", font=FONT_NORMAL, fg="black")
                self.progress_bar.pack(fill="x", pady=2) 
                self.progress_text.pack(anchor="e") 
                
                self.progress_bar['maximum'] = max_val
                self.progress_bar['value'] = value 
                self.progress_text.config(text=f"{value:,.0f} / {max_val:,.0f} đồng (lên hạng {next_rank})")
                
            else:
                self.progress_bar.pack_forget()
                self.progress_text.pack_forget()
                self.progress_label.config(text="⭐ Khách hàng Kim Cương ⭐", font=FONT_TITLE, fg="#005a9e")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hồ sơ:\n{e}", parent=self)

    def _toggle_edit(self):
        """Cho phép sửa Họ tên, SĐT, Địa chỉ."""
        self.edit_button.pack_forget()
        self.save_button.pack(side="left", padx=10)
        self.pw_button.pack_forget()

        self.entries["HoTenKH"].config(state="normal")
        self.entries["SDT"].config(state="normal")
        self.entries["DiaChi"].config(state="readonly") # Combobox dùng readonly
        
        self.entries["HoTenKH"].focus_set()

    def _save_profile(self):
        """Lưu thông tin đã sửa vào CSDL."""
        try:
            hoten = self.entries["HoTenKH"].get().strip()
            sdt = self.entries["SDT"].get().strip()
            diachi = self.entries["DiaChi"].get().strip()

            if not hoten or not (sdt.isdigit() and len(sdt) == 10):
                messagebox.showwarning("Thiếu", "Họ tên không được trống và SĐT phải là 10 chữ số.", parent=self)
                return

            cur = self.conn.cursor()
            cur.execute(
                "UPDATE dbo.ThongTinKhachHang SET HoTenKH = ?, SDT = ?, DiaChi = ? WHERE MaKH = ?",
                (hoten, sdt, diachi, self.username)
            )
            self.conn.commit()

            self.save_button.pack_forget()
            self.edit_button.pack(side="left", padx=10)
            self.pw_button.pack(side="left", padx=10)

            # Trả về trạng thái vô hiệu hóa (màu xám)
            for key in ["HoTenKH", "SDT", "DiaChi"]:
                self.entries[key].config(state="disabled")

            messagebox.showinfo("Thành công", "Đã cập nhật thông tin hồ sơ.", parent=self)
            self.load_profile()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu hồ sơ:\n{e}", parent=self)

    def _open_change_password_dialog(self):
        """Mở cửa sổ đổi mật khẩu."""
        ChangePasswordDialog(self, self.username)

# ===================================================================
# TAB LỊCH SỬ GIAO DỊCH (HISTORY)
# ===================================================================
class HistoryTab(tk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent, bg=BG_MAIN)
        self.username = username
        self.conn = get_connection()
        self.sort_cols = ("MaHD", "NgayGD", "TongGT") 
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
        
        create_button(toolbar, "⟳", command=self.load_history, kind="accent", font=FONT_ICON).pack(side="left", padx=(4,0))
        
        tk.Label(self, text="Nháy đúp vào một hóa đơn để xem chi tiết.", font=FONT_NORMAL, bg=BG_MAIN).pack(padx=10, pady=5, anchor="w")
        self.area, self.tree = create_treeview_frame(self)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        self._create_tree_columns()

    def _create_tree_columns(self):
        self.tree["columns"] = self.sort_cols
        
        headings = {"MaHD": "Mã HĐ", "NgayGD": "Ngày Giao Dịch", "TongGT": "Tổng Giá Trị"}
        for c in self.sort_cols:
            header = headings.get(c, c)
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            self.tree.column(c, anchor="w")

    def _on_heading_click(self, col):
        prev = self._sort_state.get(col, None)
        new = not prev if prev is not None else False 
        self._sort_state = {}
        self._sort_state[col] = new
        self._sort(col, new)

    def _sort(self, col, reverse):
        """Sắp xếp dữ liệu trong Treeview (in-memory)."""
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        if col == 'TongGT':
            data.sort(key=lambda t: float(t[0].replace(" đồng","").replace(",","")) if t[0] else 0, reverse=reverse)
        elif col == 'NgayGD':
             try:
                data.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y'), reverse=reverse)
             except ValueError:
                print("Lỗi định dạng ngày khi sort")
        else:
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=reverse)
        
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
            
        for c in self.sort_cols:
            header = self.tree.heading(c, "text").split(" ")[0]
            if c in self._sort_state:
                header += " ▲" if not self._sort_state[c] else " ▼"
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
    
    def _update_headings_after_load(self):
        """Reset tất cả tiêu đề cột về trạng thái không sort."""
        self._sort_state = {}
        for c in self.sort_cols:
            header = self.tree.heading(c, "text").split(" ")[0]
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            
    def _clear_filters(self):
        self.search.delete(0, "end")
        self.date_from.delete(0, "end")
        self.date_to.delete(0, "end")
        self._sort_state = {}
        self.load_history()

    def load_history(self):
        """Tải lịch sử hóa đơn của khách hàng."""
        current_sort = self._sort_state.copy()
        
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
            sql = f"SELECT MaHD, NgayGD, TongGT FROM dbo.HoaDonNongDuoc WHERE {where_sql} ORDER BY NgayGD DESC"
            
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            
            if not rows:
                self.tree.delete(*self.tree.get_children())
                return

            for r in rows:
                vals = list(r)
                if isinstance(vals[1], (datetime, date)):
                    vals[1] = vals[1].strftime('%d/%m/%Y')
                vals[2] = f"{vals[2]:,.0f} đồng"
                self.tree.insert("", "end", values=tuple(vals))
            
            auto_fit_columns(self.tree)
            
            if current_sort:
                col = list(current_sort.keys())[0]
                reverse = current_sort[col]
                self._sort(col, reverse)
            else:
                self._update_headings_after_load()

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
        InvoiceDetailWindow(self, mahd)

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

        self.title(f"Chào mừng {self.user_data.get('HoTenKH', username)}!")
        self.geometry("900x700")
        center(self, 900, 700)
        self.configure(bg=BG_MAIN)
        
        self._create_header()
        self._create_notebook()
        
        self.protocol("WM_DELETE_WINDOW", self._handle_logout)

    def _load_user_data(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM dbo.ThongTinKhachHang WHERE MaKH = ?", (self.username,))
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
        
        logout_btn = tk.Button(header_frame, text="Đăng xuất", 
                               command=self._handle_logout, 
                               bg=BTN_DANGER_BG, fg="black", font=FONT_NORMAL)
        logout_btn.pack(side="right", padx=10, pady=5)

        tk.Label(header_frame, text=f"{self.user_data.get('HoTenKH', self.username)} ({self.role})", 
                 font=FONT_TITLE, bg=BG_TOOLBAR).pack(side="right", padx=10, pady=5)

    def _create_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.profile_tab = ProfileTab(notebook, self.username, self)
        self.shop_tab = ShopTab(notebook, self.username, self.user_data) 
        self.history_tab = HistoryTab(notebook, self.username)
        self.thuoc_tab = CustomerThuocTab(notebook, self.username, self.shop_tab) 

        notebook.add(self.profile_tab, text="👤 Hồ sơ cá nhân")
        notebook.add(self.shop_tab, text="🛒 Mua hàng")
        notebook.add(self.history_tab, text="🧾 Lịch sử giao dịch")
        notebook.add(self.thuoc_tab, text="💊 Tra cứu thuốc") 
        
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