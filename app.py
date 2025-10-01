from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/")
def home():
    return {"msg": "HiAnime backend running ✅"}

@app.route("/extract", methods=["POST"])
def extract():
    """
    گرفتن اطلاعات کامل از لینک انیمه یا قسمت
    """
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # انتخاب داده‌های مهم
        result = {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url"),
                }
                for f in info.get("formats", [])
            ],
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["POST"])
def download():
    """
    برگرداندن لینک مستقیم برای فرمت انتخابی
    """
    data = request.json
    url = data.get("url")
    format_id = data.get("format_id")

    if not url or not format_id:
        return jsonify({"error": "url and format_id required"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": format_id,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "download_url": info.get("url"),
            "format_id": format_id,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
