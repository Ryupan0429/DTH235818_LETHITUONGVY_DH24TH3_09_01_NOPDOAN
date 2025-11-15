import pyodbc
import tkinter as tk
from tkinter import messagebox

# =====================================================
# CẤU HÌNH KẾT NỐI (DÙNG CHUNG)
# =====================================================
SERVER_NAME = r'TUONGVY\SQLEXPRESS' # Tên Server SQL của bạn
DATABASE_NAME = 'QuanLyNongDuoc' # Tên Database của bạn
USERNAME = 'sa' # <--- NHẬP USERNAME CỦA BẠN VÀO ĐÂY
PASSWORD = '' # <--- NHẬP MẬT KHẨU CỦA BẠN VÀO ĐÂY

# =====================================================
# HÀM KẾT NỐI
# =====================================================
def get_connection():
    """
    Tạo và trả về một kết nối CSDL SQL Server.
    """
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            f"UID={USERNAME};PWD={PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            messagebox.showerror("Lỗi Đăng Nhập", "Sai UID hoặc Password. Vui lòng kiểm tra file db.py.")
        elif sqlstate == '08001':
             messagebox.showerror("Lỗi Kết Nối", f"Không tìm thấy Server: {SERVER_NAME}. Vui lòng kiểm tra file db.py.")
        elif sqlstate == '42000':
             messagebox.showerror("Lỗi CSDL", f"Không tìm thấy Database: {DATABASE_NAME}. Bạn đã chạy file generate.py hoặc Restore CSDL chưa?")
        else:
            messagebox.showerror("Lỗi CSDL", f"Lỗi kết nối: {ex}")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi Chung", f"Lỗi không xác định: {e}")
        return None