import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from tkcalendar import DateEntry
from Modules.ui_style import center, FONT_NORMAL, create_button
from Modules.utils import create_treeview_frame
from Features.khach_hang_dialog import CustomerFormDialog
from Modules.nghiep_vu_xu_ly import them_hoa_don

class AddInvoiceDialog(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.parent = parent
        self.username = username 
        
        self.title("Tạo Hóa đơn mới")
        self.geometry("1000x700") 
        
        self.conn = get_connection()
        self.product_data_cache = self._load_product_data_cache()
        self.product_stock_map = {}
        self.cart_items = {}
        
        self._build_ui()
        self._load_customers()
        self._load_products_to_tree() 
        
        center(self, 1000, 700)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _load_product_data_cache(self):
        data = {}
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaSP, TenSP, DonGia, DVTinh FROM dbo.SanPhamNongDuoc")
            for row in cur.fetchall():
                data[row.MaSP] = {
                    "TenSP": row.TenSP,
                    "DonGia": row.DonGia,
                    "DVTinh": row.DVTinh or "cái"
                }
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm:\n{e}", parent=self)
            return {}

    def _load_customers(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaKH, TenKH, SDT FROM dbo.KhachHang ORDER BY TenKH")
            
            customer_display_list = []
            for row in cur.fetchall():
                display_name = f"{row.TenKH} - {row.SDT} ({row.MaKH})"
                customer_display_list.append(display_name)
                
            self.customer_cb["values"] = customer_display_list
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khách hàng:\n{e}", parent=self)

    def _on_add_customer(self):
        CustomerFormDialog(self, makh=None)
        self._load_customers()

    def _build_ui(self):
        
        self.grid_rowconfigure(0, weight=0) # info_frame
        self.grid_rowconfigure(1, weight=5) # product_frame (bảng trên)
        self.grid_rowconfigure(2, weight=0) # action_frame
        self.grid_rowconfigure(3, weight=4) # cart_frame (bảng dưới)
        self.grid_rowconfigure(4, weight=0) # bottom_frame (nút)
        self.grid_columnconfigure(0, weight=1)

        info_frame = tk.Frame(self)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        tk.Label(info_frame, text="Khách hàng:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.customer_cb = ttk.Combobox(info_frame, width=40, font=FONT_NORMAL, state="readonly")
        self.customer_cb.grid(row=0, column=1, padx=5, pady=5)
        
        self.add_cust_btn = create_button(info_frame, "+", self._on_add_customer, kind="accent", width=3)
        self.add_cust_btn.grid(row=0, column=2, padx=(0, 10))

        tk.Label(info_frame, text="Ngày GD:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.ngay_gd_entry = DateEntry(info_frame, width=12, date_pattern='dd/MM/yyyy')
        self.ngay_gd_entry.grid(row=0, column=4, padx=5, pady=5)

        product_frame = ttk.LabelFrame(self, text="Sản phẩm (Trong kho)")
        product_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.p_area, self.product_tree = create_treeview_frame(product_frame)
        self.product_cols = {"MaSP": "Mã SP", "TenSP": "Tên SP", "SoLuong": "Tồn Kho", "DonGia": "Đơn Giá", "DVTinh": "ĐVT"}
        
        self.product_tree["columns"] = list(self.product_cols.keys())
        for col_id, text in self.product_cols.items():
            anchor = "e" if col_id in ("SoLuong", "DonGia") else "w"
            self.product_tree.heading(col_id, text=text)
            self.product_tree.column(col_id, anchor=anchor)

        action_frame = tk.Frame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        tk.Label(action_frame, text="Số lượng:", font=FONT_NORMAL).pack(side="left", padx=(10, 5))
        self.so_luong_entry = tk.Entry(action_frame, width=8, font=FONT_NORMAL)
        self.so_luong_entry.pack(side="left")
        self.so_luong_entry.insert(0, "1")

        create_button(action_frame, "⬇ Thêm vào Hóa đơn ⬇", command=self._add_item_to_cart, kind="primary").pack(side="left", padx=10)
        create_button(action_frame, "⬆ Bỏ khỏi Hóa đơn ⬆", command=self._remove_item_from_cart, kind="danger").pack(side="left", padx=10)

        cart_frame = ttk.LabelFrame(self, text="Thông tin Hóa đơn (Sản phẩm đã chọn)")
        cart_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        
        self.c_area, self.cart_tree = create_treeview_frame(cart_frame)
        self.cart_cols = {"MaSP": "Mã SP", "TenSP": "Tên SP", "SoLuong": "Số Lượng", "DVTinh": "ĐVT", "DonGia": "Đơn Giá", "ThanhTien": "Thành Tiền"}

        self.cart_tree["columns"] = list(self.cart_cols.keys())
        for col_id, text in self.cart_cols.items():
            anchor = "e" if col_id in ("SoLuong", "DonGia", "ThanhTien") else "w"
            self.cart_tree.heading(col_id, text=text)
            self.cart_tree.column(col_id, anchor=anchor)

        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)

        self.total_label = tk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Segoe UI", 12, "bold"), fg="red")
        self.total_label.pack(side="left")

        create_button(bottom_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="right", padx=5)
        
        create_button(bottom_frame, "Lưu Hóa đơn", command=self._on_save, kind="primary").pack(side="right", padx=5)

    def _load_products_to_tree(self):
        try:
            for i in self.product_tree.get_children(): self.product_tree.delete(i)
            self.product_stock_map.clear()
            
            cur = self.conn.cursor()
            cur.execute("SELECT MaSP, SoLuong FROM dbo.SanPhamNongDuoc")
            rows = cur.fetchall()
            
            for row in rows:
                masp, so_luong_goc = row.MaSP, row.SoLuong
                self.product_stock_map[masp] = so_luong_goc
                cache = self.product_data_cache.get(masp)
                if not cache: continue
                
                self.product_tree.insert("", "end", iid=masp, values=(
                    masp,
                    cache["TenSP"],
                    so_luong_goc,
                    f"{cache['DonGia']:,.0f}",
                    cache["DVTinh"]
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải tồn kho sản phẩm:\n{e}", parent=self)

    def _update_product_tree_stock(self, masp, new_stock_value):
        try:
            cache = self.product_data_cache.get(masp)
            if not cache: return
            
            self.product_tree.item(masp, values=(
                masp,
                cache["TenSP"],
                new_stock_value, 
                f"{cache['DonGia']:,.0f}",
                cache["DVTinh"]
            ))
        except tk.TclError:
            pass 

    def _add_item_to_cart(self):
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm từ Kho (bảng trên).", parent=self)
            return
            
        try:
            sl_mua = int(self.so_luong_entry.get())
            if sl_mua <= 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Lỗi", "Số lượng mua phải là số nguyên dương.", parent=self)
            return

        masp = sel[0] 
        
        current_stock_display = int(self.product_tree.item(masp, "values")[2])
        if sl_mua > current_stock_display:
            messagebox.showwarning("Hết hàng", f"Số lượng tồn kho không đủ (Chỉ còn {current_stock_display}).", parent=self)
            return
            
        cache = self.product_data_cache.get(masp)
        if not cache: return

        don_gia_ban = cache["DonGia"]
        thanh_tien = don_gia_ban * sl_mua
        
        if masp in self.cart_items:
            new_sl_gio = self.cart_items[masp] + sl_mua
            new_thanh_tien = don_gia_ban * new_sl_gio
            self.cart_tree.item(masp, values=(
                masp, cache["TenSP"], new_sl_gio, cache["DVTinh"],
                f"{don_gia_ban:,.0f}", f"{new_thanh_tien:,.0f}"
            ))
            self.cart_items[masp] = new_sl_gio
        else:
            self.cart_tree.insert("", "end", iid=masp, values=(
                masp, cache["TenSP"], sl_mua, cache["DVTinh"],
                f"{don_gia_ban:,.0f}", f"{thanh_tien:,.0f}"
            ))
            self.cart_items[masp] = sl_mua
            
        new_stock_display = current_stock_display - sl_mua
        self._update_product_tree_stock(masp, new_stock_display)
        
        self._update_total()

    def _remove_item_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm từ Hóa đơn (bảng dưới).", parent=self)
            return
        
        masp = sel[0] 
        
        sl_tra_lai = self.cart_items.get(masp, 0)
        if sl_tra_lai == 0: return

        self.cart_tree.delete(masp)
        del self.cart_items[masp]
        
        current_stock_display = int(self.product_tree.item(masp, "values")[2])
        new_stock_display = current_stock_display + sl_tra_lai
        self._update_product_tree_stock(masp, new_stock_display)

        self._update_total()

    def _update_total(self):
        total = 0 
        for masp, sl_gio in self.cart_items.items():
            cache = self.product_data_cache.get(masp)
            if cache:
                total += cache["DonGia"] * sl_gio
        
        self.total_label.config(text=f"Tổng cộng: {total:,.0f} VNĐ")
        return total
    
    def _on_save(self):
        customer_str = self.customer_cb.get()
        if not customer_str:
            messagebox.showwarning("Thiếu", "Vui lòng chọn khách hàng.", parent=self)
            return
            
        if not self.cart_items:
            messagebox.showwarning("Thiếu", "Hóa đơn phải có ít nhất 1 mặt hàng.", parent=self)
            return

        try:
            ma_kh = customer_str.split('(')[-1].replace(')', '')
            ngay_gd = self.ngay_gd_entry.get_date()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Dữ liệu khách hàng hoặc ngày không hợp lệ: {e}", parent=self)
            return
            
        total_amount = self._update_total()

        try:
            ma_hd, error = them_hoa_don(
                ma_kh=ma_kh,
                ngay_gd=ngay_gd,
                cart_items=self.cart_items,
                total_amount=total_amount,
                product_cache=self.product_data_cache
            )

            if error:
                raise Exception(error)

            messagebox.showinfo("Thành công", f"Đã tạo thành công hóa đơn {ma_hd}.", parent=self)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu hóa đơn:\n{e}", parent=self)