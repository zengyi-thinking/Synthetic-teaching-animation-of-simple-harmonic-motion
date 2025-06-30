# -*- coding: utf-8 -*-
"""
简单测试滚动和布局修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = HarmonicSynthesizerPanel()
    window.setWindowTitle("滚动和布局测试")
    window.resize(1200, 800)
    
    # 添加几个分量来测试
    for i in range(5):
        freq = 440 * (i + 1)
        amp = 0.8 / (i + 1)
        window.add_harmonic_component(freq, amp, 0.0)
    
    window.show()
    
    print("测试窗口已打开，请检查:")
    print("1. 波形分量面板是否有滚动条")
    print("2. 波形可视化面板是否有滚动条") 
    print("3. 内容是否与边框重叠")
    print("4. 分割器是否可以拖动调整")
    
    return app.exec()

if __name__ == "__main__":
    main()
