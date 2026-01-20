@echo off
chcp 65001 >nul
echo ========================================
echo   现代化图片批处理工具
echo   启动中...
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo.
    pause
    exit /b 1
)

REM 检查依赖
echo [1/2] 检查依赖...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [提示] 依赖已安装
)

echo.
echo [2/2] 启动程序...
echo.

REM 运行程序
python image_processor.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
)
