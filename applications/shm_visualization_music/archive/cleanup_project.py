# -*- coding: utf-8 -*-
"""
项目文件清理和整理脚本
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """清理和整理项目文件"""
    
    print("🧹 开始项目文件清理和整理...")
    
    # 当前目录
    current_dir = Path(".")
    
    # 创建子目录结构
    directories_to_create = [
        "docs",           # 文档目录
        "tests",          # 测试文件目录
        "build_files",    # 构建相关文件
        "archive"         # 归档目录
    ]
    
    for dir_name in directories_to_create:
        dir_path = current_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"✅ 创建目录: {dir_name}")
    
    # 文件分类规则
    file_categories = {
        "docs": [
            "README.md",
            "INTERFACE_REFACTOR_SUMMARY.md",
            "LAYOUT_OPTIMIZATION_SUMMARY.md", 
            "UI_LAYOUT_REORGANIZATION_SUMMARY.md",
            "UNIFIED_VISUALIZATION_REFACTOR_SUMMARY.md"
        ],
        "tests": [
            "test_interface_refactor.py",
            "test_layout_changes.py",
            "test_layout_optimization.py",
            "test_refactor_simple.py",
            "test_unified_visualization.py",
            "test_waveform_fix.py",
            "debug_waveform_display.py",
            "verify_layout_functionality.py"
        ],
        "build_files": [
            "app.spec",
            "requirements.txt"
        ],
        "archive": [
            "cleanup_project.py"  # 这个脚本本身也归档
        ]
    }
    
    # 移动文件到对应目录
    for category, files in file_categories.items():
        target_dir = current_dir / category
        
        for file_name in files:
            source_file = current_dir / file_name
            target_file = target_dir / file_name
            
            if source_file.exists() and source_file != target_file:
                try:
                    shutil.move(str(source_file), str(target_file))
                    print(f"📁 移动文件: {file_name} -> {category}/")
                except Exception as e:
                    print(f"❌ 移动文件失败 {file_name}: {e}")
    
    # 清理构建目录
    build_dirs = ["build", "dist", "__pycache__"]
    for build_dir in build_dirs:
        dir_path = current_dir / build_dir
        if dir_path.exists():
            try:
                if build_dir == "__pycache__":
                    # 保留__pycache__但清理内容
                    for file in dir_path.glob("*"):
                        if file.is_file():
                            file.unlink()
                    print(f"🧹 清理目录内容: {build_dir}")
                else:
                    # 移动到build_files目录
                    target_path = current_dir / "build_files" / build_dir
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.move(str(dir_path), str(target_path))
                    print(f"📁 移动构建目录: {build_dir} -> build_files/")
            except Exception as e:
                print(f"❌ 处理目录失败 {build_dir}: {e}")
    
    # 创建项目结构说明文件
    structure_content = """# 项目文件结构说明

## 核心功能文件
- `app.py` - 主应用程序入口
- `run.py` - 运行脚本
- `harmonic_synthesizer_ui.py` - 简谐波合成器界面
- `audio_analysis_ui.py` - 音频分析界面
- `visualization_engine.py` - 可视化引擎
- `audio_engine.py` - 音频引擎
- `audio_analyzer.py` - 音频分析器
- `harmonic_core.py` - 简谐运动核心算法

## 目录结构
- `docs/` - 项目文档和总结报告
- `tests/` - 测试文件和调试脚本
- `build_files/` - 构建相关文件和目录
- `archive/` - 归档文件

## 使用说明
1. 运行主程序: `python app.py` 或 `python run.py`
2. 查看文档: 参考 `docs/` 目录下的文档
3. 运行测试: 使用 `tests/` 目录下的测试脚本

## 最新重构
- 统一可视化面板: 合并了双面板设计，实现垂直堆叠布局
- 波形显示优化: 修复了波形显示问题，确保清晰的线条显示
- 界面布局优化: 改进了用户体验和教学效果
"""
    
    with open(current_dir / "PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(structure_content)
    print("📝 创建项目结构说明文件")
    
    # 显示最终的项目结构
    print("\n📊 项目清理完成，最终结构:")
    print("shm_visualization_music/")
    print("├── 核心文件:")
    core_files = [
        "app.py", "run.py", "harmonic_synthesizer_ui.py", 
        "audio_analysis_ui.py", "visualization_engine.py",
        "audio_engine.py", "audio_analyzer.py", "harmonic_core.py"
    ]
    for file in core_files:
        if (current_dir / file).exists():
            print(f"│   ├── {file}")
    
    print("├── docs/ (文档)")
    print("├── tests/ (测试文件)")
    print("├── build_files/ (构建文件)")
    print("├── archive/ (归档文件)")
    print("└── PROJECT_STRUCTURE.md (结构说明)")
    
    print("\n✅ 项目文件清理和整理完成！")
    print("🎯 核心功能文件保留在根目录，便于直接运行")
    print("📚 文档和测试文件已分类整理到对应目录")

if __name__ == "__main__":
    cleanup_project()
