from flask import Flask, render_template, request, send_file, send_from_directory
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

OUTPUT_FOLDER = "audio"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

VOICES = {
    "male": "hi-IN-MadhurNeural",
    "female": "hi-IN-SwaraNeural"
}


@app.route("/", methods=["GET", "POST"])
def home():
    audio_file = None
    error = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        voice_type = request.form.get("voice", "male")
        speed = request.form.get("speed", "0")

        if not text:
            error = "Please enter some text."

        elif len(text) > 10000:
            error = "Text 10000 characters se kam rakho."

        else:
            try:
                voice = VOICES.get(voice_type, VOICES["male"])

                rate_value = int(speed)
                rate_value = max(-50, min(50, rate_value))
                rate = f"{rate_value:+d}%"

                filename = f"{uuid.uuid4().hex}.mp3"
                filepath = os.path.join(OUTPUT_FOLDER, filename)

                async def generate_audio():
                    communicate = edge_tts.Communicate(
                        text,
                        voice,
                        rate=rate
                    )
                    await communicate.save(filepath)

                asyncio.run(generate_audio())

                audio_file = filename

            except Exception as e:
                error = f"Audio generate nahi hua: {e}"

    return render_template(
        "index.html",
        audio_file=audio_file,
        error=error
    )


@app.route("/audio/<filename>")
def serve_audio(filename):
    if (
        not filename.endswith(".mp3")
        or os.path.basename(filename) != filename
    ):
        return "Invalid file", 400

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.isfile(filepath):
        return "Audio file nahi mili.", 404

    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/download/<filename>")
def download(filename):
    if (
        not filename.endswith(".mp3")
        or os.path.basename(filename) != filename
    ):
        return "Invalid file", 400

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.isfile(filepath):
        return "File nahi mili.", 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name="Hindi_Audio.mp3"
    )


if __name__ == "__main__":
    app.run(debug=True)
