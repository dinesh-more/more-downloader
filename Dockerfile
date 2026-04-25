FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg curl

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask yt-dlp

RUN mkdir -p /downloads

EXPOSE 5000

CMD ["python", "app.py"]
