import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import create_button, BG_TOOLBAR, FONT_NORMAL, BG_MAIN
from Modules.utils import create_treeview_frame, setup_sortable_treeview, reset_sort_headings
from Customer.mua_hang_dialog import AddToCartDialog

# Cấu hình cột
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

class CustomerSanPhamTab(tk.Frame):
    def __init__(self, parent, role, shop_tab): 
        super().__init__(parent, bg=BG_MAIN)
        self.role = role
        self.shop_tab = shop_tab # Tham chiếu đến tab Giỏ Hàng
        self.tree = None
        self._sort_state = {}
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        tk.Label(top, text="Tìm (Mã/Tên/Công dụng):", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(top, width=20)
        self.search.pack(side="left", padx=(0, 8))

        tk.Label(top, text="Loại:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.filter_loai = ttk.Combobox(top, values=["Tất cả"], width=15, state="readonly")
        self.filter_loai.pack(side="left", padx=(0, 8))
        self.filter_loai.set("Tất cả")
        self.filter_loai.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Label(top, text="Giá từ:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.price_min = tk.Entry(top, width=8)
        self.price_min.pack(side="left")
        
        tk.Label(top, text="đến:", bg=BG_TOOLBAR).pack(side="left", padx=(2,2))
        self.price_max = tk.Entry(top, width=8)
        self.price_max.pack(side="left", padx=(0, 8))

        create_button(top, "Lọc", command=self.load_data, kind="secondary").pack(side="left", padx=6)
        create_button(top, "X", command=self._clear_filters, kind="danger", width=3).pack(side="left", padx=(0,4))
        create_button(top, "Tải lại", command=self.load_data, kind="accent").pack(side="left", padx=(4,0))

        tk.Label(self, text="Nháy đúp vào một sản phẩm để thêm vào giỏ hàng.", font=FONT_NORMAL, bg=BG_MAIN).pack(padx=10, pady=5, anchor="w")

        self.area, self.tree = create_treeview_frame(self)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        setup_sortable_treeview(self.tree, VI_SANPHAM, self._sort_state)

    def _clear_filters(self):
        self.search.delete(0, "end")
        self.filter_loai.set("Tất cả")
        self.price_min.delete(0, "end")
        self.price_max.delete(0, "end")
        self._sort_state.clear()
        self.load_data()

    def _on_double_click(self, event):
        """Mở dialog thêm vào giỏ hàng."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading": return 

        sel = self.tree.selection()
        if not sel: return
            
        try:
            item = self.tree.item(sel[0], "values")
            
            masp = item[DISPLAY_COLS.index("MaSP")]
            tensp = item[DISPLAY_COLS.index("TenSP")]
            don_gia_str = item[DISPLAY_COLS.index("DonGia")]
            dvtinh = item[DISPLAY_COLS.index("DVTinh")]
            ton_kho_str = item[DISPLAY_COLS.index("SoLuong")]
            
            # Kiểm tra tồn kho trước khi mở dialog
            ton_kho = int(ton_kho_str.replace(",", ""))
            if ton_kho <= 0:
                messagebox.showwarning("Hết hàng", f"Sản phẩm '{tensp}' đã hết hàng.", parent=self)
                return

            san_pham_data = {
                "MaSP": masp,
                "TenSP": tensp,
                "DonGia": float(don_gia_str.replace(",", "")),
                "DVTinh": dvtinh,
                "SoLuongTon": ton_kho
            }
            
            # Gọi dialog
            AddToCartDialog(self, san_pham_data, self.shop_tab)
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin sản phẩm: {e}", parent=self)

    def load_data(self):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.SanPhamNongDuoc WHERE PhanLoai IS NOT NULL AND PhanLoai != '' ORDER BY PhanLoai")
            categories = [r[0] for r in cur.fetchall()]
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
                if price_max_str:
                    where.append("COALESCE(DonGia, 0) <= ?")
                    params.append(int(price_max_str.replace(",", "")))
            except ValueError:
                pass # Bỏ qua nếu nhập giá sai
            
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