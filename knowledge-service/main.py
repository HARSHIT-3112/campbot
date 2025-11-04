from fastapi import FastAPI

app = FastAPI(title="CampusBot Knowledge Service")

@app.get("/")
def root():
    return {"message": "Knowledge Service is running!"}

