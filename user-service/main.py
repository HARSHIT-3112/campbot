from fastapi import FastAPI

app = FastAPI(title="CampusBot User Management Service")

@app.get("/")
def root():
    return {"message": "User Service is running!"}
