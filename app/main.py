from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import health, generation

app = FastAPI(title="EasyBiz AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(generation.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "EasyBiz AI Service", "status": "running"}
