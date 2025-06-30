#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块导航功能测试脚本 - 模拟实际按钮点击
Module Navigation Test Script - Simulate Actual Button Clicks
"""

import os
import sys
import time
import traceback

# 添加父目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_launcher_module_navigation():
    """测试启动器的模块导航功能"""
    print("=== 测试启动器模块导航功能 ===")
    
    try:
        from ui.ui_framework import get_app_instance
        from start import SimulationLauncher
        
        # 创建应用实例
        app = get_app_instance()
        print("✅ QApplication 创建成功")
        
        # 创建启动器
        launcher = SimulationLauncher()
        print("✅ SimulationLauncher 创建成功")
        
        # 测试各个模块的导航
        test_modules = [
            "modules.orthogonal_main",
            "modules.beat_main",
            "modules.phase_main"
        ]
        
        success_count = 0
        for module_name in test_modules:
            print(f"\n🧪 测试模块: {module_name}")
            
            try:
                # 模拟 run_module 方法的调用
                print(f"  📞 调用 launcher.run_module('{module_name}')")
                
                # 保存原始的 show 方法以避免实际显示窗口
                original_show = launcher.show
                show_called = False
                
                def mock_show():
                    nonlocal show_called
                    show_called = True
                    print("  📱 启动器 show() 被调用")
                
                launcher.show = mock_show
                
                # 调用 run_module
                launcher.run_module(module_name)
                
                # 检查结果
                if launcher.current_module_window:
                    print(f"  ✅ 模块窗口创建成功: {type(launcher.current_module_window).__name__}")
                    
                    # 检查窗口是否有必要的方法
                    if hasattr(launcher.current_module_window, 'show'):
                        print("  ✅ 窗口有 show 方法")
                    if hasattr(launcher.current_module_window, 'close'):
                        print("  ✅ 窗口有 close 方法")
                    
                    # 清理窗口
                    launcher.current_module_window.close()
                    launcher.current_module_window = None
                    
                    success_count += 1
                    print(f"  ✅ {module_name} 导航测试成功")
                else:
                    print(f"  ❌ {module_name} 未创建窗口")
                
                # 恢复原始方法
                launcher.show = original_show
                
            except Exception as e:
                print(f"  ❌ {module_name} 导航测试失败: {e}")
                traceback.print_exc()
        
        print(f"\n📊 模块导航测试结果: {success_count}/{len(test_modules)} 成功")
        return success_count == len(test_modules)
        
    except Exception as e:
        print(f"❌ 启动器模块导航测试失败: {e}")
        traceback.print_exc()
        return False

def test_module_window_lifecycle():
    """测试模块窗口生命周期"""
    print("\n=== 测试模块窗口生命周期 ===")
    
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
            print(f"\n🧪 测试模块生命周期: {module_name}")
            
            try:
                # 导入模块
                module = __import__(module_name, fromlist=[class_name])
                print(f"  ✅ 模块导入成功")
                
                # 调用 main 函数
                window = module.main()
                print(f"  ✅ main() 函数调用成功")
                
                if window:
                    print(f"  ✅ 窗口创建成功: {type(window).__name__}")
                    
                    # 测试窗口方法
                    if hasattr(window, 'show'):
                        print("  ✅ 窗口有 show 方法")
                        # 不实际调用 show() 以避免显示窗口
                    
                    if hasattr(window, 'close'):
                        print("  ✅ 窗口有 close 方法")
                        window.close()  # 清理窗口
                    
                    success_count += 1
                    print(f"  ✅ {module_name} 生命周期测试成功")
                else:
                    print(f"  ❌ {module_name} main() 返回 None")
                
            except Exception as e:
                print(f"  ❌ {module_name} 生命周期测试失败: {e}")
                traceback.print_exc()
        
        print(f"\n📊 模块生命周期测试结果: {success_count}/{len(modules)} 成功")
        return success_count == len(modules)
        
    except Exception as e:
        print(f"❌ 模块生命周期测试失败: {e}")
        traceback.print_exc()
        return False

def test_launcher_button_simulation():
    """测试启动器按钮模拟"""
    print("\n=== 测试启动器按钮模拟 ===")
    
    try:
        from ui.ui_framework import get_app_instance
        from start import SimulationLauncher
        from PyQt6.QtCore import QTimer
        
        # 创建应用实例
        app = get_app_instance()
        
        # 创建启动器
        launcher = SimulationLauncher()
        
        # 模拟按钮点击的测试结果
        test_results = []
        
        # 测试模块列表
        modules = [
            "modules.orthogonal_main",
            "modules.beat_main", 
            "modules.phase_main"
        ]
        
        for module_name in modules:
            print(f"\n🖱️  模拟点击模块按钮: {module_name}")
            
            try:
                # 重置状态
                launcher.current_module_window = None
                
                # 模拟按钮点击 - 直接调用 run_module
                launcher.run_module(module_name)
                
                # 检查结果
                if launcher.current_module_window:
                    print(f"  ✅ 模块窗口创建: {type(launcher.current_module_window).__name__}")
                    
                    # 模拟窗口关闭
                    if hasattr(launcher.current_module_window, 'close'):
                        launcher.current_module_window.close()
                    
                    test_results.append(True)
                    print(f"  ✅ {module_name} 按钮模拟成功")
                else:
                    print(f"  ❌ {module_name} 按钮模拟失败 - 无窗口创建")
                    test_results.append(False)
                
            except Exception as e:
                print(f"  ❌ {module_name} 按钮模拟异常: {e}")
                test_results.append(False)
        
        success_count = sum(test_results)
        print(f"\n📊 按钮模拟测试结果: {success_count}/{len(modules)} 成功")
        
        return success_count == len(modules)
        
    except Exception as e:
        print(f"❌ 启动器按钮模拟测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("简谐运动模拟系统 - 模块导航功能测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("启动器模块导航", test_launcher_module_navigation),
        ("模块窗口生命周期", test_module_window_lifecycle),
        ("启动器按钮模拟", test_launcher_button_simulation)
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
        print("🎉 所有测试通过！模块导航功能正常")
        print("\n💡 如果打包版本仍有问题，可能是以下原因:")
        print("   1. 打包环境中的模块路径解析问题")
        print("   2. PyInstaller 的模块加载机制差异")
        print("   3. 窗口显示或事件循环问题")
        return 0
    else:
        print("⚠️  部分测试失败，存在导航功能问题")
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
