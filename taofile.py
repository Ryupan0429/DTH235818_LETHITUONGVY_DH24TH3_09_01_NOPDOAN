import pandas as pd
import random
from datetime import datetime, timedelta

# --- CƠ SỞ DỮ LIỆU MẪU CHUẨN VIỆT NAM ---
HO_VN = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Võ', 'Phan', 'Trương', 'Bùi', 'Đặng', 'Đỗ', 'Ngô', 'Hồ', 'Dương']
TEN_DEM_NAM = ['Văn', 'Hữu', 'Đức', 'Minh', 'Quốc', 'Tuấn', 'Công', 'Duy']
TEN_DEM_NU = ['Thị', 'Ngọc', 'Mỹ', 'Kim', 'Bảo', 'Thuỳ', 'Phương', 'Khánh']
TEN_NAM = ['An', 'Bình', 'Cường', 'Dũng', 'Hải', 'Hiếu', 'Hùng', 'Huy', 'Khánh', 'Lâm', 'Long', 'Nam', 'Sơn', 'Thành', 'Tuấn', 'Việt']
TEN_NU = ['Anh', 'Châu', 'Dung', 'Giang', 'Hà', 'Hương', 'Lan', 'Linh', 'Mai', 'Nga', 'Oanh', 'Phương', 'Quỳnh', 'Thảo', 'Trang', 'Yến']

TINH_THANH_VN = [
    'An Giang', 'Bà Rịa - Vũng Tàu', 'Bạc Liêu', 'Bắc Giang', 'Bắc Ninh', 'Bình Dương', 'Bình Định', 'Bình Phước',
    'Bình Thuận', 'Cà Mau', 'Cần Thơ', 'Đà Nẵng', 'Đồng Nai', 'Đồng Tháp', 'Hà Nội', 'Hải Phòng', 'Hậu Giang',
    'Khánh Hòa', 'Kiên Giang', 'Long An', 'Nghệ An', 'Quảng Nam', 'Quảng Ngãi', 'Sóc Trăng', 'Tây Ninh', 'Tiền Giang',
    'TP. Hồ Chí Minh', 'Trà Vinh', 'Vĩnh Long'
]

# --- DANH SÁCH 50 THUỐC MẪU (ĐÃ BỔ SUNG DỮ LIỆU) ---
BASE_THUOC = [
    # Nhóm 1: Trừ bệnh (5)
    {'TenThuoc': 'Amistar Top 325SC', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Strobilurin + Triazole', 'CongDung': 'Trừ lem lép hạt, khô vằn, thán thư', 'ChiDinh': 'Lúa, Cà phê, Cây ăn trái', 'ThanhPhan': 'Azoxystrobin 200g/L + Difenoconazole 125g/L', 'DonGia_Min': 110000, 'DonGia_Max': 150000, 'DVTinh': 'Lít', 'LieuLuong': '0.3 - 0.35 L/ha'},
    {'TenThuoc': 'Antracol 70WP', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Tiếp xúc', 'CongDung': 'Bổ sung kẽm, áo giáp kẽm', 'ChiDinh': 'Phòng trừ nấm bệnh phổ rộng', 'ThanhPhan': 'Propineb 700g/kg', 'DonGIA_Min': 200000, 'DonGia_Max': 250000, 'DVTinh': 'kg', 'LieuLuong': '1.5 - 2.0 kg/ha'},
    {'TenThuoc': 'Nativo 750WG', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Tổng hợp', 'CongDung': 'Trị đốm vằn, lem lép hạt', 'ChiDinh': 'Lúa, Ngô', 'ThanhPhan': 'Tebuconazole 500g/kg + Trifloxystrobin 250g/kg', 'DonGia_Min': 40000, 'DonGia_Max': 60000, 'DVTinh': 'gói 10g', 'LieuLuong': '60 - 80 g/ha'},
    {'TenThuoc': 'Ridomil Gold 68WP', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Nội hấp', 'CongDung': 'Trị sương mai, thối rễ', 'ChiDinh': 'Cà chua, Khoai tây, Tiêu', 'ThanhPhan': 'Mancozeb 640g/kg + Metalaxyl-M 40g/kg', 'DonGia_Min': 70000, 'DonGia_Max': 90000, 'DVTinh': 'gói 100g', 'LieuLuong': '2.5 kg/ha'},
    {'TenThuoc': 'Score 250EC', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Triazole', 'CongDung': 'Trị thán thư, đốm lá', 'ChiDinh': 'Cây ăn trái, Rau màu', 'ThanhPhan': 'Difenoconazole 250g/L', 'DonGia_Min': 130000, 'DonGia_Max': 180000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.25 L/ha'},
    # Nhóm 2: Trừ sâu (10)
    {'TenThuoc': 'Virtako 40WG', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Tổng hợp', 'CongDung': 'Trừ sâu đục thân, sâu cuốn lá', 'ChiDinh': 'Lúa', 'ThanhPhan': 'Chlorantraniliprole 200g/kg + Thiamethoxam 200g/kg', 'DonGia_Min': 25000, 'DonGia_Max': 35000, 'DVTinh': 'gói 3g', 'LieuLuong': '50 - 60 g/ha'},
    {'TenThuoc': 'Regent 800WG', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Phenylpyrazole', 'CongDung': 'Trừ bọ trĩ, rầy nâu', 'ChiDinh': 'Lúa, Điều, Mía', 'ThanhPhan': 'Fipronil 800g/kg', 'DonGia_Min': 15000, 'DonGia_Max': 22000, 'DVTinh': 'gói 1.6g', 'LieuLuong': '25 - 30 g/ha'},
    {'TenThuoc': 'Confidor 100SL', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Neonicotinoid', 'CongDung': 'Trừ rầy xanh, bọ trĩ, rệp sáp', 'ChiDinh': 'Bông vải, Lúa, Cà phê', 'ThanhPhan': 'Imidacloprid 100g/L', 'DonGia_Min': 90000, 'DonGia_Max': 120000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Movento 150OD', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Lưu dẫn 2 chiều', 'CongDung': 'Trừ rệp sáp, bọ phấn', 'ChiDinh': 'Cây có múi, Tiêu', 'ThanhPhan': 'Spirotetramat 150g/L', 'DonGia_Min': 150000, 'DonGia_Max': 200000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.4 L/ha'},
    {'TenThuoc': 'Actara 25WG', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Neonicotinoid', 'CongDung': 'Trừ rầy nâu, bọ trĩ', 'ChiDinh': 'Lúa', 'ThanhPhan': 'Thiamethoxam 250g/kg', 'DonGia_Min': 18000, 'DonGia_Max': 25000, 'DVTinh': 'gói 1.2g', 'LieuLuong': '20 - 30 g/ha'},
    {'TenThuoc': 'Proclaim 1.9EC', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Avermectin', 'CongDung': 'Trừ sâu tơ, sâu xanh', 'ChiDinh': 'Rau họ thập tự', 'ThanhPhan': 'Emamectin benzoate 19g/L', 'DonGia_Min': 60000, 'DonGia_Max': 80000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.3 - 0.5 L/ha'},
    {'TenThuoc': 'Dylan 2EC', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Cúc tổng hợp', 'CongDung': 'Trừ sâu cuốn lá', 'ChiDinh': 'Lúa, Đậu tương', 'ThanhPhan': 'Emamectin benzoate 20g/L', 'DonGia_Min': 45000, 'DonGia_Max': 60000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.4 - 0.6 L/ha'},
    {'TenThuoc': 'Voliam Targo 063SC', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Tổng hợp', 'CongDung': 'Trừ sâu đục quả, bọ trĩ', 'ChiDinh': 'Cà chua, Ớt', 'ThanhPhan': 'Chlorantraniliprole + Abamectin', 'DonGia_Min': 80000, 'DonGia_Max': 110000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Vimite 1.8EC', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Avermectin', 'CongDung': 'Trừ nhện, sâu vẽ bùa', 'ChiDinh': 'Cây có múi, Chè', 'ThanhPhan': 'Abamectin 18g/L', 'DonGia_Min': 100000, 'DonGia_Max': 130000, 'DVTinh': 'chai 200ml', 'LieuLuong': '0.6 - 0.8 L/ha'},
    {'TenThuoc': 'Radiant 60SC', 'PhanLoai': 'Thuốc trừ sâu', 'NhomDuocLy': 'Spinosyn', 'CongDung': 'Trừ sâu xanh da láng', 'ChiDinh': 'Hành, Cà chua', 'ThanhPhan': 'Spinetoram 60g/L', 'DonGia_Min': 25000, 'DonGia_Max': 35000, 'DVTinh': 'gói 5ml', 'LieuLuong': '100 - 150 mL/ha'},

    # Nhóm 3: Trừ cỏ (10)
    {'TenThuoc': 'Roundup 480SL', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Lưu dẫn', 'CongDung': 'Trừ cỏ lá rộng, lá hẹp', 'ChiDinh': 'Đất không trồng trọt', 'ThanhPhan': 'Glyphosate 480g/L', 'DonGia_Min': 120000, 'DonGia_Max': 180000, 'DVTinh': 'Lít', 'LieuLuong': '2.0 - 3.0 L/ha'},
    {'TenThuoc': 'Gramoxone 20SL', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Tiếp xúc', 'CongDung': 'Trừ cỏ nhanh', 'ChiDinh': 'Cà phê, Cao su', 'ThanhPhan': 'Paraquat 200g/L', 'DonGia_Min': 100000, 'DonGia_Max': 140000, 'DVTinh': 'Lít', 'LieuLuong': '1.5 - 2.5 L/ha'},
    {'TenThuoc': 'Kanzo 480SL', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Lưu dẫn', 'CongDung': 'Trừ cỏ lá rộng, lá hẹp (tương tự Roundup)', 'ChiDinh': 'Vườn cây ăn trái', 'ThanhPhan': 'Glyphosate 480g/L', 'DonGia_Min': 90000, 'DonGia_Max': 130000, 'DVTinh': 'Lít', 'LieuLuong': '2.0 - 3.0 L/ha'},
    {'TenThuoc': 'Clincher 10EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Chọn lọc', 'CongDung': 'Trừ cỏ lồng vực (cỏ gạo)', 'ChiDinh': 'Lúa (phun hậu nảy mầm)', 'ThanhPhan': 'Cyhalofop-butyl 100g/L', 'DonGia_Min': 110000, 'DonGia_Max': 150000, 'DVTinh': 'chai 250ml', 'LieuLuong': '1.0 L/ha'},
    {'TenThuoc': 'Targa Super 5EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Chọn lọc', 'CongDung': 'Trừ cỏ lá hẹp', 'ChiDinh': 'Đậu tương, Lạc, Vừng', 'ThanhPhan': 'Quizalofop-P-ethyl 50g/L', 'DonGia_Min': 70000, 'DonGia_Max': 90000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.7 - 1.0 L/ha'},
    {'TenThuoc': 'Onecide 15EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Chọn lọc', 'CongDung': 'Trừ cỏ lá hẹp', 'ChiDinh': 'Rau màu, Đậu đỗ', 'ThanhPhan': 'Fluazifop-P-butyl 150g/L', 'DonGia_Min': 65000, 'DonGia_Max': 85000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.6 L/ha'},
    {'TenThuoc': 'Dual Gold 960EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Tiền nảy mầm', 'CongDung': 'Trừ cỏ mọc từ hạt', 'ChiDinh': 'Ngô, Lạc, Đậu tương', 'ThanhPhan': 'S-Metolachlor 960g/L', 'DonGia_Min': 220000, 'DonGia_Max': 280000, 'DVTinh': 'chai 500ml', 'LieuLuong': '1.0 - 1.5 L/ha'},
    {'TenThuoc': 'Goal 24EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Tiền/hậu nảy mầm', 'CongDung': 'Trừ cỏ lá rộng', 'ChiDinh': 'Hành, Lạc', 'ThanhPhan': 'Oxyfluorfen 240g/L', 'DonGia_Min': 180000, 'DonGia_Max': 230000, 'DVTinh': 'chai 250ml', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Ronstar 25EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Tiền nảy mầm', 'CongDung': 'Trừ cỏ trên lúa cấy', 'ChiDinh': 'Lúa cấy', 'ThanhPhan': 'Oxadiazon 250g/L', 'DonGia_Min': 120000, 'DonGia_Max': 160000, 'DVTinh': 'chai 100ml', 'LieuLuong': '1.5 - 2.0 L/ha'},
    {'TenThuoc': 'Butanil 60EC', 'PhanLoai': 'Thuốc trừ cỏ', 'NhomDuocLy': 'Tiền nảy mầm', 'CongDung': 'Trừ cỏ lồng vực, đuôi phụng', 'ChiDinh': 'Lúa sạ', 'ThanhPhan': 'Butachlor 600g/L', 'DonGia_Min': 150000, 'DonGia_Max': 190000, 'DVTinh': 'Lít', 'LieuLuong': '2.0 L/ha'},

    # Nhóm 4: Điều hòa sinh trưởng (5)
    {'TenThuoc': 'Atonik 1.8SL', 'PhanLoai': 'Điều hòa sinh trưởng', 'NhomDuocLy': 'Kích thích', 'CongDung': 'Giúp cây ra rễ, nảy mầm', 'ChiDinh': 'Mọi loại cây trồng', 'ThanhPhan': 'Sodium-5-Nitroguaiacolate +...', 'DonGia_Min': 10000, 'DonGia_Max': 15000, 'DVTinh': 'gói 10mL', 'LieuLuong': '200 - 250 mL/ha'},
    {'TenThuoc': 'Boom Flower-n', 'PhanLoai': 'Điều hòa sinh trưởng', 'NhomDuocLy': 'Kích thích', 'CongDung': 'Kích thích ra hoa, đậu quả', 'ChiDinh': 'Lúa, Cây ăn trái', 'ThanhPhan': 'Nitrobenzene 20%', 'DonGia_Min': 15000, 'DonGia_Max': 20000, 'DVTinh': 'gói 10ml', 'LieuLuong': '100 - 150 mL/ha'},
    {'TenThuoc': 'K-Humate', 'PhanLoai': 'Điều hòa sinh trưởng', 'NhomDuocLy': 'Cải tạo đất', 'CongDung': 'Cải tạo đất, kích rễ', 'ChiDinh': 'Bón lót, bón thúc', 'ThanhPhan': 'Potassium Humate > 80%', 'DonGia_Min': 120000, 'DonGia_Max': 160000, 'DVTinh': 'kg', 'LieuLuong': '1.0 - 2.0 kg/ha'},
    {'TenThuoc': 'Comcat 150WP', 'PhanLoai': 'Điều hòa sinh trưởng', 'NhomDuocLy': 'Kích thích', 'CongDung': 'Tăng sức đề kháng', 'ChiDinh': 'Lúa, Rau màu', 'ThanhPhan': 'Lychnis viscaria extract', 'DonGia_Min': 20000, 'DonGia_Max': 25000, 'DVTinh': 'gói 7.5g', 'LieuLuong': '100 - 150 g/ha'},
    {'TenThuoc': 'Dekamon 22.43L', 'PhanLoai': 'Điều hòa sinh trưởng', 'NhomDuocLy': 'Kích thích', 'CongDung': 'Kích ra hoa, đậu trái', 'ChiDinh': 'Xoài, Điều', 'ThanhPhan': 'NAA + Phụ gia', 'DonGia_Min': 30000, 'DonGia_Max': 40000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.5 L/ha'},

    # Nhóm 5: Trừ Ốc (3)
    {'TenThuoc': 'Snailkill 250EC', 'PhanLoai': 'Thuốc trừ ốc', 'NhomDuocLy': 'Tiếp xúc', 'CongDung': 'Trừ ốc bươu vàng', 'ChiDinh': 'Lúa', 'ThanhPhan': 'Niclosamide 250g/L', 'DonGia_Min': 50000, 'DonGia_Max': 70000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Deadline 4%', 'PhanLoai': 'Thuốc trừ ốc', 'NhomDuocLy': 'Mồi độc', 'CongDung': 'Trừ ốc bươu vàng, ốc sên', 'ChiDinh': 'Lúa, Rau màu', 'ThanhPhan': 'Metaldehyde 4%', 'DonGia_Min': 180000, 'DonGia_Max': 220000, 'DVTinh': 'kg', 'LieuLuong': '4.0 kg/ha'},
    {'TenThuoc': 'Toxbait 120AB', 'PhanLoai': 'Thuốc trừ ốc', 'NhomDuocLy': 'Mồi độc', 'CongDung': 'Trừ ốc bươu vàng', 'ChiDinh': 'Lúa', 'ThanhPhan': 'Metaldehyde 120g/kg', 'DonGia_Min': 15000, 'DonGia_Max': 25000, 'DVTinh': 'gói 100g', 'LieuLuong': '5.0 kg/ha'},

    # Nhóm 6: Trừ Vi Khuẩn (2)
    {'TenThuoc': 'Kasumin 2SL', 'PhanLoai': 'Thuốc trừ vi khuẩn', 'NhomDuocLy': 'Kháng sinh', 'CongDung': 'Trị cháy bìa lá (bạc lá)', 'ChiDinh': 'Lúa', 'ThanhPhan': 'Kasugamycin 20g/L', 'DonGia_Min': 160000, 'DonGia_Max': 200000, 'DVTinh': 'chai 500ml', 'LieuLuong': '1.0 - 1.5 L/ha'},
    {'TenThuoc': 'Starner 20WP', 'PhanLoai': 'Thuốc trừ vi khuẩn', 'NhomDuocLy': 'Kháng sinh', 'CongDung': 'Trị thối nhũn, bạc lá', 'ChiDinh': 'Bắp cải, Lúa', 'ThanhPhan': 'Oxolinic acid 200g/kg', 'DonGia_Min': 25000, 'DonGia_Max': 35000, 'DVTinh': 'gói 20g', 'LieuLuong': '0.5 kg/ha'},

    # Nhóm 7: Trừ Bệnh/Vi Khuẩn (Kết hợp) (5)
    {'TenThuoc': 'Aliette 800WG', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Lưu dẫn 2 chiều', 'CongDung': 'Trị thối rễ, sương mai', 'ChiDinh': 'Sầu riêng, Tiêu, Cao su', 'ThanhPhan': 'Fosetyl-Aluminium 800g/kg', 'DonGia_Min': 80000, 'DonGia_Max': 100000, 'DVTinh': 'gói 100g', 'LieuLuong': '1.5 kg/ha'},
    {'TenThuoc': 'Kocide 46WP', 'PhanLoai': 'Thuốc trừ bệnh/vi khuẩn', 'NhomDuocLy': 'Gốc đồng', 'CongDung': 'Trừ nấm, vi khuẩn (phổ rộng)', 'ChiDinh': 'Cây công nghiệp, Cây ăn trái', 'ThanhPhan': 'Copper Hydroxide 460g/kg', 'DonGia_Min': 30000, 'DonGia_Max': 45000, 'DVTinh': 'gói 20g', 'LieuLuong': '0.5 - 1.0 kg/ha'},
    {'TenThuoc': 'Anvil 5SC', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Triazole', 'CongDung': 'Trị rỉ sét, khô vằn', 'ChiDinh': 'Cà phê, Lúa', 'ThanhPhan': 'Hexaconazole 50g/L', 'DonGIA_Min': 120000, 'DonGia_Max': 150000, 'DVTinh': 'Lít', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Viben-C 50BTN', 'PhanLoai': 'Thuốc trừ bệnh', 'NhomDuocLy': 'Tổng hợp', 'CongDung': 'Trị đốm vằn, thối thân', 'ChiDinh': 'Lúa, Ngô', 'ThanhPhan': 'Validamycin + Carbendazim', 'DonGia_Min': 90000, 'DonGia_Max': 110000, 'DVTinh': 'gói 500g', 'LieuLuong': '1.0 kg/ha'},
    {'TenThuoc': 'Copper B 85WP', 'PhanLoai': 'Thuốc trừ bệnh/vi khuẩn', 'NhomDuocLy': 'Gốc đồng', 'CongDung': 'Trừ nấm, vi khuẩn', 'ChiDinh': 'Cây có múi, Cà phê', 'ThanhPhan': 'Copper Oxychloride 85%', 'DonGia_Min': 60000, 'DonGia_Max': 80000, 'DVTinh': 'gói 100g', 'LieuLuong': '1.0 - 1.5 kg/ha'},

    # Nhóm 8: Dinh Dưỡng / Phân Bón Lá (5)
    {'TenThuoc': 'Đầu Trâu 701', 'PhanLoai': 'Phân bón lá', 'NhomDuocLy': 'NPK vi lượng', 'CongDung': 'Kích ra hoa, tăng đậu trái', 'ChiDinh': 'Lúa, Cây ăn trái', 'ThanhPhan': 'N, P, K + TE (Bo, Zn, ...)', 'DonGia_Min': 15000, 'DonGia_Max': 20000, 'DVTinh': 'gói 10g', 'LieuLuong': 'Pha 10g/16L'},
    {'TenThuoc': 'NPK 16-16-8', 'PhanLoai': 'Phân bón NPK', 'NhomDuocLy': 'Phân bón gốc', 'CongDung': 'Cung cấp dinh dưỡng', 'ChiDinh': 'Bón lót, bón thúc', 'ThanhPhan': 'N 16%, P2O5 16%, K2O 8%', 'DonGia_Min': 800000, 'DonGia_Max': 900000, 'DVTinh': 'bao 50kg', 'LieuLuong': '150 - 200 kg/ha'},
    {'TenThuoc': 'Super Lân', 'PhanLoai': 'Phân bón', 'NhomDuocLy': 'Phân bón gốc', 'CongDung': 'Cung cấp lân, hạ phèn', 'ChiDinh': 'Bón lót', 'ThanhPhan': 'P2O5 hữu hiệu > 16%', 'DonGia_Min': 300000, 'DonGia_Max': 400000, 'DVTinh': 'bao 50kg', 'LieuLuong': '200 - 300 kg/ha'},
    {'TenThuoc': 'Vua Đạm Cá', 'PhanLoai': 'Phân bón hữu cơ', 'NhomDuocLy': 'Hữu cơ', 'CongDung': 'Tốt đất, bung đọt, mập cây', 'ChiDinh': 'Tưới gốc hoặc phun lá', 'ThanhPhan': 'Đạm cá (Hữu cơ > 20%)', 'DonGia_Min': 130000, 'DonGia_Max': 170000, 'DVTinh': 'Lít', 'LieuLuong': '2.0 L/ha'},
    {'TenThuoc': 'Canxi Bo (Chai)', 'PhanLoai': 'Phân bón lá', 'NhomDuocLy': 'Trung vi lượng', 'CongDung': 'Chống nứt trái, thối trái', 'ChiDinh': 'Cây ăn trái, Rau màu', 'ThanhPhan': 'Canxi (Ca) 10%, Boron (B) 2000ppm', 'DonGia_Min': 70000, 'DonGia_Max': 90000, 'DVTinh': 'chai 250ml', 'LieuLuong': '0.5 L/ha'},

    # Nhóm 9: Trừ Nhện (3)
    {'TenThuoc': 'Nissorun 5EC', 'PhanLoai': 'Thuốc trừ nhện', 'NhomDuocLy': 'Tiếp xúc', 'CongDung': 'Trừ nhện đỏ (diệt trứng)', 'ChiDinh': 'Chè, Cây có múi', 'ThanhPhan': 'Hexythiazox 50g/L', 'DonGia_Min': 60000, 'DonGia_Max': 80000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.5 L/ha'},
    {'TenThuoc': 'Ortus 5SC', 'PhanLoai': 'Thuốc trừ nhện', 'NhomDuocLy': 'Tiếp xúc', 'CongDung': 'Trừ nhện đỏ (diệt nhện trưởng thành)', 'ChiDinh': 'Hoa hồng, Cam', 'ThanhPhan': 'Fenpyroximate 50g/L', 'DonGia_Min': 75000, 'DonGia_Max': 95000, 'DVTinh': 'chai 100ml', 'LieuLuong': '0.7 L/ha'},
    {'TenThuoc': 'Pegasus 500SC', 'PhanLoai': 'Thuốc trừ nhện', 'NhomDuocLy': 'Tổng hợp', 'CongDung': 'Trừ nhện, bọ phấn, sâu', 'ChiDinh': 'Rau màu, Dưa hấu', 'ThanhPhan': 'Diafenthiuron 500g/L', 'DonGia_Min': 110000, 'DonGia_Max': 140000, 'DVTinh': 'chai 200ml', 'LieuLuong': '0.5 - 0.7 L/ha'},

    # Nhóm 10: Diệt côn trùng y tế / Gia dụng (2)
    {'TenThuoc': 'Fendona 10SC', 'PhanLoai': 'Diệt côn trùng', 'NhomDuocLy': 'Cúc tổng hợp', 'CongDung': 'Diệt muỗi, kiến, gián', 'ChiDinh': 'Y tế, Gia dụng', 'ThanhPhan': 'Alpha-Cypermethrin 10%', 'DonGia_Min': 40000, 'DonGia_Max': 50000, 'DVTinh': 'lọ 50ml', 'LieuLuong': 'Pha 5ml/1L nước'},
    {'TenThuoc': 'Map Permethrin 50EC', 'PhanLoai': 'Diệt côn trùng', 'NhomDuocLy': 'Cúc tổng hợp', 'CongDung': 'Diệt muỗi, ruồi', 'ChiDinh': 'Y tế, Gia dụng', 'ThanhPhan': 'Permethrin 50%', 'DonGia_Min': 110000, 'DonGia_Max': 140000, 'DVTinh': 'chai 100ml', 'LieuLuong': 'Pha 10ml/1L nước'}
]


def normalize_dvt(dvt_text):
    """
    Chuẩn hóa DVTinh từ 'gói 10g' -> 'gói', 'chai 100ml' -> 'chai'
    """
    if pd.isna(dvt_text) or dvt_text == "":
        return "chai" 
        
    dvt_lower = str(dvt_text).lower()
    
    if 'lít' in dvt_lower:
        return 'Lít'
    if 'kg' in dvt_lower:
        return 'kg'
    if 'bao' in dvt_lower:
        return 'bao'
    if 'gói' in dvt_lower:
        return 'gói'
    if 'chai' in dvt_lower:
        return 'chai'
    if 'lọ' in dvt_lower:
        return 'lọ'
    if 'ml' in dvt_lower:
        return 'mL'
    if 'g' in dvt_lower:
        return 'g'
        
    return dvt_text.capitalize()


def build_master_thuoc_list(target=50):
    
    pool = BASE_THUOC.copy()

    normalized = []
    for it in pool:
        try:
            dn = int(it.get('DonGia_Min') or it.get('DonGiaMin') or 10000)
        except Exception:
            dn = 10000
        try:
            dx = int(it.get('DonGia_Max') or it.get('DonGiaMax') or max(dn, dn*5))
        except Exception:
            dx = max(dn, dn*5)
        
        dvt_goc = it.get('DVTinh') or ('Lít' if 'SL' in (it.get('TenThuoc') or '') else 'chai')
        dvt_chuan = normalize_dvt(dvt_goc) 
        
        lu = it.get('LieuLuong') or it.get('rate') or ''
        if not lu:
            if dvt_chuan.lower() in ('g','mg'):
                lu = f"{max(10, dn//1000)} - {max(20, dn//500)} g/ha"
            elif dvt_chuan.lower() in ('ml','mL'):
                lu = "100 - 300 mL/ha"
            else:
                lu = "0.5 - 2.0 L/ha"
        
        normalized.append({
            'TenThuoc': " ".join(str(it.get('TenThuoc') or "").strip().split()),
            'PhanLoai': it.get('PhanLoai') or 'Khác',
            'NhomDuocLy': it.get('NhomDuocLy') or '',
            'CongDung': it.get('CongDung') or '',
            'ChiDinh': it.get('ChiDinh') or '',
            'ThanhPhan': it.get('ThanhPhan') or '',
            'LieuLuong': lu,
            'DonGia_Min': int(dn),
            'DonGia_Max': int(dx),
            'DVTinh': dvt_chuan 
        })

    master = []
    i = 0
    for base in normalized:
        if len(master) >= target:
            break
        
        name_gen = base['TenThuoc']
        
        price = random.randint(base['DonGia_Min'], base['DonGia_Max'])
        price = round(price / 1000) * 1000
        
        master.append({
            'STT': len(master)+1,
            'MaThuoc': f"MT{len(master)+1:03d}",
            'TenThuoc': name_gen,
            'PhanLoai': base['PhanLoai'],
            'NhomDuocLy': base['NhomDuocLy'],
            'CongDung': base['CongDung'],
            'ChiDinh': base['ChiDinh'],
            'ThanhPhan': base['ThanhPhan'],
            'LieuLuong': base['LieuLuong'],
            'DonGia': price,
            'DVTinh': base['DVTinh'] 
        })
        i += 1

    cols = ['STT','MaThuoc','TenThuoc','PhanLoai','NhomDuocLy','CongDung','ChiDinh','ThanhPhan','LieuLuong','DonGia','DVTinh']
    df = pd.DataFrame(master)

    for c in cols:
        if c not in df.columns:
            df[c] = ""

    def clean_text(v):
        if pd.isna(v):
            return ""
        s = str(v).strip()
        s = " ".join(s.split()) 
        return "".join(ch for ch in s if ord(ch) >= 32)

    for c in ['TenThuoc','PhanLoai','NhomDuocLy','CongDung','ChiDinh','ThanhPhan','LieuLuong','DVTinh']:
        df[c] = df[c].apply(clean_text)

    def fix_lieu(v):
        if not v:
            return "Theo hướng dẫn (trên nhãn) /ha"
        if '/ha' in v or 'L nước' in v: 
            return v
        return v + " /ha" if any(ch.isdigit() for ch in v) else v

    df['LieuLuong'] = df['LieuLuong'].apply(fix_lieu)

    def to_int_price(x):
        try:
            if pd.isna(x) or x == "":
                return 0
            return int(round(float(x) / 1000) * 1000)
        except Exception:
            return 0

    df['DonGia'] = df['DonGia'].apply(to_int_price)

    df['STT'] = range(1, len(df) + 1)
    df['MaThuoc'] = df['STT'].apply(lambda i: f"MT{i:03d}")

    df = df[cols].fillna("").astype({'DonGia': int})

    return df

def lam_tron_tien(so_tien):
    return round(so_tien / 1000) * 1000

def tao_ho_ten():
    ho = random.choice(HO_VN)
    if random.random() < 0.5:
        ten_dem, ten = random.choice(TEN_DEM_NAM), random.choice(TEN_NAM)
    else:
        ten_dem, ten = random.choice(TEN_DEM_NU), random.choice(TEN_NU)
    return f"{ho} {ten_dem} {ten}"

def tao_sdt():
    dau = random.choice(['90','91','93','94','96','97','98','81','82','83','84','85','86','88','89'])
    return f"0{dau}{random.randint(0,9999999):07d}"

def tao_dia_chi():
    return random.choice(TINH_THANH_VN)

def get_rank(tct):
    """Gán hạng dựa trên TongChiTieu (TCT)."""
    if tct >= 50000000:
        return 'Kim Cương'
    if tct >= 15000000:
        return 'Bạch Kim'
    if tct >= 5000000:
        return 'Vàng'
    if tct >= 500000:
        return 'Bạc'
    return 'Đồng'

def tao_khach_hang(n=50):
    ds, used = [], set()
    for i in range(1, n+1):
        sdt = tao_sdt()
        while sdt in used: sdt = tao_sdt()
        used.add(sdt)
        
        # Tạo TongChiTieu ngẫu nhiên để Hạng có ý nghĩa
        tct = 0
        p = random.random()
        if p < 0.3: # 30% Đồng
            tct = random.randint(0, 499999)
        elif p < 0.6: # 30% Bạc
            tct = random.randint(500000, 4999999)
        elif p < 0.8: # 20% Vàng
            tct = random.randint(5000000, 14999999)
        elif p < 0.95: # 15% Bạch Kim
            tct = random.randint(15000000, 49999999)
        else: # 5% Kim Cương
            tct = random.randint(50000000, 70000000)
            
        ds.append({
            'STT': i,
            'MaKH': f"KH{i:04d}",
            'HoTenKH': tao_ho_ten(),
            'SDT': sdt,
            'DiaChi': tao_dia_chi(),
            'ThuHang': get_rank(tct), # Gán Hạng dựa trên TCT
            'TongChiTieu': tct
        })
    
    cols = ['STT','MaKH','HoTenKH','SDT','DiaChi','ThuHang','TongChiTieu']
    return pd.DataFrame(ds)[cols]