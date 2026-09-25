import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AutoClipper AI Engine")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6K02cs_VEpK-3Kg6iw8je-00RVYediwCqsj14V-lsPWMg")
client = genai.Client(api_key=GEMINI_API_KEY)

class VideoRequest(BaseModel):
    video_url: str

@app.post("/process-video")
async def process_video(req: VideoRequest):
    url = req.video_url
    if not url:
        raise HTTPException(status_code=400, detail="URL tidak boleh kosong")

    # 1. Ekstrak Direct Stream MP4 via API Cobalt Public
    try:
        cobalt_res = requests.post(
            "https://api.cobalt.tools/api/json",
            json={"url": url, "vCodec": "h264"},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=10
        ).json()
        
        mp4_download_url = cobalt_res.get("url", url)
    except Exception:
        mp4_download_url = url

    # 2. Analisis AI Momen
    try:
        prompt = f"Analisis video YouTube ini: {url}. Tentukan 1 momen paling viral. Kembalikan JSON tanpa markdown: {{\"title\": \"Klip Highlight Viral\", \"start_sec\": 10, \"end_sec\": 40}}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception:
        return {
            "title": "Klip Highlight Viral MP4",
            "download_url": mp4_download_url,
            "start_sec": 10,
            "end_sec": 40
        }
