# PROJCET THỊ GIÁC MÁY TÍNH KẾT THÚC HỌC PHẦN

# Hướng Dẫn Cài Đặt Môi Trường và Chạy Chương Trình

## 1. Tải Anaconda

- Truy cập: [Anaconda Download](https://www.anaconda.com/download)
- **Windows**: Tải bản `.exe`
- **MacOS/Linux**: Tải bản `.pkg` hoặc `.sh`

## 2. Tạo và Kích Hoạt Môi Trường Ảo

Nhớ `cd` về thư mục dự án trước khi tạo môi trường:

```sh
conda create -n myenv python=3.18 -y  # Thay 3.8 bằng phiên bản Python mong muốn mà bạn đang sài
conda activate myenv
```

## 3. Cập Nhật và Cài Đặt Thư Viện Cần Thiết

```sh
python -m pip install --upgrade pip setuptools wheel
pip install numpy pandas opencv-python dlib face-recognition tensorflow torch torchvision pymongo flask pygame
```

### 3.1. Cài `dlib` nếu bị lỗi

Nếu gặp lỗi khi cài `dlib`, sử dụng cách thủ công:

- Truy cập: [Dlib Windows Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)
- Chọn phiên bản phù hợp với Python của bạn, sau đó cài bằng lệnh:

```sh
pip install dlib‑19.24.2‑cp312‑cp312‑win_amd64.whl  # Thay đổi theo phiên bản
```

## 4. Tạo Tài Khoản và Kết Nối MongoDB Atlas

### 4.1. Tạo tài khoản MongoDB Atlas

1. Truy cập: [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Nhấn **Sign Up** để đăng ký tài khoản.
3. Chọn **Free Shared Cluster** (Miễn phí) và xác nhận email.

### 4.2. Tạo Cluster miễn phí

1. Đăng nhập, chọn **Create a New Cluster**.
2. Chọn **Shared Cluster (Miễn phí)**.
3. Chọn khu vực máy chủ (AWS, Azure hoặc Google Cloud).
4. Đặt tên Cluster (VD: `MyCluster`).
5. Nhấn **Create Cluster** và đợi khoảng 5 phút.

### 4.3. Tạo User và Lấy URL Kết Nối

1. Vào **Database Access**, chọn **+ Add New Database User**.
2. Đặt `username/password` để kết nối.
3. Vào lại Clusters **Connest**.
4. Chọn **Allow Access From Anywhere**.
5. Sao chép **Connection String**.

Ví dụ (trong `config/database.py`):

```python
from urllib.parse import quote_plus

class Database:
    def __init__(self):
        username = quote_plus("Nguyet04")  # Đổi thành username của bạn
        password = quote_plus("Nguyet1906")  # Đổi thành password vừa tạo
        uri = f"mongodb+srv://{username}:{password}@cluster0.5wunr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
```

## 5. Chạy Chương Trình

```sh
python main.py

## Demo Ứng Dụng

Dưới đây là ảnh demo :

![Giao Diện Chính](/demo/giaodien.png)
![Giao Diện Playnow](/demo/giaodien1.png)
![Giao Diện Đăng Kí Bảng Khôn Mặt](/demo/dangky.png)
![Cách Đăng Kí Bảng Khôn Mặt](/demo/cachdangky.png)
![Giao Diện Easy](/demo/daodieneasy.png)
![Giao Diện Hard](/demo/daodienhard.png)
![Giao Diện Setting](/demo/setting.png)
```
