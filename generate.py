import pandas as pd
import pyodbc
from datetime import datetime

# =====================================================
# CẤU HÌNH KẾT NỐI
# =====================================================
SERVER_NAME = r'TUONGVY\SQLEXPRESS'
DATABASE_NAME = 'QuanLyNongDuoc'
USERNAME = 'sa'
PASSWORD = ''
EXCEL_FILE = r'DuLieu_NongDuoc.xlsx'


# =====================================================
# HÀM KẾT NỐI SQL SERVER
# =====================================================
def ket_noi_sql(server, db=None):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"{'DATABASE=' + db + ';' if db else ''}"
        f"UID={USERNAME};PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, autocommit=True)


# =====================================================
# HÀM TẠO DATABASE VÀ CÁC BẢNG
# =====================================================
def tao_database_va_bang():
    print("🔧 Tạo database và cấu trúc bảng...")

    conn = ket_noi_sql(SERVER_NAME, "master")
    cursor = conn.cursor()
    cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DATABASE_NAME}')
        CREATE DATABASE {DATABASE_NAME};
    """)
    conn.close()

    conn = ket_noi_sql(SERVER_NAME, DATABASE_NAME)
    cursor = conn.cursor()

    # Xóa các bảng cũ
    cursor.execute("""
    IF OBJECT_ID('dbo.ChiTietHoaDon', 'U') IS NOT NULL DROP TABLE dbo.ChiTietHoaDon;
    IF OBJECT_ID('dbo.HoaDonNongDuoc', 'U') IS NOT NULL DROP TABLE dbo.HoaDonNongDuoc;
    IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
    IF OBJECT_ID('dbo.ThongTinKhachHang', 'U') IS NOT NULL DROP TABLE dbo.ThongTinKhachHang;
    IF OBJECT_ID('dbo.ThuocNongDuoc', 'U') IS NOT NULL DROP TABLE dbo.ThuocNongDuoc;
    """)
    conn.commit()
    
    # Tạo các bảng
    cursor.execute("""
    CREATE TABLE dbo.ThuocNongDuoc (
        STT INT IDENTITY(1,1),
        MaThuoc VARCHAR(10) PRIMARY KEY,
        TenThuoc NVARCHAR(100) NOT NULL,
        PhanLoai NVARCHAR(50),
        NhomDuocLy NVARCHAR(100),
        CongDung NVARCHAR(200),
        ChiDinh NVARCHAR(100),
        ThanhPhan NVARCHAR(200),
        LieuLuong NVARCHAR(50),
        DonGia DECIMAL(18,0) CHECK (DonGia > 0),
        DVTinh NVARCHAR(20) DEFAULT N'chai'
    );

    CREATE TABLE dbo.ThongTinKhachHang (
        STT INT IDENTITY(1,1),
        MaKH VARCHAR(10) PRIMARY KEY,
        HoTenKH NVARCHAR(100) NOT NULL,
        SDT VARCHAR(15) UNIQUE NOT NULL,
        DiaChi NVARCHAR(100),
        ThuHang NVARCHAR(20) DEFAULT N'Đồng' CHECK (ThuHang IN (N'Đồng', N'Bạc', N'Vàng', N'Bạch Kim', N'Kim Cương')),
        CHECK (LEN(SDT) = 10),
        TongChiTieu DECIMAL(18,0) NOT NULL DEFAULT 0 CHECK (TongChiTieu >= 0)
    );

    CREATE TABLE dbo.HoaDonNongDuoc (
        STT INT IDENTITY(1,1),
        MaHD VARCHAR(10) PRIMARY KEY,
        MaKH VARCHAR(10) NOT NULL,
        NgayGD DATE NOT NULL CHECK (NgayGD <= GETDATE()),
        TongGT DECIMAL(18,0) NOT NULL DEFAULT 0 CHECK (TongGT >= 0),
        FOREIGN KEY (MaKH) REFERENCES dbo.ThongTinKhachHang(MaKH)
            ON UPDATE CASCADE ON DELETE NO ACTION
    );

    CREATE TABLE dbo.ChiTietHoaDon (
        STT INT IDENTITY(1,1) PRIMARY KEY,
        MaHD VARCHAR(10) NOT NULL,
        MaThuoc VARCHAR(10) NOT NULL,
        TenSP NVARCHAR(100) NOT NULL,
        SoLuong INT CHECK (SoLuong > 0 AND SoLuong <= 1000),
        DVTinh NVARCHAR(20),
        DonGia DECIMAL(18,0) CHECK (DonGia > 0),
        ThanhTien DECIMAL(18,0) CHECK (ThanhTien > 0),
        FOREIGN KEY (MaHD) REFERENCES dbo.HoaDonNongDuoc(MaHD)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (MaThuoc) REFERENCES dbo.ThuocNongDuoc(MaThuoc)
            ON UPDATE CASCADE ON DELETE NO ACTION
    );
    
    CREATE TABLE dbo.Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        Username VARCHAR(50) NOT NULL UNIQUE,
        Password VARCHAR(50) NOT NULL,
        Role VARCHAR(20) NOT NULL CHECK (Role IN ('Admin', 'Manager', 'Customer'))
    );
    """)
    conn.commit()

    # --- TẠO TRIGGERS ---
    cursor = conn.cursor()

    cursor.execute("IF OBJECT_ID('dbo.trg_RecalcTongGT_ChiTiet','TR') IS NOT NULL DROP TRIGGER dbo.trg_RecalcTongGT_ChiTiet;")
    cursor.execute("""
    CREATE TRIGGER dbo.trg_RecalcTongGT_ChiTiet
    ON dbo.ChiTietHoaDon
    AFTER INSERT, UPDATE, DELETE
    AS
    BEGIN
        SET NOCOUNT ON;
        DECLARE @t TABLE (MaHD VARCHAR(10));
        INSERT INTO @t (MaHD)
        SELECT MaHD FROM inserted WHERE MaHD IS NOT NULL
        UNION
        SELECT MaHD FROM deleted WHERE MaHD IS NOT NULL;

        UPDATE H
        SET TongGT = ISNULL(S.Total, 0)
        FROM dbo.HoaDonNongDuoc H
        LEFT JOIN (
            SELECT MaHD, SUM(ISNULL(ThanhTien,0)) AS Total
            FROM dbo.ChiTietHoaDon
            WHERE MaHD IN (SELECT MaHD FROM @t)
            GROUP BY MaHD
        ) S ON H.MaHD = S.MaHD
        WHERE H.MaHD IN (SELECT MaHD FROM @t);

        UPDATE dbo.HoaDonNongDuoc
        SET TongGT = 0
        WHERE MaHD IN (SELECT MaHD FROM @t)
          AND MaHD NOT IN (SELECT MaHD FROM dbo.ChiTietHoaDon WHERE MaHD IN (SELECT MaHD FROM @t));
    END;
    """)

    cursor.execute("IF OBJECT_ID('dbo.trg_UpdateTongChiTieu_HoaDon','TR') IS NOT NULL DROP TRIGGER dbo.trg_UpdateTongChiTieu_HoaDon;")
    cursor.execute("""
    CREATE TRIGGER dbo.trg_UpdateTongChiTieu_HoaDon
    ON dbo.HoaDonNongDuoc
    AFTER INSERT, UPDATE, DELETE
    AS
    BEGIN
        SET NOCOUNT ON;
        WITH Affected AS (
            SELECT MaKH FROM inserted WHERE MaKH IS NOT NULL
            UNION
            SELECT MaKH FROM deleted WHERE MaKH IS NOT NULL
        )
        UPDATE T
        SET TongChiTieu = ISNULL(S.Total, 0)
        FROM dbo.ThongTinKhachHang T
        JOIN Affected a ON T.MaKH = a.MaKH
        LEFT JOIN (
            SELECT MaKH, SUM(ISNULL(TongGT,0)) AS Total
            FROM dbo.HoaDonNongDuoc
            WHERE MaKH IN (SELECT MaKH FROM Affected)
            GROUP BY MaKH
        ) S ON T.MaKH = S.MaKH;
    END;
    """)

    cursor.execute("IF OBJECT_ID('dbo.trg_SetThuHang_FromTongChi','TR') IS NOT NULL DROP TRIGGER dbo.trg_SetThuHang_FromTongChi;")
    cursor.execute("""
    CREATE TRIGGER dbo.trg_SetThuHang_FromTongChi
    ON dbo.ThongTinKhachHang
    AFTER INSERT, UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        -- Chỉ cập nhật nếu TongChiTieu thực sự thay đổi
        IF UPDATE(TongChiTieu)
        BEGIN
            UPDATE T
            SET ThuHang = CASE
                WHEN ISNULL(I.TongChiTieu,0) >= 50000000 THEN N'Kim Cương'
                WHEN ISNULL(I.TongChiTieu,0) >= 15000000 THEN N'Bạch Kim'
                WHEN ISNULL(I.TongChiTieu,0) >= 5000000 THEN N'Vàng'
                WHEN ISNULL(I.TongChiTieu,0) >= 500000 THEN N'Bạc'
                ELSE N'Đồng' END
            FROM dbo.ThongTinKhachHang T
            INNER JOIN inserted I ON T.MaKH = I.MaKH;
        END;
    END;
    """)
    
    cursor.execute("IF OBJECT_ID('dbo.trg_SetDVTinh_FromLieuLuong','TR') IS NOT NULL DROP TRIGGER dbo.trg_SetDVTinh_FromLieuLuong;")
    cursor.execute("""
    CREATE TRIGGER dbo.trg_SetDVTinh_FromLieuLuong
    ON dbo.ThuocNongDuoc
    AFTER INSERT, UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        IF UPDATE(LieuLuong)
        BEGIN
            UPDATE T
            SET DVTinh = CASE
                WHEN I.LieuLuong LIKE N'%L/ha' THEN N'chai'
                WHEN I.LieuLuong LIKE N'%g/ha' THEN N'hộp'
                WHEN I.LieuLuong LIKE N'%kg/ha' THEN N'bao'
                WHEN I.LieuLuong LIKE N'%/1L nước' THEN N'lít'
                ELSE ISNULL(T.DVTinh, N'chai') 
            END
            FROM dbo.ThuocNongDuoc T
            INNER JOIN inserted I ON T.MaThuoc = I.MaThuoc;
        END;
    END;
    """)

    conn.commit()
    conn.close()
    print("✅ Đã tạo database và các bảng thành công!")

def import_du_lieu():
    print("\n📥 Import dữ liệu từ Excel...")
    conn = ket_noi_sql(SERVER_NAME, DATABASE_NAME)
    cursor = conn.cursor()

    df_thuoc = pd.read_excel(EXCEL_FILE, sheet_name='Thuốc nông dược')
    df_kh = pd.read_excel(EXCEL_FILE, sheet_name='Thông tin khách hàng')
    df_hd = pd.read_excel(EXCEL_FILE, sheet_name='Hóa đơn nông dược')
    df_ct = pd.read_excel(EXCEL_FILE, sheet_name='Chi tiết hóa đơn')

    # --- Import Thuốc ---
    for _, row in df_thuoc.iterrows():
        cursor.execute("""
        INSERT INTO dbo.ThuocNongDuoc (MaThuoc, TenThuoc, PhanLoai, NhomDuocLy, CongDung, ChiDinh, ThanhPhan, LieuLuong, DonGia, DVTinh)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        row['MaThuoc'], row['TenThuoc'], row['PhanLoai'], row['NhomDuocLy'], row['CongDung'],
        row['ChiDinh'], row['ThanhPhan'], row['LieuLuong'], int(row['DonGia']),
        row['DVTinh'])
    print(f"✓ Đã import {len(df_thuoc)} thuốc.")

    # --- Import Khách hàng ---
    for _, row in df_kh.iterrows():
        tong_chi_tieu = 0
        try:
            tong_chi_tieu = int(row.get('TongChiTieu', 0)) if not pd.isna(row.get('TongChiTieu', 0)) else 0
        except Exception:
            pass
            
        cursor.execute("""
        INSERT INTO dbo.ThongTinKhachHang (MaKH, HoTenKH, SDT, DiaChi, ThuHang, TongChiTieu)
        VALUES (?, ?, ?, ?, ?, ?)""",
        row['MaKH'], row['HoTenKH'], str(row['SDT']).zfill(10), row['DiaChi'], row['ThuHang'], tong_chi_tieu)
    print(f"✓ Đã import {len(df_kh)} khách hàng.")

    # --- Import Hóa đơn ---
    for _, row in df_hd.iterrows():
        ngay = row['NgayGD']
        if isinstance(ngay, str):
            try:
                ngay = datetime.strptime(ngay, '%d/%m/%Y').date()
            except ValueError:
                ngay = datetime.now().date()
        elif isinstance(ngay, pd.Timestamp):
            ngay = ngay.date()
        
        cursor.execute("""
        INSERT INTO dbo.HoaDonNongDuoc (MaHD, MaKH, NgayGD, TongGT)
        VALUES (?, ?, ?, ?)""",
        row['MaHD'], row['MaKH'], ngay, int(row['TongGT']))
    print(f"✓ Đã import {len(df_hd)} hóa đơn.")

    # --- Import Chi tiết hóa đơn ---
    for _, row in df_ct.iterrows():
        cursor.execute("""
        INSERT INTO dbo.ChiTietHoaDon (MaHD, MaThuoc, TenSP, SoLuong, DVTinh, DonGia, ThanhTien)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        row['MaHD'], row['MaThuoc'], row['TenSP'], int(row['SoLuong']),
        row['DVTinh'], int(row['DonGia']), int(row['ThanhTien']))
    print(f"✓ Đã import {len(df_ct)} chi tiết hóa đơn.")

    # --- Cập nhật TCT ---
    cursor.execute("""
    UPDATE T
    SET TongChiTieu = ISNULL(S.Total, 0)
    FROM dbo.ThongTinKhachHang T
    LEFT JOIN (
        SELECT MaKH, SUM(COALESCE(TongGT, 0)) AS Total
        FROM dbo.HoaDonNongDuoc
        GROUP BY MaKH
    ) S ON T.MaKH = S.MaKH;
    """)
    
    # --- Thêm User (Admin + Khách hàng) ---
    try:
        cursor.execute("INSERT INTO dbo.Users (Username, Password, Role) VALUES (?, ?, ?)", ('admin', '123', 'Admin'))
    except Exception:
        pass
        
    for _, row in df_kh.iterrows():
        try:
            makh = row['MaKH']
            password = makh[-3:] 
            cursor.execute("INSERT INTO dbo.Users (Username, Password, Role) VALUES (?, ?, ?)", (makh, password, "Customer"))
        except Exception:
            pass
    print(f"✓ Đã tạo tài khoản Users.")

    conn.commit()
    conn.close()
    print("\n✅ IMPORT DỮ LIỆU HOÀN TẤT!")

def kiem_tra_du_lieu():
    conn = ket_noi_sql(SERVER_NAME, DATABASE_NAME)
    cursor = conn.cursor()

    print("\n📊 Kiểm tra dữ liệu sau khi import:")
    for table in ["ThuocNongDuoc", "ThongTinKhachHang", "HoaDonNongDuoc", "ChiTietHoaDon", "Users"]:
        cursor.execute(f"SELECT COUNT(*) FROM dbo.{table}")
        count = cursor.fetchone()[0]
        print(f"  {table:<25}: {count} bản ghi")

    cursor.execute("SELECT TOP 5 MaKH, HoTenKH, TongChiTieu, ThuHang FROM dbo.ThongTinKhachHang ORDER BY TongChiTieu DESC")
    rows = cursor.fetchall()
    print("\n  Top 5 khách hàng theo Tổng Chi Tiêu:")
    for r in rows:
        print(f"    {r.MaKH} - {r.HoTenKH} ({r.ThuHang}): {r.TongChiTieu:,}")

    conn.close()

if __name__ == "__main__":
    print("========================================")
    print("🔥 IMPORT TỰ ĐỘNG DỮ LIỆU NÔNG DƯỢC")
    print("========================================")

    tao_database_va_bang()
    import_du_lieu()
    kiem_tra_du_lieu()

    print("\n🎉 Hoàn tất toàn bộ quá trình!")