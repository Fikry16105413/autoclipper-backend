from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AutoClipper Engine")

class VideoRequest(BaseModel):
    video_url: str

@app.post("/process-video")
async def process_video(req: VideoRequest):
    url = req.video_url
    
    # Menghasilkan respon JSON instan
    return {
        "status": "success",
        "title": "Highlight Momen Menarik YouTube",
        "duration": "00:45",
        "download_url": url
    }
