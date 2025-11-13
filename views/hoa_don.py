import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from styles.ui_style import create_button, BG_MAIN, BG_TOOLBAR, FONT_ICON
from tkcalendar import DateEntry
from datetime import datetime, date

from styles.treeview_utils import create_treeview_frame, auto_fit_columns
from features.invoice_detail_window import InvoiceDetailWindow 
from features.add_invoice_dialog import AddInvoiceDialog 

DESIRED = ["MaHD", "NgayLap", "MaKH", "TongGT", "TongTien", "NhanVien"]

VI_HDR = {
    "STT": "STT",
    "MaHD": "Mã HĐ",
    "NgayLap": "Ngày GD",
    "NgayGD": "Ngày GD",
    "MaKH": "Mã KH",
    "TongGT": "Tổng (GT)",
    "TongTien": "Tổng tiền",
    "NhanVien": "Nhân viên"
}

class HoaDonTab(tk.Frame):
    def __init__(self, parent, role):
        super().__init__(parent, bg="#f7fff0")
        self.role = role
        self.tree = None
        self._sort_state = {}
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG_TOOLBAR)
        top.pack(fill="x", pady=8, padx=10)

        create_button(top, "Thêm", command=self._on_add_invoice, kind="primary", width=10).pack(side="left", padx=(6,4))
        create_button(top, "Xóa", command=self._delete_invoice, kind="danger", width=10).pack(side="left", padx=4)
        create_button(top, "⟳", command=self.load_data, kind="accent", font=FONT_ICON).pack(side="left", padx=(4,12))

        tk.Label(top, text="Tìm (Mã HĐ/Mã KH):", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.search = tk.Entry(top, width=18)
        self.search.pack(side="left", padx=(0, 10))

        tk.Label(top, text="Từ ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_from = DateEntry(top, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/MM/yyyy')
        self.date_from.pack(side="left")
        self.date_from.delete(0, "end") 

        tk.Label(top, text="Đến ngày:", bg=BG_TOOLBAR).pack(side="left", padx=(6,2))
        self.date_to = DateEntry(top, width=12, background='darkblue',
                                 foreground='white', borderwidth=2,
                                 date_pattern='dd/MM/yyyy')
        self.date_to.pack(side="left", padx=(0, 10))
        self.date_to.delete(0, "end") 

        create_button(top, "Lọc", command=self.load_data, kind="secondary").pack(side="left", padx=6)
        create_button(top, "X", command=self.clear_filters, kind="danger", width=3).pack(side="left", padx=(0,6))
        
        self.area, self.tree = create_treeview_frame(self) 

        self.tree.bind("<Double-1>", self._on_double_click)
        self.load_data()

    def _on_add_invoice(self):
        """Mở cửa sổ thêm hóa đơn."""
        AddInvoiceDialog(self)
        self.load_data()
        try:
            from services.finance import update_all_customer_totals
            update_all_customer_totals()
        except Exception as e:
            print(f"Lỗi khi cập nhật TCT: {e}")

    def _delete_invoice(self):
        """Xóa hóa đơn đang chọn."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Xóa", "Vui lòng chọn hóa đơn để xóa.")
            return
            
        try:
            mahd_idx = self.tree["columns"].index("MaHD")
            mahd = self.tree.item(sel[0], "values")[mahd_idx]
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Không thể tìm thấy MaHD.")
            return
            
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn XÓA Hóa đơn {mahd}?", parent=self):
            return
            
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.HoaDonNongDuoc WHERE MaHD = ?", (mahd,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Thành công", f"Đã xóa hóa đơn {mahd}.", parent=self)
            self.load_data()
            
            from services.finance import update_all_customer_totals
            update_all_customer_totals()
            
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể xóa hóa đơn:\n{e}", parent=self)

    def clear_filters(self):
        self.search.delete(0, "end")
        self.date_from.delete(0, "end")
        self.date_to.delete(0, "end")
        self._sort_state = {} # Xóa trạng thái sort
        self.load_data()

    def _find_table_and_cols(self, cur, desired):
        placeholders = ",".join("?" for _ in desired)
        cur.execute(f"SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN ({placeholders})", desired)
        rows = cur.fetchall()
        if not rows:
            return None, []
        tbl_map = {}
        for schema, name, col in rows:
            key = (schema, name)
            tbl_map.setdefault(key, set()).add(col)
        best = max(tbl_map.items(), key=lambda kv: len(kv[1]))
        (schema, name), found = best
        return f"[{schema}].[{name}]", list(found)

    def _create_tree_from_cursor(self, cur):
        cols = [d[0] for d in cur.description]
        self.tree["columns"] = cols
        for c in cols:
            header = VI_HDR.get(c, c)
            if c in self._sort_state:
                header = header + (" ▲" if not self._sort_state[c] else " ▼")
            
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))
            self.tree.column(c, anchor="w")

    def _on_heading_click(self, col):
        prev = self._sort_state.get(col, None)
        new = not prev if prev is not None else False
        self._sort_state = {}
        self._sort_state[col] = new
        self._sort(col, new)

    def _sort(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0].replace(",","")) if t[0] else 0, reverse=reverse)
        except Exception:
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=reverse)
        
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
            
        for c in self.tree["columns"]:
            header = VI_HDR.get(c, c)
            if c in self._sort_state:
                header = header + (" ▲" if not self._sort_state[c] else " ▼")
            self.tree.heading(c, text=header, command=lambda c=c: self._on_heading_click(c))

    def load_data(self):
        current_sort = self._sort_state.copy()
        
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            tbl, cols = self._find_table_and_cols(cur, DESIRED)
            if not tbl:
                messagebox.showerror("Lỗi", "Không tìm thấy bảng hóa đơn phù hợp.")
                return

            where = []
            params = []
            
            kw = self.search.get().strip()
            if kw:
                search_clauses = []
                if "MaHD" in cols:
                    search_clauses.append("MaHD LIKE ?")
                    params.append(f"%{kw}%")
                if "MaKH" in cols:
                    search_clauses.append("MaKH LIKE ?")
                    params.append(f"%{kw}%")
                if search_clauses:
                    where.append(f"({' OR '.join(search_clauses)})")

            date_col = None
            for cand in ("NgayLap", "NgayGD", "NgayHD", "NgayHoaDon"):
                if cand in cols:
                    date_col = cand
                    break

            df_str = self.date_from.get()
            dt_str = self.date_to.get()
            
            if date_col:
                try:
                    if df_str:
                        df = datetime.strptime(df_str, '%d/%m/%Y').date()
                        where.append(f"CAST({date_col} AS DATE) >= ?") 
                        params.append(df)
                    if dt_str:
                        dt = datetime.strptime(dt_str, '%d/%m/%Y').date()
                        where.append(f"CAST({date_col} AS DATE) <= ?")
                        params.append(dt)
                except ValueError:
                    if df_str or dt_str:
                        messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ (dd/MM/yyyy).", parent=self)
                        return

            where_sql = (" WHERE " + " AND ".join(where)) if where else ""
            order_sql = f" ORDER BY {date_col} DESC" if date_col else ""
            
            sql = f"SELECT * FROM {tbl}{where_sql}{order_sql}"
            
            cur.execute(sql, params)
            rows = cur.fetchall()

            if not cur.description:
                self.tree.delete(*self.tree.get_children())
                return
            
            db_cols = [d[0] for d in cur.description]
            self._create_tree_from_cursor(cur) 

            date_col_idx = -1
            if date_col in db_cols:
                date_col_idx = db_cols.index(date_col)

            for iid in self.tree.get_children():
                self.tree.delete(iid)
            
            for r in rows:
                vals = list(r)
                if date_col_idx != -1 and isinstance(vals[date_col_idx], (datetime, date)):
                    vals[date_col_idx] = vals[date_col_idx].strftime('%d/%m/%Y')
                
                str_vals = tuple("" if v is None else str(v) for v in vals)
                self.tree.insert("", "end", values=str_vals)
            
            auto_fit_columns(self.tree)
            
            if current_sort:
                col = list(current_sort.keys())[0]
                reverse = current_sort[col]
                self._sort(col, reverse)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
        finally:
            if conn: conn.close()

    def _on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return
            
        sel = self.tree.selection()
        if not sel:
            return
            
        vals = self.tree.item(sel[0], "values")
        if not vals: return
        
        cols = self.tree["columns"]
        mahd = None
        try:
            mahd_idx = cols.index("MaHD")
            mahd = vals[mahd_idx]
        except ValueError:
            for alt in ("SoHD","ID","InvoiceID"):
                if alt in cols:
                    mahd_idx = cols.index(alt)
                    mahd = vals[mahd_idx]; break
        
        if not mahd:
            messagebox.showinfo("Thông báo", "Không thể xác định Mã HĐ.", parent=self)
            return

        InvoiceDetailWindow(self, mahd)