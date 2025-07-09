#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试向量图修复效果的脚本
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# 添加模块路径
sys.path.insert(0, 'src')

from src.shm_visualization.modules.phase_main import PhasorPanel

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("向量图修复效果测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建相量图面板
        self.phasor_panel = PhasorPanel()
        layout.addWidget(self.phasor_panel)
        
        # 设置定时器来模拟动画
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_vectors)
        self.timer.start(100)  # 100ms更新一次
        
        self.time = 0
        
    def update_vectors(self):
        """更新向量显示"""
        self.time += 0.1
        
        # 模拟两个相量向量
        phasor1_x = 1.0 * np.cos(self.time)
        phasor1_y = 1.0 * np.sin(self.time)
        
        phasor2_x = 0.8 * np.cos(self.time + np.pi/3)
        phasor2_y = 0.8 * np.sin(self.time + np.pi/3)
        
        # 计算合成向量
        composite_x = phasor1_x + phasor2_x
        composite_y = phasor1_y + phasor2_y
        
        # 更新相量图
        self.phasor_panel.update_phasors(
            phasor1_x, phasor1_y,
            phasor2_x, phasor2_y,
            composite_x, composite_y
        )
        
        # 更新信息
        amplitude = np.sqrt(composite_x**2 + composite_y**2)
        phase = np.arctan2(composite_y, composite_x)
        self.phasor_panel.set_info(amplitude, phase)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("向量图外部图例布局测试启动")
    print("观察要点：")
    print("1. 向量图是否有A1、A2、A合成标签")
    print("2. 颜色说明是否移动到相量图面板右侧")
    print("3. 图例是否在面板外部，不遮挡向量")
    print("4. 布局是否美观，图例区域是否合适")
    print("5. 颜色标识是否清晰对应")
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
