# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 核心振动引擎
处理简谐振动与音频的映射关系
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Union


class HarmonicType(Enum):
    """简谐振动类型"""
    SINGLE = auto()         # 单一简谐振动
    SUPERPOSITION = auto()  # 同向叠加
    BEAT = auto()           # 拍现象
    LISSAJOUS = auto()      # 李萨如图形


@dataclass
class HarmonicParams:
    """简谐振动参数"""
    amplitude: float = 1.0    # 振幅
    frequency: float = 1.0    # 频率(Hz)
    phase: float = 0.0        # 初始相位(弧度)
    damping: float = 0.0      # 阻尼系数
    

class HarmonicMotion:
    """简谐振动基类"""
    
    def __init__(self, type: HarmonicType, params: Optional[HarmonicParams] = None):
        """初始化简谐振动
        
        Args:
            type: 振动类型
            params: 振动参数，如未提供则使用默认值
        """
        self.type = type
        self.params = params or HarmonicParams()
        
    def position(self, t: float) -> float:
        """计算给定时刻的位置
        
        Args:
            t: 时间(秒)
            
        Returns:
            位置值
        """
        amplitude = self.params.amplitude
        frequency = self.params.frequency
        phase = self.params.phase
        damping = self.params.damping
        
        # 计算阻尼衰减
        if damping > 0:
            amplitude *= np.exp(-damping * t)
            
        return amplitude * np.sin(2 * np.pi * frequency * t + phase)
    
    def velocity(self, t: float) -> float:
        """计算给定时刻的速度
        
        Args:
            t: 时间(秒)
            
        Returns:
            速度值
        """
        amplitude = self.params.amplitude
        frequency = self.params.frequency
        phase = self.params.phase
        damping = self.params.damping
        
        # 计算阻尼衰减
        if damping > 0:
            damping_factor = np.exp(-damping * t)
            # 速度由位置的导数和阻尼项组成
            return (2 * np.pi * frequency * amplitude * np.cos(2 * np.pi * frequency * t + phase) - 
                    damping * amplitude * np.sin(2 * np.pi * frequency * t + phase)) * damping_factor
        else:
            return 2 * np.pi * frequency * amplitude * np.cos(2 * np.pi * frequency * t + phase)
    
    def acceleration(self, t: float) -> float:
        """计算给定时刻的加速度
        
        Args:
            t: 时间(秒)
            
        Returns:
            加速度值
        """
        # 加速度是位置的二阶导数
        amplitude = self.params.amplitude
        frequency = self.params.frequency
        phase = self.params.phase
        damping = self.params.damping
        
        if damping > 0:
            # 复杂情况，加速度包含阻尼项
            omega = 2 * np.pi * frequency
            damping_factor = np.exp(-damping * t)
            sin_term = np.sin(omega * t + phase)
            cos_term = np.cos(omega * t + phase)
            
            return damping_factor * (
                -omega**2 * amplitude * sin_term
                - 2 * damping * omega * amplitude * cos_term
                + damping**2 * amplitude * sin_term
            )
        else:
            # 简单情况，无阻尼
            return -(2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t + phase)
    
    def energy(self) -> float:
        """计算振动的总能量
        
        Returns:
            能量值
        """
        # 简谐振动的能量与振幅和频率的平方成正比
        return 0.5 * (2 * np.pi * self.params.frequency)**2 * self.params.amplitude**2
    
    def to_dict(self) -> Dict:
        """转换为字典表示
        
        Returns:
            字典形式的参数
        """
        return {
            'type': self.type.name,
            'amplitude': self.params.amplitude,
            'frequency': self.params.frequency,
            'phase': self.params.phase,
            'damping': self.params.damping
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HarmonicMotion':
        """从字典创建实例
        
        Args:
            data: 字典表示的参数
            
        Returns:
            新创建的HarmonicMotion实例
        """
        return cls(
            type=HarmonicType[data['type']],
            params=HarmonicParams(
                amplitude=data.get('amplitude', 1.0),
                frequency=data.get('frequency', 1.0),
                phase=data.get('phase', 0.0),
                damping=data.get('damping', 0.0)
            )
        )


class SuperpositionMotion:
    """简谐振动的叠加"""
    
    def __init__(self, oscillators: List[HarmonicMotion] = None):
        """初始化叠加振动
        
        Args:
            oscillators: 简谐振动列表
        """
        self.oscillators = oscillators or []
    
    def add_oscillator(self, oscillator: HarmonicMotion):
        """添加一个简谐振动
        
        Args:
            oscillator: 要添加的简谐振动
        """
        self.oscillators.append(oscillator)
    
    def position(self, t: float) -> float:
        """计算叠加振动在给定时刻的位置
        
        Args:
            t: 时间(秒)
            
        Returns:
            位置值
        """
        return sum(osc.position(t) for osc in self.oscillators)
    
    def velocity(self, t: float) -> float:
        """计算叠加振动在给定时刻的速度
        
        Args:
            t: 时间(秒)
            
        Returns:
            速度值
        """
        return sum(osc.velocity(t) for osc in self.oscillators)
    
    def acceleration(self, t: float) -> float:
        """计算叠加振动在给定时刻的加速度
        
        Args:
            t: 时间(秒)
            
        Returns:
            加速度值
        """
        return sum(osc.acceleration(t) for osc in self.oscillators)
    
    def energy(self) -> float:
        """计算叠加振动的总能量
        
        Returns:
            能量值
        """
        # 简单叠加每个振动的能量
        # 注意：这只是近似，实际上需要考虑振动之间的相互作用
        return sum(osc.energy() for osc in self.oscillators)


class HarmonicToAudioMapper:
    """简谐振动到音频的映射器"""
    
    def __init__(self, sample_rate: int = 44100):
        """初始化映射器
        
        Args:
            sample_rate: 音频采样率
        """
        self.sample_rate = sample_rate
        
        # 定义音符频率对应的简谐振动频率映射
        self.note_to_freq = {
            'C4': 261.63,  # 中央C
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,  # 标准音高A
            'B4': 493.88,
            'C5': 523.25
        }
        
    def harmonic_to_audio(self, harmonic: Union[HarmonicMotion, SuperpositionMotion], 
                         duration: float) -> np.ndarray:
        """将简谐振动转换为音频
        
        Args:
            harmonic: 简谐振动或叠加振动
            duration: 音频时长(秒)
            
        Returns:
            音频数据数组
        """
        # 创建时间数组
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # 计算音频样本
        if isinstance(harmonic, SuperpositionMotion):
            audio = np.array([harmonic.position(time) for time in t])
        else:
            audio = np.array([harmonic.position(time) for time in t])
        
        # 归一化到[-1, 1]范围
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
            
        return audio
    
    def create_beat_motion(self, freq1: float, freq2: float, amplitude: float = 1.0) -> SuperpositionMotion:
        """创建拍现象振动
        
        Args:
            freq1: 第一个频率(Hz)
            freq2: 第二个频率(Hz)
            amplitude: 振幅
            
        Returns:
            叠加振动对象
        """
        osc1 = HarmonicMotion(
            type=HarmonicType.SINGLE,
            params=HarmonicParams(amplitude=amplitude, frequency=freq1)
        )
        
        osc2 = HarmonicMotion(
            type=HarmonicType.SINGLE,
            params=HarmonicParams(amplitude=amplitude, frequency=freq2)
        )
        
        beat = SuperpositionMotion([osc1, osc2])
        return beat
    
    def create_chord_motion(self, notes: List[str], amplitudes: List[float] = None) -> SuperpositionMotion:
        """创建和弦振动
        
        Args:
            notes: 音符名称列表
            amplitudes: 各音符的振幅，如果未提供则均匀分配
            
        Returns:
            叠加振动对象
        """
        if amplitudes is None:
            # 默认每个音符振幅相等
            amplitudes = [1.0 / len(notes)] * len(notes)
        else:
            # 确保振幅数组长度与音符数量匹配
            if len(amplitudes) < len(notes):
                amplitudes = amplitudes + [amplitudes[-1]] * (len(notes) - len(amplitudes))
        
        oscillators = []
        for i, note in enumerate(notes):
            freq = self.note_to_freq.get(note, 440.0)  # 默认A4
            osc = HarmonicMotion(
                type=HarmonicType.SINGLE,
                params=HarmonicParams(amplitude=amplitudes[i], frequency=freq)
            )
            oscillators.append(osc)
            
        return SuperpositionMotion(oscillators)
    
    def create_harmonic_series_motion(self, fundamental_freq: float, 
                                     num_harmonics: int = 5,
                                     amplitude_ratio: float = 0.5) -> SuperpositionMotion:
        """创建谐波级数振动
        
        Args:
            fundamental_freq: 基频(Hz)
            num_harmonics: 谐波数量
            amplitude_ratio: 相邻谐波的振幅比例
            
        Returns:
            叠加振动对象
        """
        oscillators = []
        
        # 添加基频
        fundamental = HarmonicMotion(
            type=HarmonicType.SINGLE,
            params=HarmonicParams(amplitude=1.0, frequency=fundamental_freq)
        )
        oscillators.append(fundamental)
        
        # 添加谐波
        current_amplitude = 1.0
        for i in range(1, num_harmonics):
            current_amplitude *= amplitude_ratio
            harmonic = HarmonicMotion(
                type=HarmonicType.SINGLE,
                params=HarmonicParams(
                    amplitude=current_amplitude,
                    frequency=fundamental_freq * (i + 1)
                )
            )
            oscillators.append(harmonic)
            
        return SuperpositionMotion(oscillators)


# 测试代码
if __name__ == "__main__":
    # 创建一个简单的简谐振动
    simple_osc = HarmonicMotion(
        type=HarmonicType.SINGLE,
        params=HarmonicParams(amplitude=1.0, frequency=2.0, phase=0.0)
    )
    
    # 测试计算
    t_values = np.linspace(0, 1, 10)
    positions = [simple_osc.position(t) for t in t_values]
    print("时间值:", t_values)
    print("位置值:", positions)
    
    # 创建映射器并生成音频
    mapper = HarmonicToAudioMapper()
    
    # 测试拍现象
    beat_motion = mapper.create_beat_motion(440, 444)
    print("拍现象振动的能量:", beat_motion.energy())
    
    # 测试和弦
    c_major = mapper.create_chord_motion(['C4', 'E4', 'G4'])
    print("C大和弦的振动包含", len(c_major.oscillators), "个简谐振动")
    
    print("测试完成") 