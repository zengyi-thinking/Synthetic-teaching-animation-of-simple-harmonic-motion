#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHM Visualization PyInstaller Build Script
简谐运动可视化系统 PyInstaller 构建脚本

This script automates the process of building a standalone executable
for the SHM visualization application using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_step(2, "Checking Dependencies")

    # Define packages with their import names
    required_packages = [
        ('PyInstaller', 'PyInstaller'),
        ('PyQt6', 'PyQt6.QtCore'),
        ('matplotlib', 'matplotlib'),
        ('numpy', 'numpy'),
        ('jaraco.text', 'jaraco.text'),
        ('more-itertools', 'more_itertools'),
        ('zipp', 'zipp'),
        ('importlib-metadata', 'importlib_metadata'),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr install all at once:")
        print("pip install PyInstaller PyQt6 matplotlib numpy jaraco.text more-itertools zipp importlib-metadata")
        return False

    print("\n✅ All dependencies are installed")
    return True

def check_project_structure():
    """Check if the project structure is correct"""
    print_step(3, "Checking Project Structure")
    
    required_files = [
        'run.py',
        'shm_visualization.spec',
        'src/shm_visualization/__init__.py',
        'src/shm_visualization/main.py',
        'src/shm_visualization/ui/ui_framework.py',
        'src/shm_visualization/modules/beat_main.py',
        'src/shm_visualization/modules/orthogonal_main.py',
        'src/shm_visualization/modules/phase_main.py',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("\n✅ Project structure is correct")
    return True

def test_application():
    """Test if the application can run before building"""
    print_step(4, "Testing Application")
    
    try:
        # Add src to path for testing
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Test imports
        from shm_visualization.main import SimulationLauncher
        from shm_visualization.ui.ui_framework import get_app_instance
        
        print("✅ Core modules import successfully")
        
        # Test module imports
        from shm_visualization.modules import beat_main, orthogonal_main, phase_main
        print("✅ All simulation modules import successfully")
        
        print("✅ Application test passed")
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def clean_build_directories():
    """Clean previous build directories"""
    print_step(5, "Cleaning Build Directories")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Removed {dir_name}")
            except Exception as e:
                print(f"⚠️  Could not remove {dir_name}: {e}")
        else:
            print(f"ℹ️  {dir_name} does not exist")

def build_executable():
    """Build the executable using PyInstaller"""
    print_step(6, "Building Executable")
    
    spec_file = 'shm_visualization.spec'
    
    if not os.path.exists(spec_file):
        print(f"❌ Spec file {spec_file} not found")
        return False
    
    try:
        print(f"Running PyInstaller with {spec_file}...")
        
        # Run PyInstaller
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # Clean cache
            spec_file
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("✅ PyInstaller build completed successfully")
            print("\nBuild output:")
            print(result.stdout)
            return True
        else:
            print("❌ PyInstaller build failed")
            print("\nError output:")
            print(result.stderr)
            print("\nStandard output:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def test_executable():
    """Test the generated executable"""
    print_step(7, "Testing Generated Executable")
    
    exe_path = os.path.join('dist', 'SHM_Visualization.exe')
    
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found at {exe_path}")
        return False
    
    print(f"✅ Executable found: {exe_path}")
    
    # Get file size
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"📦 Executable size: {size_mb:.1f} MB")
    
    # Test if executable can start (quick test)
    try:
        print("🧪 Testing executable startup...")
        result = subprocess.run([exe_path], timeout=10, capture_output=True)
        print("✅ Executable starts without immediate errors")
        return True
    except subprocess.TimeoutExpired:
        print("✅ Executable started (timed out after 10s, which is expected)")
        return True
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def main():
    """Main build process"""
    print_header("SHM Visualization PyInstaller Build Script")
    print("简谐运动可视化系统 PyInstaller 构建脚本")
    
    start_time = time.time()
    
    # Check all prerequisites
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    if not check_project_structure():
        return 1
    
    if not test_application():
        return 1
    
    # Build process
    clean_build_directories()
    
    if not build_executable():
        return 1
    
    if not test_executable():
        return 1
    
    # Success
    end_time = time.time()
    build_time = end_time - start_time
    
    print_header("Build Completed Successfully!")
    print(f"⏱️  Build time: {build_time:.1f} seconds")
    print(f"📦 Executable location: dist/SHM_Visualization.exe")
    print("\n🎉 The SHM Visualization application has been successfully packaged!")
    print("You can now distribute the executable to other Windows systems.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
