from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import get_db_pool, init_db
from app.api.v1.endpoints import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database pool
    pool = await get_db_pool()
    app.state.pool = pool
    
    # Initialize tables
    await init_db(pool)
    
    yield
    
    # Clean up the pool on shutdown
    pool.close()
    await pool.wait_closed()

app = FastAPI(title="HabitPulse API", lifespan=lifespan)



FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",FRONTEND_URL], # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HabitPulse API"}
