import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import data, conversations, chat

app = FastAPI(
    title="Data-Aware AI Assistant API",
    description="시계열 데이터 컨텍스트 기반 AI 맞춤형 대화 서비스 API",
    version="1.0.0"
)

# CORS 설정
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Data-Aware AI Assistant API Online"}