# -*- coding: utf-8 -*-
"""
波形显示问题诊断脚本
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def debug_waveform_display():
    """诊断波形显示问题"""
    app = QApplication(sys.argv)
    
    try:
        print("🔍 开始波形显示问题诊断...")
        
        # 创建面板
        panel = HarmonicSynthesizerPanel()
        panel.setWindowTitle("波形显示问题诊断")
        panel.resize(1400, 900)
        
        def diagnose_data():
            """诊断数据问题"""
            print("\n📊 诊断数据生成...")
            
            # 获取当前分量
            components = panel.harmonic_components
            print(f"当前分量数: {len(components)}")
            
            for i, comp in enumerate(components):
                print(f"分量 {i+1}: 频率={comp.frequency}Hz, 振幅={comp.amplitude}, 相位={comp.phase}, 启用={comp.enabled}")
            
            # 手动生成测试数据
            sample_rate = panel.audio_engine.sample_rate
            duration = panel.note_duration
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            print(f"时间数据: 长度={len(t)}, 范围=[{t[0]:.3f}, {t[-1]:.3f}]")
            
            # 生成合成波形
            composite = np.zeros_like(t)
            for comp in components:
                if comp.enabled:
                    omega = 2 * np.pi * comp.frequency
                    wave = comp.amplitude * np.sin(omega * t + comp.phase)
                    composite += wave
                    print(f"分量波形: 最小值={np.min(wave):.3f}, 最大值={np.max(wave):.3f}")
            
            print(f"合成波形: 长度={len(composite)}, 最小值={np.min(composite):.3f}, 最大值={np.max(composite):.3f}")
            
            # 检查数据是否有异常
            if np.any(np.isnan(composite)):
                print("❌ 合成波形包含NaN值")
            if np.any(np.isinf(composite)):
                print("❌ 合成波形包含无穷大值")
            
            # 测试matplotlib直接绘图
            print("\n🎨 测试matplotlib直接绘图...")
            plt.figure(figsize=(12, 8))
            
            # 下采样用于显示
            if len(t) > 1000:
                step = len(t) // 1000
                t_display = t[::step]
                composite_display = composite[::step]
            else:
                t_display = t
                composite_display = composite
            
            print(f"显示数据: 时间长度={len(t_display)}, 波形长度={len(composite_display)}")
            
            # 绘制合成波形
            plt.subplot(2, 1, 1)
            plt.plot(t_display, composite_display, 'cyan', linewidth=2)
            plt.title('合成波形 (直接matplotlib测试)')
            plt.ylabel('振幅')
            plt.grid(True, alpha=0.3)
            
            # 绘制第一个分量
            if components and components[0].enabled:
                comp = components[0]
                omega = 2 * np.pi * comp.frequency
                wave = comp.amplitude * np.sin(omega * t_display + comp.phase)
                
                plt.subplot(2, 1, 2)
                plt.plot(t_display, wave, 'orange', linewidth=2)
                plt.title(f'分量1: {comp.frequency}Hz (直接matplotlib测试)')
                plt.xlabel('时间 (s)')
                plt.ylabel('振幅')
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # 测试统一可视化器
            print("\n🔧 测试统一可视化器...")
            try:
                panel.unified_viz.update_waveforms(
                    components=components,
                    composite_wave=composite_display,
                    time_data=t_display,
                    duration=duration
                )
                print("✅ 统一可视化器更新成功")
            except Exception as e:
                print(f"❌ 统一可视化器更新失败: {e}")
                import traceback
                traceback.print_exc()
        
        def check_canvas_state():
            """检查画布状态"""
            print("\n🖼️ 检查画布状态...")
            
            canvas = panel.unified_viz.canvas
            figure = canvas.figure
            
            print(f"画布尺寸: {canvas.width()}x{canvas.height()}")
            print(f"图形背景色: {figure.get_facecolor()}")
            print(f"子图数量: {len(figure.get_axes())}")
            
            for i, ax in enumerate(figure.get_axes()):
                print(f"子图 {i+1}:")
                print(f"  背景色: {ax.get_facecolor()}")
                print(f"  X轴范围: {ax.get_xlim()}")
                print(f"  Y轴范围: {ax.get_ylim()}")
                print(f"  线条数量: {len(ax.get_lines())}")
                
                for j, line in enumerate(ax.get_lines()):
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    print(f"    线条 {j+1}: X长度={len(xdata)}, Y长度={len(ydata)}")
                    if len(xdata) > 0 and len(ydata) > 0:
                        print(f"      X范围=[{np.min(xdata):.3f}, {np.max(xdata):.3f}]")
                        print(f"      Y范围=[{np.min(ydata):.3f}, {np.max(ydata):.3f}]")
        
        def fix_waveform_display():
            """修复波形显示"""
            print("\n🔧 尝试修复波形显示...")
            
            # 清除当前显示
            panel.unified_viz.clear()
            
            # 重新生成数据
            panel.update_synthesis()
            
            print("✅ 波形显示修复尝试完成")
        
        # 延迟执行诊断
        QTimer.singleShot(1000, diagnose_data)
        QTimer.singleShot(3000, check_canvas_state)
        QTimer.singleShot(5000, fix_waveform_display)
        
        panel.show()
        
        print("波形显示问题诊断程序启动...")
        print("将依次执行:")
        print("1. 数据生成诊断")
        print("2. 画布状态检查")
        print("3. 波形显示修复尝试")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"诊断程序启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_waveform_display()
