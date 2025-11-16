import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from Modules.ui_style import center, FONT_NORMAL, create_button
from Modules.nghiep_vu_xu_ly import luu_san_pham

class SanPhamDialog(tk.Toplevel):
    def __init__(self, parent, masp=None):
        super().__init__(parent)
        self.parent = parent
        self.masp = masp
        self.conn = get_connection()
        
        self.title("Thêm Sản phẩm mới" if not masp else "Cập nhật Sản phẩm")
        self.geometry("500x300") 

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
        # Xây dựng giao diện người dùng cho dialog
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        grid_pad = {'pady': 6, 'padx': 5, 'sticky': 'w'}

        # Chỉ hiển thị MaSP khi đang Cập nhật (Sửa)
        if self.masp:
            tk.Label(frame, text="Mã SP:", font=FONT_NORMAL).grid(row=0, column=0, **grid_pad)
            self.ma_sp_entry = tk.Entry(frame, width=30, font=FONT_NORMAL, state="disabled")
            self.ma_sp_entry.grid(row=0, column=1, columnspan=2, **grid_pad)

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
        self.so_luong_entry = tk.Entry(frame, width=30, font=FONT_NORMAL)
        self.so_luong_entry.grid(row=5, column=1, columnspan=2, **grid_pad)

        tk.Label(frame, text="Đơn Giá (Bán):", font=FONT_NORMAL).grid(row=6, column=0, **grid_pad)
        self.don_gia_entry = tk.Entry(frame, width=30, font=FONT_NORMAL) 
        self.don_gia_entry.grid(row=6, column=1, columnspan=2, **grid_pad)
        
        if self.masp: 
             # Nếu là Sửa, vô hiệu hóa Số Lượng (chỉ được thay đổi qua Phiếu Nhập/Hóa Đơn)
             self.so_luong_entry.config(state="disabled")
        else:
             # Nếu là Thêm, cho phép nhập và đặt giá trị mặc định là 0
             self.so_luong_entry.insert(0, "0")
             self.don_gia_entry.insert(0, "0")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        create_button(btn_frame, "Lưu", command=self._on_save, kind="primary").pack(side="left", padx=10)
        create_button(btn_frame, "Hủy", command=self.destroy, kind="secondary").pack(side="left", padx=10)
        
        self.ten_sp_entry.focus_set()

    def _load_categories(self):
        # Tải danh sách Phân Loại để đưa vào combobox
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT DISTINCT PhanLoai FROM dbo.SanPhamNongDuoc WHERE PhanLoai IS NOT NULL ORDER BY PhanLoai")
            categories = [row[0] for row in cur.fetchall()]
            self.phan_loai_cb['values'] = categories
        except Exception as e:
            print(f"Lỗi tải phân loại: {e}")

    def _load_data(self):
        # Tải dữ liệu của sản phẩm hiện tại (khi Sửa)
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM dbo.SanPhamNongDuoc WHERE MaSP = ?", (self.masp,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm.", parent=self)
                self.destroy()
                return

            if hasattr(self, 'ma_sp_entry'):
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
        # Kiểm tra tính hợp lệ của dữ liệu nhập vào
        data = {}
        data["TenSP"] = self.ten_sp_entry.get().strip()
        data["PhanLoai"] = self.phan_loai_cb.get().strip()
        data["CongDung"] = self.cong_dung_entry.get().strip()
        data["DVTinh"] = self.dv_tinh_entry.get().strip()

        if not data["TenSP"]:
            messagebox.showwarning("Thiếu thông tin", "Trường 'Tên SP' không được để trống.", parent=self)
            self.ten_sp_entry.focus_set()
            return None
        if not data["PhanLoai"]:
            messagebox.showwarning("Thiếu thông tin", "Trường 'Phân Loại' không được để trống.", parent=self)
            self.phan_loai_cb.focus_set()
            return None
        if not data["DVTinh"]:
            messagebox.showwarning("Thiếu thông tin", "Trường 'ĐVT' không được để trống.", parent=self)
            self.dv_tinh_entry.focus_set()
            return None
        
        # Kiểm tra Đơn giá
        don_gia_str = self.don_gia_entry.get().strip().replace(",", "")
        try:
            data["DonGia"] = int(don_gia_str)
            if data["DonGia"] < 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai", "Đơn giá phải là một số nguyên không âm.", parent=self)
            self.don_gia_entry.focus_set()
            return None
        
        # Kiểm tra Số lượng (chỉ khi thêm mới, vì khi sửa nó bị vô hiệu hóa)
        if not self.masp:
            so_luong_str = self.so_luong_entry.get().strip().replace(",", "")
            try:
                data["SoLuong"] = int(so_luong_str)
                if data["SoLuong"] < 0: raise ValueError()
            except ValueError:
                messagebox.showwarning("Sai", "Số lượng phải là một số nguyên không âm.", parent=self)
                self.so_luong_entry.focus_set()
                return None
        
        return data

    def _on_save(self):
        # Xử lý sự kiện khi nhấn nút Lưu
        data = self._validate_input()
        if data is None:
            return
            
        try:
            result_id, error = luu_san_pham(self.masp, data)
            
            if error:
                raise Exception(error)
            
            if self.masp:
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin sản phẩm.", parent=self)
            else:
                messagebox.showinfo("Thành công", f"Đã thêm thành công sản phẩm: {result_id}", parent=self)
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu:\n{e}", parent=self)