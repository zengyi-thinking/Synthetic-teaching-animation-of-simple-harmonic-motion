# -*- coding: utf-8 -*-
"""
音频处理核心逻辑
负责音频文件的读取、预处理和基本操作
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, Optional, Union
import os

class AudioProcessor:
    """音频处理器 - 处理音频文件的读取、预处理和保存"""
    
    def __init__(self, target_sr: int = 22050):
        """
        初始化音频处理器
        
        Args:
            target_sr: 目标采样率，默认22050Hz
        """
        self.target_sr = target_sr
        self.audio_data = None
        self.original_sr = None
        self.duration = 0
        self.channels = 1
        self.file_path = None
        
    def load_audio(self, file_path: str, mono: bool = True) -> Tuple[np.ndarray, int]:
        """
        加载音频文件
        
        Args:
            file_path: 音频文件路径
            mono: 是否转换为单声道
            
        Returns:
            Tuple[音频数据, 采样率]
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"音频文件不存在: {file_path}")
            
            # 使用librosa加载音频
            audio_data, sr = librosa.load(
                file_path, 
                sr=self.target_sr,  # 重采样到目标采样率
                mono=mono,          # 转换为单声道
                dtype=np.float32    # 使用float32格式
            )
            
            # 存储音频信息
            self.audio_data = audio_data
            self.original_sr = sr
            self.duration = len(audio_data) / sr
            self.channels = 1 if mono else 2
            self.file_path = file_path
            
            print(f"✅ 音频加载成功:")
            print(f"   文件: {os.path.basename(file_path)}")
            print(f"   采样率: {sr} Hz")
            print(f"   时长: {self.duration:.2f} 秒")
            print(f"   声道: {'单声道' if mono else '立体声'}")
            print(f"   数据点数: {len(audio_data)}")
            
            return audio_data, sr
            
        except Exception as e:
            print(f"❌ 音频加载失败: {e}")
            raise
    
    def normalize_audio(self, audio_data: np.ndarray, method: str = 'peak') -> np.ndarray:
        """
        音频标准化处理
        
        Args:
            audio_data: 音频数据
            method: 标准化方法 ('peak', 'rms')
            
        Returns:
            标准化后的音频数据
        """
        if method == 'peak':
            # 峰值标准化
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                return audio_data / max_val
            return audio_data
            
        elif method == 'rms':
            # RMS标准化
            rms = np.sqrt(np.mean(audio_data ** 2))
            if rms > 0:
                return audio_data / rms * 0.1  # 调整到合适的RMS水平
            return audio_data
        
        else:
            raise ValueError(f"不支持的标准化方法: {method}")
    
    def trim_silence(self, audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        去除音频开头和结尾的静音部分
        
        Args:
            audio_data: 音频数据
            threshold: 静音阈值
            
        Returns:
            去除静音后的音频数据
        """
        # 找到非静音部分的开始和结束
        non_silent = np.abs(audio_data) > threshold
        if np.any(non_silent):
            start_idx = np.argmax(non_silent)
            end_idx = len(audio_data) - np.argmax(non_silent[::-1])
            return audio_data[start_idx:end_idx]
        return audio_data
    
    def apply_window(self, audio_data: np.ndarray, window_type: str = 'hann') -> np.ndarray:
        """
        应用窗函数
        
        Args:
            audio_data: 音频数据
            window_type: 窗函数类型
            
        Returns:
            应用窗函数后的音频数据
        """
        if window_type == 'hann':
            window = np.hanning(len(audio_data))
        elif window_type == 'hamming':
            window = np.hamming(len(audio_data))
        elif window_type == 'blackman':
            window = np.blackman(len(audio_data))
        else:
            return audio_data  # 不应用窗函数
        
        return audio_data * window
    
    def save_audio(self, audio_data: np.ndarray, output_path: str, sr: Optional[int] = None) -> bool:
        """
        保存音频文件
        
        Args:
            audio_data: 音频数据
            output_path: 输出文件路径
            sr: 采样率，默认使用当前采样率
            
        Returns:
            是否保存成功
        """
        try:
            if sr is None:
                sr = self.target_sr
            
            # 确保音频数据在有效范围内
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            # 保存音频文件
            sf.write(output_path, audio_data, sr)
            
            print(f"✅ 音频保存成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 音频保存失败: {e}")
            return False
    
    def get_audio_info(self) -> dict:
        """
        获取当前音频的详细信息
        
        Returns:
            音频信息字典
        """
        if self.audio_data is None:
            return {}
        
        return {
            'file_path': self.file_path,
            'duration': self.duration,
            'sample_rate': self.original_sr,
            'channels': self.channels,
            'samples': len(self.audio_data),
            'max_amplitude': np.max(np.abs(self.audio_data)),
            'rms': np.sqrt(np.mean(self.audio_data ** 2)),
            'dynamic_range': 20 * np.log10(np.max(np.abs(self.audio_data)) / (np.sqrt(np.mean(self.audio_data ** 2)) + 1e-10))
        }
    
    def create_test_tone(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        创建测试音调
        
        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0-1)
            
        Returns:
            生成的音频数据
        """
        t = np.linspace(0, duration, int(self.target_sr * duration), False)
        audio_data = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # 应用淡入淡出效果
        fade_samples = int(0.01 * self.target_sr)  # 10ms淡入淡出
        if len(audio_data) > 2 * fade_samples:
            # 淡入
            audio_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
            # 淡出
            audio_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return audio_data
    
    def create_chord(self, frequencies: list, duration: float, amplitudes: Optional[list] = None) -> np.ndarray:
        """
        创建和弦（多个频率的叠加）
        
        Args:
            frequencies: 频率列表
            duration: 持续时间
            amplitudes: 各频率的振幅列表
            
        Returns:
            合成的音频数据
        """
        if amplitudes is None:
            amplitudes = [0.3] * len(frequencies)
        
        if len(amplitudes) != len(frequencies):
            raise ValueError("频率和振幅列表长度必须相同")
        
        # 生成时间轴
        t = np.linspace(0, duration, int(self.target_sr * duration), False)
        
        # 叠加所有频率分量
        audio_data = np.zeros_like(t)
        for freq, amp in zip(frequencies, amplitudes):
            audio_data += amp * np.sin(2 * np.pi * freq * t)
        
        # 标准化
        audio_data = self.normalize_audio(audio_data, method='peak')
        
        return audio_data
