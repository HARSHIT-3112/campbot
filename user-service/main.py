from fastapi import FastAPI

app = FastAPI(title="CampusBot Gateway Service")

@app.get("/")
def root():
    return {"message": "Gateway "}
