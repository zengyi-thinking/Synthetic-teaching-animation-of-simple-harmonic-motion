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
        
        # 时间数据 - 增加采样点以提高动画效果
        self.t = np.linspace(0, 10, 1000)  # 增加采样点从500到1000
        
        # 初始化动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(16)  # 约60 FPS (1000/16)，提高刷新率
        
        # 优化变量，缓存上一次的参数值
        self._last_params = {}
        self._needs_full_recalculation = True
        
        # 帧率控制
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_fps = 0
        
        # 高性能模式
        self._high_performance = True
        
        # 安装事件过滤器，以便在应用空闲时进行更新
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获应用空闲事件"""
        if event.type() == QEvent.Type.Timer and not self.is_paused:
            # 在定时器事件期间，尝试预计算下一帧
            if self._high_performance and hasattr(self, '_next_frame_data'):
                # 如果已经有预计算数据，直接使用
                self.wave1_data, self.wave2_data, self.composite_data = self._next_frame_data
                del self._next_frame_data  # 清除预计算数据
            
        return super().eventFilter(obj, event)
    
    def initialize_data(self):
        """初始化数据并计算初始波形"""
        self._needs_full_recalculation = True
        self.calculate_waves(0)
        self.calculate_beat_frequency()
    
    def calculate_waves(self, t_offset):
        """计算各个波形"""
        params = self.params_controller.get_params()
        
        # 强制每一帧都重新计算，确保波形持续移动
        self._needs_full_recalculation = True
        
        # 使用向量化操作一次性计算所有波形数据
        omega1 = params['omega1']
        omega2 = params['omega2']
        A1 = params['A1']
        A2 = params['A2']
        phi1 = params['phi1']
        phi2 = params['phi2']
        
        # 完全重写波形移动逻辑
        # 波形移动速度因子 - 更慢的移动使动画更清晰
        move_speed = 0.3
        
        # 计算波形移动的偏移量 - 确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        # 这样随着时间增加，较早的波形部分（左侧）会被新的波形部分（右侧）替代
        t_array = self.t - wave_offset
        
        # 第一个简谐振动 - 使波形随时间从左向右移动
        self.wave1_data = A1 * np.sin(omega1 * t_array + phi1)
        
        # 第二个简谐振动 - 使波形随时间从左向右移动
        self.wave2_data = A2 * np.sin(omega2 * t_array + phi2)
        
        # 合成波 - 直接相加
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
        self._frame_count += 1
        current_time = time.time()
        elapsed = current_time - self._last_fps_time
        if elapsed >= 1.0:  # 每秒更新一次帧率
            self._current_fps = self._frame_count / elapsed
            self._frame_count = 0
            self._last_fps_time = current_time
            print(f"FPS: {self._current_fps:.1f}")
            
        # 如果处于高性能模式，预计算下一帧
        if self._high_performance:
            self._precompute_next_frame(t_offset + 0.01 * params['speed'])
    
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
        
        t_array = self.t - next_t_offset
        
        # 计算下一帧的所有波形数据
        next_wave1 = A1 * np.sin(omega1 * t_array + phi1)
        next_wave2 = A2 * np.sin(omega2 * t_array + phi2)
        next_composite = next_wave1 + next_wave2
        
        # 存储预计算结果
        self._next_frame_data = (next_wave1, next_wave2, next_composite)
    
    def _check_params_changed(self, current_params):
        """检查参数是否变化"""
        if not self._last_params:
            return True
            
        important_params = ['A1', 'A2', 'omega1', 'omega2', 'phi1', 'phi2']
        for param in important_params:
            if param not in self._last_params or current_params[param] != self._last_params[param]:
                return True
        return False
    
    def _update_cached_params(self, params):
        """更新缓存的参数"""
        self._last_params = params.copy()
    
    def calculate_current_position(self, t_offset):
        """计算当前位置"""
        params = self.params_controller.get_params()
        # 合成当前位置
        pos1 = params['A1'] * np.sin(params['omega1'] * (-t_offset) + params['phi1'])
        pos2 = params['A2'] * np.sin(params['omega2'] * (-t_offset) + params['phi2'])
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
        
        # 计算帧时间差，以保持平滑的动画速度
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 获取当前参数
        params = self.params_controller.get_params()
        speed = params['speed']
        
        # 更新时间
        self.time_counter += dt * speed
        t_offset = self.time_counter
        
        # 计算各波形
        self.calculate_waves(t_offset)
        
        # 计算当前点的位置（如果没有在calculate_waves中计算）
        if self._needs_full_recalculation:
            self.current_position = self.calculate_current_position(t_offset)
        
        # 发出更新信号
        self.update_signal.emit()
        
        # 强制要求下一帧重新计算，确保动画连续移动
        self._needs_full_recalculation = True
    
    def play(self):
        """播放动画"""
        if self.is_paused:
            self.is_paused = False
            self.last_frame_time = time.time()
            self._last_fps_time = time.time()
            self._frame_count = 0
            self.timer.start()
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
        self.timer.stop()
    
    def reset(self):
        """重置动画"""
        self.time_counter = 0
        self.last_frame_time = time.time()
        self._needs_full_recalculation = True
        
        # 如果动画正在播放，更新一帧以显示初始状态
        if not self.is_paused:
            self.update_animation()
        else:
            # 计算初始波形
            self.calculate_waves(0)
            self.current_position = self.calculate_current_position(0)
            self.update_signal.emit() 