from fastapi import FastAPI
import httpx

app = FastAPI(title="CampusBot Gateway Service")

@app.get("/")
def root():
    return {"message": "Gateway Service is running!"}


