@echo off
REM SHM Visualization Build Script
REM 简谐运动可视化系统构建脚本

echo ============================================================
echo SHM Visualization PyInstaller Build
echo 简谐运动可视化系统 PyInstaller 构建
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo 错误：Python未安装或不在PATH中
    pause
    exit /b 1
)

REM Run the build script
echo Running build script...
echo 正在运行构建脚本...
echo.

python build_executable.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    echo 构建失败！请检查上面的错误信息。
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo Build completed successfully!
    echo 构建成功完成！
    echo.
    echo Executable location: dist\SHM_Visualization.exe
    echo 可执行文件位置: dist\SHM_Visualization.exe
    echo ============================================================
    pause
)
