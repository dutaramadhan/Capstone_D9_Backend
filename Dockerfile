# Gunakan base image Python 3.10-slim
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tentukan direktori kerja dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Install dependensi yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Salin semua file aplikasi ke direktori kerja dalam container
COPY . /app/

# Salin file .env ke dalam container
COPY .env /app/

# Expose port aplikasi (misal 5000 atau 5001 tergantung kebutuhan)
EXPOSE 5000

# Perintah default untuk menjalankan aplikasi dengan Gunicorn menggunakan worker eventlet
CMD ["gunicorn", "-w", "4", "-k", "eventlet", "-b", "0.0.0.0:5000", "app:app"]
