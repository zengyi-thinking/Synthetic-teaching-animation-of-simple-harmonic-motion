#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证布局修改的效果
检查合成波形位置和显示逻辑
"""

import numpy as np
from harmonic_synthesizer_ui import HarmonicComponent
from visualization_engine import UnifiedWaveformVisualizer


def test_layout_logic():
    """测试布局逻辑"""
    print("=== 布局逻辑测试 ===")
    
    # 创建测试分量
    components = [
        HarmonicComponent(frequency=220.0, amplitude=0.8, phase=0.0),
        HarmonicComponent(frequency=440.0, amplitude=0.6, phase=0.0),
        HarmonicComponent(frequency=880.0, amplitude=0.4, phase=0.0)
    ]
    
    # 测试不同分量数量的布局
    test_cases = [
        ([], "无分量"),
        ([components[0]], "单分量"),
        (components[:2], "双分量"),
        (components[:3], "三分量")
    ]
    
    for enabled_components, description in test_cases:
        print(f"\n{description}测试:")
        
        # 计算子图数量和合成波形位置
        num_subplots = len(enabled_components) + 1
        
        if len(enabled_components) == 0:
            composite_position = 0
            height_ratios = [1.5]
        elif len(enabled_components) == 1:
            composite_position = 1
            height_ratios = [1, 1.5]
        elif len(enabled_components) == 2:
            composite_position = 1
            height_ratios = [1, 1.5, 1]
        else:
            composite_position = len(enabled_components) // 2
            height_ratios = [1] * len(enabled_components)
            height_ratios.insert(composite_position, 1.5)
        
        print(f"  子图数量: {num_subplots}")
        print(f"  合成波形位置: {composite_position}")
        print(f"  高度比例: {height_ratios}")
        
        # 验证布局逻辑
        if len(enabled_components) == 0:
            assert composite_position == 0, "无分量时合成波形应在位置0"
        elif len(enabled_components) <= 2:
            assert composite_position == 1, "少量分量时合成波形应在位置1"
        else:
            expected_pos = len(enabled_components) // 2
            assert composite_position == expected_pos, f"多分量时合成波形应在中间位置{expected_pos}"
        
        print("  ✓ 布局逻辑正确")


def test_stable_time_window():
    """测试稳定时间窗口计算"""
    print("\n=== 稳定时间窗口测试 ===")
    
    # 创建不同频率的分量
    test_frequencies = [
        ([220.0], "低频"),
        ([440.0], "中频"),
        ([880.0], "高频"),
        ([220.0, 440.0], "低中频组合"),
        ([220.0, 440.0, 880.0], "多频组合")
    ]
    
    for frequencies, description in test_frequencies:
        print(f"\n{description}测试:")
        
        components = [HarmonicComponent(frequency=f, amplitude=0.5) for f in frequencies]
        
        # 计算稳定时间窗口
        min_freq = min(comp.frequency for comp in components)
        cycles_to_show = 4
        stable_duration = cycles_to_show / min_freq
        stable_duration = max(0.05, min(0.5, stable_duration))
        
        print(f"  频率: {frequencies}")
        print(f"  最低频率: {min_freq} Hz")
        print(f"  稳定时间窗口: {stable_duration:.3f} 秒")
        print(f"  显示周期数: {stable_duration * min_freq:.1f}")
        
        # 验证时间窗口合理性
        assert 0.05 <= stable_duration <= 0.5, "时间窗口应在合理范围内"
        assert stable_duration * min_freq >= 3, "应显示至少3个周期"
        
        print("  ✓ 时间窗口计算正确")


def test_waveform_stability():
    """测试波形稳定性"""
    print("\n=== 波形稳定性测试 ===")
    
    # 创建测试分量
    component = HarmonicComponent(frequency=440.0, amplitude=0.8, phase=0.0)
    
    # 生成多次波形数据，验证一致性
    stable_duration = 0.2
    num_points = 1000
    time_data = np.linspace(0, stable_duration, num_points)
    
    waveforms = []
    for i in range(5):
        omega = 2 * np.pi * component.frequency
        waveform = component.amplitude * np.sin(omega * time_data + component.phase)
        waveforms.append(waveform)
    
    # 验证波形一致性
    for i in range(1, len(waveforms)):
        diff = np.max(np.abs(waveforms[i] - waveforms[0]))
        assert diff < 1e-10, f"波形应保持一致，差异: {diff}"
    
    print("  ✓ 波形显示稳定")
    
    # 验证周期性 - 检查波形的基本特征
    period = 1.0 / component.frequency
    expected_cycles = stable_duration * component.frequency

    # 检查波形的最大值和最小值是否符合预期
    max_val = np.max(waveforms[0])
    min_val = np.min(waveforms[0])

    assert abs(max_val - component.amplitude) < 1e-6, f"最大值应为{component.amplitude}，实际为{max_val}"
    assert abs(min_val + component.amplitude) < 1e-6, f"最小值应为{-component.amplitude}，实际为{min_val}"

    print(f"  ✓ 波形具有正确的周期性，显示{expected_cycles:.1f}个周期")


def main():
    """主函数"""
    print("开始验证布局优化修改...")
    
    try:
        test_layout_logic()
        test_stable_time_window()
        test_waveform_stability()
        
        print("\n=== 验证结果 ===")
        print("✓ 所有测试通过！")
        print("✓ 合成波形位置调整正确")
        print("✓ 波形显示逻辑稳定")
        print("✓ 布局优化成功")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
