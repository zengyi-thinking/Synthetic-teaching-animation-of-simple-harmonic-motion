#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简谐运动模拟系统 - PyInstaller 打包脚本
解决依赖和资源文件问题
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 添加父目录到 Python 路径以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def check_dependencies():
    """检查所有依赖模块"""
    print("=== 检查依赖模块 ===")
    
    required_modules = [
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore', 
        'PyQt6.QtGui',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'numpy',
        'ui.ui_framework',
        'modules.orthogonal_main',
        'modules.beat_main',
        'modules.phase_main',
        'animations.orthogonal_animation',
        'animations.beat_animation',
        'animations.phase_animation',
        'ui.params_controller'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺失模块: {missing_modules}")
        return False
    else:
        print("\n✅ 所有依赖模块检查通过")
        return True

def create_spec_file():
    """创建优化的 PyInstaller spec 文件"""
    print("\n=== 创建 PyInstaller 配置文件 ===")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集所有必要的数据文件
datas = []

# 添加图标文件
if os.path.exists('gui_waveform_icon_157544.ico'):
    datas.append(('gui_waveform_icon_157544.ico', '.'))

# 收集 matplotlib 数据文件
datas += collect_data_files('matplotlib')

# 收集 PyQt6 数据文件
try:
    datas += collect_data_files('PyQt6')
except:
    pass

# 隐式导入的模块
hiddenimports = [
    # PyQt6 相关
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.sip',
    
    # matplotlib 相关
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_agg',
    'matplotlib.figure',
    'matplotlib.pyplot',
    'matplotlib.font_manager',
    'matplotlib.patches',
    
    # numpy 相关
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib.format',
    
    # 项目模块
    'ui.ui_framework',
    'modules.orthogonal_main',
    'modules.beat_main',
    'modules.phase_main',
    'animations.orthogonal_animation',
    'animations.beat_animation',
    'animations.phase_animation',
    'ui.params_controller',
    
    # 其他可能需要的模块
    'importlib',
    'traceback',
    'sys',
    'os'
]

# 收集所有子模块
try:
    hiddenimports += collect_submodules('PyQt6')
except:
    pass

try:
    hiddenimports += collect_submodules('matplotlib')
except:
    pass

a = Analysis(
    ['start.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='简谐振动的合成演示平台',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为窗口模式
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui_waveform_icon_157544.ico' if os.path.exists('gui_waveform_icon_157544.ico') else None,
)
'''
    
    with open('shm_app_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 配置文件已创建: shm_app_fixed.spec")
    return True

def build_application():
    """构建应用程序"""
    print("\n=== 开始构建应用程序 ===")
    
    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 清理旧的构建目录")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 清理旧的分发目录")
    
    # 使用 spec 文件构建
    cmd = [sys.executable, '-m', 'PyInstaller', 'shm_app_fixed.spec']
    
    print(f"🔨 执行构建命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功!")
            print(f"📦 可执行文件位置: dist/简谐振动的合成演示平台.exe")
            return True
        else:
            print("❌ 构建失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现异常: {e}")
        return False

def test_executable():
    """测试可执行文件"""
    print("\n=== 测试可执行文件 ===")
    
    exe_path = Path('dist/简谐振动的合成演示平台.exe')
    
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"✅ 可执行文件存在: {exe_path}")
    print(f"📏 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    # 这里可以添加更多测试，比如启动程序并检查是否正常运行
    print("💡 请手动测试可执行文件是否能正常启动")
    
    return True

def main():
    """主函数"""
    print("简谐运动模拟系统 - PyInstaller 打包工具")
    print("=" * 50)
    
    # 检查当前目录和父目录
    if os.path.exists('start.py'):
        # 在根目录运行
        start_py_path = 'start.py'
    elif os.path.exists('../start.py'):
        # 在 build_scripts 目录运行
        start_py_path = '../start.py'
        os.chdir('..')  # 切换到根目录
    else:
        print("❌ 找不到 start.py 文件，请在项目根目录或 build_scripts 目录中运行此脚本")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请安装缺失的模块")
        return False
    
    # 创建配置文件
    if not create_spec_file():
        print("❌ 配置文件创建失败")
        return False
    
    # 构建应用程序
    if not build_application():
        print("❌ 应用程序构建失败")
        return False
    
    # 测试可执行文件
    if not test_executable():
        print("❌ 可执行文件测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 打包完成!")
    print("📦 可执行文件: dist/简谐振动的合成演示平台.exe")
    print("💡 建议在不同环境中测试程序运行")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
