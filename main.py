from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_router import router as auth_router
from sector.sector_router import router as sector_router
from interest_sector.interest_sector_router import router as interest_sector_router
from sector_summary.sector_summary_router import router as sector_summary_router
from common.scheduler import start_scheduler
from auth import dev_auth_router
from trades.trades_router import router as trades_router
from tickers.tickers_router import router as tickers_router
from insights.performance.performance_router import router as performance_router
from insights.behavior_pattern.buy.buy_router import router as buy_pattern_router
from insights.behavior_pattern.sell.sell_router import router as sell_pattern_router
from insights.confidence.scatter.confidence_scatter_router import router as confidence_scatter_router
from insights.confidence.range.confidence_range_router import router as confidence_range_router

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
app.include_router(tickers_router)
app.include_router(performance_router)
app.include_router(buy_pattern_router)
app.include_router(sell_pattern_router)
app.include_router(confidence_scatter_router)
app.include_router(confidence_range_router)