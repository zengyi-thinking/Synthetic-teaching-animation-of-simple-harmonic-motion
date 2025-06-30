# -*- coding: utf-8 -*-
"""
音频播放控制器
负责音频的播放、暂停、停止等控制功能
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QMetaObject, Qt

class AudioPlayer(QObject):
    """音频播放器 - 支持原始音频和重构音频的播放控制"""
    
    # 播放状态信号
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_resumed = pyqtSignal()
    position_changed = pyqtSignal(float)  # 播放位置变化 (秒)
    
    def __init__(self, sample_rate: int = 22050):
        """
        初始化音频播放器
        
        Args:
            sample_rate: 采样率
        """
        super().__init__()
        self.sample_rate = sample_rate
        self.is_playing = False
        self.is_paused = False
        self.current_audio = None
        self.current_position = 0.0
        self.total_duration = 0.0
        self.playback_thread = None
        self.stop_event = threading.Event()
        
        # 位置更新定时器
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.setInterval(100)  # 每100ms更新一次位置
        
        # 音频设备信息
        self.output_device = None
        self._check_audio_devices()
    
    def _check_audio_devices(self):
        """检查可用的音频输出设备"""
        try:
            devices = sd.query_devices()
            print("🔊 可用音频设备:")
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    print(f"   {i}: {device['name']} (输出通道: {device['max_output_channels']})")
            
            # 使用默认输出设备
            self.output_device = sd.default.device[1]  # 输出设备
            default_device = sd.query_devices(self.output_device)
            print(f"✅ 使用默认输出设备: {default_device['name']}")
            
        except Exception as e:
            print(f"⚠️  音频设备检查失败: {e}")
    
    def load_audio(self, audio_data: np.ndarray):
        """
        加载音频数据
        
        Args:
            audio_data: 音频数据
        """
        self.current_audio = audio_data.copy()
        self.total_duration = len(audio_data) / self.sample_rate
        self.current_position = 0.0
        
        print(f"✅ 音频加载完成，时长: {self.total_duration:.2f} 秒")
    
    def play(self, start_position: float = 0.0):
        """
        播放音频
        
        Args:
            start_position: 开始播放位置 (秒)
        """
        if self.current_audio is None:
            print("❌ 没有可播放的音频数据")
            return
        
        if self.is_playing:
            self.stop()
        
        self.current_position = start_position
        self.is_playing = True
        self.is_paused = False
        self.stop_event.clear()
        
        # 启动播放线程
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
        # 启动位置更新定时器
        self.position_timer.start()
        
        self.playback_started.emit()
        print(f"▶️  开始播放，从 {start_position:.2f} 秒开始")
    
    def pause(self):
        """暂停播放"""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            # 使用QMetaObject.invokeMethod确保在主线程中停止定时器
            QMetaObject.invokeMethod(self.position_timer, "stop", Qt.ConnectionType.QueuedConnection)
            self.playback_paused.emit()
            print("⏸️  播放已暂停")
    
    def resume(self):
        """恢复播放"""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            # 使用QMetaObject.invokeMethod确保在主线程中启动定时器
            QMetaObject.invokeMethod(self.position_timer, "start", Qt.ConnectionType.QueuedConnection)
            self.playback_resumed.emit()
            print("▶️  播放已恢复")
    
    def stop(self):
        """停止播放"""
        if self.is_playing:
            self.is_playing = False
            self.is_paused = False
            self.stop_event.set()
            # 使用QMetaObject.invokeMethod确保在主线程中停止定时器
            QMetaObject.invokeMethod(self.position_timer, "stop", Qt.ConnectionType.QueuedConnection)

            # 等待播放线程结束
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)
            
            self.current_position = 0.0
            self.playback_stopped.emit()
            print("⏹️  播放已停止")
    
    def seek(self, position: float):
        """
        跳转到指定位置
        
        Args:
            position: 目标位置 (秒)
        """
        if self.current_audio is None:
            return
        
        position = max(0.0, min(position, self.total_duration))
        
        was_playing = self.is_playing
        if was_playing:
            self.stop()
        
        self.current_position = position
        
        if was_playing:
            self.play(position)
        
        print(f"⏭️  跳转到 {position:.2f} 秒")
    
    def set_volume(self, volume: float):
        """
        设置音量
        
        Args:
            volume: 音量 (0.0-1.0)
        """
        volume = max(0.0, min(1.0, volume))
        if self.current_audio is not None:
            # 这里可以实现音量控制逻辑
            pass
        print(f"🔊 音量设置为 {volume:.1%}")
    
    def _playback_worker(self):
        """播放工作线程"""
        try:
            # 计算开始样本位置
            start_sample = int(self.current_position * self.sample_rate)
            audio_to_play = self.current_audio[start_sample:]
            
            if len(audio_to_play) == 0:
                return
            
            # 确保音频数据在有效范围内
            audio_to_play = np.clip(audio_to_play, -1.0, 1.0)
            
            # 播放音频
            sd.play(audio_to_play, samplerate=self.sample_rate, device=self.output_device)
            
            # 等待播放完成或停止信号
            while sd.get_stream().active and not self.stop_event.is_set():
                if not self.is_paused:
                    time.sleep(0.01)
                else:
                    # 暂停时停止当前播放
                    sd.stop()
                    break
            
            # 播放完成
            if not self.stop_event.is_set():
                self.is_playing = False
                self.current_position = 0.0
                # 使用QMetaObject.invokeMethod确保在主线程中停止定时器
                QMetaObject.invokeMethod(self.position_timer, "stop", Qt.ConnectionType.QueuedConnection)
                self.playback_stopped.emit()
                
        except Exception as e:
            print(f"❌ 播放错误: {e}")
            self.is_playing = False
            self.playback_stopped.emit()
    
    def _update_position(self):
        """更新播放位置"""
        if self.is_playing and not self.is_paused:
            # 估算当前播放位置
            if hasattr(sd, 'get_stream') and sd.get_stream().active:
                # 这里可以实现更精确的位置计算
                self.current_position += 0.1  # 简单的时间递增
                
                if self.current_position >= self.total_duration:
                    self.current_position = self.total_duration
                    self.stop()
                
                self.position_changed.emit(self.current_position)
    
    def get_playback_info(self) -> dict:
        """
        获取播放状态信息
        
        Returns:
            播放状态字典
        """
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_position': self.current_position,
            'total_duration': self.total_duration,
            'progress': self.current_position / self.total_duration if self.total_duration > 0 else 0.0
        }
    
    def create_comparison_audio(self, original_audio: np.ndarray, 
                              reconstructed_audio: np.ndarray, 
                              gap_duration: float = 0.5) -> np.ndarray:
        """
        创建对比音频（原始音频 + 间隔 + 重构音频）
        
        Args:
            original_audio: 原始音频
            reconstructed_audio: 重构音频
            gap_duration: 间隔时长 (秒)
            
        Returns:
            对比音频数据
        """
        # 创建静音间隔
        gap_samples = int(gap_duration * self.sample_rate)
        gap = np.zeros(gap_samples)
        
        # 确保两个音频长度相同
        min_length = min(len(original_audio), len(reconstructed_audio))
        original_trimmed = original_audio[:min_length]
        reconstructed_trimmed = reconstructed_audio[:min_length]
        
        # 拼接音频
        comparison_audio = np.concatenate([
            original_trimmed,
            gap,
            reconstructed_trimmed
        ])
        
        return comparison_audio
    
    def __del__(self):
        """析构函数 - 确保停止播放"""
        self.stop()
