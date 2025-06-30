# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 音频分析引擎
负责分析音频并分解为简谐振动分量
"""

import numpy as np
from scipy import signal
from scipy.fft import rfft, rfftfreq
from typing import List, Tuple, Dict, Optional

from harmonic_core import HarmonicMotion, HarmonicParams, HarmonicType, SuperpositionMotion


class AudioAnalyzer:
    """音频分析引擎，用于分析音频并分解为简谐振动分量"""
    
    def __init__(self, sample_rate=44100):
        """初始化音频分析引擎
        
        Args:
            sample_rate: 采样率，默认44.1kHz
        """
        self.sample_rate = sample_rate
        
        # 基本音符频率参考表
        self.freq_to_note = {
            261.63: 'C4', 277.18: 'C#4', 293.66: 'D4', 311.13: 'D#4', 
            329.63: 'E4', 349.23: 'F4', 369.99: 'F#4', 392.00: 'G4', 
            415.30: 'G#4', 440.00: 'A4', 466.16: 'A#4', 493.88: 'B4',
            523.25: 'C5'
        }
        
        # 音符频率的容差范围 (Hz)
        self.note_tolerance = 5.0
        
    def analyze_frequency_content(self, audio_data: np.ndarray, window_type='hann', zero_padding=1) -> Tuple[np.ndarray, np.ndarray]:
        """分析音频的频率内容
        
        Args:
            audio_data: 音频数据数组
            window_type: 窗函数类型 ('hann', 'hamming', 'blackman')
            zero_padding: 零填充倍数，用于增加频率分辨率
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (频率数组, 振幅数组)
        """
        # 选择窗函数
        if window_type == 'hann':
            window = signal.windows.hann(len(audio_data))
        elif window_type == 'hamming':
            window = signal.windows.hamming(len(audio_data))
        elif window_type == 'blackman':
            window = signal.windows.blackman(len(audio_data))
        else:
            window = signal.windows.hann(len(audio_data))
        
        # 应用窗函数减少频谱泄漏
        windowed_data = audio_data * window
        
        # 增加零填充以提高频率分辨率
        padded_length = len(windowed_data) * zero_padding
        
        # 计算FFT
        fft_result = rfft(windowed_data, n=padded_length)
        magnitudes = np.abs(fft_result) * 2 / len(windowed_data)
        frequencies = rfftfreq(padded_length, 1/self.sample_rate)
        
        return frequencies, magnitudes
    
    def find_dominant_frequencies(self, 
                                 audio_data: np.ndarray, 
                                 num_peaks: int = 5, 
                                 min_amplitude: float = 0.1,
                                 min_freq_distance: float = None) -> List[Tuple[float, float]]:
        """找出音频中的主要频率成分
        
        Args:
            audio_data: 音频数据数组
            num_peaks: 要返回的峰值数量
            min_amplitude: 最小振幅阈值（相对于最大振幅）
            min_freq_distance: 频率峰值间的最小距离(Hz)，若为None则自动计算
            
        Returns:
            List[Tuple[float, float]]: [(频率1, 振幅1), (频率2, 振幅2), ...]，按振幅降序排列
        """
        # 检测是否有可能是拍现象（需要更高的频率分辨率）
        # 拍现象通常由两个频率接近的正弦波组成，频率差为1-20Hz之间
        is_potential_beat = False
        
        # 首先用标准分辨率进行分析
        frequencies, magnitudes = self.analyze_frequency_content(audio_data)
        
        # 获取初步的频率峰值
        peaks, _ = signal.find_peaks(magnitudes)
        if len(peaks) >= 2:
            peak_freqs = frequencies[peaks]
            # 计算相邻峰值间的最小频率差
            peak_freqs.sort()
            freq_diffs = np.diff(peak_freqs)
            min_diff = np.min(freq_diffs) if len(freq_diffs) > 0 else float('inf')
            
            # 如果频率差小于20Hz，可能是拍现象
            if min_diff < 20:
                is_potential_beat = True
        
        # 如果可能是拍现象，使用更高分辨率再次分析
        if is_potential_beat:
            frequencies, magnitudes = self.analyze_frequency_content(audio_data, window_type='blackman', zero_padding=4)
            
            # 如果没有指定最小频率距离，则设置为较小的值以便检测接近的频率
            if min_freq_distance is None:
                min_freq_distance = 2.0  # 2Hz的最小间距，足够区分拍现象
        else:
            # 普通情况下，使用默认设置
            if min_freq_distance is None:
                min_freq_distance = 10.0
        
        # 跳过极低频率 (< 20 Hz)，这些通常是DC偏移或噪声
        min_freq_idx = np.searchsorted(frequencies, 20)
        frequencies = frequencies[min_freq_idx:]
        magnitudes = magnitudes[min_freq_idx:]
        
        # 如果没有数据，返回空列表
        if len(frequencies) == 0:
            return []
        
        # 计算振幅阈值
        max_magnitude = np.max(magnitudes)
        threshold = max_magnitude * min_amplitude
        
        # 找出所有超过阈值的峰值
        # 将最小距离从索引单位转换为频率单位
        freq_resolution = frequencies[1] - frequencies[0]
        min_distance_idx = int(min_freq_distance / freq_resolution) if freq_resolution > 0 else 10
        min_distance_idx = max(1, min_distance_idx)
        
        peaks, properties = signal.find_peaks(magnitudes, height=threshold, distance=min_distance_idx)
        
        # 按振幅降序排列
        if len(peaks) == 0:
            return []
            
        peak_heights = properties['peak_heights']
        peak_freqs = frequencies[peaks]
        
        # 排序并组合结果
        sorted_indices = np.argsort(peak_heights)[::-1]  # 降序
        peak_freqs = peak_freqs[sorted_indices]
        peak_heights = peak_heights[sorted_indices]
        
        # 返回最强的num_peaks个峰值
        peak_freqs_mags = list(zip(peak_freqs[:num_peaks], peak_heights[:num_peaks]))
        
        # 检查是否有接近的频率并打印调试信息
        if is_potential_beat and len(peak_freqs_mags) >= 2:
            freq1, amp1 = peak_freqs_mags[0]
            freq2, amp2 = peak_freqs_mags[1]
            beat_freq = abs(freq1 - freq2)
            if beat_freq < 10:  # 10Hz以内的差异视为拍现象
                print(f"检测到可能的拍现象: 频率1={freq1:.1f}Hz, 频率2={freq2:.1f}Hz, 拍频={beat_freq:.1f}Hz")
        
        return peak_freqs_mags[:num_peaks]
    
    def decompose_to_harmonics(self, audio_data: np.ndarray, num_components: int = 5) -> SuperpositionMotion:
        """将音频分解为简谐振动的叠加
        
        Args:
            audio_data: 音频数据数组
            num_components: 要分解的简谐振动分量数量
            
        Returns:
            SuperpositionMotion: 分解后的简谐振动叠加
        """
        # 判断是否可能是拍现象音频
        # 对于拍现象，我们应用特殊的分析设置，提高频率分辨率
        is_beat = False
        spectral_flatness = 0
        
        try:
            from scipy.stats import entropy
            # 计算频谱的平坦度，拍现象通常有几个明显的峰值，平坦度较低
            frequencies, magnitudes = self.analyze_frequency_content(audio_data)
            if len(magnitudes) > 0 and np.sum(magnitudes) > 0:
                # 归一化频谱
                norm_magnitudes = magnitudes / np.sum(magnitudes)
                # 计算频谱熵
                spectral_entropy = entropy(norm_magnitudes)
                # 理论上的最大熵
                max_entropy = np.log(len(norm_magnitudes))
                # 频谱平坦度 (0-1)，越低表示频谱越集中在少数频率上
                if max_entropy > 0:
                    spectral_flatness = spectral_entropy / max_entropy
                    
                    # 拍现象通常频谱平坦度较低且有几个明显的峰值
                    if spectral_flatness < 0.3:
                        is_beat = True
        except:
            pass
            
        # 使用合适的参数查找主要频率成分
        if is_beat:
            # 对于拍现象，减小最小频率距离，增加频率分辨率
            dominant_freqs = self.find_dominant_frequencies(
                audio_data, 
                num_peaks=num_components,
                min_amplitude=0.05,
                min_freq_distance=1.0  # 拍现象的最小频率距离设置得更小
            )
        else:
            # 其他音频使用标准参数
            dominant_freqs = self.find_dominant_frequencies(
                audio_data, 
                num_peaks=num_components
            )
        
        # 创建简谐振动组合
        oscillators = []
        
        for freq, amplitude in dominant_freqs:
            # 创建简谐振动
            oscillator = HarmonicMotion(
                type=HarmonicType.SINGLE,
                params=HarmonicParams(
                    amplitude=amplitude,
                    frequency=freq,
                    phase=0.0,  # 相位信息通常在FFT中丢失，这里简化为0
                    damping=0.0
                )
            )
            oscillators.append(oscillator)
            
        # 返回简谐振动的叠加
        return SuperpositionMotion(oscillators)
    
    def identify_musical_notes(self, audio_data: np.ndarray, num_notes: int = 3) -> List[Tuple[str, float, float]]:
        """识别音频中的音符
        
        Args:
            audio_data: 音频数据数组
            num_notes: 要识别的音符数量
            
        Returns:
            List[Tuple[str, float, float]]: [(音符名称, 频率, 振幅), ...]
        """
        # 找出主要频率成分
        dominant_freqs = self.find_dominant_frequencies(audio_data, num_notes)
        
        # 识别音符
        notes = []
        for freq, amplitude in dominant_freqs:
            # 查找最接近的音符
            note_name = "未知"
            min_diff = float('inf')
            
            for note_freq, name in self.freq_to_note.items():
                diff = abs(freq - note_freq)
                if diff < min_diff and diff <= self.note_tolerance:
                    min_diff = diff
                    note_name = name
            
            notes.append((note_name, freq, amplitude))
            
        return notes
    
    def calculate_harmonic_to_fundamental_ratios(self, audio_data: np.ndarray, 
                                              num_harmonics: int = 5) -> List[Tuple[float, float, float]]:
        """计算谐波与基频的比率
        
        Args:
            audio_data: 音频数据数组
            num_harmonics: 要分析的谐波数量
            
        Returns:
            List[Tuple[float, float, float]]: [(谐波序号, 频率, 相对振幅比), ...]
        """
        # 找出主要频率成分
        dominant_freqs = self.find_dominant_frequencies(audio_data, num_harmonics + 1)
        
        if not dominant_freqs:
            return []
            
        # 假设第一个峰值是基频
        fundamental_freq, fundamental_amp = dominant_freqs[0]
        
        # 计算谐波比率
        harmonic_ratios = []
        for i, (freq, amp) in enumerate(dominant_freqs):
            harmonic_number = round(freq / fundamental_freq)
            # 只有谐波序号 >= 1 才有意义
            if harmonic_number >= 1:
                ratio = amp / fundamental_amp
                harmonic_ratios.append((harmonic_number, freq, ratio))
                
        # 按谐波序号排序
        harmonic_ratios.sort(key=lambda x: x[0])
        
        return harmonic_ratios
    
    def generate_harmonic_decomposition_data(self, 
                                           superposition: SuperpositionMotion, 
                                           duration: float = 1.0,
                                           num_points: int = 1000) -> Dict[str, np.ndarray]:
        """生成谐波分解的可视化数据
        
        Args:
            superposition: 包含多个简谐振动的叠加
            duration: 生成数据的时间长度(秒)
            num_points: 数据点数量
            
        Returns:
            Dict[str, np.ndarray]: 包含时间和各分量波形的字典
        """
        # 生成时间数组
        t = np.linspace(0, duration, num_points)
        
        # 计算叠加波形
        composite_wave = np.array([superposition.position(time) for time in t])
        
        # 计算各个分量波形
        component_waves = {}
        for i, osc in enumerate(superposition.oscillators):
            wave = np.array([osc.position(time) for time in t])
            component_waves[f"component_{i}"] = wave
            
        # 整合结果
        result = {
            "time": t,
            "composite": composite_wave
        }
        result.update(component_waves)
        
        return result
    
    def analyze_chord(self, audio_data: np.ndarray) -> str:
        """分析音频中的和弦
        
        Args:
            audio_data: 音频数据数组
            
        Returns:
            str: 识别出的和弦名称
        """
        # 识别音符
        notes = self.identify_musical_notes(audio_data, num_notes=3)
        note_names = [note[0] for note in notes if note[0] != "未知"]
        
        # 简单的和弦映射
        chord_map = {
            frozenset(['C4', 'E4', 'G4']): 'C大三和弦',
            frozenset(['G4', 'B4', 'D4']): 'G大三和弦',
            frozenset(['F4', 'A4', 'C4']): 'F大三和弦',
            frozenset(['A4', 'C4', 'E4']): 'A小三和弦',
            frozenset(['D4', 'F4', 'A4']): 'D小三和弦',
            frozenset(['E4', 'G4', 'B4']): 'E小三和弦'
        }
        
        # 查找匹配的和弦
        note_set = frozenset(note_names)
        for chord_notes, chord_name in chord_map.items():
            if note_set.issubset(chord_notes) and len(note_set) >= 2:
                return chord_name
        
        return "未识别和弦"


# 测试代码
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from audio_engine import AudioEngine
    
    # 创建音频引擎和分析器
    audio_engine = AudioEngine()
    analyzer = AudioAnalyzer()
    
    # 生成测试音频 - C大三和弦
    chord_audio = audio_engine.generate_chord(['C4', 'E4', 'G4'], duration=1.0)
    
    # 分析频率内容
    frequencies, magnitudes = analyzer.analyze_frequency_content(chord_audio)
    
    # 找出主要频率成分
    dominant_freqs = analyzer.find_dominant_frequencies(chord_audio)
    print("主要频率成分:", dominant_freqs)
    
    # 识别音符
    notes = analyzer.identify_musical_notes(chord_audio)
    print("识别的音符:", notes)
    
    # 分解为简谐振动
    harmonic_motion = analyzer.decompose_to_harmonics(chord_audio)
    print(f"分解为 {len(harmonic_motion.oscillators)} 个简谐振动")
    
    # 识别和弦
    chord_name = analyzer.analyze_chord(chord_audio)
    print("识别的和弦:", chord_name)
    
    # 可视化
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies[:1000], magnitudes[:1000])
    plt.title("频谱分析")
    plt.xlabel("频率 (Hz)")
    plt.ylabel("振幅")
    plt.grid(True)
    plt.show() 