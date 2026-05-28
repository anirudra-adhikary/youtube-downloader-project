from fastapi import FastAPI, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import uuid
import shutil

from main import download_audio

app = FastAPI() 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(BASE_DIR, "templates")
static_path = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Helper function to delete the temporary folder
def cleanup_folder(folder_path: str):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Cleaned up {folder_path}")

@app.post("/download")
def process_download(background_tasks: BackgroundTasks, url: str = Form(...)):
    
    print(f"Received URL from browser: {url}")

    unique_id = str(uuid.uuid4())
    # Updated to use BASE_DIR safely
    temp_dir = os.path.join(BASE_DIR, "downloads", unique_id)
    
    # Download the audio
    download_audio(url, output_dir=temp_dir)

    downloaded_files = os.listdir(temp_dir)
    if not downloaded_files:
        return {"error": "Download failed."}
    
    file_name = downloaded_files[0]
    file_path = os.path.join(temp_dir, file_name)

    # Tell FastAPI to run the cleanup_folder function AFTER the user finishes downloading
    background_tasks.add_task(cleanup_folder, temp_dir)

    return FileResponse(path=file_path, filename=file_name, media_type='audio/mp4')

if __name__ == "__main__":
    uvicorn.run("web:app", host="0.0.0.0", port=8000, reload=True)