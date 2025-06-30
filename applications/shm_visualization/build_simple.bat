@echo off
chcp 65001 >nul
echo 简谐运动可视化系统 - 简化打包脚本
echo =====================================

echo 正在清理旧的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo 开始PyInstaller打包...
pyinstaller ^
    --onefile ^
    --name="简谐振动的合成演示平台" ^
    --paths="src" ^
    --hidden-import="shm_visualization" ^
    --hidden-import="shm_visualization.main" ^
    --hidden-import="shm_visualization.ui.ui_framework" ^
    --hidden-import="shm_visualization.modules.orthogonal_main" ^
    --hidden-import="shm_visualization.modules.beat_main" ^
    --hidden-import="shm_visualization.modules.phase_main" ^
    --hidden-import="shm_visualization.animations.orthogonal_animation" ^
    --hidden-import="shm_visualization.animations.beat_animation" ^
    --hidden-import="shm_visualization.animations.phase_animation" ^
    --hidden-import="shm_visualization.ui.params_controller" ^
    --hidden-import="PyQt6.QtWidgets" ^
    --hidden-import="PyQt6.QtCore" ^
    --hidden-import="PyQt6.QtGui" ^
    --hidden-import="matplotlib.backends.backend_qt5agg" ^
    --hidden-import="numpy" ^
    --console ^
    run.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 打包成功！
    echo 📦 可执行文件位置: dist\简谐振动的合成演示平台.exe
    echo 💡 现在可以运行测试了
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息并重试
)

pause
