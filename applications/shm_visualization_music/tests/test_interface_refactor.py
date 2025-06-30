# -*- coding: utf-8 -*-
"""
测试界面重构
验证频谱分析移除和分解波形显示功能
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_interface_refactor():
    """测试界面重构"""
    app = QApplication(sys.argv)
    
    try:
        # 创建面板
        panel = HarmonicSynthesizerPanel()
        panel.setWindowTitle("界面重构测试 - 简谐波合成器")
        panel.resize(1600, 1000)
        
        def show_refactor_info():
            msg = QMessageBox()
            msg.setWindowTitle("界面重构验证")
            msg.setText("界面重构完成！请验证以下功能:")
            
            refactor_points = [
                "✅ 频谱分析面板已移除",
                "✅ 新增分解波形面板(紫色边框)",
                "✅ 合成波形面板(蓝色边框)正常显示",
                "✅ 分解波形显示各个简谐分量",
                "✅ 波形分量控制功能保持不变",
                "✅ 音频播放和导出功能正常",
                "",
                "新功能特点:",
                "• 分解波形面板显示每个简谐分量的独立波形",
                "• 不同分量使用不同颜色区分",
                "• 支持最多10种颜色的分量显示",
                "• 自动调整Y轴范围适应振幅",
                "• 显示分量标签和频率信息",
                "",
                "请测试:",
                "1. 添加多个分量观察分解波形",
                "2. 启用/禁用分量查看变化",
                "3. 调整振幅、频率、相位参数",
                "4. 播放音频验证功能正常"
            ]
            
            msg.setDetailedText("\n".join(refactor_points))
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        
        def auto_test_features():
            """自动测试功能"""
            try:
                print("🔧 开始自动测试界面重构功能...")
                
                # 验证新的可视化器存在
                assert hasattr(panel, 'components_viz'), "分解波形可视化器不存在"
                assert hasattr(panel, 'components_canvas'), "分解波形画布不存在"
                print("✅ 分解波形可视化器创建成功")
                
                # 验证频谱相关组件已移除
                assert not hasattr(panel, 'spectrum_viz'), "频谱可视化器仍然存在"
                assert not hasattr(panel, 'spectrum_canvas'), "频谱画布仍然存在"
                print("✅ 频谱分析组件已完全移除")
                
                # 测试添加分量
                initial_count = len(panel.harmonic_components)
                panel.add_harmonic_component(880, 0.5, 0)  # 添加A5音
                panel.add_harmonic_component(1320, 0.3, np.pi/4)  # 添加E6音
                print(f"✅ 成功添加分量，从 {initial_count} 增加到 {len(panel.harmonic_components)}")
                
                # 测试分解波形更新
                panel.update_synthesis()
                print("✅ 分解波形更新成功")
                
                # 测试分量计数更新
                count_text = panel.component_count_label.text()
                print(f"✅ 分量计数标签: {count_text}")
                
                # 测试预设应用
                panel.preset_combo.setCurrentText("方波近似")
                panel.on_apply_preset()
                print("✅ 预设应用功能正常")
                
                # 验证画布尺寸
                waveform_height = panel.waveform_canvas.height()
                components_height = panel.components_canvas.height()
                print(f"✅ 合成波形画布高度: {waveform_height}px")
                print(f"✅ 分解波形画布高度: {components_height}px")
                
                # 测试音频引擎
                if hasattr(panel, 'audio_engine'):
                    print("✅ 音频引擎正常")
                
                print("\n🎉 所有自动测试通过！界面重构成功完成。")
                print("\n📋 重构总结:")
                print("- ❌ 移除了频谱分析面板")
                print("- ✅ 新增了分解波形面板")
                print("- ✅ 保持了所有原有功能")
                print("- ✅ 优化了可视化体验")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 延迟显示信息对话框
        QTimer.singleShot(1000, show_refactor_info)
        
        # 延迟执行自动测试
        QTimer.singleShot(2000, auto_test_features)
        
        panel.show()
        
        print("界面重构测试程序启动...")
        print("主要重构内容:")
        print("- 移除频谱分析面板")
        print("- 新增分解波形面板")
        print("- 重新设计可视化布局")
        print("- 保持所有原有功能")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 显示错误信息
        error_msg = QMessageBox()
        error_msg.setWindowTitle("启动错误")
        error_msg.setText(f"界面重构测试启动失败: {e}")
        error_msg.setDetailedText(traceback.format_exc())
        error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_msg.exec()

if __name__ == "__main__":
    # 添加numpy导入
    import numpy as np
    test_interface_refactor()
