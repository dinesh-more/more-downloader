# 🚀 More Downloader

A modern, web-based **universal video & audio downloader** built with Flask and yt-dlp.  
Supports YouTube (and other yt-dlp supported platforms) with real-time progress tracking, preview, and download history.

---

## ✨ Features

- 🎥 Download videos in best quality (auto merge audio + video)
- 🎧 Extract audio as MP3
- 🖼 Preview video thumbnail + title before downloading
- 📊 Real-time progress bar (percentage, speed, file size)
- 📂 Open downloaded file directly from UI
- 🗂 Download history (last 20 downloads)
- 📁 Open download folder button
- ⚡ Live log streaming using Server-Sent Events (SSE)
- 🌐 Modern dark-themed UI

---

## 📸 Preview

> (Add screenshots here after running the project)

Example:

------------------

Can we Dockerize this app?
✅ Absolutely.

Your app needs:

Python + Flask
yt-dlp
system dependency: ffmpeg (IMPORTANT for audio/video merge)
cookies access (optional but better)

Dockerfile
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

Update your app.py (IMPORTANT for Docker)
DOWNLOAD_PATH = "/downloads"

🧱 Build Docker image
docker build -t more-downloader .

## 🧪 Run Locally

```bash
docker run -p 5000:5000 -v $(pwd)/downloads:/Downloads
```

