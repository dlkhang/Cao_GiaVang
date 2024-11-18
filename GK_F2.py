import requests
from bs4 import BeautifulSoup
import pyodbc

# Kết nối tới SQL Server
connection = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAMKHANG\LAMKHANG;"  
    "Database=Cao_Gia_Vang;"  
    "UID=sa;"  
    "PWD=Khang28@;"  
)
cursor = connection.cursor()

# Tạo bảng nếu chưa có
cursor.execute("""
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='GiaVang' AND xtype='U')
CREATE TABLE GiaVang (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    LoaiVang NVARCHAR(255),
    GiaMua NVARCHAR(50),
    GiaBan NVARCHAR(50)
)
""")
connection.commit()

# URL của trang web
url = "https://www.pnj.com.vn/blog/gia-vang/?srsltid=AfmBOoqjw-O-ETgS_WVko2_6gD4izEr0sroRfXAWgC0hTM8sX3yrKg9p&r=1731689261701"

# Gửi yêu cầu GET đến trang web
response = requests.get(url)
response.raise_for_status()  # Kiểm tra nếu có lỗi

# Phân tích nội dung trang web bằng BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Tìm dữ liệu cần thiết
rows = soup.select("table tr")

# Duyệt qua các hàng trong bảng và lưu dữ liệu vào SQL Server
for row in rows[1:]:  # Bỏ qua tiêu đề bảng
    columns = row.find_all('td')
    if len(columns) >= 3:  # Đảm bảo đủ cột
        loai_vang = columns[0].text.strip()
        gia_mua = columns[1].text.strip()
        gia_ban = columns[2].text.strip()
        
        # Kiểm tra dữ liệu trùng lặp
        cursor.execute("""
        SELECT COUNT(*) 
        FROM GiaVang 
        WHERE LoaiVang = ? AND GiaMua = ? AND GiaBan = ?
        """, loai_vang, gia_mua, gia_ban)
        exists = cursor.fetchone()[0]
        
        if exists == 0:  # Nếu chưa tồn tại, thì thêm mới
            cursor.execute("""
            INSERT INTO GiaVang (LoaiVang, GiaMua, GiaBan)
            VALUES (?, ?, ?)
            """, loai_vang, gia_mua, gia_ban)

# Lưu thay đổi và đóng kết nối
connection.commit()
connection.close()

print("Dữ liệu đã được lưu vào SQL Server thành công!")
