#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的波形显示测试
验证修复后的采样范围和显示效果
"""

import sys
import os
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from harmonic_synthesizer_ui import HarmonicComponent


def test_time_calculation():
    """测试时间计算逻辑"""
    print("=== 测试时间计算逻辑 ===")
    
    # 模拟不同频率的分量
    test_cases = [
        ([20.0], "低频单分量"),
        ([20.0, 43.0], "低频双分量"),
        ([440.0, 880.0], "高频双分量"),
        ([10.0, 100.0, 1000.0], "极端频率差异"),
        ([100, 200, 300, 500, 800], "多分量")
    ]
    
    for frequencies, description in test_cases:
        print(f"\n{description}: {frequencies}Hz")
        
        # 创建分量
        components = []
        for freq in frequencies:
            comp = HarmonicComponent(frequency=freq, amplitude=0.5, phase=0.0)
            components.append(comp)
        
        # 模拟时间计算逻辑
        enabled_components = [comp for comp in components if comp.enabled]
        if enabled_components:
            min_freq = min(comp.frequency for comp in enabled_components)
            cycles_to_show = 4
            if min_freq > 0:
                display_duration = cycles_to_show / min_freq
                display_duration = min(display_duration, 0.5)  # 最多0.5秒
                display_duration = max(display_duration, 0.05)  # 最少0.05秒
            else:
                display_duration = 0.2
        else:
            display_duration = 0.2
        
        print(f"  最低频率: {min_freq:.1f}Hz")
        print(f"  显示时长: {display_duration:.3f}秒")
        print(f"  显示周期数: {display_duration * min_freq:.1f}个周期")
        
        # 生成时间数据
        t_display = np.linspace(0, display_duration, 1000)
        print(f"  采样点数: {len(t_display)}")
        print(f"  时间分辨率: {t_display[1] - t_display[0]:.6f}秒")


def test_waveform_generation():
    """测试波形生成"""
    print("\n=== 测试波形生成 ===")
    
    # 创建测试分量
    comp1 = HarmonicComponent(frequency=20.0, amplitude=0.8, phase=0.0)
    comp2 = HarmonicComponent(frequency=43.0, amplitude=0.6, phase=np.pi/4)
    
    components = [comp1, comp2]
    
    # 计算显示时间
    min_freq = min(comp.frequency for comp in components)
    display_duration = 4 / min_freq  # 4个周期
    display_duration = min(display_duration, 0.5)
    display_duration = max(display_duration, 0.05)
    
    print(f"测试分量: {[comp.frequency for comp in components]}Hz")
    print(f"显示时长: {display_duration:.3f}秒")
    
    # 生成时间数据
    t_display = np.linspace(0, display_duration, 1000)
    
    # 生成波形
    composite_wave = np.zeros_like(t_display)
    for i, component in enumerate(components):
        wave = component.amplitude * np.sin(
            2 * np.pi * component.frequency * t_display + component.phase
        )
        composite_wave += wave
        print(f"分量 {i+1}: 频率={component.frequency}Hz, 振幅={component.amplitude}")
    
    # 分析波形特征
    print(f"合成波形:")
    print(f"  最大值: {np.max(composite_wave):.3f}")
    print(f"  最小值: {np.min(composite_wave):.3f}")
    print(f"  峰峰值: {np.max(composite_wave) - np.min(composite_wave):.3f}")
    
    # 计算周期数
    period_20hz = 1 / 20.0
    periods_shown = display_duration / period_20hz
    print(f"  20Hz周期数: {periods_shown:.1f}")


def test_subplots_layout():
    """测试子图布局计算"""
    print("\n=== 测试子图布局计算 ===")
    
    test_component_counts = [1, 2, 3, 5, 8, 10]
    
    for num_components in test_component_counts:
        # 计算子图数量：合成波形 + 各个分量
        num_subplots = 1 + num_components
        
        # 计算动态高度比例
        if num_subplots == 1:
            height_ratios = [1]
        else:
            height_ratios = [1.5] + [1] * num_components
        
        # 计算动态间距
        if num_subplots <= 2:
            hspace = 0.4
        elif num_subplots <= 4:
            hspace = 0.3
        else:
            hspace = 0.2
        
        # 计算字体大小
        if num_subplots <= 3:
            tick_size = 9
            title_size = 11
        elif num_subplots <= 5:
            tick_size = 8
            title_size = 10
        else:
            tick_size = 7
            title_size = 9
        
        print(f"{num_components}个分量 ({num_subplots}个子图):")
        print(f"  高度比例: {height_ratios}")
        print(f"  间距: {hspace}")
        print(f"  字体大小: tick={tick_size}, title={title_size}")


def main():
    """主函数"""
    print("波形显示修复效果验证")
    print("=" * 50)
    
    test_time_calculation()
    test_waveform_generation()
    test_subplots_layout()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n修复要点总结：")
    print("1. 根据最低频率自动计算显示时间窗口（4个周期）")
    print("2. 限制显示时间在0.05-0.5秒范围内")
    print("3. 使用1000个采样点进行可视化显示")
    print("4. 动态调整子图高度比例和间距")
    print("5. 根据分量数量调整字体大小")


if __name__ == "__main__":
    main()
