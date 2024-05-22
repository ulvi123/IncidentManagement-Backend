from fastapi import FastAPI,Request,HTTPException,status
from src.routers import incident # type: ignore

app = FastAPI()

app.include_router(incident.router)

@app.get("/")
def root():
    return {"message": "Hello World"}
