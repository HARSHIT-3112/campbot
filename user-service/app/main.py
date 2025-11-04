from fastapi import FastAPI
from app.api.routes import auth  # import the router module
from app.api.deps import get_db
from fastapi import Depends

app = FastAPI(title="CampusBot UMS")
app.include_router(auth.router)

@app.get("/health")
def health(db=Depends(get_db)):
    # simple db health read
    try:
        next(db.execute("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

