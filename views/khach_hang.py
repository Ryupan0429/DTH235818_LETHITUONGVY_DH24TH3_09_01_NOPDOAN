import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import create_button, BG_TOOLBAR
from Modules.utils import create_treeview_frame, setup_sortable_treeview, reset_sort_headings
from Features.khach_hang_dialog import CustomerFormDialog 
from Features.lich_su_GD import CustomerHistoryDialog
from Modules.nghiep_vu_xu_ly import xoa_khach_hang

VI_KHACHHANG = {
    "MaKH": "Mã KH",
    "TenKH": "Họ Tên",
    "SDT": "SĐT",
    "GioiTinh": "Giới tính",
    "QueQuan": "Quê quán",
    "TongChiTieu": "Tổng chi tiêu"
}
DISPLAY_COLS = list(VI_KHACHHANG.keys())

class KhachHangTab(tk.Frame):
    def __init__(self, parent):
        # Khởi tạo Tab Khách Hàng
        super().__init__(parent, bg="#f7fbf8")
        self.tree = None
        self._sort_state = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # Xây dựng giao diện (Toolbar, Bảng)
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        action_frame = tk.Frame(top, bg=BG_TOOLBAR)
        action_frame.pack(side="left")
        
        create_button(action_frame, "Thêm", command=self._on_add, kind="primary", width=10).pack(side="left", padx=(6,4))
        create_button(action_frame, "Sửa", command=self._on_edit, kind="secondary", width=10).pack(side="left", padx=4)
        create_button(action_frame, "Xóa", command=self._on_delete, kind="danger", width=10).pack(side="left", padx=4)
        create_button(action_frame, "Top 3 Chi Tiêu", command=self._show_top_3, kind="accent", width=12).pack(side="left", padx=(4,10))

        filter_frame = tk.Frame(top, bg=BG_TOOLBAR)
        filter_frame.pack(side="right") 

        tk.Label(filter_frame, text="Tìm (Mã/Tên/SĐT):", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(filter_frame, width=20)
        self.search.pack(side="left", padx=(0, 8))
        
        tk.Label(filter_frame, text="Quê quán:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.filter_quequan = ttk.Combobox(filter_frame, values=["Tất cả"], width=15, state="readonly")
        self.filter_quequan.pack(side="left", padx=(0, 8))
        self.filter_quequan.set("Tất cả")
        self.filter_quequan.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        create_button(filter_frame, "Tải lại", 
                      command=self.load_data, 
                      kind="accent").pack(side="right", padx=(4,0)) 
        
        create_button(filter_frame, "X", command=self._clear_filters, kind="danger", width=3).pack(side="right", padx=(0,4))
        
        create_button(filter_frame, "Tìm kiếm", command=self.load_data, kind="secondary").pack(side="right", padx=(0,6))
        
        self.area, self.tree = create_treeview_frame(self)
        
        self.tree.bind("<Double-1>", self._on_double_click)
        
        setup_sortable_treeview(self.tree, VI_KHACHHANG, self._sort_state)

    def _on_add(self):
        # Mở cửa sổ Thêm khách hàng
        CustomerFormDialog(self, makh=None)
        self.load_data() 

    def _on_edit(self):
        # Mở cửa sổ Sửa khách hàng
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sửa", "Vui lòng chọn một khách hàng để sửa.")
            return
        if len(sel) > 1:
            messagebox.showinfo("Sửa", "Vui lòng chỉ chọn một khách hàng để sửa.")
            return
            
        try:
            item = self.tree.item(sel[0])
            makh = item["values"][DISPLAY_COLS.index("MaKH")]
            CustomerFormDialog(self, makh=makh)
            self.load_data()
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể xác định Mã Khách hàng.")

    def _on_delete(self):
        # Xóa các khách hàng đã chọn
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xóa", "Vui lòng chọn ít nhất một khách hàng để xóa.")
            return

        makh_list = []
        tenkh_list = []
        for item_id in sel:
            try:
                item = self.tree.item(item_id)
                makh = item["values"][DISPLAY_COLS.index("MaKH")]
                tenkh = item["values"][DISPLAY_COLS.index("TenKH")]
                makh_list.append(makh)
                tenkh_list.append(tenkh)
            except (ValueError, IndexError):
                pass
        
        if not makh_list:
             messagebox.showerror("Lỗi", "Không thể xác định Mã Khách hàng để xóa.")
             return

        tenkh_str = "\n- ".join(tenkh_list)
        if not messagebox.askyesno("Xác nhận", 
            f"Bạn có chắc muốn xóa {len(makh_list)} khách hàng đã chọn?\n- {tenkh_str}\n\n"
            "(Thao tác này sẽ xóa TẤT CẢ Hóa đơn của họ).", 
            parent=self, icon='warning'):
            return
            
        try:
            success, error = xoa_khach_hang(makh_list)
            
            if error:
                raise Exception(error)
            
            messagebox.showinfo("Thành công", f"Đã xóa {len(makh_list)} khách hàng thành công.", parent=self)
            self.load_data()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể xóa. Lỗi: \n{e}", parent=self)
    
    def _on_double_click(self, event):
        # Mở cửa sổ Lịch sử Giao dịch
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading": return
            
        sel = self.tree.selection()
        if not sel or len(sel) > 1: 
            return 
        
        try:
            item = self.tree.item(sel[0])
            makh = item["values"][DISPLAY_COLS.index("MaKH")]
            tenkh = item["values"][DISPLAY_COLS.index("TenKH")]
            
            CustomerHistoryDialog(self, makh, tenkh)
            
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể lấy thông tin khách hàng.")

    def _show_top_3(self):
        # Hiển thị Top 3 khách hàng chi tiêu
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            sql = "SELECT TOP 3 MaKH, TenKH, TongChiTieu FROM dbo.KhachHang ORDER BY TongChiTieu DESC"
            cur.execute(sql)
            rows = cur.fetchall()
            conn.close()
            
            if not rows:
                messagebox.showinfo("Top 3 Khách hàng", "Không có dữ liệu chi tiêu.", parent=self)
                return
            
            result_str = "Top 3 Khách hàng Chi tiêu cao nhất:\n\n"
            for i, row in enumerate(rows):
                result_str += f"{i+1}. {row.TenKH} ({row.MaKH})\n"
                result_str += f"   Tổng chi tiêu: {row.TongChiTieu:,.0f} VNĐ\n\n"
            
            messagebox.showinfo("Top 3 Khách hàng", result_str, parent=self)

        except Exception as e:
            if conn: conn.close()
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu Top 3:\n{e}", parent=self)

    def _clear_filters(self):
        # Xóa các bộ lọc và tải lại
        self.search.delete(0, "end")
        self.filter_quequan.set("Tất cả")
        self._sort_state.clear() 
        self.load_data()

    def load_data(self):
        # Tải/Tải lại dữ liệu từ CSDL
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT QueQuan FROM dbo.KhachHang WHERE QueQuan IS NOT NULL AND QueQuan != '' ORDER BY QueQuan")
            ranks = [r[0] for r in cur.fetchall()]
            if self.filter_quequan.get() not in ranks:
                self.filter_quequan.set("Tất cả")
            self.filter_quequan["values"] = ["Tất cả"] + ranks
            
            where = []
            params = []

            kw = self.search.get().strip()
            if kw:
                where.append("(MaKH LIKE ? OR TenKH LIKE ? OR SDT LIKE ?)")
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

            quequan = self.filter_quequan.get()
            if quequan and quequan != "Tất cả":
                where.append("QueQuan = ?")
                params.append(quequan)
            
            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            
            select_cols = ",".join(DISPLAY_COLS)
            sql = f"SELECT {select_cols} FROM dbo.KhachHang {where_sql}"
            
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
            
            reset_sort_headings(self.tree, VI_KHACHHANG, self._sort_state)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()