# Use official slim Python runtime as base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for compilation (e.g. bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies along with gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the backend API
EXPOSE 5000

# Set default environment variables
ENV FLASK_ENV=production
ENV DEBUG=False

# Run using the production WSGI server Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app()"]
