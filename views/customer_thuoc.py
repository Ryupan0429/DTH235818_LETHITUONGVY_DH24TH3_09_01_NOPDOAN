import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import create_button, BG_TOOLBAR, FONT_ICON, FONT_NORMAL, BG_MAIN
from styles.treeview_utils import create_treeview_frame
from features.add_to_cart_dialog import AddToCartDialog

VI_THUOC = {
    "MaThuoc": "Mã thuốc",
    "TenThuoc": "Tên thuốc",
    "PhanLoai": "Phân loại",
    "NhomDuocLy": "Nhóm dược lý",
    "CongDung": "Công dụng",
    "ChiDinh": "Chỉ Định",
    "LieuLuong": "Liều lượng",
    "DonGia": "Đơn giá",
    "ThanhPhan": "Thành phần",
    "DVTinh": "ĐVT"
}
DISPLAY_COLS = ["MaThuoc", "TenThuoc", "PhanLoai", "NhomDuocLy", "CongDung", "ChiDinh", "ThanhPhan", "LieuLuong", "DonGia", "DVTinh"]

class CustomerThuocTab(tk.Frame):
    def __init__(self, parent, role, shop_tab): 
        super().__init__(parent, bg="#f7fbf8")
        self.role = role
        self.shop_tab = shop_tab 
        self.tree = None
        self._sort_state = {}
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        tk.Label(top, text="Tìm:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(top, width=15)
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
        
        create_button(top, "⟳", command=self.load_data, kind="accent", font=FONT_ICON).pack(side="left", padx=(4,0))

        tk.Label(self, text="Nháy đúp vào một loại thuốc để thêm vào giỏ hàng.", font=FONT_NORMAL, bg=BG_MAIN).pack(padx=10, pady=5, anchor="w")

        self.area, self.tree = create_treeview_frame(self)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        self.tree["columns"] = DISPLAY_COLS
        for c in DISPLAY_COLS:
            header = VI_THUOC.get(c, c)
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            self.tree.column(c, anchor="w") 

        self.load_data()

    def _clear_filters(self):
        self.search.delete(0, "end")
        self.filter_loai.set("Tất cả")
        self.price_min.delete(0, "end")
        self.price_max.delete(0, "end")
        self._sort_state = {}
        self.load_data()

    def _on_double_click(self, event):
        """Mở dialog thêm vào giỏ hàng."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return 

        sel = self.tree.selection()
        if not sel:
            return
            
        try:
            item = self.tree.item(sel[0], "values")
            
            ma_thuoc = item[DISPLAY_COLS.index("MaThuoc")]
            ten_thuoc = item[DISPLAY_COLS.index("TenThuoc")]
            don_gia_str = item[DISPLAY_COLS.index("DonGia")]
            dv_tinh = item[DISPLAY_COLS.index("DVTinh")]
            
            thuoc_data = {
                "MaThuoc": ma_thuoc,
                "TenThuoc": ten_thuoc,
                "DonGia": float(don_gia_str.replace(",", "")),
                "DVTinh": dv_tinh
            }
            
            AddToCartDialog(self, thuoc_data, self.shop_tab)
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin thuốc: {e}", parent=self)

    def _on_heading_click(self, col):
        """Xử lý sort khi bấm vào tiêu đề."""
        prev = self._sort_state.get(col, None)
        new = not prev if prev is not None else False
        self._sort_state = {} 
        self._sort_state[col] = new
        self._sort(col, new)

    def _sort(self, col, reverse):
        """Sắp xếp dữ liệu trong Treeview (in-memory)."""
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        if col.lower() == 'dongia':
            data.sort(key=lambda t: float(t[0].replace(",","")) if t[0] else 0, reverse=reverse)
        else: 
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=reverse)
        
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
            
        for c in DISPLAY_COLS:
            header = VI_THUOC.get(c, c)
            if c in self._sort_state:
                header += " ▲" if not self._sort_state[c] else " ▼"
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
    
    def _update_headings_after_load(self):
        """Reset tất cả tiêu đề cột về trạng thái không sort."""
        self._sort_state = {}
        for c in DISPLAY_COLS:
            header = VI_THUOC.get(c, c)
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))

    def load_data(self):
        current_sort = self._sort_state.copy()
        
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.ThuocNongDuoc WHERE PhanLoai IS NOT NULL AND PhanLoai != '' ORDER BY PhanLoai")
            categories = [r[0] for r in cur.fetchall()]
            self.filter_loai["values"] = ["Tất cả"] + categories
            
            where = []
            params = []

            kw = self.search.get().strip()
            if kw:
                # Tìm kiếm trên tất cả các cột trong DISPLAY_COLS
                search_clauses = []
                search_params = []
                for col in DISPLAY_COLS:
                    if col.lower() == 'dongia':
                        search_clauses.append(f"CAST({col} AS VARCHAR(50)) LIKE ?")
                    else:
                        search_clauses.append(f"{col} LIKE ?")
                    search_params.append(f"%{kw}%")
                
                if search_clauses:
                    where.append(f"({' OR '.join(search_clauses)})")
                    params.extend(search_params)

            loai = self.filter_loai.get()
            if loai and loai != "Tất cả":
                where.append("PhanLoai = ?")
                params.append(loai)

            price_min_str = self.price_min.get().strip()
            price_max_str = self.price_max.get().strip()
            try:
                if price_min_str:
                    where.append("COALESCE(DonGia, 0) >= ?")
                    params.append(float(price_min_str))
            except ValueError:
                messagebox.showwarning("Lỗi", "Giá trị 'từ' phải là số.", parent=self)
                return 
            try:
                if price_max_str:
                    where.append("COALESCE(DonGia, 0) <= ?")
                    params.append(float(price_max_str))
            except ValueError:
                messagebox.showwarning("Lỗi", "Giá trị 'đến' phải là số.", parent=self)
                return 
            
            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            
            select_cols = ",".join(DISPLAY_COLS)
            sql = f"SELECT {select_cols} FROM dbo.ThuocNongDuoc {where_sql}"
            
            cur.execute(sql, params)
            rows = cur.fetchall()

            for iid in self.tree.get_children():
                self.tree.delete(iid)
                
            for r in rows:
                vals = []
                for col_name in DISPLAY_COLS:
                    val = getattr(r, col_name)
                    if col_name == 'DonGia':
                        val = f"{val:,.0f}" if val is not None else "0"
                    vals.append("" if val is None else str(val))
                self.tree.insert("", "end", values=tuple(vals))
            
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