from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from contextlib import asynccontextmanager
from loguru import logger

from src.core.config import settings, Environment
from src.agents.email_agent import EmailAssistantAgent
from src.api.routes import email, eval
from src.database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Email Assistant API")
    init_db()
    app.state.agent = EmailAssistantAgent()
    yield
    # Shutdown
    logger.info("Shutting down Email Assistant API")

app = FastAPI(
    title="Email Assistant AI API",
    description="Production-grade Email Assistant with Agentic AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(email.router, prefix="/api/v1/email", tags=["email"])
app.include_router(eval.router, prefix="/api/v1/eval", tags=["evaluation"])

@app.get("/")
async def root():
    return {"message": "Email Assistant AI API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == Environment.LOCAL
    )