from db import get_connection

def _find_invoice_table_and_amount_col(cur):
    """
    Tự động tìm bảng Hóa đơn và cột Tổng tiền (Ưu tiên TongGT, TongTien, Total).
    """
    cur.execute(
        "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME "
        "FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?, ?, ?, ?)",
        ("MaKH", "TongGT", "TongTien", "Total") 
    )
    rows = cur.fetchall()
    if not rows:
        return None, None
        
    tbl_map = {}
    for s, t, c in rows:
        tbl_map.setdefault((s, t), set()).add(c)
        
    for (s, t), cols in tbl_map.items():
        if "MaKH" in cols:
            # Sửa: Ưu tiên 'TongGT'
            if "TongGT" in cols:
                return f"[{s}].[{t}]", "TongGT"
            if "TongTien" in cols:
                return f"[{s}].[{t}]", "TongTien"
            if "Total" in cols:
                return f"[{s}].[{t}]", "Total"
                
    return None, None

def update_all_customer_totals():
    """
    Tính tổng chi tiêu từ bảng hóa đơn và cập nhật (nếu bảng khách có cột TongChiTieu).
    Trả về dict {MaKH: total}.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        inv_tbl, amt_col = _find_invoice_table_and_amount_col(cur)
        if not inv_tbl:
            return {}
        cur.execute(f"SELECT MaKH, SUM(COALESCE({amt_col},0)) FROM {inv_tbl} GROUP BY MaKH")
        rows = cur.fetchall()
        totals = {r[0]: float(r[1] or 0) for r in rows}

        # (Phần code còn lại để cập nhật TongChiTieu giữ nguyên)
        cur.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?, ?)",
            ("MaKH", "TongChiTieu")
        )
        rows2 = cur.fetchall()
        cust_tbl = None
        if rows2:
            tbl_map = {}
            for s, t, c in rows2:
                tbl_map.setdefault((s, t), set()).add(c)
            for (s, t), cols in tbl_map.items():
                if "MaKH" in cols and "TongChiTieu" in cols:
                    cust_tbl = f"[{s}].[{t}]"
                    break

        if cust_tbl:
            for makh, tot in totals.items():
                try:
                    cur.execute(f"UPDATE {cust_tbl} SET TongChiTieu = ? WHERE MaKH = ?", (tot, makh))
                except Exception:
                    pass
            conn.commit()
        return totals
    finally:
        conn.close()

def get_monthly_revenue(year):
    """
    Trả về list (month, total) cho năm cung cấp.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        inv_tbl, amt_col = _find_invoice_table_and_amount_col(cur)
        if not inv_tbl:
            print("Debug (Doanh thu): Không tìm thấy bảng hóa đơn (inv_tbl, amt_col).")
            return []
            
        # Tìm cột ngày
        cur.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE COLUMN_NAME IN (?, ?, ?, ?)", # Thêm NgayGD
            ("NgayLap", "NgayHD", "NgayHoaDon", "NgayGD")
        )
        date_rows = cur.fetchall()
        date_col = None
        if date_rows:
            for s, t, c in date_rows:
                if f"[{s}].[{t}]" == inv_tbl:
                    date_col = c
                    break
                    
        if not date_col:
            # Fallback nếu không tìm thấy trong list trên
            schema, tab = inv_tbl.strip("[]").split("].[")
            cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=? AND TABLE_NAME=?", (schema, tab))
            existing = [r[0] for r in cur.fetchall()]
            for cand in ("NgayLap", "NgayHD", "NgayHoaDon", "NgayGD", "CreatedDate"):
                if cand in existing:
                    date_col = cand
                    break
                    
        if not date_col:
            print("Debug (Doanh thu): Không tìm thấy cột ngày (date_col).")
            return []
        sql = (
            f"SELECT MONTH({date_col}) AS M, SUM(COALESCE({amt_col},0)) AS Total "
            f"FROM {inv_tbl} WHERE YEAR({date_col}) = ? "
            f"GROUP BY MONTH({date_col}) ORDER BY M"
        )
        
        cur.execute(sql, (year,))
        rows = cur.fetchall()
        
        # Trả về list of tuples (tháng, tổng)
        return [(int(r[0]), float(r[1] or 0)) for r in rows]
    except Exception as e:
        print(f"Lỗi khi lấy doanh thu: {e}")
        return []
    finally:
        conn.close()