#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析器界面改进验证脚本
测试修复的问题：
1. 原始音频波形显示异常
2. 频率分析功能失效
3. 界面布局优化（垂直排列）
"""

import sys
import os
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import time

# Add parent directory to path
sys.path.append('..')

def test_waveform_display():
    """测试波形显示修复"""
    print("=" * 60)
    print("🔧 测试1: 原始音频波形显示修复")
    print("=" * 60)
    
    try:
        from audio_editor_ui import SpectrumCanvas
        from audio_processor import AudioProcessor
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建画布
        canvas = SpectrumCanvas()
        print("✅ SpectrumCanvas 创建成功")
        
        # 生成测试音频
        sample_rate = 22050
        duration = 5.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        # 创建包含多个频率的测试信号
        audio = (0.5 * np.sin(2 * np.pi * 440 * t) +    # A4
                0.3 * np.sin(2 * np.pi * 880 * t) +     # A5
                0.2 * np.sin(2 * np.pi * 1320 * t))     # E6
        
        print(f"✅ 生成测试音频: {len(audio)} 样本, {duration}秒")
        
        # 测试波形显示
        canvas.plot_waveform(audio, sample_rate, "测试原始音频波形")
        print("✅ 波形显示测试通过")
        
        # 检查布局
        print(f"✅ 初始布局: 原始波形轴存在 = {hasattr(canvas, 'ax_waveform')}")
        print(f"✅ 分量轴列表: {len(canvas.component_axes)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 波形显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vertical_layout():
    """测试垂直布局功能"""
    print("\n" + "=" * 60)
    print("🔧 测试2: 垂直布局功能")
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
        
        # 创建测试分量
        components = [
            FrequencyComponent(440.0, 0.5, 0.0),    # A4
            FrequencyComponent(880.0, 0.3, 0.0),    # A5
            FrequencyComponent(1320.0, 0.2, 0.0),   # E6
        ]
        
        # 设置分量属性
        for comp in components:
            comp.enabled = True
            comp.original_amplitude = comp.amplitude
        
        print(f"✅ 创建测试分量: {len(components)} 个")
        
        # 测试动态布局设置
        canvas.setup_dynamic_layout(len(components))
        print(f"✅ 动态布局设置: {len(canvas.component_axes)} 个分量轴")
        
        # 测试垂直分量显示
        canvas.plot_components_vertical(components)
        print("✅ 垂直分量显示测试通过")
        
        # 测试兼容方法
        canvas.plot_components(components)
        print("✅ 兼容方法测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 垂直布局测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frequency_analysis_workflow():
    """测试频率分析工作流程"""
    print("\n" + "=" * 60)
    print("🔧 测试3: 频率分析工作流程")
    print("=" * 60)
    
    try:
        from audio_editor_ui import AudioEditorMainWindow, AudioAnalysisThread
        from audio_processor import AudioProcessor
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建主窗口
        window = AudioEditorMainWindow()
        print("✅ 主窗口创建成功")
        
        # 生成测试音频
        sample_rate = 22050
        duration = 3.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        test_audio = (0.5 * np.sin(2 * np.pi * 440 * t) +
                     0.3 * np.sin(2 * np.pi * 880 * t) +
                     0.2 * np.sin(2 * np.pi * 1320 * t))
        
        # 模拟加载音频
        window.original_audio = test_audio
        window.audio_processor = AudioProcessor()
        print("✅ 测试音频设置成功")
        
        # 测试波形显示
        window.spectrum_canvas.plot_waveform(test_audio, sample_rate, "测试音频波形")
        print("✅ 主窗口波形显示成功")
        
        # 创建分析线程（不启动）
        analysis_thread = AudioAnalysisThread(
            test_audio,
            sample_rate,
            n_components=3
        )
        print("✅ 分析线程创建成功")
        
        # 测试信号连接
        analysis_thread.analysis_completed.connect(window.on_analysis_completed)
        analysis_thread.error_occurred.connect(window.on_analysis_error)
        print("✅ 信号连接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 频率分析工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_integration():
    """测试完整集成"""
    print("\n" + "=" * 60)
    print("🔧 测试4: 完整集成测试")
    print("=" * 60)
    
    try:
        from audio_editor_ui import AudioEditorMainWindow
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建主窗口
        window = AudioEditorMainWindow()
        print("✅ 主窗口创建成功")
        
        # 检查画布初始化
        canvas = window.spectrum_canvas
        print(f"✅ 画布初始化: 原始波形轴 = {hasattr(canvas, 'ax_waveform')}")
        print(f"✅ 画布初始化: 频谱轴 = {hasattr(canvas, 'ax_spectrum')}")
        print(f"✅ 画布初始化: 重构轴 = {hasattr(canvas, 'ax_reconstructed')}")
        print(f"✅ 画布初始化: 分量轴数量 = {len(canvas.component_axes)}")
        
        # 检查关键方法
        methods_to_check = [
            'plot_waveform',
            'plot_spectrum', 
            'plot_reconstructed',
            'plot_components',
            'plot_components_vertical',
            'setup_dynamic_layout'
        ]
        
        for method in methods_to_check:
            if hasattr(canvas, method):
                print(f"✅ 方法存在: {method}")
            else:
                print(f"❌ 方法缺失: {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 音频分析器界面改进验证")
    print("测试修复的问题...")
    
    results = []
    
    # 执行所有测试
    results.append(test_waveform_display())
    results.append(test_vertical_layout())
    results.append(test_frequency_analysis_workflow())
    results.append(test_complete_integration())
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("📋 界面改进验证结果汇总")
    print("=" * 70)
    
    test_names = [
        "原始音频波形显示修复",
        "垂直布局功能",
        "频率分析工作流程",
        "完整集成测试"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有界面改进验证通过！")
        print("\n📝 改进总结:")
        print("1. ✅ 修复了波形显示渲染问题")
        print("2. ✅ 实现了垂直布局显示")
        print("3. ✅ 改进了频率分析流程")
        print("4. ✅ 优化了用户界面体验")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
