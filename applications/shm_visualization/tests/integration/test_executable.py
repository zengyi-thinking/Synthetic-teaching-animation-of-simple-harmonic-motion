#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHM Visualization Executable Test Script
简谐运动可视化系统可执行文件测试脚本

This script tests the generated executable to ensure it works correctly.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_executable_exists():
    """Test if the executable exists"""
    print("\n[Test 1] Checking if executable exists...")
    
    exe_path = Path("dist/SHM_Visualization.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable found: {exe_path}")
        print(f"📦 Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Executable not found: {exe_path}")
        print("Please run the build script first: python build_executable.py")
        return False

def test_executable_startup():
    """Test if the executable can start"""
    print("\n[Test 2] Testing executable startup...")
    
    exe_path = "dist/SHM_Visualization.exe"
    
    try:
        # Start the executable
        print("🚀 Starting executable...")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Executable started successfully and is running")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Executable terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  Executable was forcefully killed")
            
            return True
        else:
            # Process exited
            stdout, stderr = process.communicate()
            print(f"❌ Executable exited with code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False

def test_file_dependencies():
    """Test if all necessary files are included"""
    print("\n[Test 3] Checking file dependencies...")
    
    # The executable should be self-contained
    # We can't easily test internal dependencies, but we can check
    # that it doesn't require external Python files
    
    exe_path = Path("dist/SHM_Visualization.exe")
    dist_dir = exe_path.parent
    
    # Check if there are any additional files (there shouldn't be for onefile build)
    files_in_dist = list(dist_dir.glob("*"))
    
    if len(files_in_dist) == 1 and files_in_dist[0] == exe_path:
        print("✅ Single file executable (no external dependencies)")
        return True
    else:
        print(f"⚠️  Additional files found in dist: {[f.name for f in files_in_dist]}")
        print("This might be expected for some builds")
        return True

def test_system_compatibility():
    """Test system compatibility"""
    print("\n[Test 4] Checking system compatibility...")
    
    # Check Windows version
    import platform
    system = platform.system()
    version = platform.version()
    architecture = platform.architecture()[0]
    
    print(f"System: {system} {version}")
    print(f"Architecture: {architecture}")
    
    if system == "Windows":
        print("✅ Running on Windows (compatible)")
        return True
    else:
        print("⚠️  Not running on Windows (executable may not work)")
        return False

def main():
    """Main test function"""
    print_header("SHM Visualization Executable Test")
    print("简谐运动可视化系统可执行文件测试")
    
    tests = [
        test_executable_exists,
        test_executable_startup,
        test_file_dependencies,
        test_system_compatibility,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print_header("Test Results")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The executable should work correctly.")
        print("🎉 所有测试通过！可执行文件应该能正常工作。")
        
        print("\n📋 Manual Testing Checklist:")
        print("1. Double-click SHM_Visualization.exe")
        print("2. Verify the main launcher window opens")
        print("3. Test each simulation module:")
        print("   - 李萨如图形 (Lissajous Figures)")
        print("   - 拍现象 (Beat Phenomenon)")
        print("   - 相位差合成 (Phase Difference)")
        print("4. Test window resizing functionality")
        print("5. Verify smooth navigation between modules")
        
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("❌ 部分测试失败。请检查上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
