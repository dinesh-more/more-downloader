from flask import Flask, render_template, request, Response, jsonify, send_from_directory, session
import subprocess
import os
import json
from datetime import datetime, timedelta
import platform
import uuid

app = Flask(__name__)

AUTO_DELETE_MINUTES = 30
app.secret_key = "more-downloader-secret-key"  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_user_download_path():
    user_id = get_user_id()
    path = os.path.join(BASE_DIR, "downloads", user_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_user_history_file():
    user_id = get_user_id()
    path = os.path.join(BASE_DIR, f"history_{user_id}.json")

    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)

    return path





# ---------- Helpers ----------
def save_history(entry):
    history_file = get_user_history_file()

    data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                data = json.load(f)
        except:
            data = []

    data.insert(0, entry)

    with open(history_file, "w") as f:
        json.dump(data[:20], f, indent=2)


def cleanup_old_files():
    now = datetime.now()

    for f in os.listdir(get_user_download_path()):
        if f.endswith(".part"):
            continue

        full_path = os.path.join(get_user_download_path(), f)

        if os.path.isfile(full_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(full_path))

            if now - file_time > timedelta(minutes=AUTO_DELETE_MINUTES):
                try:
                    os.remove(full_path)
                except:
                    pass


def get_files_from_download_folder():
    files = []

    if not os.path.exists(get_user_download_path()):
        return files

    allowed_ext = (".mp4", ".mp3")

    for f in os.listdir(get_user_download_path()):
        # ❌ skip temp files
        if f.endswith(".part"):
            continue

        # ❌ skip non-media files
        if not f.lower().endswith(allowed_ext):
            continue

        full_path = os.path.join(get_user_download_path(), f)

        if os.path.isfile(full_path):
            size = os.path.getsize(full_path)

            files.append({
                "file": f,
                "time": datetime.fromtimestamp(
                    os.path.getmtime(full_path)
                ).strftime("%Y-%m-%d %H:%M"),
                "timestamp": os.path.getmtime(full_path),
                "size": f"{round(size / (1024*1024), 2)} MB"
            })

    return files


def get_history():
    cleanup_old_files()

    allowed_ext = (".mp4", ".mp3")

    history = []

    # Load history.json
    if os.path.exists(get_user_history_file()):
        try:
            with open(get_user_history_file(), "r") as f:
                raw_history = json.load(f)

                # ✅ FILTER HERE ALSO
                history = [
                    item for item in raw_history
                    if item.get("file", "").lower().endswith(allowed_ext)
                ]
        except:
            history = []

    # Load actual files
    folder_files = get_files_from_download_folder()

    existing = {item["file"] for item in history}

    for file in folder_files:
        if file["file"] not in existing:
            history.append(file)

    # ✅ sort using timestamp (better than string time)
    history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    return history[:20]


def get_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    print("get_user_download_path: "+get_user_download_path())
    print("get_user_history_file: "+get_user_history_file())
    return jsonify(get_history())


@app.route("/delete-file")
def delete_file():
    file = request.args.get("file")
    path = os.path.join(get_user_download_path(), file)

    if os.path.exists(path):
        os.remove(path)
        return "Deleted"

    return "Not found", 404


@app.route("/preview")
def preview():
    url = request.args.get("url")

    cmd = ["yt-dlp", "--dump-json", "--skip-download", url]

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

    user_id = get_user_id()  # ✅ capture here
    download_path = os.path.join(BASE_DIR, "downloads", user_id)
    os.makedirs(download_path, exist_ok=True)

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
            "-o", f"{download_path}/%(title)s.%(ext)s",
            url
        ]
    else:
        cmd = base_cmd + [
            "-f", "bv*+ba/b",
            "--merge-output-format", "mp4",
            "-o", f"{download_path}/%(title)s.%(ext)s",
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
            history_file = os.path.join(BASE_DIR, f"history_{user_id}.json")  # ✅ no session call

            data = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, "r") as f:
                        data = json.load(f)
                except:
                    data = []

            data.insert(0, {
                "file": os.path.basename(filename) if filename else "Unknown",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "timestamp": datetime.now().timestamp()
            })

            with open(history_file, "w") as f:
                json.dump(data[:20], f, indent=2)

            yield "data:DONE\n\n"
        else:
            yield "data:ERROR\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route("/download-file")
def download_file():
    file = request.args.get("file")
    return send_from_directory(get_user_download_path(), file, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)