@echo off
echo 简谐运动模拟系统 - 修复版打包脚本
echo =====================================

echo 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo 开始打包...
pyinstaller ^
    --onefile ^
    --name=简谐振动的合成演示平台 ^
    --icon=../gui_waveform_icon_157544.ico ^
    --paths=.. ^
    --hidden-import=ui.ui_framework ^
    --hidden-import=modules.orthogonal_main ^
    --hidden-import=modules.beat_main ^
    --hidden-import=modules.phase_main ^
    --hidden-import=animations.orthogonal_animation ^
    --hidden-import=animations.beat_animation ^
    --hidden-import=animations.phase_animation ^
    --hidden-import=ui.params_controller ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    --hidden-import=matplotlib.backends.backend_agg ^
    --hidden-import=matplotlib.figure ^
    --hidden-import=matplotlib.pyplot ^
    --hidden-import=matplotlib.font_manager ^
    --hidden-import=matplotlib.patches ^
    --hidden-import=numpy ^
    --hidden-import=numpy.core ^
    --hidden-import=numpy.core._methods ^
    --hidden-import=numpy.lib.format ^
    --hidden-import=importlib ^
    --hidden-import=traceback ^
    --collect-data=matplotlib ^
    --collect-data=PyQt6 ^
    --windowed ^
    ../start.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 打包成功!
    echo 📦 可执行文件位置: dist\简谐振动的合成演示平台.exe
    echo.
    echo 正在测试可执行文件...
    if exist "dist\简谐振动的合成演示平台.exe" (
        echo ✅ 可执行文件存在
        for %%A in ("dist\简谐振动的合成演示平台.exe") do (
            set size=%%~zA
            set /a sizeMB=!size!/1024/1024
            echo 📏 文件大小: !sizeMB! MB
        )
        echo.
        echo 🚀 可以运行以下命令测试:
        echo "dist\简谐振动的合成演示平台.exe"
    ) else (
        echo ❌ 可执行文件未生成
    )
) else (
    echo ❌ 打包失败，错误代码: %ERRORLEVEL%
)

pause
