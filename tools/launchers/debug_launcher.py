# -*- coding: utf-8 -*-
"""
简谐运动教学仿真系统 - 调试启动器
简化版，用于测试窗口显示
"""

import os
import sys
import traceback

def main():
    """主函数入口"""
    # 添加模块路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'shm_visualization')
    
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print("调试启动器 - 添加路径:")
    print(f"当前目录: {current_dir}")
    print(f"源代码目录: {src_dir}")
    
    try:
        # 导入和初始化PyQt
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        print("QApplication初始化成功")
        
        # 修复初始参数
        from shm_visualization.ui_framework import INITIAL_PARAMS
        print(f"原始omega2值: {INITIAL_PARAMS['omega2']}")
        print(f"原始ratio_preset值: {INITIAL_PARAMS['ratio_preset']}")
        INITIAL_PARAMS['omega2'] = 1.0
        INITIAL_PARAMS['ratio_preset'] = '1:1'
        print(f"修复后omega2值: {INITIAL_PARAMS['omega2']}")
        print(f"修复后ratio_preset值: {INITIAL_PARAMS['ratio_preset']}")
        
        # 导入启动模块
        import shm_visualization.start as start_module
        print("导入start模块成功")
        
        # 创建窗口
        window = start_module.main()
        if not window:
            print("错误: start.main()未返回窗口")
            return 1
        
        print("窗口创建成功")
        
        # 确保窗口显示
        window.show()
        print("窗口显示调用成功")
        
        # 明确开始事件循环并等待其完成
        print("开始PyQt事件循环...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    main() 