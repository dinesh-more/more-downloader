from flask import Flask, render_template, request, Response, jsonify, send_from_directory
import subprocess
import os
import json
from datetime import datetime
import platform


app = Flask(__name__)

#export DOWNLOAD_PATH=/Users/dineshmore/yt-dlp-video-downloader
DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "/downloads")
HISTORY_FILE = os.path.join(DOWNLOAD_PATH, "history.json")

os.makedirs(DOWNLOAD_PATH, exist_ok=True)


# ---------- Helpers ----------
def save_history(entry):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        except:
            data = []

    data.insert(0, entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data[:20], f, indent=2)


def get_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return jsonify(get_history())


@app.route("/preview")
def preview():
    url = request.args.get("url")

    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        url
    ]

    try:
        result = subprocess.check_output(cmd, text=True)
        data = json.loads(result)
        return jsonify({
            "title": data.get("title"),
            "thumbnail": data.get("thumbnail")
        })
    except:
        return jsonify({"error": "Failed"}), 500


@app.route("/download")
def download():
    url = request.args.get("url")
    mode = request.args.get("mode")

    base_cmd = [
        "yt-dlp",
        "--newline",
        "--no-warnings",
        "--progress-template",
        "PROGRESS:%(progress._percent_str)s|%(progress._total_bytes_str)s|%(progress._speed_str)s"
    ]

    if mode == "audio":
        cmd = base_cmd + [
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
            url
        ]
    else:
        cmd = base_cmd + [
            "-f", "bv*+ba/b",
            "--merge-output-format", "mp4",
            "-o", f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
            url
        ]

    def generate():
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        filename = None

        for line in process.stdout:
            line = line.strip()

            if "Destination:" in line:
                filename = line.split("Destination:")[-1].strip()

            if line.startswith("PROGRESS:"):
                yield f"data:{line}\n\n"
            else:
                yield f"data:LOG|{line}\n\n"

        process.wait()

        if process.returncode == 0:
            save_history({
                "file": os.path.basename(filename) if filename else "Unknown",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            yield "data:DONE\n\n"
        else:
            yield "data:ERROR\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route("/download-file")
def download_file():
    file = request.args.get("file")
    return send_from_directory(DOWNLOAD_PATH, file, as_attachment=True)


# Optional: local-only folder open
@app.route("/open-folder")
def open_folder():
    system = platform.system()

    if system == "Darwin":  # Mac
        subprocess.Popen(["open", DOWNLOAD_PATH])
    elif system == "Windows":
        subprocess.Popen(["explorer", DOWNLOAD_PATH])
    elif system == "Linux":
        subprocess.Popen(["xdg-open", DOWNLOAD_PATH])

    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)