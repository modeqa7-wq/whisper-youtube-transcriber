from fastapi import FastAPI, Request
import yt_dlp, openai, tempfile, os

# Read your OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create the FastAPI app
app = FastAPI()

# Function to download YouTube audio
def download_audio(url):
    temp_path = tempfile.mktemp(suffix=".mp3")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": temp_path,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return temp_path

# POST endpoint: /transcribe
@app.post("/transcribe")
async def transcribe(request: Request):
    data = await request.json()
    youtube_url = data.get("youtube_url")

    try:
        audio_path = download_audio(youtube_url)
        with open(audio_path, "rb") as audio_file:
            # Send audio to Whisper model
            transcript = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        os.remove(audio_path)
        return {"transcript": transcript}
    except Exception as e:
        return {"error": str(e)}
