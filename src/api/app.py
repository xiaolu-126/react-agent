from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

project_root = Path(__file__).parent.parent.parent
env_path = project_root / "config" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from .routes import router
from src.utils.logger import setup_logging


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    logger = setup_logging()
    logger.info("Starting AI Agent API server")
    app = FastAPI(
        title="AI Agent API",
        description="基于 LangGraph 的智能 Agent API，支持主播推荐、对话、知识库等功能",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    @app.get("/", summary="API 根路径")
    async def root():
        return {
            "service": "AI Agent API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    @app.get("/health", summary="健康检查")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()