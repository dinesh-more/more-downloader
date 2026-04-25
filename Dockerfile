FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir flask yt-dlp

# Create download folder
RUN mkdir -p /downloads

# Expose Flask port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]