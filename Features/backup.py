from tkinter import messagebox, filedialog
import pyodbc
import os
from datetime import datetime
from db import SERVER_NAME, DATABASE_NAME, USERNAME, PASSWORD

BACKUP_DIR = os.path.join(os.getcwd(), "Backup")

def _get_master_connection():
    """Kết nối CSDL master (dùng cho Backup)."""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE=master;"
            f"UID={USERNAME};PWD={PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str, autocommit=True, timeout=30)
        return conn
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
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            title="Lưu file backup",
            initialdir=BACKUP_DIR,
            initialfile=f"{DATABASE_NAME}_{datetime.now():%Y_%m_%d_%H%M%S}.bak",
            defaultextension=".bak",
            filetypes=[("Backup files", "*.bak")]
        )
        if not filename:
            return 

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
