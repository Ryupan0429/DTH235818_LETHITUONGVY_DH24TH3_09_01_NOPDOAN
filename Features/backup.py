import tkinter as tk
from tkinter import messagebox, filedialog
import pyodbc
import os
from datetime import datetime
from db import SERVER_NAME, DATABASE_NAME, USERNAME, PASSWORD

BACKUP_DIR = os.path.join(os.getcwd(), "Backup")

def _get_master_connection():
    """Kết nối CSDL master (dùng cho Backup/Restore)."""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE=master;"
            f"UID={USERNAME};PWD={PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, autocommit=True)
    except Exception as e:
        messagebox.showerror("Lỗi Kết nối Master", f"Không thể kết nối CSDL master. "
                             f"Vui lòng đảm bảo user '{USERNAME}' tồn tại.\nLỗi: {e}")
        return None

def create_backup_dir():
    """Tạo thư mục /Backup nếu nó chưa tồn tại."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database(parent_window):
    """Mở dialog Lưu và thực hiện BACKUP DATABASE."""
    create_backup_dir()
    try:
        # 1. Lấy đường dẫn lưu
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            title="Lưu file backup",
            initialdir=BACKUP_DIR,
            initialfile=f"{DATABASE_NAME}_{datetime.now():%Y_%m_%d_%H%M%S}.bak",
            defaultextension=".bak",
            filetypes=[("Backup files", "*.bak")]
        )
        if not filename:
            return # Người dùng nhấn Hủy

        # 2. Chạy lệnh BACKUP
        conn = _get_master_connection()
        if not conn: return
        
        cur = conn.cursor()
        sql_command = f"BACKUP DATABASE [{DATABASE_NAME}] TO DISK = N'{filename}' WITH NOFORMAT, INIT, NAME = N'{DATABASE_NAME}-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, STATS = 10"
        
        messagebox.showinfo("Đang backup", "Đang sao lưu CSDL... Vui lòng đợi.", parent=parent_window)
        cur.execute(sql_command)
        while cur.nextset():
            pass
        
        cur.close()
        conn.close()
        
        messagebox.showinfo("Thành công", f"Đã sao lưu CSDL thành công!\nĐường dẫn: {filename}", parent=parent_window)

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi Sao lưu", f"Không thể sao lưu CSDL.\nLỗi: {e}\n\n"
                             "Đảm bảo user SQL có quyền 'BACKUP DATABASE' và thư mục lưu có quyền Ghi.", parent=parent_window)
    except Exception as e:
        messagebox.showerror("Lỗi", str(e), parent=parent_window)

def restore_database(parent_window):
    """Mở dialog Mở và thực hiện RESTORE DATABASE."""
    if not messagebox.askyesno("Xác nhận Khôi phục",
        "CẢNH BÁO: Thao tác này sẽ GHI ĐÈ toàn bộ CSDL hiện tại.\n"
        "Toàn bộ dữ liệu chưa sao lưu sẽ bị MẤT.\n\n"
        "Bạn có chắc chắn muốn tiếp tục?", parent=parent_window, icon='warning'):
        return

    try:
        # 1. Lấy đường dẫn file .bak
        filename = filedialog.askopenfilename(
            parent=parent_window,
            title="Chọn file backup (.bak) để khôi phục",
            initialdir=BACKUP_DIR,
            filetypes=[("Backup files", "*.bak")]
        )
        if not filename:
            return # Người dùng nhấn Hủy

        # 2. Chạy lệnh RESTORE (phải kết nối master)
        conn = _get_master_connection()
        if not conn: return
        
        cur = conn.cursor()

        # Phải set CSDL về SINGLE_USER trước khi restore
        sql_set_single = f"ALTER DATABASE [{DATABASE_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"
        sql_restore = f"RESTORE DATABASE [{DATABASE_NAME}] FROM DISK = N'{filename}' WITH REPLACE"
        sql_set_multi = f"ALTER DATABASE [{DATABASE_NAME}] SET MULTI_USER"

        messagebox.showinfo("Đang khôi phục", "Đang khôi phục CSDL... Ứng dụng sẽ bị treo trong giây lát.\n"
                          "Vui lòng đợi thông báo thành công.", parent=parent_window)

        cur.execute(sql_set_single)
        cur.execute(sql_restore)
        cur.execute(sql_set_multi)
        
        cur.close()
        conn.close()
        
        messagebox.showinfo("Thành công", "Đã khôi phục CSDL thành công.\n"
                          "Vui lòng khởi động lại ứng dụng.", parent=parent_window)
        parent_window.destroy() # Buộc khởi động lại

    except pyodbc.Error as e:
        # Cố gắng set lại MULTI_USER nếu restore thất bại
        try:
            conn = _get_master_connection()
            conn.cursor().execute(f"ALTER DATABASE [{DATABASE_NAME}] SET MULTI_USER")
            conn.close()
        except:
            pass
        messagebox.showerror("Lỗi Khôi phục", f"Không thể khôi phục CSDL.\nLỗi: {e}\n\n"
                             "Đảm bảo user SQL có quyền 'REPLACE' và 'ALTER DATABASE'.", parent=parent_window)
    except Exception as e:
        messagebox.showerror("Lỗi", str(e), parent=parent_window)