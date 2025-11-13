import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from datetime import datetime, date

try:
    from styles.treeview_utils import create_treeview_frame, auto_fit_columns
except ImportError:
    print("Cảnh báo: Không tìm thấy styles/treeview_utils.")
    auto_fit_columns = lambda tree: None 
    
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
    "MaHD": "Mã HĐ",
    "MaThuoc": "Mã thuốc",
    "TenSP": "Tên SP",
    "TenThuoc": "Tên SP",
    "SoLuong": "Số lượng",
    "DVTinh": "ĐVT",
    "DonGia": "Đơn giá",
    "ThanhTien": "Thành tiền",
}

class InvoiceDetailWindow(tk.Toplevel):
    def __init__(self, parent, mahd):
        """Khởi tạo cửa sổ chi tiết hóa đơn."""
        super().__init__(parent)
        self.title(f"Chi tiết hóa đơn {mahd}")
        self.geometry("750x450")
        self.mahd = mahd
        
        self.makh = ""
        self.hotenkh = ""
        self.tonggt = 0
        self.ngaygd_str = "N/A"

        self._build_ui()
        self._load_details()

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _build_ui(self):
        """Tạo các thành phần giao diện tĩnh."""
        self.infof = tk.Frame(self)
        self.infof.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_makh = tk.Label(self.infof, text="Mã KH: ...", font=("Segoe UI", 10, "bold"))
        self.lbl_makh.pack(side="left", padx=(0, 12))
        
        self.lbl_hoten = tk.Label(self.infof, text="Họ tên: ...", font=("Segoe UI", 10))
        self.lbl_hoten.pack(side="left", padx=(0, 12))
        
        self.lbl_ngaygd = tk.Label(self.infof, text="Ngày GD: ...", font=("Segoe UI", 10, "bold"), fg="#005a9e")
        self.lbl_ngaygd.pack(side="left", padx=(0, 12))
        
        self.lbl_tonggt = tk.Label(self.infof, text="Tổng (GT): ...", font=("Segoe UI", 10, "bold"), fg="#2c7a2c")
        self.lbl_tonggt.pack(side="left", padx=(0, 12))

        self.area, self.tree = create_treeview_frame(self)

    def _load_details(self):
        """Kết nối CSDL, truy vấn và điền dữ liệu vào giao diện."""
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?, ?, ?)", ("MaHD", "MaKH", "TongGT"))
            rows = cur.fetchall()
            inv_tbl = None
            for s, t, c in rows:
                if c == "MaHD":
                    inv_tbl = f"[{s}].[{t}]"
                    if any(r for r in rows if r[0]==s and r[1]==t and r[2]=="MaKH"):
                        inv_tbl = f"[{s}].[{t}]"; break

            cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?, ?, ?, ?)", ("MaHD", "MaThuoc", "SoLuong", "ThanhTien"))
            drows = cur.fetchall()
            detail_tbl = None
            candidates = {}
            for s, n, c in drows:
                key = (s, n)
                candidates.setdefault(key, set()).add(c)
            for (s, n), found in candidates.items():
                if "MaHD" in found and ("MaThuoc" in found or "ThanhTien" in found or "SoLuong" in found):
                    detail_tbl = f"[{s}].[{n}]"; break

            if not detail_tbl:
                messagebox.showerror("Lỗi", "Không tìm thấy bảng chi tiết hóa đơn.", parent=self)
                self.destroy()
                return

            ngaygd = None
            date_col_name = "NgayLap"
            if inv_tbl:
                schema, tab = inv_tbl.strip("[]").split("].[")
                cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=? AND TABLE_NAME=?", (schema, tab))
                existing_cols = [r[0] for r in cur.fetchall()]
                for cand in ("NgayLap", "NgayGD", "NgayHD", "NgayHoaDon"):
                    if cand in existing_cols:
                        date_col_name = cand; break
                try:
                    sql_query = f"SELECT MaKH, COALESCE(TongGT,0), {date_col_name} FROM {inv_tbl} WHERE MaHD = ?"
                    cur.execute(sql_query, (self.mahd,))
                    r = cur.fetchone()
                    if r:
                        self.makh, self.tonggt, ngaygd = r[0], (r[1] or 0), r[2]
                except Exception as e:
                    print(f"Lỗi khi lấy chi tiết HĐ: {e}")
            
            self.ngaygd_str = ngaygd.strftime('%d/%m/%Y') if (ngaygd and isinstance(ngaygd, (datetime, date))) else "N/A"

            if self.makh:
                cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?)", ("HoTenKH",))
                r = cur.fetchone()
                if r:
                    cust_tbl = f"[{r[0]}].[{r[1]}]"
                    try:
                        cur.execute(f"SELECT HoTenKH FROM {cust_tbl} WHERE MaKH = ?", (self.makh,))
                        rr = cur.fetchone()
                        if rr: self.hotenkh = rr[0] or ""
                    except Exception:
                        self.hotenkh = ""

            self.lbl_makh.config(text=f"Mã KH: {self.makh}")
            self.lbl_hoten.config(text=f"Họ tên: {self.hotenkh}")
            self.lbl_ngaygd.config(text=f"Ngày GD: {self.ngaygd_str}")
            self.lbl_tonggt.config(text=f"Tổng (GT): {int(self.tonggt):,} đồng")

            sql_details = f"SELECT * FROM {detail_tbl} WHERE MaHD = ?"
            cur.execute(sql_details, (self.mahd,))
            rows = cur.fetchall()
            if not cur.description:
                messagebox.showinfo("Thông báo", "Không có chi tiết cho hóa đơn này.", parent=self)
                return
            
            cols = [d[0] for d in cur.description]
            display_cols = [c for c in cols if c.lower() != "stt"]
            
            self.tree["columns"] = display_cols

            for c in display_cols:
                header = VI_DETAIL.get(c, c)
                self.tree.heading(c, text=header)
            
            for r in rows:
                vals = []
                rowd = list(r)
                for i, c in enumerate(cols):
                    if c.lower() == "stt":
                        continue
                    v = rowd[i]
                    if v is None: v = ""
                    
                    # Thêm định dạng tiền
                    if c.lower() in ('dongia', 'thanhtien'):
                        try:
                            v = f"{float(v):,.0f} đồng"
                        except (ValueError, TypeError):
                            v = str(v)
                    
                    vals.append(str(v))
                self.tree.insert("", "end", values=tuple(vals))

            auto_fit_columns(self.tree)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()