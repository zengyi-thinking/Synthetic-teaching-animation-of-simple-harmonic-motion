# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 同向不同频（拍现象）动画控制器
"""

import numpy as np
import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, QEvent
import sys


class BeatAnimationController(QObject):
    """
    同向不同频（拍现象）动画控制器
    处理两个频率接近的简谐运动合成，展示拍现象
    """
    # 自定义信号，用于通知UI更新
    update_signal = pyqtSignal()
    
    def __init__(self, params_controller):
        super().__init__()
        self.params_controller = params_controller
        
        # 动画状态
        self.is_paused = True
        self.time_counter = 0
        self.last_frame_time = time.time()
        
        # 波形和轨迹数据
        self.wave1_data = []  # 第一个简谐振动
        self.wave2_data = []  # 第二个简谐振动
        self.composite_data = []  # 合成波
        self.envelope_up = []  # 包络线上部
        self.envelope_down = []  # 包络线下部
        self.current_position = 0  # 当前位置
        
        # 时间数据 - 减少采样点以优化性能
        self.t = np.linspace(0, 10, 600)  # 减少采样点从1000到600
        
        # 初始化动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(8)  # 约125 FPS (1000/8)，提高帧率，原来是14ms
        
        # 优化变量，缓存上一次的参数值
        self._last_params = {}
        self._needs_full_recalculation = True
        
        # 预计算帧数据
        self._next_frame_data = None
        
        # 帧率控制
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_fps = 0
        
        # 性能优化
        self._high_performance = True  # 高性能模式
        self._use_double_buffering = True  # 使用双缓冲
        self._log_fps = False  # 是否记录帧率
        
        # 安装事件过滤器，以便在应用空闲时进行更新
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """简化的事件过滤器，仅用于检测定时器事件"""
        return super().eventFilter(obj, event)
    
    def initialize_data(self):
        """初始化数据并计算初始波形"""
        self._needs_full_recalculation = True
        self.calculate_waves(0)
        self.calculate_beat_frequency()
    
    def calculate_waves(self, t_offset):
        """计算各个波形"""
        params = self.params_controller.get_params()
        
        # 获取波形参数
        A1 = params['A1']
        A2 = params['A2']
        omega1 = params['omega1']
        omega2 = params['omega2']
        phi1 = params['phi1']
        phi2 = params['phi2']
        
        # 如果参数没变化且不需要全面重新计算，使用预计算数据
        if not self._needs_full_recalculation and self._check_if_params_unchanged(params) and self._next_frame_data is not None:
            self.wave1_data, self.wave2_data, self.composite_data, self.envelope_up, self.envelope_down = self._next_frame_data
            self._next_frame_data = None
            return
        
        # 波形移动速度因子 - 更慢的移动使动画更清晰
        move_speed = 0.3
        
        # 计算波形移动的偏移量 - 确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        t_array = self.t - wave_offset
        
        # 使用向量化操作一次性计算所有波形，提高效率
        self.wave1_data = A1 * np.sin(omega1 * t_array + phi1)
        self.wave2_data = A2 * np.sin(omega2 * t_array + phi2)
        self.composite_data = self.wave1_data + self.wave2_data
        
        # 计算包络线（拍现象的特征）
        if abs(omega1 - omega2) > 0.001:  # 确保频率确实不同
            # 使用向量化计算包络线
            phase_diff = (omega1 - omega2) * t_array + (phi1 - phi2)
            amplitude = np.sqrt(A1**2 + A2**2 + 2*A1*A2*np.cos(phase_diff))
            self.envelope_up = amplitude
            self.envelope_down = -amplitude
        else:
            # 如果频率几乎相同，使用振幅和
            amplitude = A1 + A2
            self.envelope_up = np.ones_like(self.t) * amplitude
            self.envelope_down = np.ones_like(self.t) * -amplitude
        
        # 更新缓存的参数
        self._update_cached_params(params)
        
        # 计算帧率
        if self._log_fps:
            self._frame_count += 1
            current_time = time.time()
            elapsed = current_time - self._last_fps_time
            if elapsed >= 1.0:  # 每秒更新一次帧率
                self._current_fps = self._frame_count / elapsed
                self._frame_count = 0
                self._last_fps_time = current_time
                print(f"FPS: {self._current_fps:.1f}")
            
        # 如果处于高性能模式，预计算下一帧
        if self._high_performance and self._use_double_buffering:
            self._precompute_next_frame(t_offset + 0.008 * params['speed'])  # 根据新的定时器间隔调整
        
        # 重置重新计算标志
        self._needs_full_recalculation = False
    
    def _precompute_next_frame(self, next_t_offset):
        """预计算下一帧数据，以提高性能"""
        params = self.params_controller.get_params()
        
        # 使用向量化操作计算下一帧
        omega1 = params['omega1']
        omega2 = params['omega2']
        A1 = params['A1']
        A2 = params['A2']
        phi1 = params['phi1']
        phi2 = params['phi2']
        
        # 计算下一帧的移动偏移
        move_speed = 0.3
        next_wave_offset = (next_t_offset * move_speed) % 10
        t_array = self.t - next_wave_offset
        
        # 计算下一帧的所有波形数据 - 一次性计算所有波形
        next_wave1 = A1 * np.sin(omega1 * t_array + phi1)
        next_wave2 = A2 * np.sin(omega2 * t_array + phi2)
        next_composite = next_wave1 + next_wave2
        
        # 计算下一帧的包络线
        if abs(omega1 - omega2) > 0.001:
            phase_diff = (omega1 - omega2) * t_array + (phi1 - phi2)
            amplitude = np.sqrt(A1**2 + A2**2 + 2*A1*A2*np.cos(phase_diff))
            next_envelope_up = amplitude
            next_envelope_down = -amplitude
        else:
            amplitude = A1 + A2
            next_envelope_up = np.ones_like(self.t) * amplitude
            next_envelope_down = np.ones_like(self.t) * -amplitude
        
        # 存储预计算结果
        self._next_frame_data = (next_wave1, next_wave2, next_composite, next_envelope_up, next_envelope_down)
    
    def _check_if_params_unchanged(self, params):
        """检查参数是否变化"""
        if not self._last_params:
            return False
            
        important_params = ['A1', 'A2', 'omega1', 'omega2', 'phi1', 'phi2', 'speed']
        for param in important_params:
            if param not in self._last_params or params[param] != self._last_params[param]:
                return False
        return True
    
    def _update_cached_params(self, params):
        """更新缓存的参数"""
        self._last_params = params.copy()
    
    def calculate_current_position(self, t_offset):
        """计算当前位置 - 现在是y轴上的位置值"""
        params = self.params_controller.get_params()
        
        # 获取波形参数
        A1 = params['A1']
        A2 = params['A2']
        omega1 = params['omega1']
        omega2 = params['omega2']
        phi1 = params['phi1']
        phi2 = params['phi2']
        
        # 计算y轴上的位置（合成波振幅）
        pos1 = A1 * np.sin(omega1 * t_offset + phi1)
        pos2 = A2 * np.sin(omega2 * t_offset + phi2)
        return pos1 + pos2
    
    def calculate_beat_frequency(self):
        """计算并格式化拍频"""
        params = self.params_controller.get_params()
        omega1 = params['omega1']
        omega2 = params['omega2']
        
        # 拍频 = 频率之差
        beat_freq = abs(omega1 - omega2) / (2 * np.pi)
        # 拍周期 = 拍频的倒数
        beat_period = 1 / beat_freq if beat_freq > 0 else float('inf')
        
        # 主频 = 两个频率的平均值
        main_freq = (omega1 + omega2) / 2 / (2 * np.pi)
        
        return beat_freq, beat_period, main_freq
    
    @pyqtSlot()
    def update_animation(self):
        """更新动画帧"""
        if self.is_paused:
            return
        
        # 使用高精度计时提高帧率一致性
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 获取当前参数
        params = self.params_controller.get_params()
        speed = params['speed']
        
        # 更新时间计数器，控制动画速度
        self.time_counter += dt * speed
        t_offset = self.time_counter
        
        # 计算各波形
        self.calculate_waves(t_offset)
        
        # 计算当前点的位置
        self.current_position = self.calculate_current_position(t_offset)
        
        # 发送更新信号
        self.update_signal.emit()
    
    def play(self):
        """播放动画"""
        if self.is_paused:
            # 恢复定时器
            self.is_paused = False
            self.last_frame_time = time.time()
            self.timer.start()
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
        self.timer.stop()
    
    def reset(self):
        """重置动画"""
        # 暂停动画
        self.pause()
        
        # 重置状态
        self.time_counter = 0
        self.calculate_waves(0)
        self.current_position = self.calculate_current_position(0)
        
        # 触发UI更新
        self.update_signal.emit()
    
    def set_high_performance(self, enabled=True):
        """设置是否使用高性能模式"""
        self._high_performance = enabled 