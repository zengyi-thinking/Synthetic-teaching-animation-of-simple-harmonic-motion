# -*- coding: utf-8 -*-
"""
测试滚动和布局修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_multiple_components():
    """测试多分量场景下的滚动效果"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = HarmonicSynthesizerPanel()
    window.setWindowTitle("测试滚动和布局修复 - 多分量场景")
    window.resize(1400, 900)
    
    # 添加多个分量来测试滚动效果
    test_frequencies = [440, 880, 1320, 1760, 2200, 2640, 3080, 3520]
    test_amplitudes = [0.8, 0.6, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1]
    
    # 清除默认分量
    window.harmonic_components.clear()
    window.component_widgets.clear()
    
    # 清空布局
    for i in reversed(range(window.components_layout.count())):
        child = window.components_layout.takeAt(i)
        if child.widget():
            child.widget().deleteLater()
    
    # 添加测试分量
    for freq, amp in zip(test_frequencies, test_amplitudes):
        window.add_harmonic_component(freq, amp, 0.0)
    
    # 更新分量计数
    window.update_component_count()
    
    # 更新合成
    window.update_synthesis()
    
    print(f"已添加 {len(test_frequencies)} 个分量用于测试滚动效果")
    print("测试要点:")
    print("1. 检查波形分量面板是否有滚动条")
    print("2. 检查波形可视化面板是否有滚动条")
    print("3. 检查内容是否与边框重叠")
    print("4. 检查面板间距是否合适")
    print("5. 检查分割器是否工作正常")
    
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    test_multiple_components()
