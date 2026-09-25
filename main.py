import os
import subprocess
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
import yt_dlp

app = FastAPI(title="AutoClipper Cloud Engine")

os.makedirs("clips", exist_ok=True)
app.mount("/static", StaticFiles(directory="clips"), name="static")

# Ambil API Key dari Environment Variable sistem
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

class VideoRequest(BaseModel):
    video_url: str

@app.post("/process-video")
async def process_video(req: VideoRequest):
    url = req.video_url
    video_id = f"video_{int(time.time())}"
    raw_video = f"clips/{video_id}_raw.mp4"
    output_clip = f"clips/{video_id}_clip.mp4"

    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': raw_video,
        'overwrites': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal mengunduh video: {str(e)}")

    start_sec = 10
    end_sec = 40

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_sec),
        '-to', str(end_sec),
        '-i', raw_video,
        '-vf', 'crop=ih*(9/16):ih',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_clip
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memotong video: {str(e)}")

    if os.path.exists(raw_video):
        os.remove(raw_video)

    return {
        "status": "success",
        "title": "Klip Highlight Otomatis",
        "duration": f"{end_sec - start_sec}s",
        "download_url": f"/static/{video_id}_clip.mp4"
    }
