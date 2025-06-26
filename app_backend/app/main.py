# main.py
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
from app.redis_subscriber import redis_subscriber

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- ganti "*" jadi list origin jika ingin lebih ketat
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Global task reference
redis_task = None

@app.on_event("startup")
async def startup_event():
    global redis_task
    logger.info("[APP] Startup event triggered")
    
    # Create task and keep reference
    redis_task = asyncio.create_task(redis_subscriber())
    logger.info("[APP] Redis subscriber task created")

@app.on_event("shutdown")
async def shutdown_event():
    global redis_task
    if redis_task:
        redis_task.cancel()
        try:
            await redis_task
        except asyncio.CancelledError:
            logger.info("[APP] Redis subscriber task cancelled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)