import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from datetime import datetime, date

try:
    from Modules.utils import create_treeview_frame
except ImportError:
    # Fallback (phòng trường hợp)
    def create_treeview_frame(parent):
        area = tk.Frame(parent)
        area.pack(fill="both", expand=True, padx=8, pady=8)
        tree = ttk.Treeview(area, show="headings")
        vsb = ttk.Scrollbar(area, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(area, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        return area, tree

# Tiêu đề tiếng Việt
VI_DETAIL = {
    "MaSP": "Mã SP",
    "TenSP": "Tên SP",
    "SoLuong": "Số lượng",
    "DVTinh": "ĐVT",
    "DonGia": "Đơn giá",
    "ThanhTien": "Thành tiền",
}

class InvoiceDetailWindow(tk.Toplevel):
    def __init__(self, parent, mahd_or_sopn):
        """
        Khởi tạo cửa sổ chi tiết.
        Tự động phát hiện xem đây là Hóa đơn (HD) hay Phiếu Nhập (PN).
        """
        super().__init__(parent)
        self.mahd_or_sopn = mahd_or_sopn
        self.is_invoice = str(mahd_or_sopn).upper().startswith("HD")
        
        title_prefix = "Chi tiết Hóa đơn" if self.is_invoice else "Chi tiết Phiếu Nhập"
        self.title(f"{title_prefix} {mahd_or_sopn}")
        self.geometry("750x450")

        self._build_ui()
        self._load_details()

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build_ui(self):
        """Tạo các thành phần giao diện tĩnh."""
        self.infof = tk.Frame(self)
        self.infof.pack(fill="x", padx=10, pady=(10, 5))

        # Các label này sẽ được cấu hình trong _load_details
        self.lbl_info1 = tk.Label(self.infof, text="...", font=("Segoe UI", 10, "bold"))
        self.lbl_info1.pack(side="left", padx=(0, 12))
        
        self.lbl_info2 = tk.Label(self.infof, text="...", font=("Segoe UI", 10))
        self.lbl_info2.pack(side="left", padx=(0, 12))
        
        self.lbl_date = tk.Label(self.infof, text="Ngày: ...", font=("Segoe UI", 10, "bold"), fg="#005a9e")
        self.lbl_date.pack(side="left", padx=(0, 12))
        
        self.lbl_total = tk.Label(self.infof, text="Tổng: ...", font=("Segoe UI", 10, "bold"), fg="#2c7a2c")
        self.lbl_total.pack(side="left", padx=(0, 12))

        self.area, self.tree = create_treeview_frame(self)

    def _load_details(self):
        """Kết nối CSDL, truy vấn và điền dữ liệu vào giao diện."""
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            if self.is_invoice:
                # --- XỬ LÝ HÓA ĐƠN (BÁN) ---
                cur.execute("""
                    SELECT H.MaKH, H.NgayGD, H.TongGT, K.TenKH 
                    FROM dbo.HoaDon H
                    LEFT JOIN dbo.KhachHang K ON H.MaKH = K.MaKH
                    WHERE H.MaHD = ?
                """, (self.mahd_or_sopn,))
                header_row = cur.fetchone()
                
                if header_row:
                    self.lbl_info1.config(text=f"Mã KH: {header_row.MaKH}")
                    self.lbl_info2.config(text=f"Họ tên: {header_row.TenKH or 'N/A'}")
                    self.lbl_date.config(text=f"Ngày GD: {header_row.NgayGD.strftime('%d/%m/%Y')}")
                    self.lbl_total.config(text=f"Tổng GT: {header_row.TongGT:,.0f} đồng")

                # Tải chi tiết
                cur.execute("SELECT MaSP, TenSP, SoLuong, DVTinh, DonGia, ThanhTien FROM dbo.ChiTietHoaDon WHERE MaHD = ?", 
                            (self.mahd_or_sopn,))
                
            else:
                # --- XỬ LÝ PHIẾU NHẬP (MUA) ---
                cur.execute("""
                    SELECT NgayNhap, NguoiNhap, NguonNhap, TongGGT
                    FROM dbo.PhieuNhap
                    WHERE SoPN = ?
                """, (self.mahd_or_sopn,))
                header_row = cur.fetchone()
                
                if header_row:
                    self.lbl_info1.config(text=f"Người nhập: {header_row.NguoiNhap}")
                    self.lbl_info2.config(text=f"Nguồn: {header_row.NguonNhap or 'N/A'}")
                    self.lbl_date.config(text=f"Ngày Nhập: {header_row.NgayNhap.strftime('%d/%m/%Y')}")
                    self.lbl_total.config(text=f"Tổng Nhập: {header_row.TongGGT:,.0f} đồng")
                
                # Tải chi tiết
                cur.execute("SELECT MaSP, TenSP, SoLuong, DVTinh, DonGia, ThanhTien FROM dbo.ChiTietPhieuNhap WHERE SoPN = ?", 
                            (self.mahd_or_sopn,))

            # --- Hiển thị dữ liệu chi tiết lên Treeview (Dùng chung) ---
            rows = cur.fetchall()
            if not rows:
                messagebox.showinfo("Thông báo", "Không có chi tiết cho phiếu này.", parent=self)
                return
            
            # Lấy tên cột từ cursor (MaSP, TenSP, ...)
            cols = [d[0] for d in cur.description]
            self.tree["columns"] = cols

            for c in cols:
                header = VI_DETAIL.get(c, c)
                self.tree.heading(c, text=header)
                anchor = "e" if c in ("SoLuong", "DonGia", "ThanhTien") else "w"
                self.tree.column(c, anchor=anchor)
            
            for r in rows:
                vals = []
                for i, col_name in enumerate(cols):
                    v = r[i]
                    if v is None: v = ""
                    
                    if col_name in ('DonGia', 'ThanhTien'):
                        try:
                            v = f"{float(v):,.0f}"
                        except (ValueError, TypeError):
                            v = str(v)
                    
                    vals.append(str(v))
                self.tree.insert("", "end", values=tuple(vals))

        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()