# Sử dụng Python base image nhẹ và ổn định
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Thiết lập các biến môi trường để tối ưu hóa Python trong Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy file requirements.txt trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn backend vào container
COPY . .

# Mở cổng 8000
EXPOSE 8000

# Khởi chạy ứng dụng FastAPI bằng uvicorn (không dùng reload trong production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
