#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例音频文件生成器
生成用于演示频率分解功能的测试音频文件
"""

import numpy as np
import os
from audio_processor import AudioProcessor

def generate_single_tone(frequency=440, duration=3.0, sample_rate=22050):
    """
    生成单音调
    
    Args:
        frequency: 频率 (Hz)
        duration: 持续时间 (秒)
        sample_rate: 采样率
    
    Returns:
        音频数据
    """
    processor = AudioProcessor(sample_rate)
    audio_data = processor.create_test_tone(frequency, duration, amplitude=0.7)
    return audio_data

def generate_chord(frequencies, duration=3.0, sample_rate=22050):
    """
    生成和弦
    
    Args:
        frequencies: 频率列表
        duration: 持续时间
        sample_rate: 采样率
    
    Returns:
        音频数据
    """
    processor = AudioProcessor(sample_rate)
    amplitudes = [0.3] * len(frequencies)  # 均匀振幅
    audio_data = processor.create_chord(frequencies, duration, amplitudes)
    return audio_data

def generate_piano_notes():
    """生成钢琴音符频率"""
    # 钢琴音符频率 (基于A4=440Hz)
    notes = {
        'C4': 261.63,   # 中央C
        'D4': 293.66,
        'E4': 329.63,
        'F4': 349.23,
        'G4': 392.00,
        'A4': 440.00,   # 标准A
        'B4': 493.88,
        'C5': 523.25,
        'D5': 587.33,
        'E5': 659.25
    }
    return notes

def generate_major_chord_frequencies():
    """生成大调和弦频率"""
    chords = {
        'C_major': [261.63, 329.63, 392.00],      # C-E-G
        'F_major': [349.23, 440.00, 523.25],      # F-A-C
        'G_major': [392.00, 493.88, 587.33],      # G-B-D
        'Am_minor': [220.00, 261.63, 329.63],     # A-C-E
        'Dm_minor': [293.66, 349.23, 440.00],     # D-F-A
    }
    return chords

def generate_complex_waveform(duration=4.0, sample_rate=22050):
    """
    生成复杂波形（多个简谐波叠加）
    
    Args:
        duration: 持续时间
        sample_rate: 采样率
    
    Returns:
        音频数据
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 基频和谐波
    fundamental = 220.0  # A3
    harmonics = [
        (fundamental, 0.5),      # 基频
        (fundamental * 2, 0.3),  # 二次谐波
        (fundamental * 3, 0.2),  # 三次谐波
        (fundamental * 4, 0.1),  # 四次谐波
        (fundamental * 5, 0.05), # 五次谐波
    ]
    
    # 叠加谐波
    audio_data = np.zeros_like(t)
    for freq, amp in harmonics:
        audio_data += amp * np.sin(2 * np.pi * freq * t)
    
    # 添加包络（淡入淡出）
    envelope_length = int(0.1 * sample_rate)  # 100ms
    envelope = np.ones_like(audio_data)
    
    # 淡入
    envelope[:envelope_length] = np.linspace(0, 1, envelope_length)
    # 淡出
    envelope[-envelope_length:] = np.linspace(1, 0, envelope_length)
    
    audio_data *= envelope
    
    # 标准化
    audio_data = audio_data / np.max(np.abs(audio_data)) * 0.8
    
    return audio_data

def generate_beat_frequency_demo(freq1=440, freq2=445, duration=5.0, sample_rate=22050):
    """
    生成拍频演示音频
    
    Args:
        freq1: 第一个频率
        freq2: 第二个频率
        duration: 持续时间
        sample_rate: 采样率
    
    Returns:
        音频数据
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 两个接近频率的正弦波
    wave1 = 0.5 * np.sin(2 * np.pi * freq1 * t)
    wave2 = 0.5 * np.sin(2 * np.pi * freq2 * t)
    
    # 叠加产生拍频
    audio_data = wave1 + wave2
    
    return audio_data

def main():
    """主函数 - 生成所有示例音频文件"""
    print("🎵 开始生成示例音频文件...")
    
    # 确保输出目录存在
    output_dir = "sample_audio"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    processor = AudioProcessor()
    
    # 1. 生成单音调
    print("生成单音调...")
    piano_notes = generate_piano_notes()
    
    # A4标准音
    a4_audio = generate_single_tone(440, 3.0)
    processor.save_audio(a4_audio, os.path.join(output_dir, "A4_440Hz.wav"))
    
    # C大调音阶
    c_major_scale = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    scale_audio = []
    for note in c_major_scale:
        note_audio = generate_single_tone(piano_notes[note], 0.5)
        scale_audio.append(note_audio)
    
    # 拼接音阶
    full_scale = np.concatenate(scale_audio)
    processor.save_audio(full_scale, os.path.join(output_dir, "C_major_scale.wav"))
    
    # 2. 生成和弦
    print("生成和弦...")
    chords = generate_major_chord_frequencies()
    
    for chord_name, frequencies in chords.items():
        chord_audio = generate_chord(frequencies, 3.0)
        filename = f"{chord_name}_chord.wav"
        processor.save_audio(chord_audio, os.path.join(output_dir, filename))
    
    # 3. 生成复杂波形
    print("生成复杂波形...")
    complex_audio = generate_complex_waveform(4.0)
    processor.save_audio(complex_audio, os.path.join(output_dir, "complex_harmonics.wav"))
    
    # 4. 生成拍频演示
    print("生成拍频演示...")
    beat_audio = generate_beat_frequency_demo(440, 445, 5.0)
    processor.save_audio(beat_audio, os.path.join(output_dir, "beat_frequency_demo.wav"))
    
    # 5. 生成教学演示音频
    print("生成教学演示音频...")
    
    # 简单三和弦进行：C-F-G-C
    chord_progression = []
    progression_chords = [
        chords['C_major'],
        chords['F_major'], 
        chords['G_major'],
        chords['C_major']
    ]
    
    for chord_freqs in progression_chords:
        chord_audio = generate_chord(chord_freqs, 2.0)
        chord_progression.append(chord_audio)
        # 添加短暂间隔
        silence = np.zeros(int(0.2 * processor.target_sr))
        chord_progression.append(silence)
    
    progression_audio = np.concatenate(chord_progression)
    processor.save_audio(progression_audio, os.path.join(output_dir, "chord_progression.wav"))
    
    # 6. 生成频率分解演示音频
    print("生成频率分解演示音频...")
    
    # 包含明显频率分量的音频
    demo_frequencies = [261.63, 329.63, 392.00, 523.25, 659.25]  # C-E-G-C-E
    demo_amplitudes = [0.4, 0.3, 0.35, 0.25, 0.2]
    
    demo_audio = processor.create_chord(demo_frequencies, 4.0, demo_amplitudes)
    processor.save_audio(demo_audio, os.path.join(output_dir, "frequency_analysis_demo.wav"))
    
    print("✅ 示例音频文件生成完成！")
    print(f"文件保存在: {os.path.abspath(output_dir)}")
    
    # 列出生成的文件
    print("\n📁 生成的文件列表:")
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith('.wav'):
            filepath = os.path.join(output_dir, filename)
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"   {filename} ({size:.1f} KB)")

if __name__ == "__main__":
    main()
