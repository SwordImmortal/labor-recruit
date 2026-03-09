@echo off
REM ================================
REM Labor-Recruit 工作区初始化
REM ================================

echo.
echo ================================
echo   Labor-Recruit 工作区
echo ================================
echo.

REM 显示项目记忆核心信息
if exist PROJECT_MEMORY.md (
    echo [项目状态]
    type PROJECT_MEMORY.md | findstr /n "." | findstr "^[1-9]:" >nul
    if %errorlevel%==0 (
        for /f "tokens=1,2* delims=:" %%a in ('type PROJECT_MEMORY.md ^| findstr /n "." ^| findstr "^[1-3]:"') do echo %%b
    )
    echo.
    type PROJECT_MEMORY.md | findstr /C:"⚡" /C:"[ ]" 2>nul
    echo.
)

echo ================================
echo   快速启动命令
echo ================================
echo   后端: cd backend ^&^& python main.py
echo   前端: cd frontend ^&^& npm run dev  
echo   API:  http://localhost:8000/docs
echo ================================
echo.
