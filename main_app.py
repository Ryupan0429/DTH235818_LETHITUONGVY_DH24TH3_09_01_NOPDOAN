import tkinter as tk
from tkinter import ttk

from Views.khach_hang import KhachHangTab
from Views.san_pham import SanPhamTab
from Views.hoa_don import HoaDonTab
from Views.phieu_nhap import PhieuNhapTab
from Views.thu_chi import ThuChiTab 
from Modules.ui_style import (
    BG_MAIN, BG_TOOLBAR, FONT_TITLE, FONT_NORMAL, 
    center, style_ttk, create_button 
)
from Features.backup import backup_database, restore_database

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
    
    # --- Khung bên trái (Backup/Restore) ---
    backup_frame = tk.Frame(header_frame, bg=BG_TOOLBAR)
    backup_frame.pack(side="left", padx=10, pady=5)

    restore_btn = create_button(backup_frame, "Khôi phục", 
                                command=lambda: restore_database(app), 
                                kind="accent")
    restore_btn.pack(side="left", padx=(0, 5))
    
    backup_btn = create_button(backup_frame, "Lưu Backup", 
                               command=lambda: backup_database(app), 
                               kind="secondary")
    backup_btn.pack(side="left", padx=5)

    # --- Khung bên phải (Đăng xuất) ---
    logout_frame = tk.Frame(header_frame, bg=BG_TOOLBAR)
    logout_frame.pack(side="right", padx=10, pady=5)
    
    def _handle_logout():
        app.destroy()
        from login import login_screen 
        login_screen()

    logout_btn = ttk.Button(logout_frame, text="Đăng xuất", 
                           command=_handle_logout, 
                           style="Danger.TButton")
    logout_btn.pack(side="left")

    tk.Label(logout_frame, text=f"{username} ({role})", 
             font=FONT_TITLE, bg=BG_TOOLBAR).pack(side="left", padx=10)

    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    # Load các tab
    notebook.add(HoaDonTab(notebook, role, username), text="🧾 Hóa Đơn (Bán hàng)")
    notebook.add(PhieuNhapTab(notebook, role, username), text="📦 Phiếu Nhập (Mua hàng)")
    notebook.add(SanPhamTab(notebook, role), text="💊 Sản Phẩm")
    notebook.add(KhachHangTab(notebook, role), text="👥 Khách Hàng")
    
    notebook.add(ThuChiTab(notebook, role), text="📊 Thu Chi")

    app.protocol("WM_DELETE_WINDOW", _handle_logout)
    app.mainloop()

if __name__ == "__main__":
    from login import login_screen
    login_screen()