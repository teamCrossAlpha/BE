from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.auth_router import router as auth_router
from sector.sector_router import router as sector_router
from interest_sector.interest_sector_router import router as interest_sector_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(sector_router)
app.include_router(interest_sector_router)
