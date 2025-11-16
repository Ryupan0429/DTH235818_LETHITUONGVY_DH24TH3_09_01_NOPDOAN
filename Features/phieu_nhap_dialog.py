import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from tkcalendar import DateEntry
from Modules.ui_style import center, FONT_NORMAL, create_button
from Modules.utils import create_treeview_frame
from Modules.nghiep_vu_xu_ly import them_phieu_nhap

class AddImportDialog(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.parent = parent
        self.username = username # Người nhập
        
        self.title("Tạo Phiếu Nhập mới")
        self.geometry("1000x700") 
        
        self.conn = get_connection()
        self.product_data_cache = self._load_product_data_cache()
        self.cart_items = {}
        
        self._build_ui()
        self._load_products_to_tree()
        
        center(self, 1000, 700)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _load_product_data_cache(self):
        """Tải dữ liệu (Tên, ĐVT, Tồn Kho) của TẤT CẢ sản phẩm."""
        data = {}
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaSP, TenSP, DVTinh, SoLuong FROM dbo.SanPhamNongDuoc")
            for row in cur.fetchall():
                data[row.MaSP] = {
                    "TenSP": row.TenSP,
                    "DVTinh": row.DVTinh or "cái",
                    "SoLuong": row.SoLuong
                }
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm:\n{e}", parent=self)
            return {}

    def _build_ui(self):
        
        self.grid_rowconfigure(0, weight=0) # info_frame
        self.grid_rowconfigure(1, weight=5) # product_frame (bảng trên)
        self.grid_rowconfigure(2, weight=0) # action_frame
        self.grid_rowconfigure(3, weight=4) # cart_frame (bảng dưới)
        self.grid_rowconfigure(4, weight=0) # bottom_frame (nút)
        self.grid_columnconfigure(0, weight=1)

        info_frame = tk.Frame(self)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10) 

        tk.Label(info_frame, text="Nguồn nhập:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nguon_nhap_entry = tk.Entry(info_frame, width=40, font=FONT_NORMAL)
        self.nguon_nhap_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(info_frame, text="Ngày Nhập:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.ngay_nhap_entry = DateEntry(info_frame, width=12, date_pattern='dd/MM/yyyy')
        self.ngay_nhap_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(info_frame, text="Người nhập:", font=FONT_NORMAL).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.nguoi_nhap_label = tk.Label(info_frame, text=self.username, font=FONT_NORMAL, relief="sunken", width=10)
        self.nguoi_nhap_label.grid(row=0, column=5, padx=5, pady=5)

        product_frame = ttk.LabelFrame(self, text="Danh sách Sản Phẩm (Chọn để nhập)")
        product_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5) 

        self.p_area, self.product_tree = create_treeview_frame(product_frame)
        self.product_cols = {"MaSP": "Mã SP", "TenSP": "Tên SP", "SoLuong": "Tồn Kho", "DVTinh": "ĐVT"}
        
        self.product_tree["columns"] = list(self.product_cols.keys())
        for col_id, text in self.product_cols.items():
            anchor = "e" if col_id == "SoLuong" else "w" 
            self.product_tree.heading(col_id, text=text)
            self.product_tree.column(col_id, anchor=anchor)

        action_frame = tk.Frame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5) 
        
        tk.Label(action_frame, text="Số lượng:", font=FONT_NORMAL).pack(side="left", padx=(10, 5))
        self.so_luong_entry = tk.Entry(action_frame, width=8, font=FONT_NORMAL)
        self.so_luong_entry.pack(side="left")
        self.so_luong_entry.insert(0, "10")

        tk.Label(action_frame, text="Đơn Giá (Nhập):", font=FONT_NORMAL).pack(side="left", padx=(10, 5))
        self.don_gia_nhap_entry = tk.Entry(action_frame, width=12, font=FONT_NORMAL)
        self.don_gia_nhap_entry.pack(side="left")
        self.don_gia_nhap_entry.insert(0, "100000")

        create_button(action_frame, "⬇ Thêm vào Phiếu Nhập ⬇", command=self._add_item_to_cart, kind="primary").pack(side="left", padx=10)
        create_button(action_frame, "⬆ Bỏ khỏi Phiếu Nhập ⬆", command=self._remove_item_from_cart, kind="danger").pack(side="left", padx=10)

        cart_frame = ttk.LabelFrame(self, text="Thông tin Phiếu Nhập (Sản phẩm đã chọn)")
        cart_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5) 
        
        self.c_area, self.cart_tree = create_treeview_frame(cart_frame)
        self.cart_cols = {"MaSP": "Mã SP", "TenSP": "Tên SP", "SoLuong": "Số Lượng", "DVTinh": "ĐVT", "DonGia": "Đơn Giá (Nhập)", "ThanhTien": "Thành Tiền"}

        self.cart_tree["columns"] = list(self.cart_cols.keys())
        for col_id, text in self.cart_cols.items():
            anchor = "e" if col_id in ("SoLuong", "DonGia", "ThanhTien") else "w"
            self.cart_tree.heading(col_id, text=text)
            self.cart_tree.column(col_id, anchor=anchor)

        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10) 

        self.total_label = tk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Segoe UI", 12, "bold"), fg="blue")
        self.total_label.pack(side="left")

        create_button(bottom_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="right", padx=5)

        create_button(bottom_frame, "Lưu Phiếu Nhập", command=self._on_save, kind="primary").pack(side="right", padx=5)


    def _load_products_to_tree(self):
        """Tải TẤT CẢ sản phẩm lên cây product_tree (trên)."""
        try:
            for i in self.product_tree.get_children(): self.product_tree.delete(i)
            
            self.product_data_cache = self._load_product_data_cache()
            
            for masp, cache in self.product_data_cache.items():
                self.product_tree.insert("", "end", iid=masp, values=(
                    masp,
                    cache["TenSP"],
                    f"{cache['SoLuong']:,.0f}", 
                    cache["DVTinh"]
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm:\n{e}", parent=self)

    def _add_item_to_cart(self):
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm (bảng trên).", parent=self)
            return
            
        try:
            sl_nhap = int(self.so_luong_entry.get().replace(",", ""))
            don_gia_nhap = float(self.don_gia_nhap_entry.get().replace(",", ""))
            if sl_nhap <= 0 or don_gia_nhap < 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Lỗi", "Số lượng (>0) và Đơn giá (>=0) phải là số hợp lệ.", parent=self)
            return

        masp = sel[0] 
        cache = self.product_data_cache.get(masp)
        if not cache: return

        thanh_tien = don_gia_nhap * sl_nhap
        
        if masp in self.cart_items:
             messagebox.showwarning("Đã có", "Sản phẩm đã có trong phiếu. Xóa đi nếu muốn nhập lại.", parent=self)
             return
            
        # Thêm mới
        self.cart_tree.insert("", "end", iid=masp, values=(
            masp, cache["TenSP"], sl_nhap, cache["DVTinh"],
            f"{don_gia_nhap:,.0f}", f"{thanh_tien:,.0f}"
        ))
        self.cart_items[masp] = (sl_nhap, don_gia_nhap)
            
        self._update_total()
        
        # Cập nhật Tồn Kho (tạm thời) ở bảng trên
        current_stock = cache["SoLuong"]
        new_stock = current_stock + sl_nhap
        self.product_tree.item(masp, values=(
            masp, cache["TenSP"], f"{new_stock:,.0f}", cache["DVTinh"]
        ))
        self.product_data_cache[masp]["SoLuong"] = new_stock # Cập nhật cache tạm thời


    def _remove_item_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một sản phẩm từ Phiếu Nhập (bảng dưới).", parent=self)
            return
        
        masp = sel[0] 
        if masp in self.cart_items:
            
            sl_da_nhap, _ = self.cart_items[masp]
            
            self.cart_tree.delete(masp)
            del self.cart_items[masp]
            self._update_total()
            
            # Hoàn trả Tồn Kho (tạm thời) ở bảng trên
            cache = self.product_data_cache.get(masp)
            current_stock = cache["SoLuong"]
            new_stock = current_stock - sl_da_nhap # Trừ đi số lượng vừa thêm
            self.product_tree.item(masp, values=(
                masp, cache["TenSP"], f"{new_stock:,.0f}", cache["DVTinh"]
            ))
            self.product_data_cache[masp]["SoLuong"] = new_stock # Cập nhật cache tạm thời


    def _update_total(self):
        total = 0 
        for masp, (so_luong, don_gia_nhap) in self.cart_items.items():
            total += so_luong * don_gia_nhap
        
        self.total_label.config(text=f"Tổng cộng: {total:,.0f} VNĐ")
        return total
    
    def _on_save(self):
        nguon_nhap = self.nguon_nhap_entry.get().strip()
        if not nguon_nhap:
            messagebox.showwarning("Thiếu", "Vui lòng nhập Nguồn nhập.", parent=self)
            return
            
        if not self.cart_items:
            messagebox.showwarning("Thiếu", "Phiếu nhập phải có ít nhất 1 mặt hàng.", parent=self)
            return

        try:
            ngay_nhap = self.ngay_nhap_entry.get_date()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Ngày nhập không hợp lệ: {e}", parent=self)
            return
            
        total_amount = self._update_total()

        try:
            so_pn, error = them_phieu_nhap(
                nguoi_nhap=self.username,
                nguon_nhap=nguon_nhap,
                ngay_nhap=ngay_nhap,
                cart_items=self.cart_items,
                total_amount=total_amount,
                product_cache=self.product_data_cache
            )
            
            if error:
                raise Exception(error)

            messagebox.showinfo("Thành công", f"Đã tạo thành công phiếu nhập {so_pn}.\nKho và Giá bán đã được cập nhật.", parent=self)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu phiếu nhập:\n{e}", parent=self)