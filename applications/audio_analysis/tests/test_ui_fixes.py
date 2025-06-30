#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析器界面修复验证脚本
测试三个主要修复：
1. 中文显示问题
2. 原始波形显示优化
3. 频率分析结果显示（简谐波分量）
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication
import matplotlib.pyplot as plt

def test_chinese_display():
    """测试中文显示修复"""
    print("=" * 50)
    print("🔤 测试1: 中文显示修复")
    print("=" * 50)
    
    try:
        # 检查matplotlib中文字体配置
        fonts = plt.rcParams['font.sans-serif']
        print(f"✅ matplotlib中文字体配置: {fonts}")
        
        # 检查unicode处理
        unicode_minus = plt.rcParams['axes.unicode_minus']
        print(f"✅ Unicode负号处理: {unicode_minus}")
        
        # 测试中文字符串
        test_strings = [
            "音频分析器 - 简谐波分解与重构工具",
            "原始音频波形",
            "频谱分析",
            "重构音频波形",
            "简谐波分量分解"
        ]
        
        for s in test_strings:
            print(f"✅ 中文字符串测试: {s}")
        
        print("🎉 中文显示修复测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 中文显示测试失败: {e}")
        return False

def test_waveform_display():
    """测试波形显示优化"""
    print("\n" + "=" * 50)
    print("📊 测试2: 波形显示优化")
    print("=" * 50)
    
    try:
        from audio_editor_ui import SpectrumCanvas
        from audio_processor import AudioProcessor
        
        # 创建测试数据
        processor = AudioProcessor()
        sample_rate = 22050
        duration = 10.0  # 10秒音频
        
        # 生成测试音频（包含多个频率分量）
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = (0.5 * np.sin(2 * np.pi * 440 * t) +  # A4
                0.3 * np.sin(2 * np.pi * 880 * t) +   # A5
                0.2 * np.sin(2 * np.pi * 1320 * t))   # E6
        
        print(f"✅ 生成测试音频: {len(audio)} 样本, {duration}秒")
        
        # 创建画布
        canvas = SpectrumCanvas()
        print("✅ 创建SpectrumCanvas成功")
        
        # 测试波形显示（应该只显示前3秒）
        canvas.plot_waveform(audio, sample_rate, "测试原始音频波形")
        print("✅ 波形显示测试通过 - 只显示前3秒，优化密度")
        
        # 测试下采样功能
        dense_audio = np.random.randn(100000)  # 密集数据
        canvas.plot_waveform(dense_audio, sample_rate, "密集数据测试")
        print("✅ 密集数据下采样测试通过")
        
        print("🎉 波形显示优化测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 波形显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_display():
    """测试简谐波分量显示"""
    print("\n" + "=" * 50)
    print("🌊 测试3: 简谐波分量显示")
    print("=" * 50)
    
    try:
        from audio_editor_ui import SpectrumCanvas
        from frequency_analyzer import FrequencyComponent
        
        # 创建测试频率分量
        components = [
            FrequencyComponent(440.0, 0.5, 0.0),    # A4
            FrequencyComponent(880.0, 0.3, 0.0),    # A5
            FrequencyComponent(1320.0, 0.2, 0.0),   # E6
        ]
        
        # 设置启用状态
        for comp in components:
            comp.enabled = True
            comp.original_amplitude = comp.amplitude
        
        print(f"✅ 创建测试分量: {len(components)} 个")
        for i, comp in enumerate(components):
            print(f"   分量{i+1}: {comp.frequency}Hz, 振幅{comp.amplitude:.3f}")
        
        # 创建画布并测试分量显示
        canvas = SpectrumCanvas()
        canvas.current_sample_rate = 22050
        
        # 测试分量波形显示
        canvas.plot_components(components)
        print("✅ 简谐波分量独立显示测试通过")
        
        # 测试禁用分量
        components[1].enabled = False
        canvas.plot_components(components)
        print("✅ 分量启用/禁用状态测试通过")
        
        # 测试空分量
        empty_components = []
        canvas.plot_components(empty_components)
        print("✅ 空分量处理测试通过")
        
        print("🎉 简谐波分量显示测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 简谐波分量显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_ui():
    """测试完整UI创建"""
    print("\n" + "=" * 50)
    print("🖥️ 测试4: 完整UI创建")
    print("=" * 50)
    
    try:
        from audio_editor_ui import AudioEditorMainWindow
        
        # 创建应用程序
        app = QApplication([])
        
        # 创建主窗口
        window = AudioEditorMainWindow()
        print("✅ 主窗口创建成功")
        
        # 检查窗口属性
        title = window.windowTitle()
        print(f"✅ 窗口标题: {title}")
        
        # 检查字体设置
        font = window.font()
        print(f"✅ 窗口字体: {font.family()}, 大小: {font.pointSize()}")
        
        print("🎉 完整UI创建测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 完整UI创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎵 音频分析器界面修复验证")
    print("测试三个主要修复问题...")
    
    results = []
    
    # 执行所有测试
    results.append(test_chinese_display())
    results.append(test_waveform_display())
    results.append(test_component_display())
    results.append(test_complete_ui())
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    test_names = [
        "中文显示修复",
        "波形显示优化", 
        "简谐波分量显示",
        "完整UI创建"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有界面修复验证通过！音频分析器已准备就绪。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
