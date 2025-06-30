#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试波形显示修复效果
验证采样范围调整和多分量显示优化
"""

import sys
import os
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from harmonic_synthesizer_ui import HarmonicComponent, HarmonicSynthesizerPanel


class WaveformTestWindow(QMainWindow):
    """波形测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("波形显示修复效果测试")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加说明标签
        info_label = QLabel("测试波形显示修复效果：")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(info_label)
        
        # 创建简谐合成器面板
        self.synthesizer = HarmonicSynthesizerPanel()
        layout.addWidget(self.synthesizer)
        
        # 创建测试按钮布局
        button_layout = QHBoxLayout()
        
        # 测试按钮1：基础频率测试
        test1_btn = QPushButton("测试1: 基础频率 (20Hz, 43Hz)")
        test1_btn.clicked.connect(self.test_basic_frequencies)
        button_layout.addWidget(test1_btn)
        
        # 测试按钮2：高频测试
        test2_btn = QPushButton("测试2: 高频分量 (440Hz, 880Hz)")
        test2_btn.clicked.connect(self.test_high_frequencies)
        button_layout.addWidget(test2_btn)
        
        # 测试按钮3：多分量测试
        test3_btn = QPushButton("测试3: 多分量 (5个分量)")
        test3_btn.clicked.connect(self.test_multiple_components)
        button_layout.addWidget(test3_btn)
        
        # 测试按钮4：极端情况测试
        test4_btn = QPushButton("测试4: 极端频率差异")
        test4_btn.clicked.connect(self.test_extreme_frequencies)
        button_layout.addWidget(test4_btn)
        
        # 清除按钮
        clear_btn = QPushButton("清除所有分量")
        clear_btn.clicked.connect(self.clear_all_components)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def clear_all_components(self):
        """清除所有分量"""
        self.synthesizer.harmonic_components.clear()
        self.synthesizer.update_component_list()
        self.synthesizer.update_synthesis()
        print("已清除所有分量")
    
    def test_basic_frequencies(self):
        """测试1：基础频率，验证显示周期调整"""
        print("\n=== 测试1：基础频率 ===")
        self.clear_all_components()
        
        # 添加两个低频分量
        comp1 = HarmonicComponent(frequency=20.0, amplitude=0.8, phase=0.0)
        comp2 = HarmonicComponent(frequency=43.0, amplitude=0.6, phase=np.pi/4)
        
        self.synthesizer.harmonic_components = [comp1, comp2]
        self.synthesizer.update_component_list()
        self.synthesizer.update_synthesis()
        
        print("添加了20Hz和43Hz分量，应该显示约4个周期")
        print(f"最低频率: {min(comp.frequency for comp in self.synthesizer.harmonic_components)}Hz")
        print(f"预期显示时间: {4/20:.2f}秒")
    
    def test_high_frequencies(self):
        """测试2：高频分量，验证采样优化"""
        print("\n=== 测试2：高频分量 ===")
        self.clear_all_components()
        
        # 添加两个高频分量
        comp1 = HarmonicComponent(frequency=440.0, amplitude=0.7, phase=0.0)
        comp2 = HarmonicComponent(frequency=880.0, amplitude=0.5, phase=np.pi/3)
        
        self.synthesizer.harmonic_components = [comp1, comp2]
        self.synthesizer.update_component_list()
        self.synthesizer.update_synthesis()
        
        print("添加了440Hz和880Hz分量，应该显示清晰的波形")
        print(f"最低频率: {min(comp.frequency for comp in self.synthesizer.harmonic_components)}Hz")
        print(f"预期显示时间: {4/440:.3f}秒")
    
    def test_multiple_components(self):
        """测试3：多分量显示，验证子图布局"""
        print("\n=== 测试3：多分量显示 ===")
        self.clear_all_components()
        
        # 添加5个不同频率的分量
        frequencies = [100, 200, 300, 500, 800]
        amplitudes = [0.8, 0.6, 0.5, 0.4, 0.3]
        phases = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
        
        components = []
        for i, (freq, amp, phase) in enumerate(zip(frequencies, amplitudes, phases)):
            comp = HarmonicComponent(frequency=freq, amplitude=amp, phase=phase)
            components.append(comp)
        
        self.synthesizer.harmonic_components = components
        self.synthesizer.update_component_list()
        self.synthesizer.update_synthesis()
        
        print(f"添加了{len(components)}个分量：{frequencies}Hz")
        print("验证每个分量都能在独立子图中显示")
        print(f"最低频率: {min(frequencies)}Hz")
        print(f"预期显示时间: {4/min(frequencies):.3f}秒")
    
    def test_extreme_frequencies(self):
        """测试4：极端频率差异，验证自适应显示"""
        print("\n=== 测试4：极端频率差异 ===")
        self.clear_all_components()
        
        # 添加频率差异很大的分量
        comp1 = HarmonicComponent(frequency=10.0, amplitude=0.8, phase=0.0)    # 极低频
        comp2 = HarmonicComponent(frequency=1000.0, amplitude=0.4, phase=0.0)  # 高频
        comp3 = HarmonicComponent(frequency=50.0, amplitude=0.6, phase=np.pi/2) # 中频
        
        self.synthesizer.harmonic_components = [comp1, comp2, comp3]
        self.synthesizer.update_component_list()
        self.synthesizer.update_synthesis()
        
        print("添加了10Hz、50Hz和1000Hz分量")
        print("验证基于最低频率(10Hz)的显示时间调整")
        print(f"最低频率: {min(comp.frequency for comp in self.synthesizer.harmonic_components)}Hz")
        print(f"预期显示时间: {4/10:.2f}秒")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建测试窗口
    window = WaveformTestWindow()
    window.show()
    
    print("波形显示修复效果测试程序启动")
    print("请点击不同的测试按钮验证修复效果：")
    print("1. 基础频率测试 - 验证显示周期调整")
    print("2. 高频分量测试 - 验证采样优化")
    print("3. 多分量测试 - 验证子图布局")
    print("4. 极端频率测试 - 验证自适应显示")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
