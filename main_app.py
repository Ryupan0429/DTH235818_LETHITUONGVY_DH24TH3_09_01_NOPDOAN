import tkinter as tk
from tkinter import ttk
from db import get_connection

# Import các tab view
from views.khach_hang import KhachHangTab
from views.thuoc import ThuocTab
from views.hoa_don import HoaDonTab
from views.doanh_thu import DoanhThuTab

# Import style
from styles.ui_style import (
    BG_MAIN, BG_TOOLBAR, FONT_TITLE, FONT_NORMAL, 
    BTN_DANGER_BG, center, style_ttk
)

def open_main_admin(role, username):
    """Mở cửa sổ chính của ứng dụng (cho Admin/Manager)."""
    app = tk.Tk()
    
    style_ttk(app) 
    
    app.title(f"Quản lý Nông Dược - {username} ({role})")
    app.geometry("1300x700")
    center(app, 1300, 700)
    app.configure(bg=BG_MAIN)

    header_frame = tk.Frame(app, bg=BG_TOOLBAR, height=40)
    header_frame.pack(fill="x")
    
    def _handle_logout():
        app.destroy()
        from login import login_screen 
        login_screen()

    # --- (SỬA THỨ TỰ PACK) ---
    logout_btn = tk.Button(header_frame, text="Đăng xuất", 
                           command=_handle_logout, 
                           bg=BTN_DANGER_BG, fg="black", font=FONT_NORMAL)
    # Pack nút Đăng xuất BÊN PHẢI CÙNG
    logout_btn.pack(side="right", padx=10, pady=5)

    # Pack Tên user (nó sẽ nằm bên trái nút Đăng xuất)
    tk.Label(header_frame, text=f"{username} ({role})", 
             font=FONT_TITLE, bg=BG_TOOLBAR).pack(side="right", padx=10, pady=5)
    # --- (HẾT SỬA) ---

    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    notebook.add(HoaDonTab(notebook, role), text="🧾 Hóa đơn")
    notebook.add(KhachHangTab(notebook, role), text="👥 Khách hàng")
    notebook.add(ThuocTab(notebook, role), text="💊 Thuốc")
    notebook.add(DoanhThuTab(notebook, role), text="📊 Doanh Thu")

    app.protocol("WM_DELETE_WINDOW", _handle_logout)
    app.mainloop()

if __name__ == "__main__":
    from login import login_screen
    login_screen()