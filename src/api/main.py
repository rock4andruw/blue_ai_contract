"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
