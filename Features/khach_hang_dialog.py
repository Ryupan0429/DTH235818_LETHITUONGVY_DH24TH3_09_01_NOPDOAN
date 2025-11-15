import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import center, FONT_NORMAL, create_button

# Danh sách tỉnh thành (dùng chung)
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

def _next_makh(conn):
    """Tạo mã khách hàng mới (ví dụ: KH0001)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT MaKH FROM dbo.KhachHang WHERE MaKH LIKE 'KH%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("KH"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"KH{nxt:04d}"
    except Exception:
        return None

class CustomerFormDialog(tk.Toplevel):
    def __init__(self, parent, makh=None):
        """
        Khởi tạo dialog.
        - Nếu 'makh' là None: Chế độ Thêm mới.
        - Nếu 'makh' có giá trị: Chế độ Sửa.
        """
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

        tk.Label(frame, text="Giới tính:", font=FONT_NORMAL).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.gioitinh = ttk.Combobox(frame, width=28, values=['Nam', 'Nữ', 'Khác'], font=FONT_NORMAL, state="readonly")
        self.gioitinh.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(frame, text="Quê quán:", font=FONT_NORMAL).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.quequan = ttk.Combobox(frame, width=28, values=TINH_THANH_VN, font=FONT_NORMAL, state="readonly")
        self.quequan.grid(row=3, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        btn_text = "Lưu" if self.makh else "Thêm"
        create_button(btn_frame, btn_text, command=self._on_save, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)

        self.hoten.focus_set()
        
    def _load_data(self):
        """Tải dữ liệu hiện tại của khách hàng (chỉ dùng cho chế độ Sửa)."""
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

    def _on_save(self):
        """Kiểm tra và lưu (Thêm hoặc Sửa)."""
        hoten = self.hoten.get().strip()
        sdt = self.sdt.get().strip()
        gioitinh = self.gioitinh.get().strip()
        quequan = self.quequan.get().strip()

        if not hoten:
            messagebox.showwarning("Thiếu", "Họ tên không được để trống.", parent=self)
            self.hoten.focus_set()
            return
        if not sdt:
            messagebox.showwarning("Thiếu", "SĐT không được để trống.", parent=self)
            self.sdt.focus_set()
            return
        if not (sdt.isdigit() and len(sdt) == 10):
            messagebox.showwarning("Sai", "SĐT phải là 10 chữ số.", parent=self)
            self.sdt.focus_set()
            return
        if not gioitinh:
            messagebox.showwarning("Thiếu", "Giới tính không được để trống.", parent=self)
            self.gioitinh.focus_set()
            return
        if not quequan:
            messagebox.showwarning("Thiếu", "Quê quán không được để trống.", parent=self)
            self.quequan.focus_set()
            return
        
        cur = self.conn.cursor()
        
        try:
            # Kiểm tra SĐT trùng
            if self.makh: # Chế độ Sửa
                cur.execute("SELECT MaKH FROM dbo.KhachHang WHERE SDT = ? AND MaKH != ?", (sdt, self.makh))
            else: # Chế độ Thêm
                cur.execute("SELECT MaKH FROM dbo.KhachHang WHERE SDT = ?", (sdt,))
            
            if cur.fetchone():
                messagebox.showwarning("Trùng lặp", "Số điện thoại này đã được đăng ký.", parent=self)
                return

            if self.makh:
                # --- Chế độ SỬA ---
                cur.execute(
                    "UPDATE dbo.KhachHang SET TenKH = ?, SDT = ?, GioiTinh = ?, QueQuan = ? WHERE MaKH = ?",
                    (hoten, sdt, gioitinh, quequan, self.makh)
                )
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng.", parent=self)
            else:
                # --- Chế độ THÊM ---
                makh = _next_makh(self.conn)
                if not makh:
                    messagebox.showerror("Lỗi", "Không thể tạo Mã Khách hàng", parent=self)
                    return
                
                cur.execute(
                    "INSERT INTO dbo.KhachHang (MaKH, TenKH, SDT, GioiTinh, QueQuan) VALUES (?, ?, ?, ?, ?)",
                    (makh, hoten, sdt, gioitinh, quequan)
                )
                
                messagebox.showinfo("Thành công", f"Đã thêm khách hàng {makh}", parent=self)

            self.conn.commit()
            self.destroy()

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", str(e), parent=self)
        finally:
            pass