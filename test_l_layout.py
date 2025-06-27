#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试L型布局的简谐运动可视化系统
"""

import sys
import os

# 添加shm_visualization目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
shm_dir = os.path.join(current_dir, 'shm_visualization')
if shm_dir not in sys.path:
    sys.path.insert(0, shm_dir)

def test_l_layout():
    """测试L型布局"""
    try:
        # 导入必要的模块
        from shm_visualization.ui_framework import get_app_instance
        from shm_visualization.orthogonal_main import OrthogonalHarmonicWindow
        
        print("正在启动L型布局测试...")
        
        # 创建应用实例
        app = get_app_instance()
        
        # 创建主窗口
        window = OrthogonalHarmonicWindow()
        window.show()
        
        print("L型布局窗口已创建并显示")
        print("请检查以下布局特征:")
        print("1. 控制面板在最左侧")
        print("2. Y方向波形图在左上角（垂直显示）")
        print("3. 李萨如图形在右上角")
        print("4. X方向波形图在右下角（水平显示）")
        print("5. 左下角有空白占位符")
        print("6. 坐标轴应该对齐，辅助线应该显示对应关系")
        
        # 运行应用
        return app.exec()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保shm_visualization目录存在且包含所有必要的文件")
        return 1
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_l_layout())
