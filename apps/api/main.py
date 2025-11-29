from fastapi import FastAPI
from .database import connect_to_mongo, close_mongo_connection
from .routers import reports, analytics

app = FastAPI(title="SafeSpace AI API")

@app.on_event("startup")
def on_startup():
    connect_to_mongo()

@app.on_event("shutdown")
def on_shutdown():
    close_mongo_connection()

app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SafeSpace AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
