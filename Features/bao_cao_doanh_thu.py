from tkinter import messagebox
from db import get_connection
import pandas as pd
import calendar

def _get_data(sql, params, columns):
    """Hàm trợ giúp chạy SQL và trả về DataFrame."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        df = pd.DataFrame.from_records(rows, columns=columns)
        if df.empty:
            return pd.DataFrame(columns=columns).set_index("Period")
        return df.set_index("Period")
    finally:
        if conn: conn.close()

def get_thu_chi_data(param, mode='Monthly'):
    """
    Lấy dữ liệu THU (Hóa đơn) và CHI (Phiếu nhập) từ CSDL.
    """
    try:
        if mode == 'Monthly':
            year = param
            sql_thu = """
                SELECT MONTH(NgayGD) AS Period, SUM(COALESCE(TongGT, 0)) AS Thu
                FROM dbo.HoaDon WHERE YEAR(NgayGD) = ? GROUP BY MONTH(NgayGD)
            """
            sql_chi = """
                SELECT MONTH(NgayNhap) AS Period, SUM(COALESCE(TongGGT, 0)) AS Chi
                FROM dbo.PhieuNhap WHERE YEAR(NgayNhap) = ? GROUP BY MONTH(NgayNhap)
            """
            df_thu = _get_data(sql_thu, (year,), ["Period", "Thu"])
            df_chi = _get_data(sql_chi, (year,), ["Period", "Chi"])
            
            df_full = pd.DataFrame(index=range(1, 13))
            df_full.index.name = "Period"

        elif mode == 'Daily':
            selected_year, selected_month = param
            sql_thu = """
                SELECT DAY(NgayGD) AS Period, SUM(COALESCE(TongGT, 0)) AS Thu
                FROM dbo.HoaDon WHERE YEAR(NgayGD) = ? AND MONTH(NgayGD) = ? GROUP BY DAY(NgayGD)
            """
            sql_chi = """
                SELECT DAY(NgayNhap) AS Period, SUM(COALESCE(TongGGT, 0)) AS Chi
                FROM dbo.PhieuNhap WHERE YEAR(NgayNhap) = ? AND MONTH(NgayNhap) = ? GROUP BY DAY(NgayNhap)
            """
            df_thu = _get_data(sql_thu, (selected_year, selected_month), ["Period", "Thu"])
            df_chi = _get_data(sql_chi, (selected_year, selected_month), ["Period", "Chi"])
            
            num_days = calendar.monthrange(selected_year, selected_month)[1]
            df_full = pd.DataFrame(index=range(1, num_days + 1))
            df_full.index.name = "Period"

        elif mode == 'Yearly':
            year = param
            start_year = year - 4
            sql_thu = """
                SELECT YEAR(NgayGD) AS Period, SUM(COALESCE(TongGT, 0)) AS Thu
                FROM dbo.HoaDon WHERE YEAR(NgayGD) BETWEEN ? AND ? GROUP BY YEAR(NgayGD)
            """
            sql_chi = """
                SELECT YEAR(NgayNhap) AS Period, SUM(COALESCE(TongGGT, 0)) AS Chi
                FROM dbo.PhieuNhap WHERE YEAR(NgayNhap) BETWEEN ? AND ? GROUP BY YEAR(NgayNhap)
            """
            df_thu = _get_data(sql_thu, (start_year, year), ["Period", "Thu"])
            df_chi = _get_data(sql_chi, (start_year, year), ["Period", "Chi"])
            
            df_full = pd.DataFrame(index=range(start_year, year + 1))
            df_full.index.name = "Period"
        
        else:
            return pd.DataFrame(columns=["Period", "Thu", "Chi"])

        # Gộp (Join) dữ liệu Thu và Chi
        df_merged = df_full.join(df_thu).join(df_chi)
        # Điền 0 cho các kỳ không có dữ liệu
        df_merged = df_merged.fillna(0)
        
        return df_merged.reset_index().astype({'Thu': float, 'Chi': float})

    except Exception as e:
        messagebox.showerror("Lỗi Báo Cáo", f"Không thể lấy dữ liệu thu chi:\n{e}")
        return pd.DataFrame(columns=["Period", "Thu", "Chi"])