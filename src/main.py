from fastapi import FastAPI,Request,HTTPException,status
from src.routers import incident # type: ignore
from src.utils import load_options_from_file
from src.database import get_db
from src.config import settings
from src.schemas import IncidentCreate
from src.models import Incident
from src.utils import post_message_to_slack, create_slack_channel
import os

options = {}

app = FastAPI()
file_path = os.path.join(os.path.dirname(__file__), 'options.json')

app.include_router(incident.router)

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup_event():
    global options
    try:
        options = await load_options_from_file(file_path)
        print(f"Options loaded successfully: {options}")
    except Exception as e:
        print(f"Error loading options: {e}")
