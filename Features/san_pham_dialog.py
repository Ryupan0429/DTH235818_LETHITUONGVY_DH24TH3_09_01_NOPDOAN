import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import center, FONT_NORMAL, create_button

def _next_masp(conn):
    """Tạo mã sản phẩm mới (ví dụ: SP0001)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT MaSP FROM dbo.SanPhamNongDuoc WHERE MaSP LIKE 'SP%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("SP"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"SP{nxt:04d}" # Format SP0001
    except Exception as e:
        print(f"Lỗi tạo mã SP: {e}")
        return None

class SanPhamDialog(tk.Toplevel):
    def __init__(self, parent, masp=None):
        super().__init__(parent)
        self.parent = parent
        self.masp = masp
        self.conn = get_connection()
        
        self.title("Thêm Sản phẩm mới" if not masp else "Cập nhật Sản phẩm")
        self.geometry("500x400") 

        self._build_ui()
        self._load_categories()
        
        if self.masp:
            self._load_data()
            
        center(self, 500, 400)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        grid_pad = {'pady': 6, 'padx': 5, 'sticky': 'w'}

        tk.Label(frame, text="Mã SP:", font=FONT_NORMAL).grid(row=0, column=0, **grid_pad)
        self.ma_sp_entry = tk.Entry(frame, width=30, font=FONT_NORMAL, state="disabled")
        self.ma_sp_entry.grid(row=0, column=1, columnspan=2, **grid_pad)
        
        if not self.masp:
            self.ma_sp_entry.config(state="normal")
            self.ma_sp_entry.insert(0, "(Tự động tạo)")
            self.ma_sp_entry.config(state="disabled")

        tk.Label(frame, text="Tên SP (*):", font=FONT_NORMAL).grid(row=1, column=0, **grid_pad)
        self.ten_sp_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.ten_sp_entry.grid(row=1, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Phân Loại (*):", font=FONT_NORMAL).grid(row=2, column=0, **grid_pad)
        self.phan_loai_cb = ttk.Combobox(frame, width=38, font=FONT_NORMAL, state="readonly")
        self.phan_loai_cb.grid(row=2, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Công Dụng:", font=FONT_NORMAL).grid(row=3, column=0, **grid_pad)
        self.cong_dung_entry = tk.Entry(frame, width=40, font=FONT_NORMAL)
        self.cong_dung_entry.grid(row=3, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="ĐVT (*):", font=FONT_NORMAL).grid(row=4, column=0, **grid_pad)
        self.dv_tinh_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.dv_tinh_entry.grid(row=4, column=1, columnspan=2, **grid_pad)
        self.dv_tinh_entry.insert(0, "cái")

        tk.Label(frame, text="Số Lượng (Tồn):", font=FONT_NORMAL).grid(row=5, column=0, **grid_pad)
        self.so_luong_entry = tk.Entry(frame, width=30, font=FONT_NORMAL, state="disabled")
        self.so_luong_entry.grid(row=5, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Đơn Giá (Bán):", font=FONT_NORMAL).grid(row=6, column=0, **grid_pad)
        self.don_gia_entry = tk.Entry(frame, width=30, font=FONT_NORMAL, state="disabled") # Vẫn tắt khi Thêm
        self.don_gia_entry.grid(row=6, column=1, columnspan=2, **grid_pad)
        
        if not self.masp:
             self.so_luong_entry.config(state="normal")
             self.so_luong_entry.insert(0, "0 (Thêm từ Phiếu Nhập)")
             self.don_gia_entry.config(state="normal")
             self.don_gia_entry.insert(0, "0 (Cập nhật từ Phiếu Nhập)")
             self.so_luong_entry.config(state="disabled")
             self.don_gia_entry.config(state="disabled")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        create_button(btn_frame, "Lưu", command=self._on_save, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)
        
        self.ten_sp_entry.focus_set()

    def _load_categories(self):
        """Tải các phân loại sản phẩm hiện có."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.SanPhamNongDuoc WHERE PhanLoai IS NOT NULL ORDER BY PhanLoai")
            categories = [row[0] for row in cur.fetchall()]
            self.phan_loai_cb['values'] = categories
        except Exception as e:
            print(f"Lỗi tải phân loại: {e}")

    def _load_data(self):
        """Tải dữ liệu của sản phẩm cần sửa."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM dbo.SanPhamNongDuoc WHERE MaSP = ?", (self.masp,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm.", parent=self)
                self.destroy()
                return

            self.ma_sp_entry.config(state="normal")
            self.ma_sp_entry.insert(0, row.MaSP)
            self.ma_sp_entry.config(state="disabled")
            
            self.ten_sp_entry.insert(0, row.TenSP)
            self.phan_loai_cb.set(row.PhanLoai or "")
            self.cong_dung_entry.insert(0, row.CongDung or "")
            
            self.dv_tinh_entry.delete(0, "end")
            self.dv_tinh_entry.insert(0, row.DVTinh or "cái")
            
            self.so_luong_entry.config(state="normal")
            self.so_luong_entry.insert(0, f"{row.SoLuong:,.0f}")
            self.so_luong_entry.config(state="disabled")

            self.don_gia_entry.config(state="normal")
            self.don_gia_entry.insert(0, f"{row.DonGia:,.0f}") 

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể tải dữ liệu sản phẩm:\n{e}", parent=self)

    def _validate_input(self):
        """Kiểm tra các trường bắt buộc."""
        
        self.ten_sp = self.ten_sp_entry.get().strip()
        self.phan_loai = self.phan_loai_cb.get().strip()
        self.cong_dung = self.cong_dung_entry.get().strip()
        self.dv_tinh = self.dv_tinh_entry.get().strip()

        if not self.ten_sp:
            messagebox.showwarning("Thiếu thông tin", "Trường 'Tên SP' không được để trống.", parent=self)
            self.ten_sp_entry.focus_set()
            return False
        if not self.phan_loai:
            messagebox.showwarning("Thiếu thông tin", "Trường 'Phân Loại' không được để trống.", parent=self)
            self.phan_loai_cb.focus_set()
            return False
        if not self.dv_tinh:
            messagebox.showwarning("Thiếu thông tin", "Trường 'ĐVT' không được để trống.", parent=self)
            self.dv_tinh_entry.focus_set()
            return False
        
        if self.masp: 
            self.don_gia_str = self.don_gia_entry.get().strip().replace(",", "")
            try:
                self.don_gia = int(self.don_gia_str)
                if self.don_gia < 0: raise ValueError()
            except ValueError:
                messagebox.showwarning("Sai", "Đơn giá phải là một số nguyên không âm.", parent=self)
                self.don_gia_entry.focus_set()
                return False
        
        return True

    def _on_save(self):
        """Lưu (Thêm mới hoặc Cập nhật)."""
        if not self._validate_input():
            return
            
        try:
            cur = self.conn.cursor()
            
            # Kiểm tra tên SP trùng
            if self.masp: # Sửa
                cur.execute("SELECT MaSP FROM dbo.SanPhamNongDuoc WHERE TenSP = ? AND MaSP != ?", (self.ten_sp, self.masp))
            else: # Thêm
                cur.execute("SELECT MaSP FROM dbo.SanPhamNongDuoc WHERE TenSP = ?", (self.ten_sp,))
            
            if cur.fetchone():
                messagebox.showwarning("Trùng lặp", "Tên sản phẩm này đã tồn tại.", parent=self)
                return

            if self.masp: # Chế độ Cập nhật
                cur.execute("""
                    UPDATE dbo.SanPhamNongDuoc
                    SET TenSP = ?, PhanLoai = ?, CongDung = ?, DVTinh = ?, DonGia = ?
                    WHERE MaSP = ?
                """, (self.ten_sp, self.phan_loai, self.cong_dung, self.dv_tinh, self.don_gia, self.masp))
                
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin sản phẩm.", parent=self)
            
            else: # Chế độ Thêm mới (logic giữ nguyên)
                ma_sp_val = _next_masp(self.conn)
                if not ma_sp_val:
                    messagebox.showerror("Lỗi", "Không thể tạo Mã Sản Phẩm tự động.", parent=self)
                    return

                cur.execute("""
                    INSERT INTO dbo.SanPhamNongDuoc 
                    (MaSP, TenSP, PhanLoai, CongDung, DVTinh, SoLuong, DonGia)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                """, (ma_sp_val, self.ten_sp, self.phan_loai, self.cong_dung, self.dv_tinh))
                
                self.conn.commit()
                messagebox.showinfo("Thành công", f"Đã thêm thành công sản phẩm: {ma_sp_val}\n"
                                  "Vui lòng tạo Phiếu Nhập để cập nhật số lượng và giá bán.", parent=self)
            
            self.destroy()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu:\n{e}", parent=self)