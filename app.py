# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # اجازه می‌دهد اپ موبایل به API دسترسی داشته باشد

@app.route("/")
def home():
    return {"msg": "Anime DL backend running ✅"}

@app.route("/extract", methods=["POST"])
def extract():
    """
    POST JSON: {"url": "..."}
    Returns: title, thumbnail, description, formats (list)
    Each format: format_id, ext, resolution, filesize (approx), note
    """
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    formats = []
    for f in info.get("formats", []):
        # make resolution readable
        res = f.get("resolution") or (f.get("height") and f.get("height") and f.get("height")) or f.get("format_note")
        formats.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or f.get("height") or f.get("format_note"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "note": f.get("format_note"),
        })

    result = {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "description": info.get("description"),
        "duration": info.get("duration"),
        "formats": formats,
    }
    return jsonify(result), 200

@app.route("/get_download_url", methods=["POST"])
def get_download_url():
    """
    POST JSON: {"url":"...", "format_id":"..."}
    Returns: direct download url for that format (if available in formats)
    """
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url")
    format_id = data.get("format_id")
    if not url or not format_id:
        return jsonify({"error": "url and format_id required"}), 400

    ydl_opts = {"quiet": True, "skip_download": True, "format": format_id}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # yt-dlp typically returns final direct URL in info['url'] for the selected format
    download_url = info.get("url")
    if not download_url:
        # fallback: search in formats for url matching format_id
        for f in info.get("formats", []):
            if f.get("format_id") == format_id and f.get("url"):
                download_url = f.get("url")
                break

    if not download_url:
        return jsonify({"error": "No direct url available for requested format"}), 500

    return jsonify({"title": info.get("title"), "download_url": download_url, "format_id": format_id}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
