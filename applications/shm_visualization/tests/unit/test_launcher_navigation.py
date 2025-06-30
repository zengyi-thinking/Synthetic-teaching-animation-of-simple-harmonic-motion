#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动器导航功能测试脚本
Launcher Navigation Functionality Test Script
"""

import os
import sys
import time
import traceback
from pathlib import Path

# 添加父目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_module_imports():
    """测试模块导入功能"""
    print("=== 测试模块导入功能 ===")
    
    modules_to_test = [
        ("ui.ui_framework", "get_app_instance"),
        ("modules.orthogonal_main", "main"),
        ("modules.beat_main", "main"), 
        ("modules.phase_main", "main"),
        ("start", "SimulationLauncher")
    ]
    
    success_count = 0
    for module_name, function_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            if hasattr(module, function_name):
                print(f"✅ {module_name}.{function_name}")
                success_count += 1
            else:
                print(f"❌ {module_name} 缺少 {function_name} 函数")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name}: 未知错误 - {e}")
    
    print(f"\n📊 导入测试结果: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)

def test_launcher_creation():
    """测试启动器创建"""
    print("\n=== 测试启动器创建 ===")
    
    try:
        from ui.ui_framework import get_app_instance
        from start import SimulationLauncher
        
        # 创建应用实例
        app = get_app_instance()
        print("✅ QApplication 创建成功")
        
        # 创建启动器
        launcher = SimulationLauncher()
        print("✅ SimulationLauncher 创建成功")
        
        # 检查启动器属性
        if hasattr(launcher, 'run_module'):
            print("✅ run_module 方法存在")
        else:
            print("❌ run_module 方法不存在")
            return False
            
        if hasattr(launcher, 'current_module_window'):
            print("✅ current_module_window 属性存在")
        else:
            print("❌ current_module_window 属性不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 启动器创建失败: {e}")
        traceback.print_exc()
        return False

def test_module_main_functions():
    """测试各模块的main函数"""
    print("\n=== 测试模块main函数 ===")
    
    modules = [
        "modules.orthogonal_main",
        "modules.beat_main", 
        "modules.phase_main"
    ]
    
    success_count = 0
    for module_name in modules:
        try:
            module = __import__(module_name, fromlist=['main'])
            
            if not hasattr(module, 'main'):
                print(f"❌ {module_name}: 没有main函数")
                continue
            
            # 检查main函数是否可调用
            main_func = getattr(module, 'main')
            if callable(main_func):
                print(f"✅ {module_name}: main函数可调用")
                success_count += 1
            else:
                print(f"❌ {module_name}: main不是函数")
                
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 模块测试结果: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)

def test_module_instantiation():
    """测试模块实例化（不显示窗口）"""
    print("\n=== 测试模块实例化 ===")
    
    try:
        from ui.ui_framework import get_app_instance
        
        # 确保有应用实例
        app = get_app_instance()
        
        modules = [
            ("modules.orthogonal_main", "OrthogonalHarmonicWindow"),
            ("modules.beat_main", "BeatHarmonicWindow"),
            ("modules.phase_main", "PhaseHarmonicWindow")
        ]
        
        success_count = 0
        for module_name, class_name in modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                window_class = getattr(module, class_name)
                
                # 创建窗口实例（但不显示）
                window = window_class()
                print(f"✅ {module_name}.{class_name} 实例化成功")
                
                # 检查窗口是否有必要的方法
                if hasattr(window, 'show'):
                    print(f"  ✅ {class_name} 有show方法")
                if hasattr(window, 'close'):
                    print(f"  ✅ {class_name} 有close方法")
                
                # 清理窗口
                window.close()
                success_count += 1
                
            except Exception as e:
                print(f"❌ {module_name}.{class_name}: {e}")
                traceback.print_exc()
        
        print(f"\n📊 实例化测试结果: {success_count}/{len(modules)} 成功")
        return success_count == len(modules)
        
    except Exception as e:
        print(f"❌ 模块实例化测试失败: {e}")
        traceback.print_exc()
        return False

def test_launcher_module_loading():
    """测试启动器的模块加载逻辑"""
    print("\n=== 测试启动器模块加载逻辑 ===")
    
    try:
        from ui.ui_framework import get_app_instance
        from start import SimulationLauncher
        
        # 创建应用和启动器
        app = get_app_instance()
        launcher = SimulationLauncher()
        
        # 测试模块路径检查逻辑
        test_modules = [
            "modules.orthogonal_main",
            "modules.beat_main",
            "modules.phase_main"
        ]
        
        success_count = 0
        for module_name in test_modules:
            try:
                # 模拟启动器的路径检查逻辑
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                
                module_path_parts = module_name.split('.')
                module_file = os.path.join(parent_dir, *module_path_parts[:-1], f"{module_path_parts[-1]}.py")
                
                if os.path.exists(module_file):
                    print(f"✅ {module_name}: 文件路径正确 - {module_file}")
                    success_count += 1
                else:
                    print(f"❌ {module_name}: 文件不存在 - {module_file}")
                    
            except Exception as e:
                print(f"❌ {module_name}: 路径检查失败 - {e}")
        
        print(f"\n📊 路径检查结果: {success_count}/{len(test_modules)} 成功")
        return success_count == len(test_modules)
        
    except Exception as e:
        print(f"❌ 启动器模块加载测试失败: {e}")
        traceback.print_exc()
        return False

def test_packaged_environment():
    """测试打包环境特有的问题"""
    print("\n=== 测试打包环境兼容性 ===")
    
    try:
        # 检查是否在打包环境中运行
        if getattr(sys, 'frozen', False):
            print("✅ 检测到打包环境 (PyInstaller)")
            
            # 检查资源路径
            if hasattr(sys, '_MEIPASS'):
                print(f"✅ 临时资源目录: {sys._MEIPASS}")
            
            # 检查当前工作目录
            print(f"📁 当前工作目录: {os.getcwd()}")
            
            # 检查Python路径
            print("📚 Python路径:")
            for i, path in enumerate(sys.path[:5]):  # 只显示前5个
                print(f"  {i}: {path}")
                
        else:
            print("ℹ️  运行在开发环境中")
        
        # 检查关键文件是否可访问
        key_files = [
            "start.py",
            "modules/orthogonal_main.py",
            "modules/beat_main.py", 
            "modules/phase_main.py",
            "ui/ui_framework.py"
        ]
        
        accessible_count = 0
        for file_path in key_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} 可访问")
                accessible_count += 1
            else:
                print(f"❌ {file_path} 不可访问")
        
        print(f"\n📊 文件访问结果: {accessible_count}/{len(key_files)} 成功")
        return accessible_count == len(key_files)
        
    except Exception as e:
        print(f"❌ 打包环境测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("简谐运动模拟系统 - 启动器导航功能测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("模块导入", test_module_imports),
        ("启动器创建", test_launcher_creation),
        ("模块main函数", test_module_main_functions),
        ("模块实例化", test_module_instantiation),
        ("启动器模块加载", test_launcher_module_loading),
        ("打包环境兼容性", test_packaged_environment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
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
        print("🎉 所有测试通过！启动器导航功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，需要进一步调试")
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
        traceback.print_exc()
        sys.exit(1)
