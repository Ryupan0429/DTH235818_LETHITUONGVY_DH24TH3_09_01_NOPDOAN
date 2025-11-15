# Features/bao_cao_doanh_thu.py
import tkinter as tk
from tkinter import messagebox
from db import get_connection
import pandas as pd
import calendar

def get_revenue_data(year, mode='Monthly'):
    """
    Lấy dữ liệu doanh thu từ CSDL dựa trên chế độ xem (Daily, Monthly, Yearly).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if mode == 'Monthly':
            sql = """
            SELECT 
                MONTH(NgayGD) AS Period, 
                SUM(COALESCE(TongGT, 0)) AS Revenue
            FROM dbo.HoaDon
            WHERE YEAR(NgayGD) = ?
            GROUP BY MONTH(NgayGD)
            ORDER BY Period;
            """
            cur.execute(sql, (year,))
            rows = cur.fetchall()
            
            df_db = pd.DataFrame.from_records(rows, columns=["Period", "Revenue"])
            if df_db.empty:
                df_db = pd.DataFrame(columns=["Period", "Revenue"]).set_index("Period")
            else:
                df_db = df_db.set_index("Period")

            df_full = pd.DataFrame(index=range(1, 13))
            df_full.index.name = "Period"
            df = df_full.join(df_db).fillna(0)
            return df.reset_index()

        elif mode == 'Daily':
            selected_year, selected_month = year 
            
            sql = """
            SELECT 
                DAY(NgayGD) AS Period, 
                SUM(COALESCE(TongGT, 0)) AS Revenue
            FROM dbo.HoaDon
            WHERE YEAR(NgayGD) = ? AND MONTH(NgayGD) = ?
            GROUP BY DAY(NgayGD)
            ORDER BY Period;
            """
            cur.execute(sql, (selected_year, selected_month))
            rows = cur.fetchall()

            df_db = pd.DataFrame.from_records(rows, columns=["Period", "Revenue"])
            if df_db.empty:
                df_db = pd.DataFrame(columns=["Period", "Revenue"]).set_index("Period")
            else:
                df_db = df_db.set_index("Period")
            
            num_days = calendar.monthrange(selected_year, selected_month)[1]
            
            df_full = pd.DataFrame(index=range(1, num_days + 1))
            df_full.index.name = "Period"
            df = df_full.join(df_db).fillna(0)
            return df.reset_index()

        elif mode == 'Yearly':
            start_year = year - 4
            sql = """
            SELECT 
                YEAR(NgayGD) AS Period, 
                SUM(COALESCE(TongGT, 0)) AS Revenue
            FROM dbo.HoaDon
            WHERE YEAR(NgayGD) BETWEEN ? AND ?
            GROUP BY YEAR(NgayGD)
            ORDER BY Period;
            """
            cur.execute(sql, (start_year, year))
            rows = cur.fetchall()

            df_db = pd.DataFrame.from_records(rows, columns=["Period", "Revenue"])
            if df_db.empty:
                df_db = pd.DataFrame(columns=["Period", "Revenue"]).set_index("Period")
            else:
                df_db = df_db.set_index("Period")

            df_full = pd.DataFrame(index=range(start_year, year + 1))
            df_full.index.name = "Period"
            df = df_full.join(df_db).fillna(0)
            return df.reset_index()
            
        return pd.DataFrame(columns=["Period", "Revenue"])

    except Exception as e:
        messagebox.showerror("Lỗi Doanh Thu", f"Không thể lấy dữ liệu doanh thu:\n{e}")
        return pd.DataFrame(columns=["Period", "Revenue"])
    finally:
        if conn: conn.close()