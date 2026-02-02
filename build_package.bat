@echo off
chcp 65001 >nul
echo ========================================
echo   图片批处理工具 - 打包程序
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境
    echo 请先运行：python -m venv .venv
    echo 然后运行：.venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

echo [√] 找到虚拟环境
echo.

REM 清理旧文件
echo [1/4] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo       ✓ 完成

REM 检查并安装 PyInstaller
echo.
echo [2/4] 检查 PyInstaller...
.venv\Scripts\python.exe -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo       正在安装 PyInstaller...
    .venv\Scripts\python.exe -m pip install pyinstaller
) else (
    echo       ✓ 已安装
)

REM 开始打包
echo.
echo [3/4] 开始打包（这可能需要几分钟）...
echo.
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm "图片批处理工具.spec"

REM 检查结果
echo.
echo [4/4] 检查打包结果...
if exist "dist\图片批处理工具\图片批处理工具.exe" (
    echo.
    echo ========================================
    echo   ✓ 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置：
    echo dist\图片批处理工具\图片批处理工具.exe
    echo.
    echo 整个 dist\图片批处理工具 文件夹可以：
    echo   - 复制到其他电脑使用
    echo   - 打包成 ZIP 分发
    echo   - 无需安装 Python 环境
    echo.
) else (
    echo.
    echo [错误] 打包失败，请检查错误信息
    echo.
)

pause
