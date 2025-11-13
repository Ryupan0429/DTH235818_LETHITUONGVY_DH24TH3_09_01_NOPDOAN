import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import create_button, BG_TOOLBAR, FONT_ICON
from styles.treeview_utils import create_treeview_frame, auto_fit_columns
# Import dialog mới cho cả Thêm và Sửa
from features.customer_dialog import CustomerFormDialog
from services.finance import update_all_customer_totals

VI_KHACHHANG = {
    "MaKH": "Mã KH",
    "HoTenKH": "Họ Tên",
    "SDT": "SĐT",
    "DiaChi": "Địa chỉ",
    "TongChiTieu": "Tổng chi tiêu",
    "ThuHang": "Hạng"
}
DISPLAY_COLS = ["MaKH", "HoTenKH", "SDT", "DiaChi", "TongChiTieu", "ThuHang"]

# Thêm từ điển để sort Hạng
RANK_ORDER = {
    "Đồng": 0,
    "Bạc": 1,
    "Vàng": 2,
    "Bạch Kim": 3,
    "Kim Cương": 4
}

class KhachHangTab(tk.Frame):
    def __init__(self, parent, role):
        super().__init__(parent, bg="#f7fbf8")
        self.role = role
        self.tree = None
        self._sort_state = {}
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        create_button(top, "Thêm", command=self._on_add, kind="primary", width=10).pack(side="left", padx=(6,4))
        # Thêm nút Sửa và Xóa
        create_button(top, "Sửa", command=self._on_edit, kind="secondary", width=10).pack(side="left", padx=4)
        create_button(top, "Xóa", command=self._on_delete, kind="danger", width=10).pack(side="left", padx=(4,10))
        
        tk.Label(top, text="Tìm (Tên/SĐT):", bg=BG_TOOLBAR).pack(side="left", padx=(10,2))
        self.search = tk.Entry(top, width=15)
        self.search.pack(side="left", padx=(0, 8))

        tk.Label(top, text="Hạng:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.filter_hang = ttk.Combobox(top, values=["Tất cả"], width=15, state="readonly")
        self.filter_hang.pack(side="left", padx=(0, 8))
        self.filter_hang.set("Tất cả")
        
        create_button(top, "Lọc", command=self.load_data, kind="secondary").pack(side="left", padx=6)
        create_button(top, "X", command=self._clear_filters, kind="danger", width=3).pack(side="left", padx=(0,4))
        
        create_button(top, "⟳", 
                      command=self._on_reload_and_recalculate, 
                      kind="accent", 
                      font=FONT_ICON).pack(side="left", padx=(4,0)) 

        self.area, self.tree = create_treeview_frame(self)
        
        self.tree["columns"] = DISPLAY_COLS
        for c in DISPLAY_COLS:
            header = VI_KHACHHANG.get(c, c)
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            self.tree.column(c, anchor="w") 

        self.load_data()

    def _on_add(self):
        # Gọi CustomerFormDialog ở chế độ Thêm
        CustomerFormDialog(self, makh=None)
        self.load_data() 

    def _on_edit(self):
        """Mở dialog Sửa cho khách hàng đang chọn."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sửa", "Vui lòng chọn một khách hàng để sửa.")
            return
            
        try:
            item = self.tree.item(sel[0])
            makh = item["values"][DISPLAY_COLS.index("MaKH")]
            
            # Gọi CustomerFormDialog ở chế độ Sửa
            CustomerFormDialog(self, makh=makh)
            self.load_data()
            
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể xác định Mã Khách hàng.")

    def _on_delete(self):
        """Xóa khách hàng đang chọn khỏi CSDL."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xóa", "Vui lòng chọn một khách hàng để xóa.")
            return

        try:
            item = self.tree.item(sel[0])
            makh = item["values"][DISPLAY_COLS.index("MaKH")]
            hoten = item["values"][DISPLAY_COLS.index("HoTenKH")]
            
            if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa khách hàng:\n{hoten} ({makh})?\n\n(Thao tác này cũng sẽ xóa tài khoản đăng nhập của họ).", parent=self):
                return
                
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.ThongTinKhachHang WHERE MaKH = ?", (makh,))
            cur.execute("DELETE FROM dbo.Users WHERE Username = ?", (makh,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Thành công", "Đã xóa khách hàng thành công.", parent=self)
            self.load_data()

        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể xác định Mã Khách hàng.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể xóa. Có thể khách hàng đã có hóa đơn.\n{e}", parent=self)
        finally:
            if conn: conn.close()

    def _clear_filters(self):
        self.search.delete(0, "end")
        self.filter_hang.set("Tất cả")
        self._sort_state = {} 
        self.load_data()

    def _on_reload_and_recalculate(self):
        """
        Tính toán lại hạng của TẤT CẢ khách hàng, SAU ĐÓ tải lại dữ liệu.
        """
        try:
            # 1. Chạy cập nhật CSDL TRƯỚC
            totals = update_all_customer_totals()
            print(f"Đã cập nhật hạng cho {len(totals)} khách hàng.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật hạng:\n{e}", parent=self)
        
        # 2. Luôn tải lại dữ liệu sau khi cập nhật
        self.load_data()

    def _on_heading_click(self, col):
        if col.lower() not in ['makh', 'hotenkh', 'tongchitieu', 'thuhang']:
            return 
            
        prev = self._sort_state.get(col, None)
        new = not prev if prev is not None else False 
        self._sort_state = {} 
        self._sort_state[col] = new
        self._sort(col, new)

    def _sort(self, col, reverse):
        """Sắp xếp dữ liệu trong Treeview (in-memory)."""
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        if col.lower() == 'tongchitieu':
            data.sort(key=lambda t: float(t[0].replace(",","")) if t[0] else 0, reverse=reverse)
        elif col.lower() == 'thuhang':
            # Sắp xếp theo thứ tự Hạng, không phải A-Z
            data.sort(key=lambda t: RANK_ORDER.get(t[0], -1), reverse=reverse)
        else: 
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=reverse)
        
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
            
        for c in DISPLAY_COLS:
            header = VI_KHACHHANG.get(c, c)
            if c in self._sort_state:
                header += " ▲" if not self._sort_state[c] else " ▼"
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            
    def _update_headings_after_load(self):
        """Reset tất cả tiêu đề cột về trạng thái không sort."""
        self._sort_state = {}
        for c in DISPLAY_COLS:
            header = VI_KHACHHANG.get(c, c)
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))

    def load_data(self):
        current_sort = self._sort_state.copy()
        
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT ThuHang FROM dbo.ThongTinKhachHang WHERE ThuHang IS NOT NULL AND ThuHang != '' ORDER BY ThuHang")
            ranks = [r[0] for r in cur.fetchall()]
            if self.filter_hang.get() not in ranks:
                self.filter_hang.set("Tất cả")
            self.filter_hang["values"] = ["Tất cả"] + ranks
            
            where = []
            params = []

            kw = self.search.get().strip()
            if kw:
                where.append("(HoTenKH LIKE ? OR SDT LIKE ?)")
                params.extend([f"%{kw}%", f"%{kw}%"])

            hang = self.filter_hang.get()
            if hang and hang != "Tất cả":
                where.append("ThuHang = ?")
                params.append(hang)
            
            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            
            select_cols = ",".join(DISPLAY_COLS)
            sql = f"SELECT {select_cols} FROM dbo.ThongTinKhachHang {where_sql}"
            
            cur.execute(sql, params)
            rows = cur.fetchall()

            for iid in self.tree.get_children():
                self.tree.delete(iid)
                
            for r in rows:
                vals = []
                for col_name in DISPLAY_COLS:
                    val = getattr(r, col_name)
                    if col_name == 'TongChiTieu':
                        val = f"{val:,.0f}" if val is not None else "0"
                    vals.append("" if val is None else str(val))
                self.tree.insert("", "end", values=tuple(vals))
            
            auto_fit_columns(self.tree)
            
            if current_sort:
                col = list(current_sort.keys())[0]
                reverse = current_sort[col]
                self._sort(col, reverse)
            else:
                self._update_headings_after_load()
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()