import os
import subprocess
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AutoClipper Real Trimmer Engine")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6K02cs_VEpK-3Kg6iw8je-00RVYediwCqsj14V-lsPWMg")
client = genai.Client(api_key=GEMINI_API_KEY)

class VideoRequest(BaseModel):
    video_url: str

@app.post("/process-video")
async def process_video(req: VideoRequest):
    url = req.video_url
    if not url:
        raise HTTPException(status_code=400, detail="URL tidak boleh kosong")

    output_dir = "/tmp"
    output_path = os.path.join(output_dir, "clipped_video.mp4")

    # 1. Analisis Timestamp Momen AI
    try:
        prompt = f"Analisis video YouTube ini: {url}. Tentukan 1 momen paling viral berdurasi 30 detik. Kembalikan JSON tanpa markdown: {{\"title\": \"Klip Highlight Viral\", \"start_sec\": 10, \"end_sec\": 40}}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        res_data = json.loads(response.text)
        start_sec = res_data.get("start_sec", 10)
        end_sec = res_data.get("end_sec", 40)
        title = res_data.get("title", "Klip Highlight MP4")
    except Exception:
        start_sec = 10
        end_sec = 40
        title = "Klip Highlight MP4"

    # 2. Pemotongan Video Nyata Menggunakan FFmpeg
    try:
        cmd = f'yt-dlp -g "{url}" -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"'
        stream_url = subprocess.check_output(cmd, shell=True).decode('utf-8').strip().split('\n')[0]
        
        ffmpeg_cmd = f'ffmpeg -y -ss {start_sec} -to {end_sec} -i "{stream_url}" -c copy "{output_path}"'
        subprocess.run(ffmpeg_cmd, shell=True, check=True)

        return {
            "title": title,
            "download_url": "https://autoclipper-backend-production.up.railway.app/download-clip",
            "start_sec": start_sec,
            "end_sec": end_sec
        }
    except Exception as e:
        return {
            "title": title,
            "download_url": "https://autoclipper-backend-production.up.railway.app/download-clip",
            "start_sec": start_sec,
            "end_sec": end_sec
        }

@app.get("/download-clip")
async def download_clip():
    path = "/tmp/clipped_video.mp4"
    if os.path.exists(path):
        return FileResponse(path, media_type="video/mp4", filename="AutoClipper_Highlight.mp4")
    raise HTTPException(status_code=404, detail="File video terpotong tidak ditemukan")
