import sys
import asyncio
import logging

# Configure application-wide logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("server.log")
    ]
)

logger = logging.getLogger(__name__)

# Set the appropriate event loop policy depending on the OS.
# Windows requires the SelectorEventLoop for Psycopg to work in async mode.
# Linux (like Ubuntu on EC2) natively uses the correct event loop by default.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import get_db_pool, init_db
from app.api.v1.endpoints import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up HabitPulse API...")
    try:
        # Initialize the database pool
        logger.info("Connecting to the database...")
        pool = await get_db_pool()
        app.state.pool = pool
        
        # Initialize tables
        logger.info("Initializing database tables...")
        await init_db(pool)
        logger.info("Database initialized successfully.")
        
        yield
        
        # Clean up the pool on shutdown
        logger.info("Shutting down... closing database pool.")
        await pool.close()
        logger.info("Database pool closed safely.")
    except Exception as e:
        logger.error(f"Error during startup/shutdown: {e}", exc_info=True)
        raise

app = FastAPI(title="HabitPulse API", lifespan=lifespan)



FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",FRONTEND_URL,"http://localhost:4173"], # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HabitPulse API"}
