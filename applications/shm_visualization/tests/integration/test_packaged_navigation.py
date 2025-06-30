#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包应用导航功能测试脚本
Packaged Application Navigation Test Script
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def test_packaged_executable_launch():
    """测试打包可执行文件启动"""
    print("=== 测试打包可执行文件启动 ===")
    
    exe_path = "dist/简谐振动的合成演示平台.exe"
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    print(f"✅ 可执行文件存在: {exe_path}")
    
    # 获取文件大小
    size_mb = os.path.getsize(exe_path) / 1024 / 1024
    print(f"📏 文件大小: {size_mb:.1f} MB")
    
    return True

def test_packaged_executable_startup():
    """测试打包可执行文件启动过程"""
    print("\n=== 测试打包可执行文件启动过程 ===")
    
    exe_path = "dist/简谐振动的合成演示平台.exe"
    
    try:
        print("🚀 启动可执行文件...")
        
        # 启动进程并捕获输出
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 等待一段时间让程序启动
        time.sleep(5)
        
        # 检查进程状态
        if process.poll() is None:
            print("✅ 程序成功启动并正在运行")
            
            # 等待更长时间以观察是否稳定
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ 程序运行稳定")
                
                # 终止进程
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ 程序正常终止")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print("⚠️  程序被强制终止")
                
                return True
            else:
                print("❌ 程序启动后不稳定")
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"错误输出: {stderr}")
                return False
        else:
            print("❌ 程序启动失败或立即退出")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"错误输出: {stderr}")
            if stdout:
                print(f"标准输出: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        return False

def test_packaged_executable_with_interaction():
    """测试打包可执行文件的交互功能"""
    print("\n=== 测试打包可执行文件交互功能 ===")
    
    exe_path = "dist/简谐振动的合成演示平台.exe"
    
    try:
        print("🚀 启动可执行文件进行交互测试...")
        
        # 启动进程
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 等待程序启动
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ 程序启动成功，正在运行")
            
            # 模拟用户交互 - 发送一些按键
            print("🖱️  模拟用户交互...")
            
            # 等待更长时间以观察程序行为
            time.sleep(5)
            
            if process.poll() is None:
                print("✅ 程序在交互期间保持稳定")
                
                # 正常终止
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print("✅ 程序正常响应终止信号")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print("⚠️  程序需要强制终止")
                
                return True
            else:
                print("❌ 程序在交互期间崩溃")
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"错误输出: {stderr}")
                return False
        else:
            print("❌ 程序启动失败")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"错误输出: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 交互测试失败: {e}")
        return False

def test_packaged_executable_error_output():
    """测试打包可执行文件的错误输出"""
    print("\n=== 分析打包可执行文件错误输出 ===")
    
    exe_path = "dist/简谐振动的合成演示平台.exe"
    
    try:
        print("🔍 启动程序并收集详细输出...")
        
        # 启动进程并等待完成或超时
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 等待程序运行一段时间
        try:
            stdout, stderr = process.communicate(timeout=15)
            
            print("📋 程序输出分析:")
            if stdout:
                print("标准输出:")
                print(stdout[:1000])  # 限制输出长度
            
            if stderr:
                print("错误输出:")
                print(stderr[:1000])  # 限制输出长度
                
                # 分析常见错误模式
                if "ModuleNotFoundError" in stderr:
                    print("🔍 检测到模块导入错误")
                if "ImportError" in stderr:
                    print("🔍 检测到导入错误")
                if "Permission" in stderr:
                    print("🔍 检测到权限错误")
                if "No module named" in stderr:
                    print("🔍 检测到模块缺失错误")
            
            return_code = process.returncode
            print(f"📊 程序退出码: {return_code}")
            
            if return_code == 0:
                print("✅ 程序正常退出")
                return True
            else:
                print("❌ 程序异常退出")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ 程序运行超时，正在终止...")
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
                print("✅ 程序在超时后正常终止")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  程序需要强制终止")
                return False
            
    except Exception as e:
        print(f"❌ 错误输出分析失败: {e}")
        return False

def main():
    """主测试函数"""
    print("简谐运动模拟系统 - 打包应用导航功能测试")
    print("=" * 60)
    
    # 切换到正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    print(f"📁 工作目录: {project_root}")
    
    # 运行测试
    tests = [
        ("可执行文件存在性", test_packaged_executable_launch),
        ("启动过程", test_packaged_executable_startup),
        ("交互功能", test_packaged_executable_with_interaction),
        ("错误输出分析", test_packaged_executable_error_output)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
            print(f"{'='*60}")
        except Exception as e:
            print(f"❌ {test_name} 测试发生异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！打包应用导航功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，需要进一步调试")
        
        # 提供诊断建议
        print("\n🔧 诊断建议:")
        print("1. 检查是否有其他程序实例正在运行")
        print("2. 确认所有依赖模块都已正确打包")
        print("3. 验证模块导入路径是否正确")
        print("4. 检查是否有权限或安全软件阻止")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
