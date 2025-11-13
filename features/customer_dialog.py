import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import center, FONT_NORMAL, BTN_PRIMARY_BG

# Danh sách tỉnh thành
TINH_THANH_VN = [
    'An Giang', 'Bà Rịa - Vũng Tàu', 'Bạc Liêu', 'Bắc Giang', 'Bắc Ninh', 'Bình Dương', 'Bình Định', 'Bình Phước',
    'Bình Thuận', 'Cà Mau', 'Cần Thơ', 'Đà Nẵng', 'Đồng Nai', 'Đồng Tháp', 'Hà Nội', 'Hải Phòng', 'Hậu Giang',
    'Khánh Hòa', 'Kiên Giang', 'Long An', 'Nghệ An', 'Quảng Nam', 'Quảng Ngãi', 'Sóc Trăng', 'Tây Ninh', 'Tiền Giang',
    'TP. Hồ Chí Minh', 'Trà Vinh', 'Vĩnh Long', 'Hà Giang', 'Cao Bằng', 'Lai Châu', 'Lào Cai', 'Tuyên Quang', 'Lạng Sơn',
    'Bắc Kạn', 'Thái Nguyên', 'Yên Bái', 'Sơn La', 'Phú Thọ', 'Vĩnh Phúc', 'Quảng Ninh', 'Hải Dương', 'Hưng Yên',
    'Hà Nam', 'Nam Định', 'Ninh Bình', 'Thái Bình', 'Thanh Hóa', 'Hà Tĩnh', 'Quảng Bình', 'Quảng Trị', 'Thừa Thiên Huế',
    'Kon Tum', 'Gia Lai', 'Đắk Lắk', 'Đắk Nông', 'Lâm Đồng', 'Ninh Thuận', 'Phú Yên'
]
TINH_THANH_VN.sort()

def _next_makh(conn, cust_tbl):
    """Tạo mã khách hàng mới (ví dụ: KH0001)."""
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT MaKH FROM {cust_tbl} WHERE MaKH LIKE 'KH%'")
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
        self.height = 250
        
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        
        if self.makh:
            self._load_data()
        
        center(self, self.width, self.height)
        self.wait_window(self)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Họ Tên:", font=FONT_NORMAL).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.hoten = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.hoten.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frame, text="SĐT:", font=FONT_NORMAL).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.sdt = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.sdt.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frame, text="Địa chỉ:", font=FONT_NORMAL).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.diachi = ttk.Combobox(frame, width=28, values=TINH_THANH_VN, font=FONT_NORMAL)
        self.diachi.grid(row=2, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        btn_text = "Lưu" if self.makh else "Thêm"
        tk.Button(btn_frame, text=btn_text, command=self._on_save, bg=BTN_PRIMARY_BG, font=FONT_NORMAL).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.destroy, font=FONT_NORMAL).pack(side="left", padx=10)

        self.hoten.focus_set()
        
    def _load_data(self):
        """Tải dữ liệu hiện tại của khách hàng (chỉ dùng cho chế độ Sửa)."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT HoTenKH, SDT, DiaChi FROM dbo.ThongTinKhachHang WHERE MaKH = ?", (self.makh,))
            row = cur.fetchone()
            if row:
                self.hoten.insert(0, row.HoTenKH or "")
                self.sdt.insert(0, row.SDT or "")
                self.diachi.set(row.DiaChi or "")
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
        diachi = self.diachi.get().strip()

        if not hoten:
            messagebox.showwarning("Thiếu", "Họ tên không được để trống.", parent=self)
            return
        if not (sdt.isdigit() and len(sdt) == 10):
            messagebox.showwarning("Sai", "SĐT phải là 10 chữ số.", parent=self)
            return
        
        cur = self.conn.cursor()
        
        try:
            cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME='MaKH'")
            r = cur.fetchone()
            if not r:
                messagebox.showerror("Lỗi", "Không tìm thấy bảng khách hàng.", parent=self)
                return
            cust_tbl = f"[{r[0]}].[{r[1]}]"

            if self.makh: 
                cur.execute(f"SELECT MaKH FROM {cust_tbl} WHERE SDT = ? AND MaKH != ?", (sdt, self.makh))
            else:
                cur.execute(f"SELECT MaKH FROM {cust_tbl} WHERE SDT = ?", (sdt,))
            
            if cur.fetchone():
                messagebox.showwarning("Trùng lặp", "Số điện thoại này đã được đăng ký.", parent=self)
                return

            if self.makh:
                cur.execute(
                    f"UPDATE {cust_tbl} SET HoTenKH = ?, SDT = ?, DiaChi = ? WHERE MaKH = ?",
                    (hoten, sdt, diachi, self.makh)
                )
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng.", parent=self)
            else:
                makh = _next_makh(self.conn, cust_tbl)
                if not makh:
                    messagebox.showerror("Lỗi", "Không thể tạo MaKH", parent=self)
                    return
                
                cur.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=? AND TABLE_NAME=?", (r[0], r[1]))
                cols = [c[0] for c in cur.fetchall()]
                
                insert_cols = []; params = []
                if "MaKH" in cols: insert_cols.append("MaKH"); params.append(makh)
                if "HoTenKH" in cols: insert_cols.append("HoTenKH"); params.append(hoten)
                if "SDT" in cols: insert_cols.append("SDT"); params.append(sdt)
                if "DiaChi" in cols and diachi: 
                    insert_cols.append("DiaChi")
                    params.append(diachi)
                
                placeholders = ",".join("?" for _ in insert_cols)
                sql = f"INSERT INTO {cust_tbl} ({', '.join(insert_cols)}) VALUES ({placeholders})"
                cur.execute(sql, params)
                
                try:
                    cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='Users'")
                    ur = cur.fetchone()
                    if ur:
                        users_tbl = f"[{ur[0]}].[{ur[1]}]"
                        password = makh[-3:] 
                        cur.execute(f"INSERT INTO {users_tbl} (Username, Password, Role) VALUES (?, ?, ?)", (makh, password, "Customer"))
                except Exception:
                    pass 
                
                messagebox.showinfo("Thành công", f"Đã thêm khách hàng {makh}", parent=self)

            self.conn.commit()
            self.destroy()

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", str(e), parent=self)
        finally:
            if self.conn:
                self.conn.close()