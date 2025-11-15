import tkinter as tk
from tkinter import messagebox
from db import get_connection
from Modules.ui_style import create_button, BG_TOOLBAR
from tkcalendar import DateEntry
from datetime import datetime, date
from Modules.utils import create_treeview_frame, setup_sortable_treeview, reset_sort_headings
from Features.chi_tiet import InvoiceDetailWindow 
from Features.phieu_nhap_dialog import AddImportDialog 
from Features.xuat_file import export_import_bill_to_word

VI_PHIEUNHAP = {
    "SoPN": "Số Phiếu Nhập",
    "NgayNhap": "Ngày Nhập",
    "NguoiNhap": "Người Nhập",
    "NguonNhap": "Nguồn Nhập",
    "TongGGT": "Tổng Giá Trị Nhập"
}
DISPLAY_COLS = list(VI_PHIEUNHAP.keys())

class PhieuNhapTab(tk.Frame):
    def __init__(self, parent, role, username):
        super().__init__(parent, bg="#fbf8f7")
        self.role = role
        self.username = username
        self.tree = None
        self._sort_state = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        action_frame = tk.Frame(top, bg=BG_TOOLBAR)
        action_frame.pack(side="left")
        
        create_button(action_frame, "Thêm", command=self._on_add_import, kind="primary", width=10).pack(side="left", padx=(6,4))
        create_button(action_frame, "Xóa", command=self._delete_import, kind="danger", width=10).pack(side="left", padx=4)
        create_button(action_frame, "Xuất Phiếu Nhập", command=self._on_export_import, kind="accent", width=14).pack(side="left", padx=(4,10))

        filter_frame = tk.Frame(top, bg=BG_TOOLBAR)
        filter_frame.pack(side="right")

        tk.Label(filter_frame, text="Tìm (Số PN/Nguồn):", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(filter_frame, width=18)
        self.search.pack(side="left", padx=(0, 10))

        tk.Label(filter_frame, text="Từ ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_from = DateEntry(filter_frame, width=12, date_pattern='dd/MM/yyyy')
        self.date_from.pack(side="left")
        self.date_from.delete(0, "end") 

        tk.Label(filter_frame, text="Đến ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_to = DateEntry(filter_frame, width=12, date_pattern='dd/MM/yyyy')
        self.date_to.pack(side="left", padx=(0, 10))
        self.date_to.delete(0, "end") 

        create_button(filter_frame, "Tải lại", command=self.load_data, kind="accent").pack(side="right", padx=(4,0))
        create_button(filter_frame, "X", command=self.clear_filters, kind="danger", width=3).pack(side="right", padx=(0,6))
        create_button(filter_frame, "Tìm kiếm", command=self.load_data, kind="secondary").pack(side="right", padx=6)
        
        self.area, self.tree = create_treeview_frame(self) 
        self.tree.bind("<Double-1>", self._on_double_click) 
        
        setup_sortable_treeview(self.tree, VI_PHIEUNHAP, self._sort_state)

    def _on_export_import(self):
        """Xuất phiếu nhập đã chọn ra file Word."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xuất file", "Vui lòng chọn một phiếu nhập để xuất.")
            return
        if len(sel) > 1:
            messagebox.showinfo("Xuất file", "Vui lòng chỉ chọn một phiếu nhập mỗi lần xuất.")
            return
            
        try:
            sopn = self.tree.item(sel[0], "values")[DISPLAY_COLS.index("SoPN")]
            export_import_bill_to_word(self, sopn)
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể xác định Số Phiếu Nhập.")

    def _on_add_import(self):
        """Mở cửa sổ thêm phiếu nhập mới."""
        AddImportDialog(self, self.username)
        self.load_data()

    def _delete_import(self):
        """Xóa phiếu nhập đang chọn. Trigger CSDL sẽ tự động TRỪ KHO."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xóa", "Vui lòng chọn phiếu nhập để xóa.")
            return
            
        try:
            sopn = self.tree.item(sel[0], "values")[DISPLAY_COLS.index("SoPN")]
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể tìm thấy Số Phiếu Nhập.")
            return
            
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn XÓA Phiếu Nhập {sopn}?\n\n(CẢNH BÁO: Thao tác này sẽ tự động TRỪ KHỎI KHO số lượng sản phẩm đã nhập).", parent=self):
            return
            
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.PhieuNhap WHERE SoPN = ?", (sopn,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Thành công", f"Đã xóa phiếu nhập {sopn}.\nĐã trừ kho sản phẩm.", parent=self)
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể xóa phiếu nhập:\n{e}", parent=self)

    def clear_filters(self):
        self.search.delete(0, "end")
        self.date_from.delete(0, "end")
        self.date_to.delete(0, "end")
        self._sort_state.clear()
        self.load_data()

    def load_data(self):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            where = []
            params = []
            
            kw = self.search.get().strip()
            if kw:
                where.append("(SoPN LIKE ? OR NguonNhap LIKE ?)")
                params.extend([f"%{kw}%", f"%{kw}%"])

            df_str = self.date_from.get()
            dt_str = self.date_to.get()
            
            try:
                if df_str:
                    df = datetime.strptime(df_str, '%d/%m/%Y').date()
                    where.append("CAST(NgayNhap AS DATE) >= ?") 
                    params.append(df)
                if dt_str:
                    dt = datetime.strptime(dt_str, '%d/%m/%Y').date()
                    where.append("CAST(NgayNhap AS DATE) <= ?")
                    params.append(dt)
            except ValueError:
                if df_str or dt_str:
                    messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ (dd/MM/yyyy).", parent=self)
                    return

            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            
            select_cols = ",".join(DISPLAY_COLS)
            
            sql = f"SELECT {select_cols} FROM dbo.PhieuNhap {where_sql} ORDER BY SoPN ASC"
            
            cur.execute(sql, params)
            rows = cur.fetchall()

            for iid in self.tree.get_children():
                self.tree.delete(iid)
                
            for r in rows:
                vals = []
                for col_name in DISPLAY_COLS:
                    val = getattr(r, col_name)
                    if col_name == 'NgayNhap' and isinstance(val, (datetime, date)):
                        val = val.strftime('%d/%m/%Y')
                    elif col_name == 'TongGGT':
                        val = f"{val:,.0f}" if val is not None else "0"
                    vals.append("" if val is None else str(val))
                self.tree.insert("", "end", values=tuple(vals))

            reset_sort_headings(self.tree, VI_PHIEUNHAP, self._sort_state)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()

    def _on_double_click(self, event):
        """Mở cửa sổ chi tiết (Tái sử dụng InvoiceDetailWindow)."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading": return
            
        sel = self.tree.selection()
        if not sel: return
        
        vals = self.tree.item(sel[0], "values")
        if not vals: return
        
        sopn = vals[DISPLAY_COLS.index("SoPN")]
        InvoiceDetailWindow(self, sopn)