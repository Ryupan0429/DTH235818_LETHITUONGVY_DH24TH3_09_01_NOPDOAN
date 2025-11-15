# Đồ án: Quản lý cửa hàng mua bán thuốc nông dược (Đề tài 09)

## Thông tin
-   **Tên đề tài:** Quản lý cửa hàng mua bán thuốc nông dược
-   **Sinh viên thực hiện:** Lê Thị Tường Vy
-   **MSSV:** DTH235818
-   **Lớp:** DH24TH3
-   **Môn:** Chuyên đề Python, Trường Đại học An Giang

## Mục tiêu dự án
Xây dựng một ứng dụng Desktop (GUI) bằng Python (Tkinter) và SQL Server để quản lý toàn diện nghiệp vụ tại một cửa hàng nông dược.
Ứng dụng cung cấp các công cụ để quản lý kho hàng, nhập hàng, bán hàng, quản lý đối tác (Khách hàng) và theo dõi tình hình tài chính (Báo cáo Thu Chi) một cách trực quan.

## Hướng dẫn cài đặt và chạy

### Yêu cầu
1.  **Python 3.x** và `pip`.
2.  **Microsoft SQL Server** (ví dụ: bản Express) và SQL Server Management Studio (SSMS).
3.  **Microsoft ODBC Driver 17 for SQL Server** (Bắt buộc).

### 1. Cài đặt thư viện
Mở Terminal (CMD hoặc PowerShell) và chạy lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install pyodbc tkcalendar pandas numpy matplotlib
```
### 2. Phục hồi Cơ sở dữ liệu (CSDL)
Đây là bước quan trọng nhất. Bạn phải khôi phục CSDL từ file backup .bak đi kèm.

1. Mở SSMS (SQL Server Management Studio) và kết nối vào Server của bạn.

2. Trong thư mục /Backup của dự án, tìm tệp có đuôi .bak (Vd: QuanLyNongDuoc.bak.)

3. Trong SSMS, nhấp chuột phải vào thư mục Databases -> Restore Database....

4. Trong cửa sổ mới:

    -Chọn Device và nhấp vào nút ... (ba chấm).

    -Nhấn Add, duyệt đến tệp QuanLyNongDuoc.bak và nhấn OK.

    -Nhấn OK một lần nữa để xác nhận file.

5. Quan trọng: Ở menu bên trái của cửa sổ Restore, chọn mục Options.

6. Đánh dấu vào ô "Close existing connections to destination database". (Việc này để tránh CSDL bị kẹt ở trạng thái "Restoring").

7. Nhấn OK để bắt đầu khôi phục.

### 3. Cấu hình kết nối
Mở tệp db.py (nằm ở thư mục gốc) và cập nhật chính xác các thông số sau để khớp với SQL Server của bạn:

```Python
SERVER_NAME = r'TUONGVY\SQLEXPRESS' # Tên Server SQL của bạn
DATABASE_NAME = 'QuanLyNongDuoc'
USERNAME = 'sa' # User id của bạn
PASSWORD = '' # Mật khẩu của bạn
```
### 4. Chạy ứng dụng
#### Cách 1: Chạy bằng file thực thi (EXE)

Chạy tệp QLCHNongDuoc.exe trong thư mục dist (nếu đã được đóng gói).
Nếu chưa thì dùng sau để đóng gói ứng dụng thành file.exe
```Python

pyinstaller --onefile --windowed --name "QLCHNongDuoc" --paths=. --hidden-import="tkcalendar" --hidden-import="pandas" --hidden-import="numpy" --hidden-import="matplotlib.pyplot" login.py
```
#### Cách 2: Chạy bằng mã nguồn Python
Thực thi tệp login.py từ Terminal:

```Bash

python login.py
```
Tài khoản Admin mặc định: Quanli01 / 123

## Các chức năng của ứng dụng:
1. Quản lý Hóa Đơn (Bán hàng)
- Thêm Hóa Đơn: Giao diện trực quan gồm 2 bảng (Kho hàng và Giỏ hàng). Tự động kiểm tra và trừ tồn kho tạm thời khi thêm vào giỏ. Hỗ trợ thêm khách hàng mới ngay từ giao diện.
- Xóa Hóa Đơn: Hỗ trợ chọn và xóa nhiều hóa đơn cùng lúc. Tồn kho sản phẩm sẽ được tự động hoàn trả (Trigger CSDL).
- Xem Chi Tiết: Nháy đúp vào hóa đơn để xem chi tiết.
- Tìm kiếm & Lọc: Tìm theo Mã HĐ/Mã KH và lọc theo khoảng ngày.

2. Quản lý Phiếu Nhập (Mua hàng)
- Thêm Phiếu Nhập: Giao diện 2 bảng (Sản phẩm và Phiếu nhập). Tự động cập nhật tồn kho tạm thời để theo dõi.
- Xóa Phiếu Nhập: Hỗ trợ chọn và xóa nhiều phiếu nhập. Tồn kho sản phẩm sẽ bị tự động trừ đi (Trigger CSDL).
- Tự động cập nhật: Khi Lưu phiếu nhập, CSDL tự động cộng tồn kho.
- Tính và cập nhật giá bán mới (Giá bán = Giá nhập * 1.3).
- Xem Chi Tiết: Nháy đúp vào phiếu nhập để xem chi tiết.
- Tìm kiếm & Lọc: Tìm theo Số PN/Nguồn nhập và lọc theo khoảng ngày.

3. Quản lý Sản Phẩm
- Thêm/Sửa/Xóa:
+ Thêm: Thêm sản phẩm mới (tồn kho và giá bán mặc định là 0).
+ Sửa: Cho phép sửa thông tin mô tả và Đơn giá bán của sản phẩm.
+ Xóa: Hỗ trợ xóa nhiều sản phẩm (nếu sản phẩm chưa phát sinh giao dịch).
+ Đổi giá hàng loạt: Chọn nhiều sản phẩm và cập nhật giá đồng loạt theo phần trăm (%).
+ Tìm kiếm & Lọc: Tìm kiếm (Mã/Tên/Công dụng), Lọc tự động (Phân loại) và Lọc theo khoảng giá.

4. Quản lý Khách Hàng
- Thêm/Sửa/Xóa: Quản lý thông tin khách hàng (Họ tên, SĐT, Giới tính, Quê quán). Hỗ trợ xóa nhiều.
- Xem Lịch sử Giao dịch: Nháy đúp vào một khách hàng để mở cửa sổ mới hiển thị toàn bộ lịch sử hóa đơn của khách hàng đó.
- Tìm kiếm & Lọc: Tìm kiếm (Mã/Tên/SĐT) và Lọc tự động (Quê quán).

5. Báo cáo Thu Chi
- Thay thế cho báo cáo Doanh thu, hiển thị so sánh:
- Tổng Thu: Tiền bán hàng (từ Hóa Đơn).
Tổng Chi: Tiền nhập hàng (từ Phiếu Nhập).
- Biểu đồ cột: Trực quan hóa Thu/Chi và Lợi nhuận (Lợi nhuận được tô màu xanh/đỏ trong bảng).
- Lọc linh hoạt: Xem báo cáo theo Ngày, Tháng, hoặc Năm.

6. Tính năng chung
- Sao lưu (Backup): Cho phép người dùng lưu một bản sao lưu (.bak) của CSDL ra thư mục /Backup bất cứ lúc nào.
- Giao diện: Hỗ trợ kéo-chọn nhiều dòng trên tất cả các bảng. Hỗ trợ sắp xếp (sort) dữ liệu khi nhấn vào tiêu đề cột.

### Liên hệ
Email: vy_dth235818@student.agu.edu.vn
