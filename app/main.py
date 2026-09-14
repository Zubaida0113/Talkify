from fastapi import FastAPI
from app.database import engine
from app.models.task import Base
from app.routes.tasks import router as task_router

app = FastAPI(title="Talkify")
Base.metadata.create_all(bind=engine)
app.include_router(task_router)

@app.get("/")
def home():
    return {
        "message": "Talkify API is running"
    }

#uvicorn app.main:app --reload (main.py in app folder, having FastAPI instance named app)
#app is the object that holds all your routes and configuration. title="Talkify" sets the API title shown in docs and metadata.This is the object that uvicorn runs.

#This registers a GET endpoint at the root URL /.
#@app.get("/") means: “when someone sends a GET request to /, run this function”
#def home(): is the function that handles the request