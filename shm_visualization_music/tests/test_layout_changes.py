# -*- coding: utf-8 -*-
"""
测试界面布局重组更改
验证音色增强面板移至底部，波形分量面板移至中心并扩大
"""

import sys
from PyQt6.QtWidgets import QApplication
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_layout_changes():
    """测试布局更改"""
    app = QApplication(sys.argv)
    
    # 创建简谐波合成器面板
    panel = HarmonicSynthesizerPanel()
    panel.setWindowTitle("测试布局重组 - 简谐波合成器")
    panel.resize(1400, 900)  # 设置较大的窗口尺寸以便观察布局
    panel.show()
    
    print("布局重组测试:")
    print("1. 音色增强面板应位于界面底部")
    print("2. 波形分量面板应位于界面中心并占据主要空间")
    print("3. 预设控制应位于界面顶部")
    print("4. 所有功能应保持正常工作")
    print("\n请检查界面布局是否符合要求...")
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    test_layout_changes()
