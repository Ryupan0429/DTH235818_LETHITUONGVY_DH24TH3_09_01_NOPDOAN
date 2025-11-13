import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

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

class AddCustomerDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title("Thêm Khách hàng")
        self.top.transient(parent)
        self.top.grab_set()
        
        tk.Label(self.top, text="Họ tên (*):").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        self.hoten = tk.Entry(self.top, width=30)
        self.hoten.grid(row=0,column=1,padx=8,pady=6)
        
        tk.Label(self.top, text="SĐT (*):").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        self.sdt = tk.Entry(self.top, width=30)
        self.sdt.grid(row=1,column=1,padx=8,pady=6)
        
        tk.Label(self.top, text="Địa chỉ:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
        self.diachi = ttk.Combobox(self.top, width=28, values=TINH_THANH_VN)
        self.diachi.grid(row=2,column=1,padx=8,pady=6)
        
        btnf = tk.Frame(self.top)
        btnf.grid(row=3,column=0,columnspan=2,pady=10)
        tk.Button(btnf, text="Thêm", command=self._on_add).pack(side="left", padx=6)
        tk.Button(btnf, text="Hủy", command=self.top.destroy).pack(side="left")
        
        self.hoten.focus_set()

    def _validate_input(self, hoten, sdt):
        """Kiểm tra ràng buộc dữ liệu đầu vào."""
        if not hoten:
            messagebox.showwarning("Thiếu thông tin", "Họ tên không được để trống.", parent=self.top)
            self.hoten.focus_set()
            return False
            
        if not sdt:
            messagebox.showwarning("Thiếu thông tin", "Số điện thoại không được để trống.", parent=self.top)
            self.sdt.focus_set()
            return False
            
        if not sdt.isdigit() or len(sdt) != 10:
            messagebox.showwarning("Dữ liệu sai", "Số điện thoại phải là 10 chữ số.", parent=self.top)
            self.sdt.focus_set()
            return False
            
        return True

    def _on_add(self):
        """Xử lý logic khi bấm nút Thêm."""
        hoten = self.hoten.get().strip()
        sdt = self.sdt.get().strip()
        diachi = self.diachi.get().strip()
        
        if not self._validate_input(hoten, sdt):
            return 

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME='MaKH'")
            r = cur.fetchone()
            if not r:
                messagebox.showerror("Lỗi", "Không tìm thấy bảng khách hàng để chèn", parent=self.top)
                conn.close()
                return
            
            cust_tbl = f"[{r[0]}].[{r[1]}]"
            
            cur.execute(f"SELECT 1 FROM {cust_tbl} WHERE SDT = ?", (sdt,))
            if cur.fetchone():
                messagebox.showwarning("Trùng lặp", "Số điện thoại này đã được đăng ký.", parent=self.top)
                self.sdt.focus_set()
                return

            makh = _next_makh(conn, cust_tbl)
            if not makh:
                messagebox.showerror("Lỗi", "Không thể tạo MaKH", parent=self.top)
                conn.close()
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
            
            # Tự động tạo tài khoản User
            try:
                cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='Users'")
                ur = cur.fetchone()
                if ur:
                    users_tbl = f"[{ur[0]}].[{ur[1]}]"
                    
                    # --- (THAY ĐỔI MẬT KHẨU) ---
                    # Lấy 3 ký tự cuối của MaKH làm mật khẩu
                    password = makh[-3:] 
                    cur.execute(f"INSERT INTO {users_tbl} (Username, Password, Role) VALUES (?, ?, ?)", (makh, password, "Customer"))
                    # --- (HẾT THAY ĐỔI) ---

            except Exception:
                pass 
                
            conn.commit()
            messagebox.showinfo("Thêm", f"Đã thêm khách hàng {makh}", parent=self.top)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self.top)
        finally:
            conn.close()