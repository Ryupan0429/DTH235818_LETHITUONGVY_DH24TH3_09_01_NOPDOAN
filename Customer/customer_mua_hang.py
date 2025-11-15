import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import create_button, BG_MAIN, FONT_NORMAL, FONT_TITLE, BG_TOOLBAR
from Modules.utils import create_treeview_frame
from datetime import datetime
from Features.hoa_don_dialog import _next_mahd

class ShopTab(tk.Frame):
    def __init__(self, parent, username, user_data):
        super().__init__(parent, bg=BG_MAIN)
        self.username = username
        self.user_data = user_data
        
        self.conn = get_connection()
        
        self.product_data_cache = {}
        self.product_stock_map = {}
        self.cart_items = {}

        self._build_ui()
        self._load_products_to_tree() 

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _load_products_to_tree(self):
        """Tải dữ liệu TÊN, GIÁ, ĐVT, TỒN KHO GỐC vào cache, map và cây (trên)."""
        self.product_data_cache.clear()
        self.product_stock_map.clear()
        for i in self.product_tree.get_children(): self.product_tree.delete(*self.product_tree.get_children())
        
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaSP, TenSP, DonGia, DVTinh, SoLuong FROM dbo.SanPhamNongDuoc")
            rows = cur.fetchall()
            
            if not rows:
                messagebox.showwarning("Lỗi", "Không tải được danh sách sản phẩm.", parent=self)
                return

            for r in rows:
                masp, tensp, dongia, dvtinh, soluong = r.MaSP, r.TenSP, r.DonGia, (r.DVTinh or "cái"), r.SoLuong
                
                self.product_data_cache[masp] = { 
                    "TenSP": tensp, 
                    "DonGia": dongia, 
                    "DVTinh": dvtinh
                }
                self.product_stock_map[masp] = soluong
                
                self.product_tree.insert("", "end", iid=masp, values=(
                    masp, 
                    tensp, 
                    f"{soluong:,.0f}", 
                    f"{dongia:,.0f}", 
                    dvtinh
                ))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm:\n{e}", parent=self)
    
    def _filter_products(self):
        """Lọc và hiển thị sản phẩm trên Treeview (bảng trên)."""
        kw = self.search_entry.get().strip().lower() 
        
        for iid in self.product_tree.get_children():
            self.product_tree.reattach(iid, "", "end")

        if not kw: # rỗng ko tìm
             return

        for masp, cache in self.product_data_cache.items():
            if (kw not in masp.lower()) and (kw not in cache["TenSP"].lower()):
                try:
                    self.product_tree.detach(masp)
                except tk.TclError:
                    pass

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=4) # Product list
        self.grid_rowconfigure(1, weight=0) # Action frame
        self.grid_rowconfigure(2, weight=5) # Cart
        self.grid_rowconfigure(3, weight=0) # Total/Order
        self.grid_columnconfigure(0, weight=1)

        product_frame = ttk.LabelFrame(self, text="Danh sách sản phẩm")
        product_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,5))
        
        product_toolbar = tk.Frame(product_frame, bg=BG_TOOLBAR)
        product_toolbar.pack(fill="x", padx=5, pady=5)

        tk.Label(product_toolbar, text="Tìm (Mã/Tên):", bg=BG_TOOLBAR).pack(side="left", padx=(5,2))
        self.search_entry = tk.Entry(product_toolbar, width=30) 
        self.search_entry.pack(side="left", padx=(0,10))

        create_button(product_toolbar, "Tìm", command=self._filter_products, kind="secondary").pack(side="left", padx=5)
        
        def _clear_search():
            self.search_entry.delete(0, "end")
            self._filter_products()
        
        create_button(product_toolbar, "X", command=_clear_search, kind="danger", width=3).pack(side="left", padx=5)

        self.product_area, self.product_tree = create_treeview_frame(product_frame)
        self.product_cols = {"MaSP": "Mã", "TenSP": "Tên SP", "SoLuong": "Tồn Kho", "DonGia": "Đơn Giá", "DVTinh": "ĐVT"}
        
        self.product_tree["columns"] = list(self.product_cols.keys())
        for col_id, text in self.product_cols.items():
            anchor = "e" if col_id in ("SoLuong", "DonGia") else "w"
            self.product_tree.heading(col_id, text=text)
            self.product_tree.column(col_id, anchor=anchor)

        action_frame = tk.Frame(self, bg=BG_MAIN)
        action_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        tk.Label(action_frame, text="Số lượng:", font=FONT_NORMAL, bg=BG_MAIN).pack(side="left", padx=(10, 5))
        self.so_luong_entry = tk.Entry(action_frame, width=8)
        self.so_luong_entry.pack(side="left")
        self.so_luong_entry.insert(0, "1")

        create_button(action_frame, "⬇ Thêm vào giỏ ⬇", command=self._add_item_to_cart_internal, kind="primary").pack(side="left", padx=10)
        
        cart_frame = ttk.LabelFrame(self, text="Giỏ hàng của bạn")
        cart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5,10))
        
        cols_cart = ("MaSP", "TenSP", "SoLuong", "DVTinh", "DonGia", "ThanhTien")
        self.cart_area, self.cart_tree = create_treeview_frame(cart_frame)
        self.cart_tree["columns"] = cols_cart
        
        headings_cart = {"MaSP": ("Mã", "w"), "TenSP": ("Tên Sản Phẩm", "w"), "SoLuong": ("SL", "e"), 
                    "DVTinh": ("ĐVT", "w"), "DonGia": ("Đơn Giá", "e"), "ThanhTien": ("Thành Tiền", "e")}
        for col, (text, anchor) in headings_cart.items():
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, anchor=anchor)

        bottom_frame = tk.Frame(self, bg=BG_MAIN)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.total_label = tk.Label(bottom_frame, text="Tổng cộng: 0 đồng", font=FONT_TITLE, fg="red", bg=BG_MAIN)
        self.total_label.pack(side="left")
        
        create_button(bottom_frame, "⬆ Xóa khỏi giỏ ⬆", command=self._remove_item_from_cart, kind="danger").pack(side="right", padx=10)
        create_button(bottom_frame, "Đặt Hàng", command=self._on_place_order, kind="primary").pack(side="right", padx=10)

    def _update_product_tree_stock(self, masp, new_stock_value):
        """Cập nhật SỐ LƯỢNG TẠM THỜI trên cây product_tree (trên)."""
        try:
            cache = self.product_data_cache.get(masp)
            if not cache: return
            
            self.product_tree.item(masp, values=(
                masp,
                cache["TenSP"],
                f"{new_stock_value:,.0f}", # Giá trị tồn kho mới (tạm thời)
                f"{cache['DonGia']:,.0f}",
                cache["DVTinh"]
            ))
        except tk.TclError:
            pass # Lỗi nếu item không tồn tại

    def _add_item_to_cart_internal(self):
        """Thêm hàng vào giỏ từ DANH SÁCH SẢN PHẨM (Tab này)."""
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm từ danh sách.", parent=self)
            return
            
        try:
            so_luong = int(self.so_luong_entry.get())
            if so_luong <= 0: raise ValueError("Số lượng phải lớn hơn 0")
        except ValueError as e:
            messagebox.showwarning("Lỗi", f"Số lượng không hợp lệ.\n{e}", parent=self)
            return
        
        masp = sel[0]
        
        cache = self.product_data_cache.get(masp)
        ton_kho_goc = self.product_stock_map.get(masp, 0)
        
        san_pham_data_to_add = {
            "MaSP": masp,
            "TenThuoc": cache["TenSP"],
            "DonGia": float(cache["DonGia"]),
            "DVTinh": cache["DVTinh"],
            "SoLuongTon": ton_kho_goc
        }
        
        self.add_item_externally(san_pham_data_to_add, so_luong, show_message=False)
        
        self.so_luong_entry.delete(0, "end")
        self.so_luong_entry.insert(0, "1")
        
    def get_item_qty_in_cart(self, masp):
        """Hàm public: Trả về số lượng của MaSP trong giỏ hàng (dưới)."""
        return self.cart_items.get(masp, 0)
        
    def add_item_externally(self, san_pham_data, so_luong, show_message=True):
        """Hàm public: Thêm một mặt hàng vào giỏ từ một nguồn bên ngoài (dialog hoặc tab khác)."""
        try:
            masp = san_pham_data["MaSP"]
            tensp = san_pham_data["TenThuoc"]
            don_gia_goc = float(san_pham_data["DonGia"]) 
            dvtinh = san_pham_data["DVTinh"]
            ton_kho_goc = self.product_stock_map.get(masp, 0)

            sl_hien_tai_trong_gio = self.cart_items.get(masp, 0)
            sl_tong_cong_se_mua = sl_hien_tai_trong_gio + so_luong
            
            if sl_tong_cong_se_mua > ton_kho_goc:
                messagebox.showwarning("Không đủ hàng", 
                    f"Tồn kho sản phẩm '{tensp}' chỉ còn {ton_kho_goc}.\n"
                    f"Bạn đã có {sl_hien_tai_trong_gio} trong giỏ và không thể thêm {so_luong} nữa.", 
                    parent=self)
                return

            thanh_tien = don_gia_goc * sl_tong_cong_se_mua
            if masp in self.cart_items:
                self.cart_tree.item(masp, values=(
                    masp, tensp, sl_tong_cong_se_mua, dvtinh, 
                    f"{don_gia_goc:,.0f}", f"{thanh_tien:,.0f} đồng"
                ))
            else:
                self.cart_tree.insert("", "end", iid=masp, values=(
                    masp, tensp, sl_tong_cong_se_mua, dvtinh, 
                    f"{don_gia_goc:,.0f}", f"{thanh_tien:,.0f} đồng"
                ))
            
            self.cart_items[masp] = sl_tong_cong_se_mua
            
            ton_kho_tam_thoi_moi = ton_kho_goc - sl_tong_cong_se_mua
            self._update_product_tree_stock(masp, ton_kho_tam_thoi_moi)
            
            self._update_total()
            
            if show_message:
                messagebox.showinfo("Thành công", f"Đã thêm {so_luong} x {tensp} vào giỏ hàng.", parent=self)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm vào giỏ: {e}", parent=self)

    def _remove_item_from_cart(self):
        """Trả sản phẩm từ cây (dưới) về cây (trên)."""
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một mặt hàng trong giỏ để xóa.", parent=self)
            return
        
        masp = sel[0] 
        if masp in self.cart_items:
            self.cart_tree.delete(masp)
            del self.cart_items[masp]
            
            ton_kho_goc = self.product_stock_map.get(masp, 0)
            self._update_product_tree_stock(masp, ton_kho_goc)
            
            self._update_total()

    def _update_total(self):
        self.total_amount = 0
        for masp, sl_gio in self.cart_items.items():
            cache = self.product_data_cache.get(masp)
            if cache:
                self.total_amount += cache["DonGia"] * sl_gio
                
        self.total_label.config(text=f"Tổng cộng: {self.total_amount:,.0f} đồng")

    def _on_place_order(self):
        """Khách hàng tự đặt hàng."""
        if not self.cart_items:
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
                "INSERT INTO dbo.HoaDon (MaHD, MaKH, NgayGD, TongGT) VALUES (?, ?, ?, ?)",
                (ma_hd, ma_kh, ngay_gd, self.total_amount)
            )

            items_to_insert = []
            for masp, sl_gio in self.cart_items.items():
                cache = self.product_data_cache.get(masp)
                thanh_tien = cache["DonGia"] * sl_gio
                items_to_insert.append((
                    ma_hd,
                    masp,
                    cache["TenSP"],
                    int(sl_gio),
                    cache["DVTinh"],
                    cache["DonGia"],
                    thanh_tien
                ))
            
            sql_insert_detail = """
            INSERT INTO dbo.ChiTietHoaDon (MaHD, MaSP, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.executemany(sql_insert_detail, items_to_insert)

            self.conn.commit()
            
            messagebox.showinfo("Thành công", f"Đã đặt hàng thành công!\nMã hóa đơn của bạn là: {ma_hd}", parent=self)
            
            self.cart_tree.delete(*self.cart_tree.get_children())
            self.cart_items.clear()
            self._update_total()
            
            self._load_products_to_tree()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể đặt hàng:\n{e}", parent=self)