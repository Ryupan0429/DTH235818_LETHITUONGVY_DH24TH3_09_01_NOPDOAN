import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import center, FONT_NORMAL, create_button
from Modules.nghiep_vu_xu_ly import luu_khach_hang

TINH_THANH_VN = [
    'An Giang', 'Bà Rịa - Vũng Tàu', 'Bạc Liêu', 'Bắc Giang', 'Bắc Ninh', 'Bình Dương', 
    'Bình Định', 'Bình Phước', 'Bình Thuận', 'Cà Mau', 'Cần Thơ', 'Đà Nẵng', 
    'Đồng Nai', 'Đồng Tháp', 'Hà Nội', 'Hải Phòng', 'Hậu Giang', 'Khánh Hòa', 
    'Kiên Giang', 'Long An', 'Nghệ An', 'Quảng Nam', 'Quảng Ngãi', 'Sóc Trăng', 
    'Tây Ninh', 'Tiền Giang', 'TP. Hồ Chí Minh', 'Trà Vinh', 'Vĩnh Long', 'Hà Giang', 
    'Cao Bằng', 'Lai Châu', 'Lào Cai', 'Tuyên Quang', 'Lạng Sơn', 'Bắc Kạn', 
    'Thái Nguyên', 'Yên Bái', 'Sơn La', 'Phú Thọ', 'Vĩnh Phúc', 'Quảng Ninh', 
    'Hải Dương', 'Hưng Yên', 'Hà Nam', 'Nam Định', 'Ninh Bình', 'Thái Bình', 
    'Thanh Hóa', 'Hà Tĩnh', 'Quảng Bình', 'Quảng Trị', 'Thừa Thiên Huế',
    'Kon Tum', 'Gia Lai', 'Đắk Lắk', 'Đắk Nông', 'Lâm Đồng', 'Ninh Thuận', 'Phú Yên'
]
TINH_THANH_VN.sort()

class CustomerFormDialog(tk.Toplevel):
    def __init__(self, parent, makh=None):
        super().__init__(parent)
        self.parent = parent
        self.makh = makh
        self.conn = get_connection()

        self.title("Thêm Khách hàng" if not self.makh else "Cập nhật Khách hàng")
        self.width = 400
        self.height = 300 
        
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        
        if self.makh:
            self._load_data()
        
        center(self, self.width, self.height)
        self.wait_window()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Họ Tên (*):", font=FONT_NORMAL).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.hoten = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.hoten.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frame, text="SĐT (*):", font=FONT_NORMAL).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.sdt = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.sdt.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frame, text="Giới tính (*):", font=FONT_NORMAL).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.gioitinh = ttk.Combobox(frame, width=28, values=['Nam', 'Nữ', 'Khác'], font=FONT_NORMAL, state="readonly")
        self.gioitinh.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(frame, text="Quê quán (*):", font=FONT_NORMAL).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.quequan = ttk.Combobox(frame, width=28, values=TINH_THANH_VN, font=FONT_NORMAL, state="readonly")
        self.quequan.grid(row=3, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        btn_text = "Lưu" if self.makh else "Thêm"
        create_button(btn_frame, btn_text, command=self._on_save, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)

        self.hoten.focus_set()
        
    def _load_data(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT TenKH, SDT, GioiTinh, QueQuan FROM dbo.KhachHang WHERE MaKH = ?", (self.makh,))
            row = cur.fetchone()
            if row:
                self.hoten.insert(0, row.TenKH or "")
                self.sdt.insert(0, row.SDT or "")
                self.gioitinh.set(row.GioiTinh or "")
                self.quequan.set(row.QueQuan or "")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy khách hàng.", parent=self)
                self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể tải dữ liệu:\n{e}", parent=self)
            self.destroy()

    def _validate_input(self):
        data = {}
        data["TenKH"] = self.hoten.get().strip()
        data["SDT"] = self.sdt.get().strip()
        data["GioiTinh"] = self.gioitinh.get().strip()
        data["QueQuan"] = self.quequan.get().strip()

        if not data["TenKH"]:
            messagebox.showwarning("Thiếu", "Họ tên không được để trống.", parent=self)
            self.hoten.focus_set()
            return None
        if not data["SDT"]:
            messagebox.showwarning("Thiếu", "SĐT không được để trống.", parent=self)
            self.sdt.focus_set()
            return None
        if not (data["SDT"].isdigit() and len(data["SDT"]) == 10):
            messagebox.showwarning("Sai", "SĐT phải là 10 chữ số.", parent=self)
            self.sdt.focus_set()
            return None
        if not data["GioiTinh"]:
            messagebox.showwarning("Thiếu", "Giới tính không được để trống.", parent=self)
            self.gioitinh.focus_set()
            return None
        if not data["QueQuan"]:
            messagebox.showwarning("Thiếu", "Quê quán không được để trống.", parent=self)
            self.quequan.focus_set()
            return None
            
        return data

    def _on_save(self):
        data = self._validate_input()
        if data is None:
            return
        
        try:
            result_id, error = luu_khach_hang(self.makh, data)

            if error:
                raise Exception(error)
            
            if self.makh:
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng.", parent=self)
            else:
                messagebox.showinfo("Thành công", f"Đã thêm khách hàng {result_id}", parent=self)

            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", str(e), parent=self)