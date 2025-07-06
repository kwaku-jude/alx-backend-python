# Dockerfile

# Use python: 3.10 as the base image
FROM python:3.10-slim

# Set the environment variable
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt --no-cache-dir

# Copy the application code to another container directory
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Default command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]