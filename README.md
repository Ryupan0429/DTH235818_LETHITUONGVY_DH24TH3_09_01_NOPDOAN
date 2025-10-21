# Đồ án: Quản lý cửa hàng mua bán thuốc nông dược (Đề tài 09)

## Thông tin
- Tên đề tài: Quản lý cửa hàng mua bán thuốc nông dược  
- Sinh viên thực hiện: Lê Thị Tường Vy  
- MSSV: DTH235818  
- Lớp: DH24TH3  
- Khóa: K24 — Sinh viên năm 3, ngành Công nghệ Thông tin  
- Môn: Chuyên đề Python, Trường Đại học An Giang

## Mục tiêu
Xây dựng ứng dụng quản lý bán hàng cho cửa hàng thuốc nông dược với giao diện đồ họa, quản lý sản phẩm, khách hàng, đơn hàng và báo cáo cơ bản.

## Tính năng chính
- Quản lý danh mục thuốc nông dược (thêm, sửa, xóa, tìm kiếm)  
- Quản lý khách hàng và nhà cung cấp  
- Tạo và quản lý đơn bán hàng, tính tổng tiền và in hóa đơn  
- Quản lý tồn kho, cảnh báo sản phẩm sắp hết hạn hoặc thiếu hàng  
- Báo cáo doanh thu theo ngày/tháng/sản phẩm

## Công nghệ sử dụng
- Giao diện: Tkinter (Python)  
- Cơ sở dữ liệu: MySQL  
- Ngôn ngữ lập trình: Python 3.x  
- Thư viện bổ trợ: mysql-connector-python (hoặc pymysql), Pillow (nếu cần xử lý ảnh)

## Kiến trúc & CSDL
- CSDL MySQL lưu trữ bảng: products, customers, suppliers, orders, order_items, users, inventory_logs  
- Thiết kế đơn giản, dễ mở rộng; các thao tác CRUD qua kết nối MySQL

## Hướng dẫn nhanh
1. Cài Python 3.x và pip.  
2. Cài phụ thuộc:
   - pip install mysql-connector-python
   - pip install Pillow
3. Tạo database trên MySQL và import file cấu trúc (nếu có).  
4. Cấu hình kết nối DB trong file cấu hình (host, user, password, database).  
5. Chạy ứng dụng:
   - python main.py

## Ghi chú
- Đề nghị kiểm tra cấu hình MySQL trước khi chạy.  
- Bản demo có thể được mở rộng với tính năng phân quyền và sao lưu dữ liệu.

## Liên hệ
- Email: vy_dth235818@student.agu.edu.vn
