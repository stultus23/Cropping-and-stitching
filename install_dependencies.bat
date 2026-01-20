@echo off
chcp 65001 >nul
echo ========================================
echo   安装依赖包
echo ========================================
echo.

python --version
if errorlevel 1 (
    echo [错误] 未检测到 Python
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [错误] 安装失败
    pause
    exit /b 1
) else (
    echo.
    echo [成功] 所有依赖已安装完成！
    echo.
    echo 可以运行 start.bat 启动程序
    echo.
    pause
)
