from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from app.utils.windbot.windbot import WriteOtcFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List
import os

app = FastAPI()
FILE_FOLDER = f'{os.path.dirname(os.getcwd())}/app/file_manager'
templates = Jinja2Templates(directory=f'{FILE_FOLDER}/app/templates/')

VALID_EXTENSIONS = ['xml']

@app.get('/', response_class=HTMLResponse)
def render_index(request: Request):
    return templates.TemplateResponse('upload.html', {'title': 'Windbot to OTC', 'request': request})
    

# upload file
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    ext = filename.split('.')[-1]
    if ext not in VALID_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File extension not allowed")
    WriteOtcFiles(file.file, filename).create_all_configs()
    return FileResponse(path=f'{filename}.zip', filename=f'{filename}.zip', media_type='application/octet-stream')