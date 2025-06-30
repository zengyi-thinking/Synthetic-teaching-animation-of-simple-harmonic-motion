# -*- coding: utf-8 -*-
"""
频率分析器
负责音频信号的频域分解、FFT处理和频率分量提取
"""

import numpy as np
import librosa
from scipy import signal
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt

class FrequencyComponent:
    """频率分量类 - 表示单个简谐波分量"""
    
    def __init__(self, frequency: float, amplitude: float, phase: float, enabled: bool = True):
        self.frequency = frequency  # 频率 (Hz)
        self.amplitude = amplitude  # 振幅
        self.phase = phase         # 相位 (弧度)
        self.enabled = enabled     # 是否启用
        self.original_amplitude = amplitude  # 原始振幅
    
    def __repr__(self):
        return f"FreqComp(f={self.frequency:.1f}Hz, A={self.amplitude:.3f}, φ={self.phase:.2f})"

class FrequencyAnalyzer:
    """频率分析器 - 分析音频信号的频率成分"""
    
    def __init__(self, sample_rate: int = 22050):
        """
        初始化频率分析器
        
        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
        self.frequency_components = []
        self.fft_data = None
        self.frequencies = None
        self.magnitude_spectrum = None
        self.phase_spectrum = None
        
    def analyze_audio(self, audio_data: np.ndarray, n_components: int = 5, 
                     min_frequency: float = 80.0, max_frequency: float = 2000.0) -> List[FrequencyComponent]:
        """
        分析音频信号，提取主要频率分量
        
        Args:
            audio_data: 音频数据
            n_components: 提取的主要频率分量数量
            min_frequency: 最小频率 (Hz)
            max_frequency: 最大频率 (Hz)
            
        Returns:
            频率分量列表
        """
        # 执行FFT
        self.fft_data = np.fft.fft(audio_data)
        self.frequencies = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        
        # 只取正频率部分
        positive_freq_idx = self.frequencies > 0
        positive_frequencies = self.frequencies[positive_freq_idx]
        positive_fft = self.fft_data[positive_freq_idx]
        
        # 计算幅度谱和相位谱
        self.magnitude_spectrum = np.abs(positive_fft)
        self.phase_spectrum = np.angle(positive_fft)
        
        # 在指定频率范围内寻找峰值
        freq_mask = (positive_frequencies >= min_frequency) & (positive_frequencies <= max_frequency)
        masked_frequencies = positive_frequencies[freq_mask]
        masked_magnitudes = self.magnitude_spectrum[freq_mask]
        masked_phases = self.phase_spectrum[freq_mask]
        
        # 寻找峰值
        peaks, properties = signal.find_peaks(
            masked_magnitudes,
            height=np.max(masked_magnitudes) * 0.1,  # 至少是最大值的10%
            distance=int(len(masked_magnitudes) * 0.01)  # 峰值间最小距离
        )
        
        # 按幅度排序，取前n_components个
        peak_magnitudes = masked_magnitudes[peaks]
        peak_frequencies = masked_frequencies[peaks]
        peak_phases = masked_phases[peaks]
        
        # 排序并选择最强的分量
        sorted_indices = np.argsort(peak_magnitudes)[::-1]
        top_indices = sorted_indices[:min(n_components, len(sorted_indices))]
        
        # 创建频率分量对象
        self.frequency_components = []
        for idx in top_indices:
            peak_idx = peaks[idx]
            frequency = peak_frequencies[idx]
            # 修正振幅计算 - 使用更合理的标准化方法
            raw_amplitude = peak_magnitudes[idx]
            # 标准化到合理的范围，保持相对比例
            amplitude = (raw_amplitude * 2.0) / len(audio_data)  # 乘以2是因为我们只取了正频率部分
            # 确保振幅在可见范围内
            amplitude = max(amplitude, 0.001)  # 最小振幅
            phase = peak_phases[idx]

            print(f"分量: 频率={frequency:.1f}Hz, 原始幅度={raw_amplitude:.2e}, 标准化幅度={amplitude:.6f}")

            component = FrequencyComponent(frequency, amplitude, phase)
            self.frequency_components.append(component)
        
        # 按频率排序
        self.frequency_components.sort(key=lambda x: x.frequency)
        
        print(f"✅ 频率分析完成，提取了 {len(self.frequency_components)} 个主要分量:")
        for i, comp in enumerate(self.frequency_components):
            print(f"   {i+1}. {comp.frequency:.1f} Hz, 振幅: {comp.amplitude:.4f}, 相位: {comp.phase:.2f}")
        
        return self.frequency_components
    
    def reconstruct_audio(self, duration: Optional[float] = None) -> np.ndarray:
        """
        根据当前的频率分量重构音频信号

        Args:
            duration: 重构音频的时长，None表示使用原始时长

        Returns:
            重构的音频数据
        """
        if not self.frequency_components:
            raise ValueError("没有可用的频率分量进行重构")

        # 确定重构时长
        if duration is None:
            if self.fft_data is not None:
                duration = len(self.fft_data) / self.sample_rate
            else:
                duration = 3.0  # 默认3秒

        # 确保duration是数字类型
        if isinstance(duration, (list, tuple, np.ndarray)):
            duration = float(duration[0]) if len(duration) > 0 else 3.0
        else:
            duration = float(duration)

        # 确保sample_rate是数字类型
        sample_rate = self.sample_rate
        if isinstance(sample_rate, (list, tuple, np.ndarray)):
            sample_rate = float(sample_rate[0]) if len(sample_rate) > 0 else 22050
        else:
            sample_rate = float(sample_rate)

        print(f"重构音频: 时长={duration:.2f}秒, 采样率={sample_rate:.0f}Hz")

        # 生成时间轴
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)

        print(f"时间轴: {len(t)} 个采样点")

        # 叠加所有启用的频率分量
        reconstructed = np.zeros_like(t)
        enabled_count = 0

        for component in self.frequency_components:
            if component.enabled:
                wave = component.amplitude * np.sin(
                    2 * np.pi * component.frequency * t + component.phase
                )
                reconstructed += wave
                enabled_count += 1
                print(f"  添加分量: {component.frequency:.1f}Hz, 振幅={component.amplitude:.4f}")

        print(f"重构完成: 使用了 {enabled_count} 个分量")
        return reconstructed
    
    def get_frequency_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取频率谱
        
        Returns:
            Tuple[频率数组, 幅度谱]
        """
        if self.frequencies is None or self.magnitude_spectrum is None:
            raise ValueError("请先执行频率分析")
        
        # 只返回正频率部分
        positive_idx = self.frequencies > 0
        return self.frequencies[positive_idx], self.magnitude_spectrum
    
    def update_component_amplitude(self, component_index: int, amplitude_scale: float):
        """
        更新指定频率分量的振幅
        
        Args:
            component_index: 分量索引
            amplitude_scale: 振幅缩放因子 (0-2.0)
        """
        if 0 <= component_index < len(self.frequency_components):
            component = self.frequency_components[component_index]
            component.amplitude = component.original_amplitude * amplitude_scale
            print(f"更新分量 {component_index}: {component.frequency:.1f}Hz, 新振幅: {component.amplitude:.4f}")
    
    def toggle_component(self, component_index: int):
        """
        切换指定频率分量的启用状态
        
        Args:
            component_index: 分量索引
        """
        if 0 <= component_index < len(self.frequency_components):
            component = self.frequency_components[component_index]
            component.enabled = not component.enabled
            status = "启用" if component.enabled else "禁用"
            print(f"{status}分量 {component_index}: {component.frequency:.1f}Hz")
    
    def get_component_info(self) -> List[Dict]:
        """
        获取所有频率分量的信息
        
        Returns:
            分量信息列表
        """
        info_list = []
        for i, component in enumerate(self.frequency_components):
            info = {
                'index': i,
                'frequency': component.frequency,
                'amplitude': component.amplitude,
                'original_amplitude': component.original_amplitude,
                'phase': component.phase,
                'enabled': component.enabled,
                'amplitude_scale': component.amplitude / component.original_amplitude if component.original_amplitude > 0 else 0
            }
            info_list.append(info)
        return info_list
    
    def create_spectrogram(self, audio_data: np.ndarray, window_size: int = 2048, 
                          hop_length: int = 512) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        创建频谱图
        
        Args:
            audio_data: 音频数据
            window_size: 窗口大小
            hop_length: 跳跃长度
            
        Returns:
            Tuple[频谱图, 频率轴, 时间轴]
        """
        # 使用librosa计算短时傅里叶变换
        stft = librosa.stft(audio_data, n_fft=window_size, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # 转换为dB
        magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
        
        # 生成频率和时间轴
        frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=window_size)
        times = librosa.frames_to_time(np.arange(magnitude.shape[1]), 
                                      sr=self.sample_rate, hop_length=hop_length)
        
        return magnitude_db, frequencies, times
    
    def analyze_harmonic_content(self, fundamental_freq: float, n_harmonics: int = 5) -> List[Dict]:
        """
        分析谐波内容
        
        Args:
            fundamental_freq: 基频
            n_harmonics: 分析的谐波数量
            
        Returns:
            谐波信息列表
        """
        if self.frequencies is None or self.magnitude_spectrum is None:
            raise ValueError("请先执行频率分析")
        
        harmonics = []
        for n in range(1, n_harmonics + 1):
            harmonic_freq = fundamental_freq * n
            
            # 在频谱中寻找最接近的频率
            freq_diff = np.abs(self.frequencies[self.frequencies > 0] - harmonic_freq)
            closest_idx = np.argmin(freq_diff)
            
            actual_freq = self.frequencies[self.frequencies > 0][closest_idx]
            amplitude = self.magnitude_spectrum[closest_idx]
            
            harmonic_info = {
                'harmonic_number': n,
                'expected_frequency': harmonic_freq,
                'actual_frequency': actual_freq,
                'amplitude': amplitude,
                'amplitude_db': 20 * np.log10(amplitude + 1e-10)
            }
            harmonics.append(harmonic_info)
        
        return harmonics
