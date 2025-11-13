import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import create_button, BG_MAIN, FONT_NORMAL, FONT_TITLE, BG_TOOLBAR
from styles.treeview_utils import create_treeview_frame, auto_fit_columns
from services.finance import get_discount_rate
from features.add_invoice_dialog import _next_mahd
from datetime import datetime

class ShopTab(tk.Frame):
    def __init__(self, parent, username, user_data):
        super().__init__(parent, bg=BG_MAIN)
        self.username = username
        self.user_data = user_data
        self.discount_rate = get_discount_rate(self.user_data.get("ThuHang"))
        
        self.conn = get_connection()
        self.thuoc_data_dict = {} 
        self.total_amount = 0.0

        self._build_ui()
        self._load_products_to_tree() # Tải toàn bộ data vào self.thuoc_data_dict
        self._filter_products() # Hiển thị lần đầu (không lọc)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _load_products_to_tree(self):
        """Chỉ tải DS sản phẩm vào self.thuoc_data_dict."""
        self.thuoc_data_dict = {}
        
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaThuoc, TenThuoc, DonGia, PhanLoai, CongDung, DVTinh FROM dbo.ThuocNongDuoc")
            rows = cur.fetchall()
            
            if not rows:
                messagebox.showwarning("Lỗi", "Không tải được danh sách sản phẩm.", parent=self)
                return

            for r in rows:
                dv_tinh = r.DVTinh or "cái"
                self.thuoc_data_dict[r.MaThuoc] = { 
                    "MaThuoc": r.MaThuoc,
                    "TenThuoc": r.TenThuoc, 
                    "DonGia": r.DonGia, 
                    "DVTinh": dv_tinh,
                    "PhanLoai": r.PhanLoai,
                    "CongDung": r.CongDung
                }
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách thuốc:\n{e}", parent=self)
    
    def _filter_products(self):
        """Lọc và hiển thị sản phẩm trên Treeview."""
        # Xóa tree cũ
        for i in self.product_tree.get_children(): self.product_tree.delete(i)
        
        # Lấy từ khóa tìm kiếm
        kw_ma = self.product_search_id.get().strip().lower()
        kw_ten = self.product_search_name.get().strip().lower()

        for ma_thuoc, data in self.thuoc_data_dict.items():
            # Lọc
            if (kw_ma and kw_ma not in data["MaThuoc"].lower()) or \
               (kw_ten and kw_ten not in data["TenThuoc"].lower()):
                continue
                
            # Thêm vào tree
            self.product_tree.insert("", "end", values=(
                data["MaThuoc"], 
                data["TenThuoc"], 
                f"{data['DonGia']:,.0f}", 
                data["DVTinh"], 
                data["PhanLoai"], 
                data["CongDung"]
            ))
            
        auto_fit_columns(self.product_tree)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=4) # Product list
        self.grid_rowconfigure(1, weight=0) # Action frame
        self.grid_rowconfigure(2, weight=5) # Cart
        self.grid_rowconfigure(3, weight=0) # Total/Order
        self.grid_columnconfigure(0, weight=1)

        product_frame = ttk.LabelFrame(self, text="Danh sách sản phẩm")
        product_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,5))
        
        # --- (THÊM THANH TÌM KIẾM) ---
        product_toolbar = tk.Frame(product_frame, bg=BG_TOOLBAR)
        product_toolbar.pack(fill="x", padx=5, pady=5)

        tk.Label(product_toolbar, text="Tìm Mã:", bg=BG_TOOLBAR).pack(side="left", padx=(5,2))
        self.product_search_id = tk.Entry(product_toolbar, width=12)
        self.product_search_id.pack(side="left", padx=(0,10))

        tk.Label(product_toolbar, text="Tìm Tên:", bg=BG_TOOLBAR).pack(side="left", padx=(5,2))
        self.product_search_name = tk.Entry(product_toolbar, width=20)
        self.product_search_name.pack(side="left", padx=(0,10))

        create_button(product_toolbar, "Tìm", command=self._filter_products, kind="secondary").pack(side="left", padx=5)
        
        def _clear_search():
            self.product_search_id.delete(0, "end")
            self.product_search_name.delete(0, "end")
            self._filter_products()
        
        create_button(product_toolbar, "X", command=_clear_search, kind="danger", width=3).pack(side="left", padx=5)
        # --- (HẾT THANH TÌM KIẾM) ---

        self.product_area, self.product_tree = create_treeview_frame(product_frame)
        self.product_tree.bind("<<TreeviewSelect>>", self._on_product_select)
        
        # Cấu hình cột cho product_tree (chuyển từ _load_products về đây)
        cols = ("MaThuoc", "TenThuoc", "DonGia", "DVTinh", "PhanLoai", "CongDung")
        self.product_tree["columns"] = cols
        headings = {"MaThuoc": "Mã", "TenThuoc": "Tên Thuốc", "DonGia": "Đơn Giá", "DVTinh": "ĐVT", "PhanLoai": "Loại", "CongDung": "Công Dụng"}
        for col, text in headings.items():
            self.product_tree.heading(col, text=text)
            self.product_tree.column(col, anchor="w")
        # --- (HẾT CẤU HÌNH CỘT) ---

        action_frame = tk.Frame(self, bg=BG_MAIN)
        action_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        tk.Label(action_frame, text="Sản phẩm đã chọn:", font=FONT_NORMAL, bg=BG_MAIN).pack(side="left", padx=(0, 5))
        self.selected_product_label = tk.Label(action_frame, text="...", font=FONT_NORMAL, bg="white", relief="sunken", width=30)
        self.selected_product_label.pack(side="left")
        
        tk.Label(action_frame, text="Số lượng:", font=FONT_NORMAL, bg=BG_MAIN).pack(side="left", padx=(10, 5))
        self.so_luong_entry = tk.Entry(action_frame, width=8)
        self.so_luong_entry.pack(side="left")
        self.so_luong_entry.insert(0, "1")

        create_button(action_frame, "Thêm vào giỏ", command=self._add_item_to_cart, kind="primary").pack(side="left", padx=10)
        
        cart_frame = ttk.LabelFrame(self, text="Giỏ hàng của bạn")
        cart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5,10))
        
        cols_cart = ("MaThuoc", "TenSP", "SoLuong", "DVTinh", "DonGiaGoc", "Giam", "DonGiaSau", "ThanhTien")
        self.cart_area, self.cart_tree = create_treeview_frame(cart_frame)
        self.cart_tree["columns"] = cols_cart
        
        headings_cart = {"MaThuoc": ("Mã", "w"), "TenSP": ("Tên Sản Phẩm", "w"), "SoLuong": ("SL", "e"), 
                    "DVTinh": ("ĐVT", "w"), "DonGiaGoc": ("Giá Gốc", "e"), "Giam": ("Giảm", "e"),
                    "DonGiaSau": ("Đơn Giá", "e"), "ThanhTien": ("Thành Tiền", "e")}
        for col, (text, anchor) in headings_cart.items():
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, anchor=anchor)

        auto_fit_columns(self.cart_tree)

        bottom_frame = tk.Frame(self, bg=BG_MAIN)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.total_label = tk.Label(bottom_frame, text="Tổng cộng: 0 đồng", font=FONT_TITLE, fg="red", bg=BG_MAIN)
        self.total_label.pack(side="left")
        
        create_button(bottom_frame, "Xóa khỏi giỏ", command=self._remove_item, kind="danger").pack(side="right", padx=10)
        create_button(bottom_frame, "Đặt Hàng", command=self._on_place_order, kind="primary").pack(side="right", padx=10)

    def _on_product_select(self, event):
        """Hiển thị tên thuốc khi chọn từ Treeview."""
        sel = self.product_tree.selection()
        if not sel:
            return
        item = self.product_tree.item(sel[0], "values")
        self.selected_product_label.config(text=item[1])
        self.so_luong_entry.delete(0, "end")
        self.so_luong_entry.insert(0, "1")

    def _add_item_to_cart(self):
        """Thêm hàng vào giỏ từ DANH SÁCH SẢN PHẨM (Tab này)."""
        sel = self.product_tree.selection()
        so_luong_str = self.so_luong_entry.get()

        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm từ danh sách.", parent=self)
            return
        
        try:
            so_luong = int(so_luong_str)
            if so_luong <= 0: raise ValueError("Số lượng phải lớn hơn 0")
        except ValueError as e:
            messagebox.showwarning("Lỗi", f"Số lượng không hợp lệ.\n{e}", parent=self)
            return
        
        item = self.product_tree.item(sel[0], "values")
        ma_thuoc = item[0]
        
        thuoc_info = self.thuoc_data_dict.get(ma_thuoc)
        if not thuoc_info:
             messagebox.showerror("Lỗi", "Lỗi tra cứu sản phẩm.", parent=self)
             return
             
        # Gói dữ liệu và gọi hàm public
        thuoc_data_to_add = {
            "MaThuoc": ma_thuoc,
            "TenThuoc": thuoc_info["TenThuoc"],
            "DonGia": float(thuoc_info["DonGia"]),
            "DVTinh": thuoc_info["DVTinh"]
        }
        
        self.add_item_externally(thuoc_data_to_add, so_luong, show_message=False)
        
        # Xóa lựa chọn
        self.so_luong_entry.delete(0, "end")
        self.so_luong_entry.insert(0, "1")
        self.product_tree.selection_remove(sel[0])
        self.selected_product_label.config(text="...")
        
    def add_item_externally(self, thuoc_data, so_luong, show_message=True):
        """Thêm một mặt hàng vào giỏ từ một nguồn bên ngoài (dialog hoặc tab khác)."""
        try:
            ma_thuoc = thuoc_data["MaThuoc"]
            ten_thuoc = thuoc_data["TenThuoc"]
            don_gia_goc = float(thuoc_data["DonGia"]) 
            dv_tinh = thuoc_data["DVTinh"]

            giam_str = f"{self.discount_rate * 100:,.0f}%"
            don_gia_sau = don_gia_goc * (1 - self.discount_rate)
            
            for item_id in self.cart_tree.get_children():
                item_ma_thuoc = self.cart_tree.item(item_id, "values")[0]
                if item_ma_thuoc == ma_thuoc:
                    old_sl = int(self.cart_tree.item(item_id, "values")[2])
                    new_sl = old_sl + so_luong
                    new_thanh_tien = don_gia_sau * new_sl
                    self.cart_tree.item(item_id, values=(
                        ma_thuoc, ten_thuoc, new_sl, dv_tinh, f"{don_gia_goc:,.0f}", 
                        giam_str, f"{don_gia_sau:,.0f}", f"{new_thanh_tien:,.0f} đồng"
                    ))
                    break
            else:
                thanh_tien = don_gia_sau * so_luong
                self.cart_tree.insert("", "end", values=(
                    ma_thuoc, ten_thuoc, so_luong, dv_tinh, f"{don_gia_goc:,.0f}", 
                    giam_str, f"{don_gia_sau:,.0f}", f"{thanh_tien:,.0f} đồng"
                ))
            
            self._update_total()
            auto_fit_columns(self.cart_tree)
            
            if show_message:
                messagebox.showinfo("Thành công", f"Đã thêm {so_luong} x {ten_thuoc} vào giỏ hàng.", parent=self)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm vào giỏ: {e}", parent=self)

    def _remove_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một mặt hàng trong giỏ để xóa.", parent=self)
            return
        for item_id in sel:
            self.cart_tree.delete(item_id)
        self._update_total()

    def _update_total(self):
        self.total_amount = 0.0
        for item_id in self.cart_tree.get_children():
            thanh_tien_str = self.cart_tree.item(item_id, "values")[7].replace(" đồng","").replace(",", "")
            self.total_amount += float(thanh_tien_str)
        self.total_label.config(text=f"Tổng cộng: {self.total_amount:,.0f} đồng")

    def _on_place_order(self):
        if not self.cart_tree.get_children():
            messagebox.showwarning("Giỏ hàng trống", "Vui lòng thêm sản phẩm vào giỏ.", parent=self)
            return
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đặt hàng?", parent=self):
            return

        try:
            cur = self.conn.cursor()
            ma_hd = _next_mahd(self.conn) 
            ngay_gd = datetime.now().date()
            ma_kh = self.username

            cur.execute(
                "INSERT INTO dbo.HoaDonNongDuoc (MaHD, MaKH, NgayGD, TongGT) VALUES (?, ?, ?, ?)",
                (ma_hd, ma_kh, ngay_gd, self.total_amount)
            )

            items_to_insert = []
            for item_id in self.cart_tree.get_children():
                vals = self.cart_tree.item(item_id, "values")
                item_data = (
                    ma_hd,
                    vals[0], # MaThuoc
                    vals[1], # TenSP
                    int(vals[2]), # SoLuong
                    vals[3], # DVTinh
                    float(vals[6].replace(",", "")), # DonGiaSau
                    float(vals[7].replace(" đồng","").replace(",", ""))  # ThanhTien
                )
                items_to_insert.append(item_data)
            
            sql_insert_detail = """
            INSERT INTO dbo.ChiTietHoaDon (MaHD, MaThuoc, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.executemany(sql_insert_detail, items_to_insert)

            cur.execute(
                "UPDATE dbo.ThongTinKhachHang SET TongChiTieu = COALESCE(TongChiTieu, 0) + ? WHERE MaKH = ?",
                (self.total_amount, ma_kh)
            )

            self.conn.commit()
            
            messagebox.showinfo("Thành công", f"Đã đặt hàng thành công!\nMã hóa đơn của bạn là: {ma_hd}", parent=self)
            self.cart_tree.delete(*self.cart_tree.get_children())
            self._update_total()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể đặt hàng:\n{e}", parent=self)