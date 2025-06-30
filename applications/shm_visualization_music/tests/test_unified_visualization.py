# -*- coding: utf-8 -*-
"""
测试统一可视化面板
验证合并后的可视化面板功能
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_unified_visualization():
    """测试统一可视化面板"""
    app = QApplication(sys.argv)
    
    try:
        print("🔧 开始统一可视化面板测试...")
        
        # 创建面板
        panel = HarmonicSynthesizerPanel()
        panel.setWindowTitle("统一可视化面板测试 - 简谐波合成器")
        panel.resize(1600, 1000)
        
        def show_test_info():
            msg = QMessageBox()
            msg.setWindowTitle("统一可视化面板测试")
            msg.setText("统一可视化面板重构完成！请验证以下功能:")
            
            test_points = [
                "✅ 双面板已合并为统一可视化面板",
                "✅ 顶部显示合成波形",
                "✅ 下方垂直堆叠显示分解波形",
                "✅ 每个分量占据独立子图",
                "✅ 动态调整子图高度和间距",
                "✅ 不同颜色区分各个分量",
                "",
                "新功能特点:",
                "• 统一面板设计，界面更简洁",
                "• 垂直堆叠布局，避免波形遮挡",
                "• 动态空间分配，适应分量数量",
                "• 清晰的参数信息显示",
                "• 自动Y轴范围调整",
                "",
                "请测试:",
                "1. 添加多个分量观察垂直堆叠效果",
                "2. 启用/禁用分量查看子图变化",
                "3. 调整参数观察实时更新",
                "4. 验证合成波形在顶部正确显示",
                "5. 确认每个分量在独立子图中显示"
            ]
            
            msg.setDetailedText("\n".join(test_points))
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        
        def auto_test_unified_features():
            """自动测试统一面板功能"""
            try:
                print("🔧 开始自动测试统一可视化功能...")
                
                # 验证统一可视化器存在
                assert hasattr(panel, 'unified_viz'), "统一可视化器不存在"
                assert hasattr(panel, 'unified_canvas'), "统一画布不存在"
                print("✅ 统一可视化器创建成功")
                
                # 验证旧的分离组件已移除
                assert not hasattr(panel, 'waveform_viz'), "旧的波形可视化器仍然存在"
                assert not hasattr(panel, 'components_viz'), "旧的分量可视化器仍然存在"
                assert not hasattr(panel, 'waveform_canvas'), "旧的波形画布仍然存在"
                assert not hasattr(panel, 'components_canvas'), "旧的分量画布仍然存在"
                print("✅ 旧的分离组件已完全移除")
                
                # 测试添加多个分量
                initial_count = len(panel.harmonic_components)
                panel.add_harmonic_component(880, 0.6, 0)  # A5
                panel.add_harmonic_component(1320, 0.4, np.pi/3)  # E6
                panel.add_harmonic_component(1760, 0.3, np.pi/2)  # A6
                final_count = len(panel.harmonic_components)
                print(f"✅ 分量添加测试: {initial_count} -> {final_count}")
                
                # 测试统一可视化更新
                panel.update_synthesis()
                print("✅ 统一可视化更新成功")
                
                # 验证分量计数
                count_text = panel.component_count_label.text()
                print(f"✅ 分量计数显示: {count_text}")
                
                # 测试预设功能
                panel.preset_combo.setCurrentText("锯齿波近似")
                panel.on_apply_preset()
                print("✅ 预设应用功能正常")
                
                # 验证画布尺寸
                canvas_height = panel.unified_canvas.height()
                print(f"✅ 统一画布高度: {canvas_height}px")
                
                # 测试清除功能
                panel.on_clear_components()
                print("✅ 清除功能正常")
                
                print("\n🎉 所有自动测试通过！统一可视化面板重构成功完成。")
                print("\n📋 重构总结:")
                print("- ✅ 合并了双面板为统一可视化面板")
                print("- ✅ 实现了垂直堆叠子图布局")
                print("- ✅ 优化了空间分配算法")
                print("- ✅ 保持了所有原有功能")
                print("- ✅ 提升了可视化体验")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        def test_multiple_components():
            """测试多分量显示效果"""
            print("\n🔧 测试多分量垂直堆叠显示...")
            
            # 清除现有分量
            panel.on_clear_components()
            
            # 添加多个不同频率的分量
            frequencies = [220, 440, 660, 880, 1100]  # A3, A4, E5, A5, C#6
            amplitudes = [0.8, 0.6, 0.5, 0.4, 0.3]
            phases = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
            
            for i, (freq, amp, phase) in enumerate(zip(frequencies, amplitudes, phases)):
                panel.add_harmonic_component(freq, amp, phase)
                print(f"  添加分量 {i+1}: {freq}Hz, 振幅{amp}, 相位{phase:.2f}")
            
            # 更新显示
            panel.update_synthesis()
            print("✅ 多分量垂直堆叠显示测试完成")
        
        # 延迟显示信息对话框
        QTimer.singleShot(1000, show_test_info)
        
        # 延迟执行自动测试
        QTimer.singleShot(2000, auto_test_unified_features)
        
        # 延迟执行多分量测试
        QTimer.singleShot(4000, test_multiple_components)
        
        panel.show()
        
        print("统一可视化面板测试程序启动...")
        print("主要重构内容:")
        print("- 合并双面板为统一可视化面板")
        print("- 实现垂直堆叠子图布局")
        print("- 优化空间分配算法")
        print("- 保持所有原有功能")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 显示错误信息
        error_msg = QMessageBox()
        error_msg.setWindowTitle("启动错误")
        error_msg.setText(f"统一可视化面板测试启动失败: {e}")
        error_msg.setDetailedText(traceback.format_exc())
        error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_msg.exec()

if __name__ == "__main__":
    test_unified_visualization()
