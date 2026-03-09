from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, users, projects, candidates, onboardings, channels, dicts, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 正在启动应用...")
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    print("👋 应用关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="蓝领招聘与项目运营系统 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["候选人"])
app.include_router(onboardings.router, prefix="/api/v1/onboardings", tags=["入职"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["渠道"])
app.include_router(dicts.router, prefix="/api/v1/dicts", tags=["字典"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["工作台"])


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用蓝领招聘与项目运营系统",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
