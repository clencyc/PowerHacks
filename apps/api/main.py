from fastapi import FastAPI
from .routers import reports, analytics
from .database import create_db_and_tables

app = FastAPI(title="SafeSpace AI API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SafeSpace AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
