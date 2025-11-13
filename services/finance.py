# KHÔNG import 'get_connection' ở đây nữa
# from db import get_connection

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
            if "TongGT" in cols:
                return f"[{s}].[{t}]", "TongGT"
            if "TongTien" in cols:
                return f"[{s}].[{t}]", "TongTien"
            if "Total" in cols:
                return f"[{s}].[{t}]", "Total"
                
    return None, None

def update_all_customer_totals():
    """
    Tính tổng chi tiêu từ bảng hóa đơn và cập nhật TongChiTieu VÀ ThuHang.
    Trả về dict {MaKH: total}.
    """
    # Import get_connection bên trong hàm
    from db import get_connection
    conn = get_connection()
    try:
        cur = conn.cursor()
        inv_tbl, amt_col = _find_invoice_table_and_amount_col(cur)
        if not inv_tbl:
            return {}
        cur.execute(f"SELECT MaKH, SUM(COALESCE({amt_col},0)) FROM {inv_tbl} GROUP BY MaKH")
        rows = cur.fetchall()
        totals = {r[0]: float(r[1] or 0) for r in rows}

        cur.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME IN (?, ?, ?)",
            ("MaKH", "TongChiTieu", "ThuHang")
        )
        rows2 = cur.fetchall()
        cust_tbl = None
        if rows2:
            tbl_map = {}
            for s, t, c in rows2:
                tbl_map.setdefault((s, t), set()).add(c)
            for (s, t), cols in tbl_map.items():
                if "MaKH" in cols and "TongChiTieu" in cols and "ThuHang" in cols:
                    cust_tbl = f"[{s}].[{t}]"
                    break

        if cust_tbl:
            for makh, tot in totals.items():
                try:
                    (new_rank, _, _, _) = get_next_rank_info(tot)
                    cur.execute(f"UPDATE {cust_tbl} SET TongChiTieu = ?, ThuHang = ? WHERE MaKH = ?", 
                                (tot, new_rank, makh))
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
    # Import get_connection bên trong hàm
    from db import get_connection
    conn = get_connection()
    try:
        cur = conn.cursor()
        inv_tbl, amt_col = _find_invoice_table_and_amount_col(cur)
        if not inv_tbl:
            print("Debug (Doanh thu): Không tìm thấy bảng hóa đơn (inv_tbl, amt_col).")
            return []
            
        cur.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE COLUMN_NAME IN (?, ?, ?, ?)", 
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
        
        return [(int(r[0]), float(r[1] or 0)) for r in rows]
    except Exception as e:
        print(f"Lỗi khi lấy doanh thu: {e}")
        return []
    finally:
        conn.close()

def get_discount_rate(thu_hang):
    """
    Trả về tỷ lệ giảm giá (ví dụ: 0.05 cho 5%) dựa trên thứ hạng.
    (Hàm này không cần CSDL)
    """
    if thu_hang == 'Kim Cương':
        return 0.10 # 10%
    if thu_hang == 'Bạch Kim':
        return 0.05 # 5%
    if thu_hang == 'Vàng':
        return 0.02 # 2%
    if thu_hang == 'Bạc':
        return 0.01 # 1%
    return 0.0 # Đồng = 0%

def get_next_rank_info(tong_chi_tieu):
    """
    Trả về thông tin tiến trình lên hạng.
    (Hàm này không cần CSDL)
    """
    tct = tong_chi_tieu
    
    RANKS = {
        'Đồng': (0, 'Bạc', 500000),
        'Bạc': (500000, 'Vàng', 5000000),
        'Vàng': (5000000, 'Bạch Kim', 15000000),
        'Bạch Kim': (15000000, 'Kim Cương', 50000000),
        'Kim Cương': (50000000, None, 50000000)
    }
    
    current_rank = 'Kim Cương' 
    for rank, (min_val, next_rank, max_val) in RANKS.items():
        if tct < max_val:
            current_rank = rank
            return (current_rank, next_rank, tct, max_val)
            
    return ('Kim Cương', None, tct, 50000000)