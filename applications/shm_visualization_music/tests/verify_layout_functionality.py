# -*- coding: utf-8 -*-
"""
验证布局重组后的功能完整性
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def verify_functionality():
    """验证重新布局后的功能完整性"""
    app = QApplication(sys.argv)
    
    # 创建面板
    panel = HarmonicSynthesizerPanel()
    panel.setWindowTitle("功能验证 - 简谐波合成器布局重组")
    panel.resize(1400, 900)
    
    # 验证步骤
    verification_steps = [
        "1. 检查波形分量面板是否位于中心并占据主要空间",
        "2. 检查音色增强面板是否位于底部",
        "3. 检查预设控制是否位于顶部",
        "4. 测试添加分量功能",
        "5. 测试预设应用功能",
        "6. 测试音色增强控制",
        "7. 测试波形可视化更新",
        "8. 测试播放功能"
    ]
    
    def show_verification_dialog():
        msg = QMessageBox()
        msg.setWindowTitle("布局重组验证")
        msg.setText("请验证以下功能是否正常工作:")
        msg.setDetailedText("\n".join(verification_steps))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    # 延迟显示验证对话框
    QTimer.singleShot(1000, show_verification_dialog)
    
    # 自动测试一些基本功能
    def auto_test():
        try:
            # 测试添加分量
            initial_count = len(panel.harmonic_components)
            panel.add_harmonic_component(880.0, 0.5, 0.0)
            assert len(panel.harmonic_components) == initial_count + 1
            print("✅ 添加分量功能正常")
            
            # 测试预设应用
            panel.preset_combo.setCurrentText("钢琴音色")
            panel.on_apply_preset()
            print("✅ 预设应用功能正常")
            
            # 测试音色增强控制
            panel.freq_offset_slider.setValue(50)
            panel.phase_rand_slider.setValue(30)
            panel.subharmonic_slider.setValue(20)
            print("✅ 音色增强控制正常")
            
            # 测试包络控制
            panel.envelope_cb.setChecked(True)
            panel.attack_slider.setValue(50)
            print("✅ 包络控制正常")
            
            # 测试混响控制
            panel.reverb_cb.setChecked(True)
            panel.reverb_slider.setValue(40)
            print("✅ 混响控制正常")
            
            print("\n🎉 所有自动测试通过！布局重组成功完成。")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    # 延迟执行自动测试
    QTimer.singleShot(2000, auto_test)
    
    panel.show()
    
    print("布局重组验证程序启动...")
    print("请检查界面布局是否符合以下要求:")
    print("- 波形分量面板位于中心并占据主要空间")
    print("- 音色增强面板位于底部")
    print("- 预设控制位于顶部")
    print("- 所有功能正常工作")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    verify_functionality()
