import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import center, FONT_NORMAL, BTN_PRIMARY_BG

def _next_mathuoc(conn):
    """Tạo mã thuốc mới (ví dụ: MT0001)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT MaThuoc FROM dbo.ThuocNongDuoc WHERE MaThuoc LIKE 'MT%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("MT"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"MT{nxt:04d}" # Format MT0001
    except Exception as e:
        print(f"Lỗi tạo mã thuốc: {e}")
        return None

class ThuocDialog(tk.Toplevel):
    def __init__(self, parent, mathuoc=None):
        super().__init__(parent)
        self.parent = parent
        self.mathuoc = mathuoc
        self.conn = get_connection()
        
        self.title("Thêm Thuốc mới" if not mathuoc else "Cập nhật Thuốc")
        self.geometry("500x500")

        self._build_ui()
        self._load_categories()
        
        if self.mathuoc:
            self._load_data()
            
        center(self, 500, 500)
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        grid_pad = {'pady': 6, 'padx': 5, 'sticky': 'w'}

        tk.Label(frame, text="Mã Thuốc:", font=FONT_NORMAL).grid(row=0, column=0, **grid_pad)
        self.ma_thuoc_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.ma_thuoc_entry.grid(row=0, column=1, columnspan=2, **grid_pad)
        
        if self.mathuoc: # Nếu là Sửa, không cho sửa Mã
            self.ma_thuoc_entry.config(state="readonly")
        else: # Nếu là Thêm, vô hiệu hóa và thông báo
            self.ma_thuoc_entry.insert(0, "(Tự động tạo)")
            self.ma_thuoc_entry.config(state="disabled")

        tk.Label(frame, text="Tên Thuốc:", font=FONT_NORMAL).grid(row=1, column=0, **grid_pad)
        self.ten_thuoc_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.ten_thuoc_entry.grid(row=1, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Phân Loại:", font=FONT_NORMAL).grid(row=2, column=0, **grid_pad)
        self.phan_loai_cb = ttk.Combobox(frame, width=38, font=FONT_NORMAL)
        self.phan_loai_cb.grid(row=2, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Nhóm Dược Lý:", font=FONT_NORMAL).grid(row=3, column=0, **grid_pad)
        self.nhom_dl_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.nhom_dl_entry.grid(row=3, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Công Dụng:", font=FONT_NORMAL).grid(row=4, column=0, **grid_pad)
        self.cong_dung_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.cong_dung_entry.grid(row=4, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Chỉ Định:", font=FONT_NORMAL).grid(row=5, column=0, **grid_pad)
        self.chi_dinh_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.chi_dinh_entry.grid(row=5, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Thành Phần:", font=FONT_NORMAL).grid(row=6, column=0, **grid_pad)
        self.thanh_phan_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.thanh_phan_entry.grid(row=6, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Liều Lượng:", font=FONT_NORMAL).grid(row=7, column=0, **grid_pad)
        self.lieu_luong_entry = tk.Entry(frame, width=15, font=FONT_NORMAL)
        self.lieu_luong_entry.grid(row=7, column=1, sticky='w', padx=5, pady=6)
        self.lieu_luong_unit_cb = ttk.Combobox(frame, width=10, 
                                               values=["L/ha", "g/ha", "kg/ha", "ml/ha", "/1L nước", "chai"], 
                                               font=FONT_NORMAL)
        self.lieu_luong_unit_cb.grid(row=7, column=2, sticky='w', padx=0, pady=6)
        self.lieu_luong_unit_cb.set("L/ha")

        tk.Label(frame, text="Đơn Giá:", font=FONT_NORMAL).grid(row=8, column=0, **grid_pad)
        self.don_gia_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.don_gia_entry.grid(row=8, column=1, columnspan=2, **grid_pad)
        
        tk.Label(frame, text="ĐVT:", font=FONT_NORMAL).grid(row=9, column=0, **grid_pad)
        self.dv_tinh_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.dv_tinh_entry.grid(row=9, column=1, columnspan=2, **grid_pad)
        self.dv_tinh_entry.insert(0, "chai") # Mặc định

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        tk.Button(btn_frame, text="Lưu", command=self._on_save, bg=BTN_PRIMARY_BG, font=FONT_NORMAL).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.destroy, font=FONT_NORMAL).pack(side="left", padx=10)
        
        self.ten_thuoc_entry.focus_set() # Focus vào Tên thuốc thay vì Mã

    def _load_categories(self):
        """Tải các phân loại thuốc hiện có."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.ThuocNongDuoc WHERE PhanLoai IS NOT NULL ORDER BY PhanLoai")
            categories = [row[0] for row in cur.fetchall()]
            self.phan_loai_cb['values'] = categories
        except Exception as e:
            print(f"Lỗi tải phân loại: {e}")

    def _load_data(self):
        """Tải dữ liệu của thuốc cần sửa."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM dbo.ThuocNongDuoc WHERE MaThuoc = ?", (self.mathuoc,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Không tìm thấy thuốc.", parent=self)
                self.destroy()
                return

            self.ma_thuoc_entry.insert(0, row.MaThuoc)
            self.ten_thuoc_entry.insert(0, row.TenThuoc)
            self.phan_loai_cb.set(row.PhanLoai or "")
            self.nhom_dl_entry.insert(0, row.NhomDuocLy or "")
            self.cong_dung_entry.insert(0, row.CongDung or "")
            self.chi_dinh_entry.insert(0, row.ChiDinh or "")
            self.thanh_phan_entry.insert(0, row.ThanhPhan or "")
            self.don_gia_entry.insert(0, f"{row.DonGia:,.0f}")
            self.dv_tinh_entry.delete(0, "end")
            self.dv_tinh_entry.insert(0, row.DVTinh or "chai")
            
            if row.LieuLuong:
                parts = str(row.LieuLuong).split(' ')
                if len(parts) > 1:
                    unit = parts[-1]
                    value = " ".join(parts[:-1])
                    self.lieu_luong_entry.insert(0, value)
                    if unit in self.lieu_luong_unit_cb['values']:
                        self.lieu_luong_unit_cb.set(unit)
                    else:
                         self.lieu_luong_unit_cb.set(unit) 
                else:
                    self.lieu_luong_entry.insert(0, row.LieuLuong)

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể tải dữ liệu thuốc:\n{e}", parent=self)

    def _validate_input(self):
        """Kiểm tra ràng buộc tất cả các trường không được trống."""
        
        # Lấy tất cả giá trị
        self.ten_thuoc = self.ten_thuoc_entry.get().strip()
        self.phan_loai = self.phan_loai_cb.get().strip()
        self.nhom_dl = self.nhom_dl_entry.get().strip()
        self.cong_dung = self.cong_dung_entry.get().strip()
        self.chi_dinh = self.chi_dinh_entry.get().strip()
        self.thanh_phan = self.thanh_phan_entry.get().strip()
        self.lieu_luong_val = self.lieu_luong_entry.get().strip()
        self.lieu_luong_unit = self.lieu_luong_unit_cb.get().strip()
        self.don_gia_str = self.don_gia_entry.get().strip().replace(",", "")
        self.dv_tinh = self.dv_tinh_entry.get().strip()

        # Danh sách các trường cần kiểm tra
        fields_to_check = [
            (self.ten_thuoc_entry, self.ten_thuoc, "Tên Thuốc"),
            (self.phan_loai_cb, self.phan_loai, "Phân Loại"),
            (self.nhom_dl_entry, self.nhom_dl, "Nhóm Dược Lý"),
            (self.cong_dung_entry, self.cong_dung, "Công Dụng"),
            (self.chi_dinh_entry, self.chi_dinh, "Chỉ Định"),
            (self.thanh_phan_entry, self.thanh_phan, "Thành Phần"),
            (self.lieu_luong_entry, self.lieu_luong_val, "Liều Lượng"),
            (self.lieu_luong_unit_cb, self.lieu_luong_unit, "Đơn vị Liều Lượng"),
            (self.don_gia_entry, self.don_gia_str, "Đơn Giá"),
            (self.dv_tinh_entry, self.dv_tinh, "ĐVT")
        ]

        # Vòng lặp kiểm tra
        for widget, value, name in fields_to_check:
            if not value:
                messagebox.showwarning("Thiếu thông tin", f"Trường '{name}' không được để trống.", parent=self)
                widget.focus_set()
                return False
        
        # Kiểm tra Đơn Giá
        try:
            self.don_gia = int(self.don_gia_str)
            if self.don_gia <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai", "Đơn giá phải là một số nguyên dương.", parent=self)
            self.don_gia_entry.focus_set()
            return False
            
        # Ghép Liều Lượng
        self.lieu_luong = f"{self.lieu_luong_val} {self.lieu_luong_unit}"
        
        return True

    def _on_save(self):
        """Lưu (Thêm mới hoặc Cập nhật)."""
        if not self._validate_input():
            return
            
        try:
            cur = self.conn.cursor()
            if self.mathuoc: # Chế độ Cập nhật
                cur.execute("""
                    UPDATE dbo.ThuocNongDuoc
                    SET TenThuoc = ?, PhanLoai = ?, NhomDuocLy = ?, CongDung = ?, ChiDinh = ?,
                        ThanhPhan = ?, LieuLuong = ?, DonGia = ?, DVTinh = ?
                    WHERE MaThuoc = ?
                """, (self.ten_thuoc, self.phan_loai, self.nhom_dl, self.cong_dung, self.chi_dinh,
                      self.thanh_phan, self.lieu_luong, self.don_gia, self.dv_tinh, self.mathuoc))
                
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin thuốc.", parent=self)
            
            else: # Chế độ Thêm mới
                # 1. Tự động tạo mã
                ma_thuoc_val = _next_mathuoc(self.conn)
                if not ma_thuoc_val:
                    messagebox.showerror("Lỗi", "Không thể tạo Mã Thuốc tự động.", parent=self)
                    return

                # 2. Chèn dữ liệu
                cur.execute("""
                    INSERT INTO dbo.ThuocNongDuoc 
                    (MaThuoc, TenThuoc, PhanLoai, NhomDuocLy, CongDung, ChiDinh, ThanhPhan, LieuLuong, DonGia, DVTinh)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ma_thuoc_val, self.ten_thuoc, self.phan_loai, self.nhom_dl, self.cong_dung, self.chi_dinh,
                      self.thanh_phan, self.lieu_luong, self.don_gia, self.dv_tinh))
                
                self.conn.commit()
                # 3. Thông báo mã thuốc mới
                messagebox.showinfo("Thành công", f"Đã thêm thành công thuốc có mã: {ma_thuoc_val}", parent=self)
            
            self.destroy()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu:\n{e}", parent=self)