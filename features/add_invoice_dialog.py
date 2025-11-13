import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from tkcalendar import DateEntry
from datetime import datetime
from styles.ui_style import center
from services.finance import get_discount_rate

def _next_mahd(conn):
    """Tạo mã hóa đơn mới (ví dụ: HD00001)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT MaHD FROM dbo.HoaDonNongDuoc WHERE MaHD LIKE 'HD%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("HD"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"HD{nxt:05d}"
    except Exception:
        return None

class AddInvoiceDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tạo Hóa đơn mới")
        self.geometry("800x600")
        
        self.conn = get_connection()
        self.thuoc_data = self._load_thuoc_data()
        self.customer_data_map = {} 
        self.customer_display_list = [] 
        self.total_amount = 0.0
        self.current_discount_rate = 0.0
        
        # Biến để kiểm soát việc trì hoãn tìm kiếm
        self._search_job = None

        self._build_ui()
        self._load_customers()
        
        center(self, 800, 600)
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _load_thuoc_data(self):
        """Tải danh sách thuốc (Thêm lại DVTinh)."""
        data = {}
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaThuoc, TenThuoc, DonGia, DVTinh FROM dbo.ThuocNongDuoc")
            for row in cur.fetchall():
                data[row.TenThuoc] = {
                    "MaThuoc": row.MaThuoc,
                    "DonGia": row.DonGia,
                    "DVTinh": row.DVTinh or "cái"
                }
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách thuốc:\n{e}", parent=self)
            return {}

    def _load_customers(self):
        """Tải danh sách khách hàng VÀ THỨ HẠNG."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MaKH, HoTenKH, ThuHang FROM dbo.ThongTinKhachHang ORDER BY HoTenKH")
            
            self.customer_display_list = []
            self.customer_data_map = {}
            
            for row in cur.fetchall():
                display_name = f"{row.HoTenKH} ({row.MaKH})"
                self.customer_display_list.append(display_name)
                self.customer_data_map[row.MaKH] = row.ThuHang
                
            self.customer_cb["values"] = self.customer_display_list
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khách hàng:\n{e}", parent=self)

    def _schedule_customer_search(self, event):
        """Lên lịch (hoặc hủy lịch) một tác vụ tìm kiếm."""
        # Hủy tác vụ tìm kiếm cũ (nếu có)
        if self._search_job:
            self.after_cancel(self._search_job)
        
        # Lên lịch tác vụ mới sau 750ms
        self._search_job = self.after(750, self._on_customer_search)

    def _on_customer_search(self):
        """Lọc danh sách khách hàng dựa trên nội dung đã gõ."""
        search_term = self.customer_cb.get().lower()
        
        if not search_term:
            self.customer_cb["values"] = self.customer_display_list
            return

        filtered_list = [
            name for name in self.customer_display_list 
            if search_term in name.lower()
        ]
        
        # Lưu lại văn bản và vị trí con trỏ
        current_text = self.customer_cb.get()
        cursor_pos = self.customer_cb.index(tk.INSERT)
        
        # Cập nhật danh sách
        self.customer_cb["values"] = filtered_list
        
        # Phục hồi văn bản và con trỏ
        self.customer_cb.set(current_text)
        self.customer_cb.icursor(cursor_pos)
        
        # Mở dropdown
        self.customer_cb.event_generate('<Down>')


    def _on_customer_select(self, event):
        """Khi chọn khách hàng, cập nhật tỷ lệ giảm giá."""
        customer_str = self.customer_cb.get()
        if not customer_str:
            self.current_discount_rate = 0.0
            return
            
        try:
            ma_kh = customer_str.split('(')[-1].replace(')', '')
            thu_hang = self.customer_data_map.get(ma_kh)
            self.current_discount_rate = get_discount_rate(thu_hang)
            
            self._recalculate_cart_prices()
            self._update_total()
        except Exception:
            self.current_discount_rate = 0.0

    def _build_ui(self):
        info_frame = tk.Frame(self)
        info_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(info_frame, text="Khách hàng:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.customer_cb = ttk.Combobox(info_frame, width=30)
        self.customer_cb.grid(row=0, column=1, padx=5, pady=5)
        
        self.customer_cb.bind("<<ComboboxSelected>>", self._on_customer_select)
        # Thêm binding để tìm kiếm (gọi hàm lên lịch)
        self.customer_cb.bind("<KeyRelease>", self._schedule_customer_search)

        tk.Label(info_frame, text="Ngày GD:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.ngay_gd_entry = DateEntry(info_frame, width=12, date_pattern='dd/MM/yyyy',
                                       background='darkblue', foreground='white')
        self.ngay_gd_entry.grid(row=0, column=3, padx=5, pady=5)

        add_frame = ttk.LabelFrame(self, text="Thêm mặt hàng")
        add_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(add_frame, text="Tên thuốc:").grid(row=0, column=0, padx=5, pady=5)
        self.thuoc_cb = ttk.Combobox(add_frame, width=40, values=list(self.thuoc_data.keys()))
        self.thuoc_cb.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Số lượng:").grid(row=0, column=2, padx=5, pady=5)
        self.so_luong_entry = tk.Entry(add_frame, width=8)
        self.so_luong_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(add_frame, text="Thêm vào HĐ", command=self._add_item_to_tree).grid(row=0, column=4, padx=10, pady=5)
        tk.Button(add_frame, text="Xóa", command=self._remove_item, bg="#f7c6c6").grid(row=0, column=5, padx=5, pady=5)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = ("MaThuoc", "TenSP", "SoLuong", "DVTinh", "DonGia", "Giam", "ThanhTien")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        
        self.tree.heading("MaThuoc", text="Mã Thuốc")
        self.tree.heading("TenSP", text="Tên Sản Phẩm")
        self.tree.heading("SoLuong", text="SL")
        self.tree.heading("DVTinh", text="ĐVT")
        self.tree.heading("DonGia", text="Đơn Giá (đã giảm)")
        self.tree.heading("Giam", text="Giảm")
        self.tree.heading("ThanhTien", text="Thành Tiền")
        
        self.tree.column("TenSP", width=250)
        self.tree.column("SoLuong", width=60, anchor="e")
        self.tree.column("DVTinh", width=60, anchor="w")
        self.tree.column("DonGia", width=120, anchor="e")
        self.tree.column("Giam", width=60, anchor="e")
        self.tree.column("ThanhTien", width=120, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = tk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Segoe UI", 12, "bold"), fg="red")
        self.total_label.pack(side="left")

        tk.Button(bottom_frame, text="Hủy", command=self.destroy).pack(side="right", padx=5)
        tk.Button(bottom_frame, text="Lưu Hóa đơn", command=self._on_save).pack(side="right", padx=5)

    def _add_item_to_tree(self):
        ten_thuoc = self.thuoc_cb.get()
        so_luong_str = self.so_luong_entry.get()

        if not ten_thuoc or not so_luong_str or ten_thuoc not in self.thuoc_data:
            messagebox.showwarning("Lỗi", "Vui lòng chọn thuốc hợp lệ và nhập số lượng.", parent=self)
            return

        try:
            so_luong = int(so_luong_str)
            if so_luong <= 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Lỗi", "Số lượng phải là số nguyên dương.", parent=self)
            return
        
        thuoc = self.thuoc_data[ten_thuoc]
        ma_thuoc = thuoc["MaThuoc"]
        don_gia_goc = float(thuoc["DonGia"])
        dv_tinh = thuoc["DVTinh"]
        
        rate = self.current_discount_rate
        don_gia_sau = don_gia_goc * (1 - rate)
        thanh_tien = don_gia_sau * so_luong
        giam_str = f"{rate * 100:,.0f}%"

        for item_id in self.tree.get_children():
            item_ma_thuoc = self.tree.item(item_id, "values")[0]
            if item_ma_thuoc == ma_thuoc:
                old_sl = int(self.tree.item(item_id, "values")[2])
                new_sl = old_sl + so_luong
                new_thanh_tien = don_gia_sau * new_sl
                self.tree.item(item_id, values=(
                    ma_thuoc, ten_thuoc, new_sl, dv_tinh, f"{don_gia_sau:,.0f}", giam_str, f"{new_thanh_tien:,.0f}"
                ))
                break
        else:
            self.tree.insert("", "end", values=(
                ma_thuoc, ten_thuoc, so_luong, dv_tinh, f"{don_gia_sau:,.0f}", giam_str, f"{thanh_tien:,.0f}"
            ))
        
        self._update_total()
        self.thuoc_cb.set("")
        self.so_luong_entry.delete(0, "end")

    def _recalculate_cart_prices(self):
        """Tính toán lại toàn bộ giỏ hàng khi đổi khách hàng."""
        for item_id in self.tree.get_children():
            vals = self.tree.item(item_id, "values")
            ma_thuoc, ten_thuoc, so_luong_str, dv_tinh = vals[0], vals[1], vals[2], vals[3]
            so_luong = int(so_luong_str)
            
            don_gia_goc = float(self.thuoc_data[ten_thuoc]["DonGia"])
            
            rate = self.current_discount_rate
            don_gia_sau = don_gia_goc * (1 - rate)
            thanh_tien = don_gia_sau * so_luong
            giam_str = f"{rate * 100:,.0f}%"

            self.tree.item(item_id, values=(
                ma_thuoc, ten_thuoc, so_luong, dv_tinh, f"{don_gia_sau:,.0f}", giam_str, f"{thanh_tien:,.0f}"
            ))
        
        self._update_total()
        
    def _remove_item(self):
        sel = self.tree.selection()
        if not sel: return
        for item_id in sel:
            self.tree.delete(item_id)
        self._update_total()

    def _update_total(self):
        self.total_amount = 0.0
        for item_id in self.tree.get_children():
            thanh_tien_str = self.tree.item(item_id, "values")[6].replace(",", "")
            self.total_amount += float(thanh_tien_str)
        self.total_label.config(text=f"Tổng cộng: {self.total_amount:,.0f} VNĐ")

    def _on_save(self):
        customer_str = self.customer_cb.get()
        if not customer_str:
            messagebox.showwarning("Thiếu", "Vui lòng chọn khách hàng.", parent=self)
            return
            
        if not self.tree.get_children():
            messagebox.showwarning("Thiếu", "Hóa đơn phải có ít nhất 1 mặt hàng.", parent=self)
            return

        try:
            ma_kh = customer_str.split('(')[-1].replace(')', '')
            ngay_gd = self.ngay_gd_entry.get_date()
            
            if ma_kh not in self.customer_data_map:
                messagebox.showwarning("Sai", "Khách hàng không hợp lệ.", parent=self)
                return
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {e}", parent=self)
            return

        try:
            cur = self.conn.cursor()
            ma_hd = _next_mahd(self.conn)
            if not ma_hd:
                raise Exception("Không thể tạo Mã Hóa đơn.")

            cur.execute(
                "INSERT INTO dbo.HoaDonNongDuoc (MaHD, MaKH, NgayGD, TongGT) VALUES (?, ?, ?, ?)",
                (ma_hd, ma_kh, ngay_gd, self.total_amount) 
            )

            items_to_insert = []
            for item_id in self.tree.get_children():
                vals = self.tree.item(item_id, "values")
                item_data = (
                    ma_hd,
                    vals[0], # MaThuoc
                    vals[1], # TenSP
                    int(vals[2]), # SoLuong
                    vals[3], # DVTinh
                    float(vals[4].replace(",", "")), # DonGia (đã giảm)
                    float(vals[6].replace(",", ""))  # ThanhTien
                )
                items_to_insert.append(item_data)
            
            sql_insert_detail = """
            INSERT INTO dbo.ChiTietHoaDon (MaHD, MaThuoc, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.executemany(sql_insert_detail, items_to_insert)

            cur.execute(
                "UPDATE dbo.ThongTinKhachHang SET TongChiTieu = COALESCE(TongChiTieu, 0) + ? WHERE MaKH = ?",
                (self.total_amount, ma_kh)
            )

            self.conn.commit()
            messagebox.showinfo("Thành công", f"Đã tạo thành công hóa đơn {ma_hd}.", parent=self)
            self.destroy()

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi CSDL", f"Không thể lưu hóa đơn:\n{e}", parent=self)