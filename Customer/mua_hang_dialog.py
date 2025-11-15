import tkinter as tk
from tkinter import messagebox
from Modules.ui_style import FONT_NORMAL, FONT_TITLE, create_button, center

class AddToCartDialog(tk.Toplevel):
    def __init__(self, parent, san_pham_data, shop_tab):
        """
        Mở một cửa sổ dialog để nhập số lượng và thêm vào giỏ hàng.
        - parent: Cửa sổ cha (CustomerSanPhamTab)
        - san_pham_data: Dict thông tin sản phẩm được chọn (chứa SoLuongTon)
        - shop_tab: Tham chiếu đến tab Mua hàng (ShopTab)
        """
        super().__init__(parent)
        self.title("Thêm vào giỏ hàng")
        
        self.san_pham_data = san_pham_data
        self.shop_tab = shop_tab
        self.max_qty = san_pham_data.get("SoLuongTon", 0)
        
        self.geometry("400x220")
        center(self, 400, 220)
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self.wait_window()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        ten_sp_label = tk.Label(frame, text=self.san_pham_data.get("TenSP", "..."), font=FONT_TITLE)
        ten_sp_label.pack(pady=(0, 10))
        
        # Thêm thông tin tồn kho
        stock_label = tk.Label(frame, text=f"(Số lượng tồn: {self.max_qty:,.0f})", font=FONT_NORMAL, fg="blue")
        stock_label.pack(pady=(0, 10))

        info_frame = tk.Frame(frame)
        info_frame.pack(pady=10)

        tk.Label(info_frame, text="Số lượng:", font=FONT_NORMAL).grid(row=0, column=0, padx=5, sticky="e")
        
        self.so_luong_entry = tk.Entry(info_frame, width=10, font=FONT_NORMAL)
        self.so_luong_entry.grid(row=0, column=1, padx=5)
        self.so_luong_entry.insert(0, "1") # Mặc định là 1
        self.so_luong_entry.focus_set()
        
        tk.Label(info_frame, text=self.san_pham_data.get("DVTinh", "đơn vị"), font=FONT_NORMAL).grid(row=0, column=2, padx=5, sticky="w")
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)
        
        create_button(btn_frame, "Thêm vào giỏ", command=self._on_add, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)

        self.bind("<Return>", lambda e: self._on_add())

    def _on_add(self):
        """Xử lý thêm vào giỏ hàng."""
        try:
            so_luong = int(self.so_luong_entry.get())
            if so_luong <= 0:
                raise ValueError("Số lượng phải lớn hơn 0")
            
            # Kiểm tra số lượng tồn kho
            if so_luong > self.max_qty:
                 messagebox.showwarning("Không đủ hàng", f"Số lượng tồn kho không đủ (chỉ còn {self.max_qty}).", parent=self)
                 return
            
            # Kiểm tra số lượng tồn kho TẠM THỜI trong giỏ hàng (nếu đã thêm trước đó)
            current_cart_qty = self.shop_tab.get_item_qty_in_cart(self.san_pham_data["MaSP"])
            if (so_luong + current_cart_qty) > self.max_qty:
                messagebox.showwarning("Không đủ hàng", 
                    f"Bạn đã có {current_cart_qty} trong giỏ.\n"
                    f"Không thể thêm {so_luong} nữa (tổng tồn kho là {self.max_qty}).", parent=self)
                return

            # Gọi hàm public của ShopTab để thêm hàng
            self.shop_tab.add_item_externally(self.san_pham_data, so_luong)
            
            self.destroy() # Đóng cửa sổ sau khi thêm
            
        except ValueError as e:
            messagebox.showwarning("Lỗi", f"Số lượng không hợp lệ.\n{e}", parent=self)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm vào giỏ: {e}", parent=self)