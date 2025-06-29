# -*- coding: utf-8 -*-
"""
测试波形显示修复
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_waveform_fix():
    """测试波形显示修复"""
    app = QApplication(sys.argv)
    
    try:
        print("🔧 测试波形显示修复...")
        
        # 创建面板
        panel = HarmonicSynthesizerPanel()
        panel.setWindowTitle("波形显示修复测试")
        panel.resize(1400, 900)
        
        def setup_test_components():
            """设置测试分量"""
            print("设置测试分量...")
            
            # 清除现有分量
            panel.on_clear_components()
            
            # 添加几个测试分量
            panel.add_harmonic_component(220, 0.8, 0)      # A3
            panel.add_harmonic_component(440, 0.6, 0)      # A4
            panel.add_harmonic_component(880, 0.4, 0)      # A5
            
            # 更新显示
            panel.update_synthesis()
            
            print("✅ 测试分量设置完成")
            print("请检查右侧可视化面板中的波形显示是否正常")
            print("应该看到:")
            print("- 顶部: 青色的合成波形线条")
            print("- 下方: 三个不同颜色的分量波形线条")
            print("- 所有波形都应该是清晰的线条，而不是填充的色块")
        
        def apply_preset_test():
            """应用预设测试"""
            print("\n应用预设测试...")
            panel.preset_combo.setCurrentText("锯齿波近似")
            panel.on_apply_preset()
            print("✅ 锯齿波预设应用完成")
        
        # 延迟执行测试
        QTimer.singleShot(1000, setup_test_components)
        QTimer.singleShot(3000, apply_preset_test)
        
        panel.show()
        
        print("波形显示修复测试启动...")
        print("请观察右侧可视化面板中的波形是否正常显示为线条")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"测试启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_waveform_fix()
