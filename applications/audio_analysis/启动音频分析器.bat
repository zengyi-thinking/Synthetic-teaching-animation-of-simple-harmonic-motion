@echo off
chcp 65001 >nul
title 音频分析器 - 简谐波分解与重构工具

echo.
echo ========================================
echo 音频分析器 - 简谐波分解与重构工具
echo ========================================
echo.
echo 正在启动应用程序...
echo.

cd /d "%~dp0"
python run_audio_analyzer.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败！
    echo 请确保已安装Python和所需依赖库
    echo 运行: python install_dependencies.py
    echo.
    pause
)
