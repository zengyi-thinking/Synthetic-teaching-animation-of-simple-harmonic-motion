# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 音频引擎模块
负责生成和处理音频
"""

import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import librosa
import time
import threading
import queue


class AudioEngine:
    """音频引擎类，负责生成和播放简谐振动对应的音频"""
    
    def __init__(self, sample_rate=44100, buffer_size=1024):
        """初始化音频引擎
        
        Args:
            sample_rate: 采样率，默认44.1kHz (CD音质)
            buffer_size: 音频缓冲区大小
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_playing = False
        self.stream = None
        self.current_audio = None
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        self.loop_playback = False  # 循环播放标志
        
        # 设置sounddevice参数
        sd.default.samplerate = sample_rate
        sd.default.channels = 1  # 单声道
        
        # 音乐音高与频率的映射（标准A4=440Hz）
        self.note_freqs = {
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 
            'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 
            'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            'C5': 523.25
        }
        
        # 预缓存常用声音
        self._cache = {}

    def generate_sine_wave(self, frequency, amplitude=0.5, duration=1.0, phase=0.0):
        """生成正弦波
        
        Args:
            frequency: 频率(Hz)
            amplitude: 振幅，范围[0,1]
            duration: 持续时间(秒)
            phase: 初始相位(弧度)
            
        Returns:
            numpy.ndarray: 音频数据
        """
        # 检查缓存中是否已有相同参数的波形
        cache_key = f"sine_{frequency}_{amplitude}_{duration}_{phase}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
            
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        # 应用淡入淡出以避免爆音
        fade_samples = int(0.01 * self.sample_rate)  # 10ms淡入淡出
        if len(audio) > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[:fade_samples] *= fade_in
            audio[-fade_samples:] *= fade_out
        
        # 缓存结果
        if len(self._cache) < 100:  # 限制缓存大小
            self._cache[cache_key] = audio.copy()
            
        return audio
    
    def generate_harmonic_series(self, fundamental_freq, num_harmonics=5, amplitudes=None, duration=1.0):
        """生成谐波级数 (基频加上多个谐波)
        
        Args:
            fundamental_freq: 基频(Hz)
            num_harmonics: 谐波数量
            amplitudes: 各谐波的相对振幅，如果为None则自动设为1/n
            duration: 持续时间(秒)
            
        Returns:
            numpy.ndarray: 合成的音频数据
        """
        if amplitudes is None:
            # 默认振幅按1/n衰减
            amplitudes = [1.0 / (i + 1) for i in range(num_harmonics)]
        elif len(amplitudes) < num_harmonics:
            # 补全振幅数组
            amplitudes = amplitudes + [0.0] * (num_harmonics - len(amplitudes))
            
        # 生成基频
        audio = self.generate_sine_wave(fundamental_freq, amplitudes[0], duration)
        
        # 添加谐波
        for i in range(1, num_harmonics):
            harmonic = self.generate_sine_wave(fundamental_freq * (i + 1), amplitudes[i], duration)
            audio += harmonic
            
        # 归一化，防止削波
        if np.max(np.abs(audio)) > 1.0:
            audio = audio / np.max(np.abs(audio))
            
        return audio
    
    def generate_chord(self, notes, duration=1.0, equal_amplitude=True):
        """生成和弦 (同时播放的多个音符)
        
        Args:
            notes: 音符列表，可以是音符名称或频率
            duration: 持续时间(秒)
            equal_amplitude: 是否所有音符使用相同振幅
            
        Returns:
            numpy.ndarray: 合成的和弦音频
        """
        # 检查缓存
        cache_key = f"chord_{'_'.join(str(n) for n in notes)}_{duration}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
            
        chord_audio = np.zeros(int(self.sample_rate * duration))
        
        # 确定每个音符的振幅
        if equal_amplitude:
            amplitude = 1.0 / len(notes)
        else:
            amplitude = 0.5
        
        # 音符到频率的扩展映射（增加更多音符）
        extended_note_freqs = {
            # 第三个八度
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56,
            'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00,
            'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
            
            # 第四个八度（中央C所在的八度）
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
            'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
            'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            
            # 第五个八度
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
            'E5': 659.26, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99,
            'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
            
            # 第六个八度
            'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51,
            'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98,
            'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53
        }
        
        # 合成每个音符
        for note in notes:
            # 如果输入是音符名称而非频率
            if isinstance(note, str):
                if note in extended_note_freqs:
                    frequency = extended_note_freqs[note]
                elif note in self.note_freqs:
                    frequency = self.note_freqs[note]
                else:
                    try:
                        # 尝试直接转换为频率
                        frequency = float(note)
                    except ValueError:
                        print(f"警告: 未知音符 '{note}'，将被忽略")
                        continue
            else:
                try:
                    # 如果是数值类型，直接作为频率使用
                    frequency = float(note)
                except (ValueError, TypeError):
                    print(f"警告: 无法转换为频率的值 '{note}'，将被忽略")
                    continue
                
            note_audio = self.generate_sine_wave(frequency, amplitude, duration)
            chord_audio += note_audio
            
        # 归一化
        if np.max(np.abs(chord_audio)) > 1.0:
            chord_audio = chord_audio / np.max(np.abs(chord_audio))
            
        # 应用淡入淡出以避免爆音
        fade_samples = int(0.01 * self.sample_rate)  # 10ms淡入淡出
        if len(chord_audio) > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            chord_audio[:fade_samples] *= fade_in
            chord_audio[-fade_samples:] *= fade_out
        
        # 缓存结果
        if len(self._cache) < 100:  # 限制缓存大小
            self._cache[cache_key] = chord_audio.copy()
            
        return chord_audio
    
    def generate_beat(self, freq1, freq2, amplitude=0.5, duration=3.0):
        """生成拍现象音频 (两个频率接近的正弦波叠加)
        
        Args:
            freq1: 第一个频率(Hz)
            freq2: 第二个频率(Hz)
            amplitude: 振幅
            duration: 持续时间(秒)
            
        Returns:
            numpy.ndarray: 拍频音频
        """
        # 检查缓存
        cache_key = f"beat_{freq1}_{freq2}_{amplitude}_{duration}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
            
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave1 = amplitude * np.sin(2 * np.pi * freq1 * t)
        wave2 = amplitude * np.sin(2 * np.pi * freq2 * t)
        beat_wave = wave1 + wave2
        
        # 归一化
        if np.max(np.abs(beat_wave)) > 1.0:
            beat_wave = beat_wave / np.max(np.abs(beat_wave))
            
        # 应用淡入淡出以避免爆音
        fade_samples = int(0.01 * self.sample_rate)  # 10ms淡入淡出
        if len(beat_wave) > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            beat_wave[:fade_samples] *= fade_in
            beat_wave[-fade_samples:] *= fade_out
        
        # 缓存结果
        if len(self._cache) < 100:  # 限制缓存大小
            self._cache[cache_key] = beat_wave.copy()
            
        return beat_wave
    
    def _playback_worker(self):
        """音频播放工作线程"""
        try:
            with sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                channels=1,
                callback=self._audio_callback
            ) as stream:
                self.stream = stream
                
                while self.is_playing:
                    # 线程保持活动状态，通过回调函数处理音频输出
                    time.sleep(0.1)
                    
                self.stream = None
                
        except Exception as e:
            print(f"音频播放错误: {e}")
            self.is_playing = False
            self.stream = None
    
    def _audio_callback(self, outdata, frames, time, status):
        """音频回调函数，提供音频数据给声卡
        
        Args:
            outdata: 输出缓冲区
            frames: 要填充的帧数
            time: 时间戳
            status: 状态标志
        """
        if status:
            print(f"回调状态: {status}")
        
        if self.current_audio is None:
            # 没有音频数据，输出静音
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)
            return
        
        # 尝试从循环队列获取音频数据
        try:
            if not hasattr(self, '_playback_position'):
                self._playback_position = 0
                
            # 计算从当前播放位置开始的可用采样数量
            remaining = len(self.current_audio) - self._playback_position
            
            if remaining >= frames:
                # 有足够的数据可以播放
                outdata[:, 0] = self.current_audio[self._playback_position:self._playback_position+frames]
                self._playback_position += frames
                
            else:
                # 当前音频数据不足以填满输出缓冲区
                if remaining > 0:
                    # 先复制剩余的音频数据
                    outdata[:remaining, 0] = self.current_audio[self._playback_position:]
                    
                # 根据是否循环播放决定后续操作
                if self.loop_playback:
                    # 循环播放: 从头开始继续填充
                    self._playback_position = 0
                    still_needed = frames - remaining
                    
                    # 可能需要多次循环才能填满缓冲区
                    while still_needed > 0 and self.loop_playback:
                        if still_needed <= len(self.current_audio):
                            # 一次循环足够填充剩余空间
                            outdata[remaining:, 0] = self.current_audio[:still_needed]
                            self._playback_position = still_needed
                            still_needed = 0
                        else:
                            # 需要多次循环
                            outdata[remaining:remaining+len(self.current_audio), 0] = self.current_audio
                            still_needed -= len(self.current_audio)
                            remaining += len(self.current_audio)
                else:
                    # 非循环播放: 用静音填充剩余部分并结束播放
                    outdata[remaining:, 0] = 0
                    # 播放结束，重置状态
                    self.is_playing = False
                    self._playback_position = 0
                    
        except Exception as e:
            print(f"音频回调错误: {e}")
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)
            self.is_playing = False
    
    def play_audio(self, audio_data, blocking=False, loop=False):
        """播放音频数据
        
        Args:
            audio_data: 要播放的音频数据，numpy.ndarray
            blocking: 是否阻塞线程等待播放完成
            loop: 是否循环播放
        """
        if audio_data is None or len(audio_data) == 0:
            print("警告: 尝试播放空音频数据")
            return
            
        # 归一化到[-1, 1]区间，避免失真
        if np.max(np.abs(audio_data)) > 1.0:
            audio_data = audio_data / np.max(np.abs(audio_data))
            
        # 如果已经在播放，先停止
        if self.is_playing:
            self.stop_audio()
            time.sleep(0.1)  # 等待清理完成
            
        # 设置循环播放状态
        self.loop_playback = loop
            
        # 设置当前音频
        self.current_audio = audio_data
        self._playback_position = 0  # 重置播放位置
            
        # 启动播放线程
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
        if blocking:
            # 阻塞模式：等待播放完成
            try:
                # 计算大致的播放时间
                play_duration = len(audio_data) / self.sample_rate
                # 增加一点余量以确保完全播放
                time.sleep(play_duration + 0.1)
            except KeyboardInterrupt:
                self.stop_audio()
                
    def set_loop(self, loop_state):
        """设置循环播放状态
        
        Args:
            loop_state: 是否循环播放
        """
        self.loop_playback = loop_state
                
    def stop_audio(self):
        """停止音频播放"""
        self.is_playing = False
        self.loop_playback = False
        if self.playback_thread and self.playback_thread.is_alive():
            # 等待播放线程结束
            time.sleep(0.1)
        self.current_audio = None
        self._playback_position = 0
    
    def save_audio(self, audio_data, filename):
        """保存音频到WAV文件
        
        Args:
            audio_data: 音频数组
            filename: 保存的文件名
        """
        # 确保振幅在[-1, 1]范围内
        normalized_audio = np.copy(audio_data)
        if np.max(np.abs(normalized_audio)) > 1.0:
            normalized_audio = normalized_audio / np.max(np.abs(normalized_audio))
            
        # 转换为16位整数
        scaled = np.int16(normalized_audio * 32767)
        wavfile.write(filename, self.sample_rate, scaled)
        
    def analyze_frequency_content(self, audio_data):
        """分析音频的频率内容，返回频率和对应的振幅
        
        Args:
            audio_data: 音频数组
            
        Returns:
            tuple: (频率数组, 振幅数组)
        """
        # 执行FFT
        n = len(audio_data)
        fft_result = np.fft.rfft(audio_data)
        magnitudes = np.abs(fft_result) * 2 / n
        frequencies = np.fft.rfftfreq(n, 1/self.sample_rate)
        
        return frequencies, magnitudes
    
    def cleanup(self):
        """清理资源"""
        self.stop_audio()
        
        # 发送退出信号给播放线程
        if self.playback_thread and self.playback_thread.is_alive():
            self.audio_queue.put(None)
            self.playback_thread.join(timeout=1.0)


# 测试代码
if __name__ == "__main__":
    audio_engine = AudioEngine()
    
    try:
        # 测试生成和播放简单的正弦波
        print("生成并播放440Hz的A4音...")
        sine_wave = audio_engine.generate_sine_wave(440, duration=1.0)
        audio_engine.play_audio(sine_wave, blocking=True)
        
        # 测试生成和播放C大和弦 (C-E-G)
        print("生成并播放C大和弦...")
        c_major = audio_engine.generate_chord(['C4', 'E4', 'G4'], duration=2.0)
        audio_engine.play_audio(c_major, blocking=True)
        
        # 测试谐波级数
        print("生成并播放带有谐波的C4音...")
        harmonic_c4 = audio_engine.generate_harmonic_series(261.63, num_harmonics=5, duration=2.0)
        audio_engine.play_audio(harmonic_c4, blocking=True)
        
        # 测试拍现象
        print("生成并播放拍现象 (440Hz 和 444Hz)...")
        beat_wave = audio_engine.generate_beat(440, 444, duration=3.0)
        audio_engine.play_audio(beat_wave, blocking=True)
        
        print("测试完成")
    finally:
        # 确保资源被清理
        audio_engine.cleanup() 