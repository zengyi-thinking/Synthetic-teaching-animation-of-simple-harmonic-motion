@echo off
echo 简谐运动教学仿真系统 - 启动脚本
echo ======================================
echo.

:: 检查是否有可执行文件
if exist "dist\简谐运动教学仿真系统\简谐运动教学仿真系统.exe" (
    echo 找到打包版本，正在启动...
    start "" "dist\简谐运动教学仿真系统\简谐运动教学仿真系统.exe"
) else if exist "简谐运动教学仿真系统.exe" (
    echo 找到当前目录可执行文件，正在启动...
    start "" "简谐运动教学仿真系统.exe"
) else (
    echo 未找到打包版本，尝试启动调试版本...
    
    :: 检查Python环境
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        echo 找到Python环境，正在启动调试版本...
        python debug_launcher.py
    ) else (
        echo 未找到Python环境，尝试使用虚拟环境...
        if exist ".venv\Scripts\python.exe" (
            echo 使用虚拟环境启动...
            .venv\Scripts\python.exe debug_launcher.py
        ) else (
            echo 错误: 未找到可用的Python环境或可执行文件
            echo 请确保已安装Python或已打包程序
            pause
            exit /b 1
        )
    )
)

echo.
echo 程序已启动，此窗口可以关闭
timeout /t 5 