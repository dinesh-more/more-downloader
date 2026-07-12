Here's an updated version of your **README.md** with a proper **Run Locally** section added before the Docker section.

````markdown
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

---

# 🧪 Run Locally

## 1. Clone the repository

```bash
git clone https://github.com/dinesh-more/more-downloader.git
cd more-downloader
```

## 2. Create a Python virtual environment

```bash
python3 -m venv venv
```

## 3. Activate the virtual environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows (Command Prompt)

```cmd
venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```bash
pip install flask yt-dlp
```

> If you have a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## 5. Install FFmpeg

FFmpeg is required to merge audio and video streams and convert audio to MP3.

### macOS

```bash
brew install ffmpeg
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows

Download FFmpeg and add it to your system PATH.

## 6. Run the application

```bash
python app.py
```

or

```bash
python3 app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

# 🐳 Run with Docker

## Dockerfile

```dockerfile
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
```

### Update `app.py`

```python
DOWNLOAD_PATH = "/downloads"
```

### Build Docker image

```bash
docker build -t more-downloader .
```

### Run Docker container

```bash
docker run \
  -p 5000:5000 \
  -v $(pwd)/downloads:/downloads \
  more-downloader
```

Open:

```
http://localhost:5000
```

---

## 📁 Project Structure

```
more-downloader/
├── app.py
├── Dockerfile
├── README.md
├── static/
├── templates/
├── downloads/
├── history/
└── venv/
```

---

## 🛠 Tech Stack

- Python 3
- Flask
- yt-dlp
- FFmpeg
- HTML5
- CSS3
- JavaScript
- Server-Sent Events (SSE)

---

## 📄 License

MIT License
````

A couple of improvements I'd also recommend:

* Create a `requirements.txt` (`pip freeze > requirements.txt`) and update the Dockerfile to use `RUN pip install -r requirements.txt` instead of installing packages individually.
* Add screenshots or a GIF under the **Preview** section—GitHub repositories with visuals tend to be much more engaging.
