import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import create_button, BG_TOOLBAR
from Modules.utils import create_treeview_frame, setup_sortable_treeview, reset_sort_headings
from Features.san_pham_dialog import SanPhamDialog 
from Modules.nghiep_vu_xu_ly import xoa_san_pham, cap_nhat_gia_hang_loat

VI_SANPHAM = {
    "MaSP": "Mã SP",
    "TenSP": "Tên Sản Phẩm",
    "PhanLoai": "Phân loại",
    "CongDung": "Công dụng",
    "SoLuong": "Tồn kho",
    "DVTinh": "ĐVT",
    "DonGia": "Đơn giá" 
}
DISPLAY_COLS = list(VI_SANPHAM.keys())

class SanPhamTab(tk.Frame):
    def __init__(self, parent):
        # Khởi tạo Tab Sản Phẩm
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
        create_button(action_frame, "Đổi Giá (%)", command=self._on_batch_price_change, kind="accent", width=10).pack(side="left", padx=(4,10))

        filter_frame = tk.Frame(top, bg=BG_TOOLBAR)
        filter_frame.pack(side="right") 

        tk.Label(filter_frame, text="Tìm (Mã/Tên/CD):", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(filter_frame, width=20)
        self.search.pack(side="left", padx=(0, 8))
        
        tk.Label(filter_frame, text="Loại:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.filter_loai = ttk.Combobox(filter_frame, values=["Tất cả"], width=15, state="readonly")
        self.filter_loai.pack(side="left", padx=(0, 8))
        self.filter_loai.set("Tất cả")
        self.filter_loai.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Label(filter_frame, text="Giá từ:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.price_min = tk.Entry(filter_frame, width=8)
        self.price_min.pack(side="left")
        
        tk.Label(filter_frame, text="đến:", bg=BG_TOOLBAR).pack(side="left", padx=(2,2))
        self.price_max = tk.Entry(filter_frame, width=8)
        self.price_max.pack(side="left", padx=(0, 8))

        create_button(filter_frame, "Tải lại", command=self.load_data, kind="accent").pack(side="right", padx=(4,0))
        create_button(filter_frame, "X", command=self._clear_filters, kind="danger", width=3).pack(side="right", padx=(0,4))
        create_button(filter_frame, "Tìm kiếm", command=self.load_data, kind="secondary").pack(side="right", padx=6)

        self.area, self.tree = create_treeview_frame(self)
        setup_sortable_treeview(self.tree, VI_SANPHAM, self._sort_state)

    def _on_add(self):
        # Mở cửa sổ Thêm sản phẩm
        SanPhamDialog(self, masp=None)
        self.load_data() 

    def _on_edit(self):
        # Mở cửa sổ Sửa sản phẩm
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sửa", "Vui lòng chọn một sản phẩm để sửa.")
            return
        if len(sel) > 1:
            messagebox.showinfo("Sửa", "Vui lòng chỉ chọn một sản phẩm để sửa.")
            return
            
        try:
            item = self.tree.item(sel[0])
            masp = item["values"][DISPLAY_COLS.index("MaSP")]
            
            SanPhamDialog(self, masp=masp)
            self.load_data()
            
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể xác định Mã Sản Phẩm.")

    def _on_delete(self):
        # Xóa các sản phẩm đã chọn
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xóa", "Vui lòng chọn ít nhất một sản phẩm để xóa.")
            return

        masp_list = []
        tensp_list = []
        for item_id in sel:
            try:
                item = self.tree.item(item_id)
                masp = item["values"][DISPLAY_COLS.index("MaSP")]
                tensp = item["values"][DISPLAY_COLS.index("TenSP")]
                masp_list.append(masp)
                tensp_list.append(tensp)
            except (ValueError, IndexError):
                pass
        
        if not masp_list:
             messagebox.showerror("Lỗi", "Không thể xác định Mã Sản Phẩm để xóa.")
             return

        tensp_str = "\n- ".join(tensp_list)
        if not messagebox.askyesno("Xác nhận", 
            f"Bạn có chắc muốn xóa {len(masp_list)} sản phẩm đã chọn?\n- {tensp_str}\n\n"
            "CẢNH BÁO: Thao tác này sẽ thất bại nếu sản phẩm đã tồn tại trong Hóa đơn hoặc Phiếu nhập.",
            parent=self, icon='warning'):
            return
            
        try:
            success, error = xoa_san_pham(masp_list)
            
            if error:
                raise Exception(error)
            
            messagebox.showinfo("Thành công", f"Đã xóa {len(masp_list)} sản phẩm thành công.", parent=self)
            self.load_data()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể xóa. Có thể sản phẩm đã có trong Hóa đơn hoặc Phiếu nhập.\n{e}", parent=self)

    def _on_batch_price_change(self):
        # Thay đổi giá hàng loạt
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Chọn sản phẩm", "Vui lòng chọn ít nhất một sản phẩm từ danh sách để thay đổi giá.", parent=self)
            return
        
        from Features.doi_gia_dialog import PriceChangeDialog
        
        dialog = PriceChangeDialog(self, product_count=len(sel))
        multiplier = dialog.result 
        
        if multiplier is None:
            return 
            
        percent_str = f"{ (multiplier - 1) * 100:+.0f}%"
        
        if not messagebox.askyesno("Xác nhận", 
            f"Bạn có chắc muốn thay đổi giá của {len(sel)} sản phẩm đã chọn ({percent_str}) không?\n\n"
            "Đơn giá mới sẽ được làm tròn đến hàng nghìn.", parent=self):
            return
        
        masp_list = []
        for item_id in sel:
            masp = self.tree.item(item_id, "values")[DISPLAY_COLS.index("MaSP")]
            masp_list.append(masp)
            
        try:
            success, error = cap_nhat_gia_hang_loat(masp_list, multiplier)
            
            if error:
                raise Exception(error)
            
            messagebox.showinfo("Thành công", f"Đã cập nhật giá cho {len(masp_list)} sản phẩm.", parent=self)
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể cập nhật giá:\n{e}", parent=self)

    def _clear_filters(self):
        # Xóa các bộ lọc và tải lại
        self.search.delete(0, "end")
        self.filter_loai.set("Tất cả")
        self.price_min.delete(0, "end")
        self.price_max.delete(0, "end")
        self._sort_state.clear() 
        self.load_data()

    def load_data(self):
        # Tải/Tải lại dữ liệu từ CSDL
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.SanPhamNongDuoc WHERE PhanLoai IS NOT NULL AND PhanLoai != '' ORDER BY PhanLoai")
            categories = [r[0] for r in cur.fetchall()]
            if self.filter_loai.get() not in categories:
                self.filter_loai.set("Tất cả")
            self.filter_loai["values"] = ["Tất cả"] + categories
            
            where = []
            params = []

            kw = self.search.get().strip()
            if kw:
                where.append("(MaSP LIKE ? OR TenSP LIKE ? OR CongDung LIKE ?)")
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

            loai = self.filter_loai.get()
            if loai and loai != "Tất cả":
                where.append("PhanLoai = ?")
                params.append(loai)

            price_min_str = self.price_min.get().strip()
            price_max_str = self.price_max.get().strip()
            try:
                if price_min_str:
                    where.append("COALESCE(DonGia, 0) >= ?")
                    params.append(int(price_min_str.replace(",", "")))
            except ValueError:
                 pass 
            try:
                if price_max_str:
                    where.append("COALESCE(DonGia, 0) <= ?")
                    params.append(int(price_max_str.replace(",", "")))
            except ValueError:
                 pass 
            
            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            
            select_cols = ",".join(DISPLAY_COLS)
            sql = f"SELECT {select_cols} FROM dbo.SanPhamNongDuoc {where_sql}"
            
            cur.execute(sql, params)
            rows = cur.fetchall()

            for iid in self.tree.get_children():
                self.tree.delete(iid)
                
            for r in rows:
                vals = []
                for col_name in DISPLAY_COLS:
                    val = getattr(r, col_name)
                    if col_name == 'DonGia' or col_name == 'SoLuong':
                        val = f"{val:,.0f}" if val is not None else "0"
                    vals.append("" if val is None else str(val))
                self.tree.insert("", "end", values=tuple(vals))
            
            reset_sort_headings(self.tree, VI_SANPHAM, self._sort_state)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()