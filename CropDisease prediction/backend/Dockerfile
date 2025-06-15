# Use official python base image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["sh", "-c", "uvicorn api.predict:app --host 0.0.0.0 --port ${PORT}"]

