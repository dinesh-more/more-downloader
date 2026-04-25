from flask import Flask, render_template, request, Response, jsonify
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

# For local development, you can set this to any folder you want
# DOWNLOAD_PATH = "/Users/dineshmore/yt-dlp-video-downloader"
# For Docker, we will use the /downloads folder inside the container
DOWNLOAD_PATH = "/downloads"
HISTORY_FILE = "history.json"


# ---------- Helpers ----------
def save_history(entry):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.insert(0, entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data[:20], f, indent=2)


def get_history():
    try:
        if os.path.exists(HISTORY_FILE):
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


@app.route("/open-folder")
def open_folder():
    subprocess.Popen(["open", DOWNLOAD_PATH])
    return "OK"


@app.route("/open-file")
def open_file():
    file = request.args.get("file")
    if file:
        subprocess.Popen(["open", os.path.join(DOWNLOAD_PATH, file)])
    return "OK"


# 🔥 Thumbnail + title API
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
        "--cookies-from-browser", "brave",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",

        # ✅ Accurate progress
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


# if __name__ == "__main__":
#     app.run(debug=True)
#     os.makedirs(DOWNLOAD_PATH, exist_ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)