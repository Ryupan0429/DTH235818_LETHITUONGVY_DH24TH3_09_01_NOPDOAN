import tkinter as tk
from tkinter import messagebox
from db import get_connection
from datetime import datetime, date
from Modules.ui_style import center, FONT_NORMAL, FONT_TITLE, create_button, BG_MAIN
from Modules.utils import create_treeview_frame
from Features.chi_tiet import InvoiceDetailWindow

class CustomerHistoryDialog(tk.Toplevel):
    def __init__(self, parent, makh, tenkh):
        """
        Khởi tạo cửa sổ Lịch sử Giao dịch cho một khách hàng cụ thể.
        """
        super().__init__(parent)
        self.makh = makh
        self.tenkh = tenkh
        
        self.title(f"Lịch sử Giao dịch - {self.tenkh} ({self.makh})")
        self.geometry("800x500")
        self.configure(bg=BG_MAIN)
        
        self.conn = get_connection()
        self.tree = None

        self._build_ui()
        self._load_history()

        center(self, 800, 500)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _build_ui(self):
        """Tạo các thành phần giao diện tĩnh."""
        tk.Label(self, text=f"Khách hàng: {self.tenkh} ({self.makh})", 
                 font=FONT_TITLE, bg=BG_MAIN).pack(pady=(10, 5))
        
        tk.Label(self, text="Nháy đúp vào một hóa đơn để xem chi tiết.", 
                 font=FONT_NORMAL, bg=BG_MAIN).pack(pady=(0, 5))

        self.area, self.tree = create_treeview_frame(self)
        
        cols = ("MaHD", "NgayGD", "TongGT")
        headings = {"MaHD": "Mã HĐ", "NgayGD": "Ngày Giao Dịch", "TongGT": "Tổng Giá Trị"}
        
        self.tree["columns"] = cols
        for col_id, text in headings.items():
            anchor = "e" if col_id == "TongGT" else "w"
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, anchor=anchor)
            
        self.tree.bind("<Double-1>", self._on_double_click)

    def _load_history(self):
        """Tải lịch sử hóa đơn của khách hàng này."""
        try:
            cur = self.conn.cursor()
            
            sql = "SELECT MaHD, NgayGD, TongGT FROM dbo.HoaDon WHERE MaKH = ? ORDER BY NgayGD DESC"
            cur.execute(sql, (self.makh,))
            rows = cur.fetchall()
            
            for r in rows:
                vals = list(r)
                if isinstance(vals[1], (datetime, date)):
                    vals[1] = vals[1].strftime('%d/%m/%Y')
                vals[2] = f"{vals[2]:,.0f} đồng"
                self.tree.insert("", "end", values=tuple(vals))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lịch sử:\n{e}", parent=self)

    def _on_double_click(self, event):
        """Mở chi tiết hóa đơn (tái sử dụng)."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading": return
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        if not vals: return
        
        mahd = vals[0]
        InvoiceDetailWindow(self, mahd)