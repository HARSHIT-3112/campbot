from fastapi import FastAPI

app = FastAPI(title="CampusBot AI Service")

@app.get("/")
def root():
    return {"message": "AI Service is running!"}
