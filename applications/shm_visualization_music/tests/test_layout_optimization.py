#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试布局优化效果
验证合成波形位置调整和波形显示稳定性
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from visualization_engine import MatplotlibCanvas, UnifiedWaveformVisualizer
from harmonic_synthesizer_ui import HarmonicComponent


class LayoutTestWindow(QMainWindow):
    """布局测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("波形布局优化测试")
        self.setGeometry(100, 100, 1000, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建画布和可视化器
        self.canvas = MatplotlibCanvas()
        self.visualizer = UnifiedWaveformVisualizer(self.canvas)
        layout.addWidget(self.canvas)
        
        # 创建测试分量
        self.components = [
            HarmonicComponent(frequency=220.0, amplitude=0.8, phase=0.0),
            HarmonicComponent(frequency=440.0, amplitude=0.6, phase=0.0),
            HarmonicComponent(frequency=880.0, amplitude=0.4, phase=0.0)
        ]
        
        # 设置定时器进行测试
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_test)
        self.timer.start(100)  # 每100ms更新一次
        
        self.test_counter = 0
        
    def update_test(self):
        """更新测试"""
        self.test_counter += 1
        
        # 测试不同的分量组合
        if self.test_counter < 50:
            # 测试1：单分量
            enabled_components = [self.components[0]]
            print(f"测试1 - 单分量: {self.test_counter}/50")
        elif self.test_counter < 100:
            # 测试2：双分量
            enabled_components = self.components[:2]
            print(f"测试2 - 双分量: {self.test_counter-50}/50")
        elif self.test_counter < 150:
            # 测试3：三分量
            enabled_components = self.components[:3]
            print(f"测试3 - 三分量: {self.test_counter-100}/50")
        else:
            # 测试完成
            print("测试完成！")
            self.timer.stop()
            return
        
        # 计算合成波形
        duration = 0.2
        t = np.linspace(0, duration, 1000)
        composite = np.zeros_like(t)
        
        for comp in enabled_components:
            omega = 2 * np.pi * comp.frequency
            wave = comp.amplitude * np.sin(omega * t + comp.phase)
            composite += wave
        
        # 更新可视化
        self.visualizer.update_waveforms(
            components=enabled_components,
            composite_wave=composite,
            time_data=t,
            duration=duration
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
            color: white;
        }
    """)
    
    window = LayoutTestWindow()
    window.show()
    
    print("布局优化测试启动...")
    print("测试内容：")
    print("1. 合成波形位置是否居中")
    print("2. 波形显示是否稳定")
    print("3. 布局是否美观平衡")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
