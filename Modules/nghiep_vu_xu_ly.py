from db import get_connection

def _next_mahd(cur):
    try:
        cur.execute("SELECT MaHD FROM dbo.HoaDon WHERE MaHD LIKE 'HD%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("HD"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"HD{nxt:04d}"
    except Exception:
        return None

def _next_sopn(cur):
    try:
        cur.execute("SELECT SoPN FROM dbo.PhieuNhap WHERE SoPN LIKE 'PN%'")
        rows = cur.fetchall()
        nums = []
        for r in rows:
            s = str(r[0])
            if s.upper().startswith("PN"):
                num = ''.join(ch for ch in s[2:] if ch.isdigit())
                if num: nums.append(int(num))
        nxt = (max(nums)+1) if nums else 1
        return f"PN{nxt:04d}"
    except Exception:
        return None

def them_hoa_don(ma_kh, ngay_gd, cart_items, product_cache, total_amount):
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        for masp, sl_mua in cart_items.items():
            cur.execute("SELECT SoLuong FROM dbo.SanPhamNongDuoc WHERE MaSP = ?", (masp,))
            row = cur.fetchone()
            if not row or row.SoLuong < sl_mua:
                raise Exception(f"Sản phẩm {masp} không đủ tồn kho (còn {row.SoLuong if row else 0}).")
        
        ma_hd = _next_mahd(cur)
        if not ma_hd:
            raise Exception("Không thể tạo Mã Hóa đơn.")

        cur.execute(
            "INSERT INTO dbo.HoaDon (MaHD, MaKH, NgayGD, TongGT) VALUES (?, ?, ?, ?)",
            (ma_hd, ma_kh, ngay_gd, total_amount) 
        )

        items_to_insert = []
        for masp, sl_gio in cart_items.items():
            cache = product_cache[masp]
            thanh_tien = cache["DonGia"] * sl_gio
            items_to_insert.append((
                ma_hd, masp, cache["TenSP"], int(sl_gio),
                cache["DVTinh"], cache["DonGia"], thanh_tien
            ))
        
        sql_insert_detail = """
        INSERT INTO dbo.ChiTietHoaDon (MaHD, MaSP, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(sql_insert_detail, items_to_insert)

        for masp, sl_gio in cart_items.items():
            cur.execute(
                "UPDATE dbo.SanPhamNongDuoc SET SoLuong = SoLuong - ? WHERE MaSP = ?",
                (sl_gio, masp)
            )

        cur.execute(
            "UPDATE dbo.KhachHang SET TongChiTieu = COALESCE(TongChiTieu, 0) + ? WHERE MaKH = ?",
            (total_amount, ma_kh)
        )

        conn.commit()
        return ma_hd, None
    
    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def xoa_hoa_don(mahd_list):
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        for mahd in mahd_list:
            cur.execute("SELECT MaKH, TongGT FROM dbo.HoaDon WHERE MaHD = ?", (mahd,))
            hd_row = cur.fetchone()
            if not hd_row:
                continue 

            ma_kh, tong_gt = hd_row.MaKH, hd_row.TongGT

            cur.execute("SELECT MaSP, SoLuong FROM dbo.ChiTietHoaDon WHERE MaHD = ?", (mahd,))
            items_to_restore = cur.fetchall()
            
            cur.execute("DELETE FROM dbo.HoaDon WHERE MaHD = ?", (mahd,))
            
            for item in items_to_restore:
                cur.execute(
                    "UPDATE dbo.SanPhamNongDuoc SET SoLuong = SoLuong + ? WHERE MaSP = ?",
                    (item.SoLuong, item.MaSP)
                )
            
            cur.execute(
                "UPDATE dbo.KhachHang SET TongChiTieu = COALESCE(TongChiTieu, 0) - ? WHERE MaKH = ?",
                (tong_gt, ma_kh)
            )
            
        conn.commit()
        return True, None
    
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def them_phieu_nhap(nguoi_nhap, nguon_nhap, ngay_nhap, cart_items, total_amount, product_cache):
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        so_pn = _next_sopn(cur)
        if not so_pn:
            raise Exception("Không thể tạo Số Phiếu Nhập.")

        cur.execute(
            "INSERT INTO dbo.PhieuNhap (SoPN, NgayNhap, NguoiNhap, NguonNhap, TongGGT) VALUES (?, ?, ?, ?, ?)",
            (so_pn, ngay_nhap, nguoi_nhap, nguon_nhap, total_amount) 
        )

        items_to_insert = []
        for masp, (so_luong, don_gia_nhap) in cart_items.items():
            cache = product_cache[masp]
            thanh_tien = so_luong * don_gia_nhap
            items_to_insert.append((
                so_pn, masp, cache["TenSP"], int(so_luong),
                cache["DVTinh"], don_gia_nhap, thanh_tien
            ))
            
            gia_ban_moi = round((don_gia_nhap * 1.3) / 1000) * 1000
            cur.execute(
                "UPDATE dbo.SanPhamNongDuoc SET SoLuong = SoLuong + ?, DonGia = ? WHERE MaSP = ?",
                (so_luong, gia_ban_moi, masp)
            )
        
        sql_insert_detail = """
        INSERT INTO dbo.ChiTietPhieuNhap (SoPN, MaSP, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(sql_insert_detail, items_to_insert)

        conn.commit()
        return so_pn, None
    
    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

def xoa_phieu_nhap(sopn_list):
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        for sopn in sopn_list:
            cur.execute("SELECT MaSP, SoLuong FROM dbo.ChiTietPhieuNhap WHERE SoPN = ?", (sopn,))
            items_to_remove = cur.fetchall()
            
            if not items_to_remove:
                continue

            cur.execute("DELETE FROM dbo.PhieuNhap WHERE SoPN = ?", (sopn,))
            
            for item in items_to_remove:
                cur.execute(
                    "UPDATE dbo.SanPhamNongDuoc SET SoLuong = SoLuong - ? WHERE MaSP = ?",
                    (item.SoLuong, item.MaSP)
                )
            
        conn.commit()
        return True, None
    
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn:
            conn.autocommit = True
            conn.close()