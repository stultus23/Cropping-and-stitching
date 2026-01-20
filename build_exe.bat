@echo off
chcp 65001 >nul
echo ========================================
echo   图片批处理工具 - 打包成 EXE
echo ========================================
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

echo [1/4] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [安装] PyInstaller 未安装，正在安装...
    pip install pyinstaller
)

echo.
echo [2/4] 清理旧的打包文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo.
echo [3/4] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

pyinstaller --noconfirm ^
    --onedir ^
    --windowed ^
    --name "图片批处理工具" ^
    --icon=NONE ^
    --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" ^
    --hidden-import=PIL ^
    --hidden-import=PIL._imaging ^
    --hidden-import=customtkinter ^
    --hidden-import=darkdetect ^
    --collect-data customtkinter ^
    --collect-data darkdetect ^
    image_processor.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [4/4] 打包完成！
echo.
echo ========================================
echo   打包成功！
echo ========================================
echo.
echo 可执行文件位置：
echo   dist\图片批处理工具\图片批处理工具.exe
echo.
echo 您可以：
echo 1. 将整个 "dist\图片批处理工具" 文件夹复制给朋友
echo 2. 朋友双击 "图片批处理工具.exe" 即可运行
echo 3. cropped 和 stitched 文件夹会在 exe 同目录下自动创建
echo.
echo ========================================
pause
