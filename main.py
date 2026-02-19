from common.database import Base, engine

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_router import router as auth_router
from sector.sector_router import router as sector_router
from interest_sector.interest_sector_router import router as interest_sector_router
from sector_summary.sector_summary_router import router as sector_summary_router
from common.scheduler import start_scheduler
from auth import dev_auth_router
from trades.trades_router import router as trades_router

import user.user_entity
import trades.trades_entity

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    start_scheduler(app)

# routers
app.include_router(auth_router)
app.include_router(sector_router)
app.include_router(interest_sector_router)
app.include_router(sector_summary_router)
app.include_router(dev_auth_router.router)
app.include_router(trades_router)

#테이블 자동생성
Base.metadata.create_all(bind=engine)