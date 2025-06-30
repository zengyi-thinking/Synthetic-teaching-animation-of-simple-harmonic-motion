#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版PyInstaller打包脚本 - 解决模块导入问题
Fixed PyInstaller Build Script - Resolves Module Import Issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_paths():
    """设置路径"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir
    src_dir = project_root / "src"
    
    # 添加src目录到Python路径
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    
    return project_root, src_dir

def check_dependencies():
    """检查依赖模块"""
    print("=== 检查依赖模块 ===")
    
    required_modules = [
        'PyQt6',
        'matplotlib',
        'numpy',
        'shm_visualization.main',
        'shm_visualization.ui.ui_framework',
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ 缺少依赖模块: {missing_modules}")
        return False
    
    print("\n✅ 所有依赖模块检查通过")
    return True

def create_fixed_spec_file(project_root, src_dir):
    """创建修复版PyInstaller配置文件"""
    print("\n=== 创建修复版PyInstaller配置文件 ===")
    
    # 确保构建目录存在
    build_dir = project_root / "build" / "specs"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # 路径配置
    src_path = str(src_dir)
    icon_path = str(project_root / "assets" / "icons" / "gui_waveform_icon_157544.ico")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 路径配置
src_path = r'{src_path}'
icon_path = r'{icon_path}'

# 添加源代码路径到sys.path
sys.path.insert(0, src_path)

# 数据文件收集
datas = []

# 收集matplotlib数据文件
try:
    datas += collect_data_files('matplotlib')
except:
    pass

# 收集PyQt6数据文件
try:
    datas += collect_data_files('PyQt6')
except:
    pass

# 添加整个shm_visualization包作为数据
shm_viz_path = os.path.join(src_path, 'shm_visualization')
if os.path.exists(shm_viz_path):
    for root, dirs, files in os.walk(shm_viz_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, src_path)
                datas.append((file_path, os.path.dirname(rel_path)))

# 隐式导入模块 - 完整列表
hiddenimports = [
    # PyQt6完整导入
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.sip',
    'PyQt6.QtOpenGL',
    
    # matplotlib完整导入
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends._backend_agg',
    'matplotlib.figure',
    'matplotlib.pyplot',
    'matplotlib.font_manager',
    'matplotlib.patches',
    'matplotlib.animation',
    
    # numpy完整导入
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib.format',
    'numpy.random',
    'numpy.linalg',
    'numpy.fft',
    
    # shm_visualization包 - 完整导入
    'shm_visualization',
    'shm_visualization.main',
    'shm_visualization.ui',
    'shm_visualization.ui.ui_framework',
    'shm_visualization.ui.params_controller',
    'shm_visualization.modules',
    'shm_visualization.modules.orthogonal_main',
    'shm_visualization.modules.beat_main',
    'shm_visualization.modules.phase_main',
    'shm_visualization.animations',
    'shm_visualization.animations.orthogonal_animation',
    'shm_visualization.animations.beat_animation',
    'shm_visualization.animations.phase_animation',
    
    # 标准库模块
    'importlib',
    'importlib.util',
    'traceback',
    'sys',
    'os',
    'pathlib',
    'threading',
    'time',
    'math',
    'functools',
]

# 收集子模块
try:
    hiddenimports += collect_submodules('PyQt6')
except:
    pass

try:
    hiddenimports += collect_submodules('matplotlib')
except:
    pass

try:
    hiddenimports += collect_submodules('shm_visualization')
except:
    pass

a = Analysis(
    [r'{project_root / "run.py"}'],
    pathex=[src_path],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest'],
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
    name='简谐振动的合成演示平台_修复版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 设置为True以便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
)
'''
    
    spec_file = build_dir / "shm_fixed.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ 修复版配置文件已创建: {spec_file}")
    return spec_file

def build_application(project_root, spec_file):
    """构建应用程序"""
    print("\n=== 开始构建修复版应用程序 ===")
    
    # 清理旧的构建目录
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        print("🧹 清理旧的分发目录")
        shutil.rmtree(dist_dir)
    
    # 执行PyInstaller构建
    python_exe = sys.executable
    build_cmd = [python_exe, '-m', 'PyInstaller', str(spec_file)]
    
    print(f"🔨 执行构建命令: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, cwd=project_root, 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功!")
        else:
            print("❌ 构建失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False
    
    return True

def test_executable(project_root):
    """测试可执行文件"""
    print("\n=== 测试可执行文件 ===")
    
    exe_path = project_root / "dist" / "简谐振动的合成演示平台_修复版.exe"
    
    if exe_path.exists():
        print(f"✅ 可执行文件存在: {exe_path}")
        
        # 获取文件大小
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"📏 文件大小: {file_size:.1f} MB")
        
        return True
    else:
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False

def main():
    """主函数"""
    print("简谐运动可视化系统 - 修复版PyInstaller打包工具")
    print("=" * 60)
    
    # 设置路径
    project_root, src_dir = setup_paths()
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 源代码目录: {src_dir}")
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请安装缺少的模块")
        return 1
    
    # 创建配置文件
    spec_file = create_fixed_spec_file(project_root, src_dir)
    if not spec_file:
        print("❌ 配置文件创建失败")
        return 1
    
    # 构建应用程序
    if not build_application(project_root, spec_file):
        print("❌ 应用程序构建失败")
        return 1
    
    # 测试可执行文件
    if not test_executable(project_root):
        print("❌ 可执行文件测试失败")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 修复版打包完成!")
    print("📦 可执行文件: dist/简谐振动的合成演示平台_修复版.exe")
    print("💡 现在应该可以正常运行，不会出现模块导入错误")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断构建过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
