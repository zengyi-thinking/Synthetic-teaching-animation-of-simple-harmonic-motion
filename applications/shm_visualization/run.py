#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Harmonic Motion Visualization - Main Entry Point
简谐运动可视化系统 - 主入口点

This script serves as the main entry point for the SHM visualization application.
It imports and executes the main application from the installed package.
"""

import sys
from pathlib import Path

def setup_python_path():
    """Setup Python path to include the src directory (fallback for development)"""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()

    # Add the src directory to Python path as fallback
    src_dir = script_dir / "src"
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"Added to Python path: {src_dir}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Simple Harmonic Motion Visualization System")
    print("简谐运动可视化系统")
    print("=" * 60)
    print("Version: 1.0.0")
    print("Author: SHM Visualization Team")
    print("=" * 60)

    try:
        # Try to import the installed package first
        from shm_visualization.main import main as app_main

        print("Starting application...")
        print("正在启动应用程序...")

        # Run the application and return its exit code
        exit_code = app_main()
        return exit_code if exit_code is not None else 0

    except ImportError as e:
        print(f"Package import failed, trying development mode: {e}")
        print("包导入失败，尝试开发模式...")

        # Fallback: Setup Python path and try again
        setup_python_path()

        try:
            from shm_visualization.main import main as app_main

            print("Starting application in development mode...")
            print("以开发模式启动应用程序...")

            # Run the application and return its exit code
            exit_code = app_main()
            return exit_code if exit_code is not None else 0

        except ImportError as e2:
            print(f"Import Error: {e2}")
            print("Please ensure the application is properly installed or run:")
            print("请确保应用程序已正确安装或运行：")
            print("  pip install -e .")
            return 1

    except Exception as e:
        print(f"Error starting application: {e}")
        print(f"启动应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
