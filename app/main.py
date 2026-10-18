"""FastAPI entry point: uvicorn app.main:app --reload."""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.api_core.exceptions import GoogleAPICallError

from app.routers import chat, conversations, data

logger = logging.getLogger(__name__)
app = FastAPI(
    title="Data-Aware AI Assistant API",
    description="시계열 데이터 요약을 활용하는 학습 비서",
    version="1.1.0",
)
origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)
app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.exception_handler(GoogleAPICallError)
async def database_error(request: Request, exc: GoogleAPICallError):
    logger.error("Firestore request failed: %s", type(exc).__name__)
    return JSONResponse(
        status_code=503, content={"detail": "Database temporarily unavailable"}
    )


@app.get("/")
def root():
    """Liveness check; credentials are validated by data requests."""
    return {"message": "Data-Aware AI Assistant API Online", "docs": "/docs"}
