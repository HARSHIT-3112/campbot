from fastapi import FastAPI

app = FastAPI(title="CampusBot Chat Service")

@app.get("/")
def root():
    return {"message": "Chat Service is running!"}
