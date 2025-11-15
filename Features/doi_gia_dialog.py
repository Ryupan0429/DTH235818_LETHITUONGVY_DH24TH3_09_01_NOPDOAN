import tkinter as tk
from tkinter import ttk, messagebox
from Modules.ui_style import center, FONT_NORMAL, create_button

class PriceChangeDialog(tk.Toplevel):
    def __init__(self, parent, product_count):
        """
        Khởi tạo dialog để nhập % thay đổi giá.
        product_count: Số lượng sản phẩm đang được chọn.
        """
        super().__init__(parent)
        self.title("Thay đổi giá hàng loạt")
        self.geometry("350x220")
        center(self, 350, 250)
        
        # self.result sẽ lưu hệ số nhân (ví dụ: 1.1 cho +10%)
        self.result = None 

        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=f"Áp dụng cho {product_count} sản phẩm đã chọn.", font=FONT_NORMAL).pack(pady=(0, 5))
        tk.Label(frame, text="Nhập phần trăm thay đổi:", font=FONT_NORMAL).pack(pady=(0, 5))

        entry_frame = tk.Frame(frame)
        entry_frame.pack(pady=5)
        
        self.percent_entry = tk.Entry(entry_frame, width=10, font=FONT_NORMAL)
        self.percent_entry.pack(side="left")
        tk.Label(entry_frame, text="%", font=FONT_NORMAL).pack(side="left", padx=5)
        
        tk.Label(frame, text="(Ví dụ: 10 cho tăng 10%, -5 cho giảm 5%)", font=("Segoe UI", 9, "italic")).pack()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)

        create_button(btn_frame, "OK", command=self._on_ok, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)

        self.percent_entry.focus_set()
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _on_ok(self):
        """Kiểm tra và trả về hệ số nhân."""
        percent_str = self.percent_entry.get().strip()
        try:
            percent_val = float(percent_str)
            
            # Chuyển đổi sang hệ số nhân
            # Ví dụ: 10% -> 1.10
            self.result = 1.0 + (percent_val / 100.0)
            
            if self.result < 0:
                messagebox.showwarning("Lỗi", "Không thể giảm giá về số âm.", parent=self)
                self.result = None
                return
                
            self.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một con số (ví dụ: 10 hoặc -5).", parent=self)