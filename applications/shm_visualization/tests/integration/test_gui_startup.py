#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI启动功能测试
GUI Startup Functionality Test
"""

import sys
import os
import time
import threading
from pathlib import Path

# Setup path for reorganized structure
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_gui_startup():
    """测试GUI启动功能"""
    print("=== 测试GUI启动功能 ===")
    
    try:
        from shm_visualization.ui.ui_framework import get_app_instance
        from shm_visualization.main import SimulationLauncher
        
        # 创建应用实例
        app = get_app_instance()
        print("✅ QApplication 创建成功")
        
        # 创建启动器
        launcher = SimulationLauncher()
        print("✅ SimulationLauncher 创建成功")
        
        # 检查启动器属性
        if hasattr(launcher, 'show'):
            print("✅ 启动器有show方法")
        else:
            print("❌ 启动器缺少show方法")
            return False
            
        # 测试显示窗口（不实际显示）
        try:
            # 检查窗口是否可以显示
            launcher.setVisible(True)
            is_visible = launcher.isVisible()
            print(f"✅ 窗口可见性设置: {is_visible}")
            
            # 检查窗口大小
            size = launcher.size()
            print(f"✅ 窗口大小: {size.width()}x{size.height()}")
            
            # 检查窗口标题
            title = launcher.windowTitle()
            print(f"✅ 窗口标题: {title}")
            
            # 隐藏窗口以避免实际显示
            launcher.setVisible(False)
            
        except Exception as e:
            print(f"❌ 窗口显示测试失败: {e}")
            return False
        
        # 测试按钮功能
        try:
            # 检查是否有按钮
            buttons = launcher.findChildren(launcher.__class__.__bases__[0])
            print(f"✅ 找到 {len(buttons)} 个子组件")
            
        except Exception as e:
            print(f"⚠️  按钮检查失败: {e}")
        
        print("✅ GUI启动功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ GUI启动功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_function():
    """测试main函数（不启动事件循环）"""
    print("\n=== 测试main函数逻辑 ===")
    
    try:
        from shm_visualization.ui.ui_framework import get_app_instance
        from shm_visualization.main import SimulationLauncher
        
        # 创建应用实例
        app = get_app_instance()
        
        # 创建启动器（模拟main函数的逻辑，但不启动事件循环）
        launcher = SimulationLauncher()
        launcher.show()
        
        # 检查应用状态
        print(f"✅ 应用实例类型: {type(app).__name__}")
        print(f"✅ 启动器类型: {type(launcher).__name__}")
        print(f"✅ 启动器可见性: {launcher.isVisible()}")
        
        # 隐藏窗口
        launcher.hide()
        
        print("✅ main函数逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"❌ main函数逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_loop_simulation():
    """测试事件循环模拟"""
    print("\n=== 测试事件循环模拟 ===")
    
    try:
        from shm_visualization.ui.ui_framework import get_app_instance
        from shm_visualization.main import SimulationLauncher
        from PyQt6.QtCore import QTimer
        
        # 创建应用实例
        app = get_app_instance()
        
        # 创建启动器
        launcher = SimulationLauncher()
        launcher.show()
        
        # 创建定时器来模拟短暂的事件循环
        timer = QTimer()
        timer.timeout.connect(app.quit)  # 1秒后退出
        timer.start(1000)  # 1000毫秒 = 1秒
        
        print("✅ 启动短暂的事件循环测试...")
        
        # 运行事件循环（1秒后自动退出）
        exit_code = app.exec()
        
        print(f"✅ 事件循环退出，退出码: {exit_code}")
        print("✅ 事件循环模拟测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 事件循环模拟测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("SHM可视化系统 - GUI启动功能测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("GUI启动功能", test_gui_startup),
        ("main函数逻辑", test_main_function),
        ("事件循环模拟", test_event_loop_simulation)
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
    print("\n" + "=" * 50)
    print("📋 测试结果汇总")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有GUI启动测试通过！")
        print("💡 应用程序应该能够正确显示GUI窗口")
        return 0
    else:
        print("⚠️  部分测试失败，GUI启动可能有问题")
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
