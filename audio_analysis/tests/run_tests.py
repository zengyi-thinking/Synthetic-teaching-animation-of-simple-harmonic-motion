#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for Audio Analyzer
Runs all test scripts in the tests directory
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.append('..')

def run_test_script(script_name):
    """Run a single test script"""
    print(f"\n{'='*60}")
    print(f"Running {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Audio Analyzer Test Suite")
    print("Running all test scripts...")
    
    test_scripts = [
        'test_audio_analysis.py',
        'test_final_fixes.py', 
        'test_sine_wave_display.py',
        'test_ui_improvements.py',
        'demo_audio_analysis.py'
    ]
    
    results = []
    
    for script in test_scripts:
        if os.path.exists(script):
            success = run_test_script(script)
            results.append((script, success))
        else:
            print(f"⚠️ Test script not found: {script}")
            results.append((script, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Results Summary")
    print(f"{'='*60}")
    
    passed = 0
    for script, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{script}: {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
