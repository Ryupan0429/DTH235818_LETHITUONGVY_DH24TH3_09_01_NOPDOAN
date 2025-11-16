from db import get_connection

def _get_next_id(cur, prefix, table, column):
    # Hàm lấy ID tiếp theo từ CSDL.
    try:
        prefix_len = len(prefix)
        
        sql = f"""
            SELECT ISNULL(MAX(CAST(SUBSTRING({column}, {prefix_len + 1}, 10) AS INT)), 0) + 1
            FROM dbo.{table}
            WHERE {column} LIKE ? AND ISNUMERIC(SUBSTRING({column}, {prefix_len + 1}, 10)) = 1
        """
        
        cur.execute(sql, (f"{prefix}%",))
        next_num = cur.fetchone()[0]
        
        # Tất cả các mã đều dùng 4 chữ số
        return f"{prefix}{next_num:04d}"
             
    except Exception as e:
        print(f"Lỗi tạo ID cho {prefix}: {e}")
        return None

def them_hoa_don(ma_kh, ngay_gd, cart_items, product_cache, total_amount):
    # Xử lý nghiệp vụ thêm Hóa Đơn (Bán hàng)
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
        
        ma_hd = _get_next_id(cur, "HD", "HoaDon", "MaHD")
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
    # Xử lý nghiệp vụ xóa Hóa Đơn (hoàn kho)
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
    # Xử lý nghiệp vụ thêm Phiếu Nhập (cộng kho, cập nhật giá bán)
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        so_pn = _get_next_id(cur, "PN", "PhieuNhap", "SoPN")
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
    # Xử lý nghiệp vụ xóa Phiếu Nhập (trừ kho)
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

def luu_san_pham(masp, data):
    # Xử lý nghiệp vụ Thêm hoặc Sửa Sản phẩm
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if masp: 
            # Trường hợp Cập nhật (Sửa)
            cur.execute("SELECT MaSP FROM dbo.SanPhamNongDuoc WHERE TenSP = ? AND MaSP != ?", (data["TenSP"], masp))
            if cur.fetchone():
                return None, "Tên sản phẩm này đã tồn tại."
            
            cur.execute("""
                UPDATE dbo.SanPhamNongDuoc
                SET TenSP = ?, PhanLoai = ?, CongDung = ?, DVTinh = ?, DonGia = ?
                WHERE MaSP = ?
            """, (data["TenSP"], data["PhanLoai"], data["CongDung"], data["DVTinh"], data["DonGia"], masp))
            
            conn.commit()
            return masp, None
        
        else: 
            # Trường hợp Thêm mới
            cur.execute("SELECT MaSP FROM dbo.SanPhamNongDuoc WHERE TenSP = ?", (data["TenSP"],))
            if cur.fetchone():
                return None, "Tên sản phẩm này đã tồn tại."

            ma_sp_val = _get_next_id(cur, "SP", "SanPhamNongDuoc", "MaSP")
            if not ma_sp_val:
                return None, "Không thể tạo Mã Sản Phẩm tự động."

            # Lấy Số lượng và Đơn giá từ 'data' thay vì gán 0
            so_luong_moi = data.get("SoLuong", 0)
            don_gia_moi = data.get("DonGia", 0)

            cur.execute("""
                INSERT INTO dbo.SanPhamNongDuoc 
                (MaSP, TenSP, PhanLoai, CongDung, DVTinh, SoLuong, DonGia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ma_sp_val, data["TenSP"], data["PhanLoai"], data["CongDung"], data["DVTinh"], so_luong_moi, don_gia_moi))
            
            conn.commit()
            return ma_sp_val, None

    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.close()

def xoa_san_pham(masp_list):
    # Xử lý nghiệp vụ xóa Sản phẩm
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ", ".join("?" for _ in masp_list)
        cur.execute(f"DELETE FROM dbo.SanPhamNongDuoc WHERE MaSP IN ({placeholders})", masp_list)
        conn.commit()
        return True, None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn:
            conn.close()

def cap_nhat_gia_hang_loat(masp_list, multiplier):
    # Xử lý nghiệp vụ thay đổi giá bán hàng loạt
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ", ".join("?" for _ in masp_list)
        
        sql = f"""
        UPDATE dbo.SanPhamNongDuoc
        SET DonGia = ROUND((COALESCE(DonGia, 0) * ?) / 1000, 0) * 1000
        WHERE MaSP IN ({placeholders})
        """
        params = [multiplier] + masp_list
        
        cur.execute(sql, params)
        conn.commit()
        return True, None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn:
            conn.close()

def luu_khach_hang(makh, data):
    # Xử lý nghiệp vụ Thêm hoặc Sửa Khách hàng
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        if makh: 
            # Trường hợp Cập nhật (Sửa)
            cur.execute("SELECT MaKH FROM dbo.KhachHang WHERE SDT = ? AND MaKH != ?", (data["SDT"], makh))
            if cur.fetchone():
                return None, "Số điện thoại này đã được đăng ký."
            
            cur.execute(
                "UPDATE dbo.KhachHang SET TenKH = ?, SDT = ?, GioiTinh = ?, QueQuan = ? WHERE MaKH = ?",
                (data["TenKH"], data["SDT"], data["GioiTinh"], data["QueQuan"], makh)
            )
            conn.commit()
            return makh, None
        
        else: 
            # Trường hợp Thêm mới
            cur.execute("SELECT MaKH FROM dbo.KhachHang WHERE SDT = ?", (data["SDT"],))
            if cur.fetchone():
                return None, "Số điện thoại này đã được đăng ký."

            makh_val = _get_next_id(cur, "KH", "KhachHang", "MaKH")
            if not makh_val:
                return None, "Không thể tạo Mã Khách hàng"
            
            cur.execute(
                "INSERT INTO dbo.KhachHang (MaKH, TenKH, SDT, GioiTinh, QueQuan) VALUES (?, ?, ?, ?, ?)",
                (makh_val, data["TenKH"], data["SDT"], data["GioiTinh"], data["QueQuan"])
            )
            conn.commit()
            return makh_val, None

    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.close()

def xoa_khach_hang(makh_list):
    # Xử lý nghiệp vụ xóa Khách hàng (và các Hóa đơn liên quan)
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()
        
        makh_placeholders = ", ".join("?" for _ in makh_list)
        
        cur.execute(f"DELETE FROM dbo.HoaDon WHERE MaKH IN ({makh_placeholders})", makh_list)
        cur.execute(f"DELETE FROM dbo.KhachHang WHERE MaKH IN ({makh_placeholders})", makh_list)
        
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