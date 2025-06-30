#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重组后的导航功能测试
Reorganized Navigation Functionality Test
"""

import os
import sys
import traceback
from pathlib import Path

# Setup path for reorganized structure
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_launcher_navigation():
    """测试启动器导航功能"""
    print("=== 测试重组后的启动器导航功能 ===")
    
    try:
        from shm_visualization.ui.ui_framework import get_app_instance
        from shm_visualization.main import SimulationLauncher
        
        # 创建应用实例
        app = get_app_instance()
        print("✅ QApplication 创建成功")
        
        # 创建启动器
        launcher = SimulationLauncher()
        print("✅ SimulationLauncher 创建成功")
        
        # 测试各个模块的导航
        test_modules = [
            ".modules.orthogonal_main",
            ".modules.beat_main",
            ".modules.phase_main"
        ]
        
        success_count = 0
        for module_name in test_modules:
            print(f"\n🧪 测试模块: {module_name}")
            
            try:
                # 保存原始的 show 方法以避免实际显示窗口
                original_show = launcher.show
                show_called = False
                
                def mock_show():
                    nonlocal show_called
                    show_called = True
                    print(f"  📱 启动器 show() 被调用")
                
                launcher.show = mock_show
                
                # 调用 run_module
                launcher.run_module(module_name)
                
                # 检查结果
                if launcher.current_module_window:
                    print(f"  ✅ 模块窗口创建成功: {type(launcher.current_module_window).__name__}")
                    
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

def test_module_main_functions():
    """测试各模块的main函数"""
    print("\n=== 测试重组后的模块main函数 ===")
    
    modules = [
        "shm_visualization.modules.orthogonal_main",
        "shm_visualization.modules.beat_main", 
        "shm_visualization.modules.phase_main"
    ]
    
    success_count = 0
    for module_name in modules:
        try:
            module = __import__(module_name, fromlist=['main'])
            
            if not hasattr(module, 'main'):
                print(f"❌ {module_name}: 没有main函数")
                continue
            
            # 测试main函数调用
            window = module.main()
            if window:
                print(f"✅ {module_name}: main函数调用成功")
                window.close()  # 清理窗口
                success_count += 1
            else:
                print(f"❌ {module_name}: main函数返回None")
                
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 模块main函数测试结果: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)

def test_package_structure():
    """测试包结构完整性"""
    print("\n=== 测试重组后的包结构 ===")
    
    # 检查关键模块是否可以导入
    key_modules = [
        'shm_visualization',
        'shm_visualization.main',
        'shm_visualization.ui.ui_framework',
        'shm_visualization.ui.params_controller',
        'shm_visualization.modules.orthogonal_main',
        'shm_visualization.modules.beat_main',
        'shm_visualization.modules.phase_main',
        'shm_visualization.animations.orthogonal_animation',
        'shm_visualization.animations.beat_animation',
        'shm_visualization.animations.phase_animation'
    ]
    
    success_count = 0
    for module_name in key_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 包结构测试结果: {success_count}/{len(key_modules)} 成功")
    return success_count == len(key_modules)

def main():
    """主测试函数"""
    print("重组后的简谐运动模拟系统 - 导航功能测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("包结构完整性", test_package_structure),
        ("模块main函数", test_module_main_functions),
        ("启动器导航", test_launcher_navigation)
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
        print("🎉 所有测试通过！重组后的导航功能正常")
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
