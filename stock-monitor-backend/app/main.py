from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth, stocks, monitors, charts, notifications, enhanced_stocks, users
from app.api.realtime_monitor import router as realtime_router
from app.websocket.handler import router as ws_router
from app.database import engine
from app.models import Base
from app.core.logging import get_logger
import time

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"收到请求: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"请求完成: {request.method} {request.url} - 状态码: {response.status_code} - 耗时: {process_time:.4f}s")
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["股票"])
app.include_router(monitors.router, prefix="/api/monitors", tags=["监测"])
app.include_router(charts.router, prefix="/api/charts", tags=["图表"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知"])
app.include_router(enhanced_stocks.router, tags=["增强功能"])
app.include_router(realtime_router, tags=["实时监测"])
app.include_router(ws_router, prefix="/ws")

@app.on_event("startup")
async def startup_event():
    from app.core.scheduler import start_scheduler
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    from app.core.scheduler import shutdown_scheduler
    shutdown_scheduler()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
