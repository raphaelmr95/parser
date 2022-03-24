import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, BackgroundTasks
from app.utils.windbot.windbot import WriteOtcFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
		allow_headers=["*"],
    max_age=3600,
)

FILE_FOLDER = f'./app/file_manager'
templates = Jinja2Templates(directory="./app/file_manager/templates/")

VALID_EXTENSIONS = ['xml']

@app.get('/', response_class=HTMLResponse)
def render_index(request: Request):
    return templates.TemplateResponse('upload.html', {'title': 'Windbot to OTC', 'request': request})
    
def delete_file(file_path: list):
    try:
        for file in file_path:
            os.remove(file)
    except OSError:
        pass

# upload file
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
    ):
    
    filename = file.filename
    ext = filename.split('.')[-1]
    if ext not in VALID_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File extension not allowed")
    filename = filename.split('.')[0]
    await WriteOtcFiles(file.file, filename).create_all_configs()
    background_tasks.add_task(delete_file, [f'{FILE_FOLDER}/server/{filename}.json', f'{FILE_FOLDER}/server/{filename}.cfg', f'{filename}.zip'])
    return FileResponse(
            path=f'{filename}.zip', 
            filename=f'{filename}.zip', 
            media_type='application/octet-stream'
        )