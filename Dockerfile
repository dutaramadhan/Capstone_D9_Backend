# Base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libglib2.0-0

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

# Copy application files and .env
COPY . .

# Expose the application port
EXPOSE 5000

# Default command to run the application
CMD ["gunicorn", "-w", "4", "-k", "eventlet", "-b", "0.0.0.0:5000", "app:app"]
