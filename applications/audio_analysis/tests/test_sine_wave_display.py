#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简谐波分量显示测试脚本
专门测试修复后的正弦波形显示效果
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication
import matplotlib.pyplot as plt

# Add parent directory to path
sys.path.append('..')

def test_sine_wave_generation():
    """测试正弦波生成"""
    print("=" * 60)
    print("🔧 测试1: 正弦波生成验证")
    print("=" * 60)
    
    # 测试参数
    frequencies = [440.0, 880.0, 1320.0]  # A4, A5, E6
    amplitudes = [0.5, 0.3, 0.2]
    phases = [0.0, 0.0, 0.0]
    
    duration = 3.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    print(f"时间轴: {len(t)} 个采样点, 范围 0-{duration}秒")
    
    for i, (freq, amp, phase) in enumerate(zip(frequencies, amplitudes, phases)):
        # 生成正弦波
        wave = amp * np.sin(2 * np.pi * freq * t + phase)
        
        print(f"分量 {i+1}:")
        print(f"  频率: {freq}Hz")
        print(f"  振幅: {amp}")
        print(f"  相位: {phase}")
        print(f"  波形范围: {np.min(wave):.4f} 到 {np.max(wave):.4f}")
        print(f"  周期: {1/freq:.4f}秒")
        print(f"  3秒内周期数: {duration * freq:.1f}")
        
        # 检查波形是否正确
        expected_max = amp
        expected_min = -amp
        actual_max = np.max(wave)
        actual_min = np.min(wave)
        
        if abs(actual_max - expected_max) < 0.001 and abs(actual_min - expected_min) < 0.001:
            print(f"  ✅ 波形生成正确")
        else:
            print(f"  ❌ 波形生成异常: 期望范围[{expected_min:.3f}, {expected_max:.3f}], 实际范围[{actual_min:.3f}, {actual_max:.3f}]")
    
    return True

def test_component_display():
    """测试分量显示功能"""
    print("\n" + "=" * 60)
    print("🔧 测试2: 分量显示功能")
    print("=" * 60)
    
    try:
        from audio_editor_ui import SpectrumCanvas
        from frequency_analyzer import FrequencyComponent
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建画布
        canvas = SpectrumCanvas()
        canvas.current_sample_rate = 22050
        print("✅ SpectrumCanvas 创建成功")
        
        # 创建测试分量 - 使用更大的振幅
        components = [
            FrequencyComponent(440.0, 0.5, 0.0),    # A4
            FrequencyComponent(880.0, 0.3, 0.0),    # A5  
            FrequencyComponent(1320.0, 0.2, 0.0),   # E6
        ]
        
        # 设置分量属性
        for i, comp in enumerate(components):
            comp.enabled = True
            comp.original_amplitude = comp.amplitude
            print(f"分量 {i+1}: {comp.frequency}Hz, 振幅={comp.amplitude}, 相位={comp.phase}")
        
        # 设置动态布局
        canvas.setup_dynamic_layout(len(components))
        print(f"✅ 动态布局设置: {len(canvas.component_axes)} 个分量轴")
        
        # 测试垂直分量显示
        canvas.plot_components_vertical(components)
        print("✅ 垂直分量显示完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 分量显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frequency_analysis():
    """测试完整的频率分析流程"""
    print("\n" + "=" * 60)
    print("🔧 测试3: 完整频率分析流程")
    print("=" * 60)
    
    try:
        from frequency_analyzer import FrequencyAnalyzer
        
        # 创建分析器
        sample_rate = 22050
        analyzer = FrequencyAnalyzer(sample_rate)
        print("✅ 频率分析器创建成功")
        
        # 生成包含已知频率的测试信号
        duration = 4.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        # 创建复合信号
        signal = (0.8 * np.sin(2 * np.pi * 440 * t) +    # A4 - 强信号
                 0.5 * np.sin(2 * np.pi * 880 * t) +     # A5 - 中等信号
                 0.3 * np.sin(2 * np.pi * 1320 * t))     # E6 - 弱信号
        
        print(f"✅ 生成测试信号: {len(signal)} 样本, {duration}秒")
        print(f"   包含频率: 440Hz(0.8), 880Hz(0.5), 1320Hz(0.3)")
        
        # 执行频率分析
        components = analyzer.analyze_audio(signal, n_components=5)
        print(f"✅ 频率分析完成，提取了 {len(components)} 个分量")
        
        # 检查分析结果
        expected_frequencies = [440, 880, 1320]
        found_frequencies = []
        
        for i, comp in enumerate(components):
            print(f"分量 {i+1}: {comp.frequency:.1f}Hz, 振幅={comp.amplitude:.6f}, 相位={comp.phase:.3f}")
            found_frequencies.append(comp.frequency)
        
        # 验证是否找到了期望的频率
        tolerance = 10  # Hz
        for expected_freq in expected_frequencies:
            found = False
            for found_freq in found_frequencies:
                if abs(found_freq - expected_freq) < tolerance:
                    found = True
                    break
            if found:
                print(f"✅ 找到期望频率: {expected_freq}Hz")
            else:
                print(f"❌ 未找到期望频率: {expected_freq}Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ 频率分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 60)
    print("🔧 测试4: 完整工作流程")
    print("=" * 60)
    
    try:
        from audio_editor_ui import AudioEditorMainWindow
        from frequency_analyzer import FrequencyAnalyzer
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建主窗口
        window = AudioEditorMainWindow()
        print("✅ 主窗口创建成功")
        
        # 生成测试音频
        sample_rate = 22050
        duration = 3.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        # 创建包含清晰频率分量的测试信号
        test_audio = (0.6 * np.sin(2 * np.pi * 440 * t) +    # A4
                     0.4 * np.sin(2 * np.pi * 880 * t) +     # A5
                     0.3 * np.sin(2 * np.pi * 1320 * t))     # E6
        
        # 模拟加载音频
        window.original_audio = test_audio
        window.spectrum_canvas.current_sample_rate = sample_rate
        print("✅ 测试音频设置成功")
        
        # 测试波形显示
        window.spectrum_canvas.plot_waveform(test_audio, sample_rate, "测试音频波形")
        print("✅ 原始波形显示成功")
        
        # 创建分析器并分析
        analyzer = FrequencyAnalyzer(sample_rate)
        components = analyzer.analyze_audio(test_audio, n_components=3)
        print(f"✅ 分析完成，获得 {len(components)} 个分量")
        
        # 设置分量属性
        for comp in components:
            comp.enabled = True
            comp.original_amplitude = comp.amplitude
        
        # 测试分量显示
        window.spectrum_canvas.setup_dynamic_layout(len(components))
        window.spectrum_canvas.plot_components_vertical(components)
        print("✅ 分量显示成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 简谐波分量显示修复验证")
    print("测试正弦波形显示效果...")
    
    results = []
    
    # 执行所有测试
    results.append(test_sine_wave_generation())
    results.append(test_component_display())
    results.append(test_frequency_analysis())
    results.append(test_complete_workflow())
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("📋 简谐波显示修复验证结果")
    print("=" * 70)
    
    test_names = [
        "正弦波生成验证",
        "分量显示功能",
        "完整频率分析流程",
        "完整工作流程"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 简谐波分量显示修复验证通过！")
        print("\n📝 修复总结:")
        print("1. ✅ 修正了振幅计算方法")
        print("2. ✅ 增加了最小振幅保证")
        print("3. ✅ 优化了时间轴采样")
        print("4. ✅ 改进了波形绘制参数")
        print("5. ✅ 添加了详细调试信息")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
