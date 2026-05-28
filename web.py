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
templates = Jinja2Templates(directory="templates") #for the html file
app.mount("/static", StaticFiles(directory="static"), name="static") #mounting the css file into fastapi

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Helper function to delete the temporary folder
def cleanup_folder(folder_path: str):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Cleaned up {folder_path}")

@app.post("/download")
# BackgroundTasks added here!
def process_download(background_tasks: BackgroundTasks, url: str = Form(...)):
    
    print(f"Received URL from browser: {url}")

    unique_id = str(uuid.uuid4())
    temp_dir = os.path.join("downloads", unique_id)
    
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
    uvicorn.run(app, host="127.0.0.1", port=8000)