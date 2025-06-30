#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析项目测试脚本
验证所有核心功能的正确性
"""

import sys
import os
import numpy as np
import time
import unittest

# 添加路径
sys.path.append('..')

from audio_processor import AudioProcessor
from frequency_analyzer import FrequencyAnalyzer
from audio_player import AudioPlayer

class TestAudioProcessor(unittest.TestCase):
    """测试音频处理器"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = AudioProcessor(sample_rate=22050)
    
    def test_create_test_tone(self):
        """测试生成测试音调"""
        frequency = 440.0
        duration = 1.0
        amplitude = 0.5
        
        audio_data = self.processor.create_test_tone(frequency, duration, amplitude)
        
        # 验证音频数据
        self.assertEqual(len(audio_data), int(self.processor.target_sr * duration))
        self.assertLessEqual(np.max(np.abs(audio_data)), amplitude)
        
        print(f"✅ 测试音调生成: {frequency}Hz, {duration}s, 最大振幅: {np.max(np.abs(audio_data)):.3f}")
    
    def test_create_chord(self):
        """测试生成和弦"""
        frequencies = [261.63, 329.63, 392.00]  # C大调和弦
        duration = 2.0
        amplitudes = [0.3, 0.3, 0.3]
        
        audio_data = self.processor.create_chord(frequencies, duration, amplitudes)
        
        # 验证音频数据
        self.assertEqual(len(audio_data), int(self.processor.target_sr * duration))
        self.assertLessEqual(np.max(np.abs(audio_data)), 1.0)
        
        print(f"✅ 和弦生成: {frequencies} Hz, 时长: {duration}s")
    
    def test_normalize_audio(self):
        """测试音频标准化"""
        # 创建测试音频
        test_audio = np.array([0.1, 0.5, -0.8, 0.3, -0.2])
        
        # 峰值标准化
        normalized_peak = self.processor.normalize_audio(test_audio, method='peak')
        self.assertAlmostEqual(np.max(np.abs(normalized_peak)), 1.0, places=5)
        
        # RMS标准化
        normalized_rms = self.processor.normalize_audio(test_audio, method='rms')
        rms = np.sqrt(np.mean(normalized_rms ** 2))
        self.assertAlmostEqual(rms, 0.1, places=2)
        
        print("✅ 音频标准化测试通过")

class TestFrequencyAnalyzer(unittest.TestCase):
    """测试频率分析器"""
    
    def setUp(self):
        """测试前准备"""
        self.analyzer = FrequencyAnalyzer(sample_rate=22050)
        self.processor = AudioProcessor(sample_rate=22050)
    
    def test_analyze_single_frequency(self):
        """测试单频率分析"""
        # 生成440Hz测试音调
        test_frequency = 440.0
        duration = 2.0
        audio_data = self.processor.create_test_tone(test_frequency, duration, 0.8)
        
        # 分析频率
        components = self.analyzer.analyze_audio(audio_data, n_components=3)
        
        # 验证结果
        self.assertGreater(len(components), 0)
        
        # 检查是否检测到目标频率
        detected_freqs = [comp.frequency for comp in components]
        closest_freq = min(detected_freqs, key=lambda x: abs(x - test_frequency))
        frequency_error = abs(closest_freq - test_frequency)
        
        self.assertLess(frequency_error, 5.0)  # 允许5Hz误差
        
        print(f"✅ 单频率分析: 目标{test_frequency}Hz, 检测到{closest_freq:.1f}Hz, 误差{frequency_error:.1f}Hz")
    
    def test_analyze_chord(self):
        """测试和弦分析"""
        # 生成C大调和弦
        frequencies = [261.63, 329.63, 392.00]
        duration = 3.0
        amplitudes = [0.4, 0.3, 0.3]
        
        audio_data = self.processor.create_chord(frequencies, duration, amplitudes)
        
        # 分析频率
        components = self.analyzer.analyze_audio(audio_data, n_components=5)
        
        # 验证结果
        self.assertGreaterEqual(len(components), 3)
        
        detected_freqs = [comp.frequency for comp in components]
        
        # 检查是否检测到所有目标频率
        for target_freq in frequencies:
            closest_freq = min(detected_freqs, key=lambda x: abs(x - target_freq))
            frequency_error = abs(closest_freq - target_freq)
            self.assertLess(frequency_error, 10.0)  # 允许10Hz误差
        
        detected_str = [f'{f:.1f}' for f in detected_freqs[:3]]
        print(f"✅ 和弦分析: 目标{frequencies}Hz, 检测到{detected_str}Hz")
    
    def test_reconstruct_audio(self):
        """测试音频重构"""
        # 生成测试音频
        test_frequency = 523.25  # C5
        duration = 1.5
        original_audio = self.processor.create_test_tone(test_frequency, duration, 0.6)
        
        # 分析频率
        components = self.analyzer.analyze_audio(original_audio, n_components=3)
        
        # 重构音频
        reconstructed_audio = self.analyzer.reconstruct_audio(duration)
        
        # 验证重构音频
        self.assertEqual(len(reconstructed_audio), len(original_audio))
        
        # 计算相关性
        correlation = np.corrcoef(original_audio, reconstructed_audio)[0, 1]
        self.assertGreater(correlation, 0.8)  # 相关性应该很高
        
        print(f"✅ 音频重构: 相关性{correlation:.3f}")

class TestAudioPlayer(unittest.TestCase):
    """测试音频播放器"""
    
    def setUp(self):
        """测试前准备"""
        self.player = AudioPlayer(sample_rate=22050)
        self.processor = AudioProcessor(sample_rate=22050)
    
    def test_load_audio(self):
        """测试音频加载"""
        # 生成测试音频
        test_audio = self.processor.create_test_tone(440, 2.0, 0.5)
        
        # 加载音频
        self.player.load_audio(test_audio)
        
        # 验证加载结果
        self.assertIsNotNone(self.player.current_audio)
        self.assertEqual(len(self.player.current_audio), len(test_audio))
        self.assertAlmostEqual(self.player.total_duration, 2.0, places=1)
        
        print(f"✅ 音频加载: 时长{self.player.total_duration:.2f}s")
    
    def test_playback_info(self):
        """测试播放信息"""
        # 生成测试音频
        test_audio = self.processor.create_test_tone(330, 1.0, 0.4)
        self.player.load_audio(test_audio)
        
        # 获取播放信息
        info = self.player.get_playback_info()
        
        # 验证信息
        self.assertIn('is_playing', info)
        self.assertIn('total_duration', info)
        self.assertIn('current_position', info)
        self.assertIn('progress', info)
        
        self.assertFalse(info['is_playing'])
        self.assertAlmostEqual(info['total_duration'], 1.0, places=1)
        
        print("✅ 播放信息获取正常")

def run_integration_test():
    """运行集成测试"""
    print("\n🔄 运行集成测试...")
    
    try:
        # 创建组件
        processor = AudioProcessor()
        analyzer = FrequencyAnalyzer()
        player = AudioPlayer()
        
        # 生成复杂测试音频
        frequencies = [220, 330, 440, 660]  # A3, E4, A4, E5
        amplitudes = [0.4, 0.3, 0.5, 0.2]
        duration = 3.0
        
        print("生成复杂测试音频...")
        test_audio = processor.create_chord(frequencies, duration, amplitudes)
        
        # 频率分析
        print("执行频率分析...")
        components = analyzer.analyze_audio(test_audio, n_components=6)
        
        # 验证检测结果
        detected_freqs = [comp.frequency for comp in components]
        print(f"检测到的频率: {[f'{f:.1f}Hz' for f in detected_freqs]}")
        
        # 音频重构
        print("重构音频...")
        reconstructed = analyzer.reconstruct_audio(duration)
        
        # 计算重构质量
        correlation = np.corrcoef(test_audio, reconstructed)[0, 1]
        print(f"重构质量 (相关性): {correlation:.3f}")
        
        # 测试播放器
        print("测试播放器...")
        player.load_audio(test_audio)
        playback_info = player.get_playback_info()
        print(f"播放器状态: 时长{playback_info['total_duration']:.2f}s")
        
        print("✅ 集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎵 音频分析项目测试")
    print("=" * 50)
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行单元测试
    print("运行单元测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestAudioProcessor))
    test_suite.addTest(unittest.makeSuite(TestFrequencyAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestAudioPlayer))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 运行集成测试
    integration_success = run_integration_test()
    
    # 计算耗时
    end_time = time.time()
    duration = end_time - start_time
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    unit_tests_passed = result.wasSuccessful()
    
    print(f"单元测试: {'✅ 通过' if unit_tests_passed else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    print(f"总耗时: {duration:.2f}秒")
    
    if unit_tests_passed and integration_success:
        print("\n🎉 所有测试通过！音频分析项目功能正常。")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
