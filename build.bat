@echo off
REM Claude Email Bridge 打包脚本 (Windows)

echo ======================================
echo Claude Email Bridge 打包工具
echo ======================================
echo.

echo [1/3] 安装打包依赖...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 错误: 安装 PyInstaller 失败
    pause
    exit /b 1
)

echo.
echo [2/3] 开始打包...
pyinstaller claude-email-bridge.spec
if %errorlevel% neq 0 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成!
echo 可执行文件位置: dist\Claude Email Bridge.exe
echo.
pause
