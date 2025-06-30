# -*- coding: utf-8 -*-
"""
测试 beat_main.py 的 TypeError 修复
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_beat_window_initialization():
    """测试 BeatHarmonicWindow 的初始化是否正常"""
    try:
        from PyQt6.QtWidgets import QApplication
        from modules.beat_main import BeatHarmonicWindow
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 尝试创建窗口实例
        print("正在创建 BeatHarmonicWindow 实例...")
        window = BeatHarmonicWindow()
        
        print("✅ BeatHarmonicWindow 初始化成功！")
        print("✅ update_beat_info() 方法调用正常")
        
        # 测试参数获取
        params = window.params_controller.get_params()
        print(f"✅ 参数获取成功: omega1={params['omega1']}, omega2={params['omega2']}")
        
        # 测试 update_beat_info 方法调用
        window.update_beat_info(params['omega1'], params['omega2'])
        print("✅ update_beat_info(omega1, omega2) 调用成功")
        
        # 显示窗口（可选）
        window.show()
        print("✅ 窗口显示成功")
        
        # 不运行事件循环，只是测试初始化
        window.close()
        app.quit()
        
        return True
        
    except TypeError as e:
        print(f"❌ TypeError 错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("测试 beat_main.py TypeError 修复")
    print("=" * 50)
    
    success = test_beat_window_initialization()
    
    print("=" * 50)
    if success:
        print("🎉 所有测试通过！TypeError 已修复")
    else:
        print("💥 测试失败，仍有问题需要解决")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()
