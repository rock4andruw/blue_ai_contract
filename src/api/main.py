"""FastAPI application entry point."""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .contracts import router as contracts_router

app = FastAPI(
    title="Blue-AI 合約智能比對助理",
    description="上傳兩份合約，自動比對差異、標示風險、給出協商對策。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo 階段開放，正式上線收緊
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(contracts_router)

_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")


@app.get("/demo", summary="Demo UI")
async def demo_ui():
    return FileResponse(os.path.join(_frontend_dir, "demo.html"))


@app.get("/", summary="Root")
async def root():
    return {
        "service": "Blue-AI Contract Comparison API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "compare_upload": "POST /api/v1/contracts/compare",
            "compare_example": "GET /api/v1/contracts/compare/example/{v2|v3|v4|v5}",
            "health": "GET /api/v1/contracts/health",
        },
    }
