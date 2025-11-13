# Đồ án: Quản lý cửa hàng mua bán thuốc nông dược (Đề tài 09)

## Thông tin
-   **Tên đề tài:** Quản lý cửa hàng mua bán thuốc nông dược
-   **Sinh viên thực hiện:** Lê Thị Tường Vy
-   **MSSV:** DTH235818
-   **Lớp:** DH24TH3
-   **Môn:** Chuyên đề Python, Trường Đại học An Giang

## Mục tiêu
Xây dựng ứng dụng quản lý bán hàng cho cửa hàng thuốc nông dược, sử dụng Python và cơ sở dữ liệu SQL Server. Ứng dụng có giao diện đồ họa (GUI) thân thiện, phân chia chức năng rõ ràng cho Quản trị viên (Admin) và Khách hàng (Customer).

## Tính năng chính

Ứng dụng được chia thành hai phân hệ chính với các chức năng riêng biệt:

### 1. Phân hệ Quản trị viên (Admin)
-   **Quản lý Thuốc:** Toàn quyền Thêm, Sửa, Xóa, Lọc và Tìm kiếm (trên mọi trường) sản phẩm thuốc nông dược.
-   **Quản lý Khách hàng:** Toàn quyền Thêm, Sửa, Xóa khách hàng. Tích hợp chức năng tính toán và cập nhật lại `TongChiTieu` (Tổng chi tiêu) và `ThuHang` (Hạng) cho toàn bộ khách hàng chỉ bằng một nút bấm.
-   **Quản lý Hóa đơn:** Tạo hóa đơn mới cho khách (với chức năng tìm kiếm khách hàng động), xem, lọc, và xóa hóa đơn.
-   **Báo cáo Doanh thu:** Xem biểu đồ doanh thu theo tháng/năm.

### 2. Phân hệ Khách hàng (Customer)
-   **Quản lý Hồ sơ:** Xem thông tin cá nhân, hạng thành viên (Đồng, Bạc, Vàng, Bạch Kim, Kim Cương) và tiến trình lên hạng. Hạng và tiến trình được tự động tính toán và cập nhật vào CSDL khi xem.
-   **Cập nhật thông tin:** Khách hàng có thể tự sửa đổi thông tin cá nhân (Họ tên, SĐT, Địa chỉ) và thay đổi mật khẩu.
-   **Tra cứu thuốc:** Xem, lọc, và tìm kiếm danh mục thuốc (trên mọi trường). Hỗ trợ nháy đúp để mở cửa sổ thêm thuốc vào giỏ hàng.
-   **Giỏ hàng & Mua hàng:** Giao diện cho phép khách hàng tự thêm sản phẩm vào giỏ (với ô tìm kiếm riêng) và tiến hành "Đặt hàng" (tạo hóa đơn).
-   **Lịch sử giao dịch:** Xem lại danh sách các hóa đơn đã mua và xem chi tiết từng hóa đơn.

## Công nghệ sử dụng

### 1. Ứng dụng chính
-   **Ngôn ngữ:** Python 3.x
-   **Giao diện (GUI):** Tkinter (và `ttk`)
-   **Cơ sở dữ liệu:** SQL Server
-   **Thư viện:** `pyodbc` (kết nối CSDL), `tkcalendar` (chọn ngày)

### 2. Script tạo dữ liệu
-   **Thư viện:** `pandas` và `openpyxl` (để tạo và đọc file Excel)
-   **Thư viện:** `pyodbc` (để ghi dữ liệu vào SQL Server)

## Cấu trúc Cơ sở dữ liệu
Ứng dụng sử dụng CSDL SQL Server (`QuanLyNongDuoc`) với 5 bảng chính:
-   `dbo.ThuocNongDuoc`: Lưu thông tin các sản phẩm thuốc.
-   `dbo.ThongTinKhachHang`: Lưu thông tin khách hàng, tổng chi tiêu và thứ hạng.
-   `dbo.HoaDonNongDuoc`: Lưu thông tin hóa đơn (mã KH, ngày, tổng tiền).
-   `dbo.ChiTietHoaDon`: Lưu các sản phẩm trong một hóa đơn.
-   `dbo.Users`: Lưu tài khoản đăng nhập (Admin và Customer).

Hệ thống sử dụng Triggers trong SQL Server để tự động cập nhật `TongGT` khi `ChiTietHoaDon` thay đổi, và tự động cập nhật `TongChiTieu` và `ThuHang` khi `HoaDonNongDuoc` thay đổi. Logic xếp hạng (500K, 5M, 15M, 50M) được đồng bộ giữa Trigger và logic ứng dụng.

## Hướng dẫn cài đặt và chạy

### Yêu cầu
1.  Python 3.x và `pip`.
2.  Microsoft SQL Server (ví dụ: bản Express).
3.  **Microsoft ODBC Driver 17 for SQL Server**. (Đây là yêu cầu bắt buộc, được chỉ định trong tệp `generate.py`).

### 1. Cài đặt thư viện
Cài đặt các thư viện cần thiết cho ứng dụng:
```bash
pip install pyodbc tkcalendar
```
Cài đặt các thư viện cần thiết để tạo dữ liệu (chỉ chạy một lần):
```bash
pip install pandas openpyxl
```
2. Tạo và Import dữ liệu
Đây là bước quan trọng để ứng dụng có dữ liệu mẫu.

Tạo file Excel: Chạy tệp taofile.py để tạo file DuLieu_NongDuoc.xlsx.

```bash
python taofile.py
```
Cấu hình SQL Server: Mở tệp generate.py và chỉnh sửa các thông số sau cho đúng với máy của bạn:

```python
SERVER_NAME = r'TUONGVY\SQLEXPRESS' # Tên Server SQL của bạn
DATABASE_NAME = 'QuanLyNongDuoc'
USERNAME = 'sa'
PASSWORD = '' # Mật khẩu của bạn
```
Tạo CSDL và Import: Chạy tệp generate.py. Script này sẽ tự động tạo CSDL, tạo Bảng, tạo Trigger, và import dữ liệu từ file Excel đã tạo ở bước 1.

```bash
python generate.py
```
3. Cấu hình ứng dụng
Tạo tệp db.py trong thư mục gốc của dự án (nếu chưa có) và đảm bảo thông tin đăng nhập trong hàm get_connection() khớp với thông tin bạn đã cấu hình trong generate.py.

Nội dung bắt buộc của tệp db.py:

```Python

import pyodbc

def get_connection():
    SERVER_NAME = r'TUONGVY\SQLEXPRESS' # Phải giống hệt file generate.py
    DATABASE_NAME = 'QuanLyNongDuoc'
    USERNAME = 'sa'
    PASSWORD = '' # Mật khẩu của bạn

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};" # Phải là Driver 17
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        f"UID={USERNAME};PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)
```
4. Chạy ứng dụng
Chạy ứng dụng bằng cách thực thi tệp login.py.
```bash
python login.py
Tài khoản Admin: admin / 123
Tài khoản Customer: (Ví dụ) KH0001 / 001 (Mật khẩu là 3 số cuối của MaKH)
```
## Liên hệ
Email: vy_dth235818@student.agu.edu.vn