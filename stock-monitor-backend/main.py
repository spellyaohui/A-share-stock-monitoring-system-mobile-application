# ============================================
# 宝塔面板入口文件
# ============================================
# 此文件用于宝塔 Python 项目管理器
# 入口文件选择：main.py
# ============================================

from app.main import app

# 宝塔需要这个变量
application = app

if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
