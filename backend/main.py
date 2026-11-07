from fastapi import FastAPI

from backend.api.consultations import router as consultations_router


app = FastAPI(title="AI Skin Specialist API")
app.include_router(consultations_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
