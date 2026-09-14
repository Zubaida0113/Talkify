from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine
from app.models.task import Base
from app.routes.tasks import router as task_router
from app.routes.audio import router as audio_router

app = FastAPI(title="Talkify")
Base.metadata.create_all(bind=engine) # Create database tables
app.include_router(task_router) # Task API
app.include_router(audio_router) # Audio API

# Serve frontend files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def home():
    return FileResponse("app/static/index.html")

#uvicorn app.main:app --reload (main.py in app folder, having FastAPI instance named app)
#app is the object that holds all your routes and configuration. title="Talkify" sets the API title shown in docs and metadata.This is the object that uvicorn runs.

#This registers a GET endpoint at the root URL /.
#@app.get("/") means: “when someone sends a GET request to /, run this function”
#def home(): is the function that handles the request