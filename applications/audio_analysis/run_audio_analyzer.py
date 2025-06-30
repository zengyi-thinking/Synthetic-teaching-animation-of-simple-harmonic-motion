#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析器启动脚本
独立的桌面应用程序，用于音频信号的简谐波分解与重构
"""

import sys
import os

def main():
    """启动音频分析器"""
    print("🎵 启动音频分析器...")
    print("=" * 50)
    print("音频分析器 - 简谐波分解与重构工具")
    print("版本: 1.0.0")
    print("功能: 音频信号的傅里叶分析、频率分解、交互式编辑、音频重构")
    print("=" * 50)
    
    # 确保在正确的目录中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    try:
        # 导入并启动主应用
        from audio_editor_ui import main as audio_main
        audio_main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖库已正确安装")
        print("运行: python install_dependencies.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
