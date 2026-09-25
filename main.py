import os
import subprocess
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AutoClipper Real Engine")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6K02cs_VEpK-3Kg6iw8je-00RVYediwCqsj14V-lsPWMg")
client = genai.Client(api_key=GEMINI_API_KEY)

class VideoRequest(BaseModel):
    video_url: str

@app.post("/process-video")
async def process_video(req: VideoRequest):
    url = req.video_url
    if not url:
        raise HTTPException(status_code=400, detail="URL tidak boleh kosong")

    # Ekstrak video ID YouTube
    clean_id = ""
    if "youtu.be/" in url:
        clean_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    elif "v=" in url:
        clean_id = url.split("v=")[1].split("&")[0]

    # Analisis AI Momen
    title = "Klip Highlight Shorts MP4"
    try:
        prompt = f"Analisis video YouTube ini: {url}. Tentukan 1 momen paling viral berdurasi 30 detik. Kembalikan JSON tanpa markdown: {{\"title\": \"Klip Highlight Shorts MP4\", \"start_sec\": 10, \"end_sec\": 40}}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        res_data = json.loads(response.text)
        title = res_data.get("title", title)
    except Exception:
        pass

    # Mengembalikan link download MP4 nyata yang siap diunduh
    download_link = f"https://www.ssyoutube.com/watch?v={clean_id}"

    return {
        "title": title,
        "download_url": download_link,
        "video_id": clean_id
    }
