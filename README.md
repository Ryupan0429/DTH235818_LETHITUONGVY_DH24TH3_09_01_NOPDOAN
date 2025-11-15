# Đồ án: Quản lý cửa hàng mua bán thuốc nông dược (Đề tài 09)

## Thông tin
-   **Tên đề tài:** Quản lý cửa hàng mua bán thuốc nông dược
-   **Sinh viên thực hiện:** Lê Thị Tường Vy
-   **MSSV:** DTH235818
-   **Lớp:** DH24TH3
-   **Môn:** Chuyên đề Python, Trường Đại học An Giang

## Mục tiêu
Xây dựng ứng dụng quản lý kho và bán hàng cho cửa hàng thuốc nông dược, sử dụng Python (Tkinter) và SQL Server. Ứng dụng tập trung vào việc quản lý tồn kho (nhập/xuất) và quản lý khách hàng, có giao diện đồ họa (GUI) thân thiện và phân chia chức năng rõ ràng cho Quản trị viên (Admin) và Khách hàng (Customer).

## Tính năng chính

Ứng dụng được chia thành hai phân hệ chính:

### 1. Phân hệ Quản trị viên (Admin)
-   **Quản lý Sản phẩm:** Thêm, Sửa (bao gồm cả Đơn giá), Xóa, Lọc (theo Phân loại, Giá) và Tìm kiếm (Mã/Tên/Công dụng). Hỗ trợ chức năng **thay đổi giá hàng loạt** theo phần trăm (%).
-   **Quản lý Khách hàng:** Thêm, Sửa, Xóa, Lọc (tự động theo Quê quán) và Tìm kiếm (Mã/Tên/SĐT).
-   **Quản lý Phiếu Nhập (Nhập hàng):** Tạo phiếu nhập kho. Khi nhập, số lượng tồn kho và đơn giá bán (Giá bán = Giá nhập \* 1.3, làm tròn) của sản phẩm sẽ được **tự động cập nhật** qua Trigger CSDL.
-   **Quản lý Hóa đơn (Bán hàng):** Tạo hóa đơn bán hàng cho khách (có thể thêm khách hàng mới trực tiếp). Khi bán, số lượng tồn kho của sản phẩm sẽ **tự động bị trừ**.
-   **Báo cáo Doanh thu:** Xem biểu đồ doanh thu và bảng thống kê linh hoạt theo **Ngày**, **Tháng**, hoặc **Năm**.

### 2. Phân hệ Khách hàng (Customer)
-   **Quản lý Hồ sơ:** Xem và tự cập nhật thông tin cá nhân (Họ tên, SĐT, Giới tính, Quê quán) và thay đổi mật khẩu.
-   **Tra cứu sản phẩm:** Xem, lọc, và tìm kiếm danh mục sản phẩm (bao gồm cả tồn kho).
-   **Giỏ hàng & Mua hàng:** Giao diện cho phép khách hàng tự thêm sản phẩm vào giỏ (với tính năng kiểm tra tồn kho) và tiến hành "Đặt hàng" (tự tạo hóa đơn).
-   **Lịch sử giao dịch:** Xem lại danh sách các hóa đơn đã mua và xem chi tiết.

## Công nghệ sử dụng
-   **Ngôn ngữ:** Python 3.x
-   **Giao diện (GUI):** Tkinter (và `ttk`)
-   **Cơ sở dữ liệu:** SQL Server
-   **Thư viện:** `pyodbc` (kết nối CSDL), `tkcalendar` (chọn ngày), `matplotlib` (vẽ biểu đồ), `pandas` & `numpy` (xử lý dữ liệu báo cáo).

## Cấu trúc Cơ sở dữ liệu
Ứng dụng sử dụng CSDL SQL Server (`QuanLyNongDuoc`) với 7 bảng chính:
-   `dbo.SanPhamNongDuoc`: Lưu thông tin sản phẩm, tồn kho và giá bán.
-   `dbo.KhachHang`: Lưu thông tin khách hàng (bao gồm Giới tính, Quê quán) và tổng chi tiêu.
-   `dbo.PhieuNhap`: Lưu thông tin phiếu nhập kho (đầu vào).
-   `dbo.ChiTietPhieuNhap`: Chi tiết các sản phẩm trong phiếu nhập.
-   `dbo.HoaDon`: Lưu thông tin hóa đơn (đầu ra).
-   `dbo.ChiTietHoaDon`: Chi tiết các sản phẩm trong hóa đơn.
-   `dbo.Users`: Lưu tài khoản đăng nhập (Admin và Customer).

Hệ thống sử dụng **Triggers** trong SQL Server để tự động hóa hoàn toàn logic nghiệp vụ:
-   Tự động cập nhật `SoLuong` (tồn kho) và `DonGia` (bán) khi nhập hàng.
-   Tự động cập nhật (trừ) `SoLuong` (tồn kho) khi bán hàng hoặc hoàn kho khi xóa hóa đơn.
-   Tự động cập nhật `TongGT` (Hóa đơn) và `TongChiTieu` (Khách hàng) khi dữ liệu thay đổi.

## Hướng dẫn cài đặt và chạy

### Yêu cầu
1.  Python 3.x và `pip`.
2.  Microsoft SQL Server (ví dụ: bản Express) và SQL Server Management Studio (SSMS).
3.  **Microsoft ODBC Driver 17 for SQL Server**. (Yêu cầu bắt buộc).

### 1. Cài đặt thư viện
Cài đặt các thư viện cần thiết cho ứng dụng:
```bash
pip install pyodbc tkcalendar pandas numpy matplotlib
```
2. Phục hồi Cơ sở dữ liệu (CSDL)
Mở SSMS (SQL Server Management Studio).

Trong thư mục /CSDL của dự án, tìm tệp QuanLyNongDuoc.bak.

Phục hồi (Restore) tệp .bak này để tạo CSDL QuanLyNongDuoc với toàn bộ cấu trúc bảng, triggers và dữ liệu mẫu.

3. Cấu hình ứng dụng
Mở tệp db.py (nằm ở thư mục gốc) và cập nhật chính xác các thông số sau để khớp với SQL Server của bạn:

```Python

SERVER_NAME = r'TUONGVY\SQLEXPRESS' # Tên Server SQL của bạn
DATABASE_NAME = 'QuanLyNongDuoc'
USERNAME = 'sa'
PASSWORD = '' # Mật khẩu của bạn
```
4. Chạy ứng dụng
Chạy ứng dụng bằng cách thực thi tệp login.py.

```Bash

python login.py
```
Tài khoản Admin: admin / 123

Tài khoản Customer: (Ví dụ) KH0001 / 001 (Mật khẩu là 3 số cuối của Mã Khách Hàng).

Liên hệ
Email: vy_dth235818@student.agu.edu.vn