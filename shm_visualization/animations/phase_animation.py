# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 同向同频（相位差合成）动画控制器
"""

import numpy as np
import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot


class PhaseAnimationController(QObject):
    """
    同向同频（相位差合成）动画控制器
    处理两个频率相同的简谐运动合成，展示相位差效应
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
        self.current_position = 0  # 当前位置
        
        # 当前相量数据
        self.phasor1_x = 0
        self.phasor1_y = 0
        self.phasor2_x = 0
        self.phasor2_y = 0
        self.composite_x = 0
        self.composite_y = 0
        
        # 时间数据 - 优化采样点数量以提高性能
        self.t = np.linspace(0, 10, 300)  # 减少采样点，原来是400
        
        # 初始化动画定时器 - 优化流畅度
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(10)  # 约100 FPS (1000/10) - 平衡性能和流畅度
        
        # 添加性能优化变量
        self._last_params = {}
        self._needs_full_recalculation = True
        self._next_frame_data = None
        self._use_double_buffering = True

        # 帧率监控
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_fps = 0
        self._monitor_fps = False

        # 数学计算优化
        self._trig_cache = {}
        self._cache_size_limit = 500

        # 数学计算优化
        self._trig_cache = {}
        self._cache_size_limit = 500
    
    def initialize_data(self):
        """初始化数据并计算初始波形"""
        # 设置两个波形的频率相同
        params = self.params_controller.get_params()
        self.params_controller.set_param('omega2', params['omega1'])
        self.calculate_waves(0)
        self.calculate_phasors(0)
        self._needs_full_recalculation = False
    
    def calculate_waves(self, t_offset):
        """计算各个波形"""
        params = self.params_controller.get_params()
        
        # 使用预计算的数据以提高性能
        if not self._needs_full_recalculation and self._check_if_params_unchanged(params) and self._next_frame_data is not None:
            self.wave1_data, self.wave2_data, self.composite_data = self._next_frame_data
            self._next_frame_data = None
            return
        
        # 确保两个波形频率相同
        omega = params['omega1']
        
        # 波形移动速度因子
        move_speed = 0.3
        
        # 计算波形移动的偏移量，确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        # 使用-5到5的范围，与PhaseCompositePanel中的设置匹配
        t_array = self.t - wave_offset
        
        # 使用向量化操作一次性计算所有波形，提高性能
        self.wave1_data = params['A1'] * np.sin(omega * t_array + params['phi1'])
        self.wave2_data = params['A2'] * np.sin(omega * t_array + params['phi2'])
        self.composite_data = self.wave1_data + self.wave2_data
        
        # 如果使用双缓冲，预计算下一帧
        if self._use_double_buffering:
            self._precompute_next_frame(t_offset + 0.008 * params['speed'])
            
        # 标记已完成全面重新计算
        self._needs_full_recalculation = False
        
        # 更新缓存的参数
        self._update_cached_params(params)
        
        # 监控帧率
        if self._monitor_fps:
            self._frame_count += 1
            current_time = time.time()
            elapsed = current_time - self._last_fps_time
            if elapsed >= 1.0:
                self._current_fps = self._frame_count / elapsed
                self._frame_count = 0
                self._last_fps_time = current_time
                print(f"相位动画FPS: {self._current_fps:.1f}")
            
    def _precompute_next_frame(self, next_t_offset):
        """预计算下一帧数据，提高性能"""
        params = self.params_controller.get_params()
        omega = params['omega1']
        
        # 计算下一帧波形移动的偏移量
        move_speed = 0.3
        next_wave_offset = (next_t_offset * move_speed) % 10
        next_t_array = self.t - next_wave_offset
        
        # 预计算下一帧的波形数据
        next_wave1 = params['A1'] * np.sin(omega * next_t_array + params['phi1'])
        next_wave2 = params['A2'] * np.sin(omega * next_t_array + params['phi2'])
        next_composite = next_wave1 + next_wave2
        
        # 存储预计算的数据
        self._next_frame_data = (next_wave1, next_wave2, next_composite)
    
    def _check_if_params_unchanged(self, params):
        """检查关键参数是否变化"""
        if not self._last_params:
            return False
            
        key_params = ['A1', 'A2', 'omega1', 'omega2', 'phi1', 'phi2', 'speed']
        for param in key_params:
            if param not in self._last_params or params[param] != self._last_params[param]:
                return False
        return True
        
    def _update_cached_params(self, params):
        """缓存当前参数"""
        self._last_params = params.copy()
        
    def calculate_current_position(self, t_offset):
        """计算当前位置 - 现在是y轴上的位置值"""
        params = self.params_controller.get_params()
        omega = params['omega1']  # 使用相同频率
        
        # 计算y轴上的位置（合成波振幅）
        pos1 = params['A1'] * np.sin(omega * t_offset + params['phi1'])
        pos2 = params['A2'] * np.sin(omega * t_offset + params['phi2'])
        return pos1 + pos2
    
    def calculate_phasors(self, t_offset):
        """计算相量图中的向量"""
        params = self.params_controller.get_params()
        omega = params['omega1']
        # 修改相位计算方式，使其与calculate_current_position保持一致
        phase_at_t = omega * t_offset
        
        # 使用缓存的三角函数值提高性能
        sin_phase1 = np.sin(phase_at_t + params['phi1'])
        cos_phase1 = np.cos(phase_at_t + params['phi1'])
        sin_phase2 = np.sin(phase_at_t + params['phi2'])
        cos_phase2 = np.cos(phase_at_t + params['phi2'])
        
        # 第一个相量
        self.phasor1_x = params['A1'] * cos_phase1
        self.phasor1_y = params['A1'] * sin_phase1
        
        # 第二个相量
        self.phasor2_x = params['A2'] * cos_phase2
        self.phasor2_y = params['A2'] * sin_phase2
        
        # 合成相量（通过向量相加）
        self.composite_x = self.phasor1_x + self.phasor2_x
        self.composite_y = self.phasor1_y + self.phasor2_y
    
    def calculate_composite_amplitude(self):
        """计算合成波的振幅和相位"""
        params = self.params_controller.get_params()
        A1 = params['A1']
        A2 = params['A2']
        phi1 = params['phi1']
        phi2 = params['phi2']
        
        # 计算相位差
        phase_diff = phi2 - phi1
        
        # 使用余弦定理计算合成振幅
        composite_amp = np.sqrt(A1**2 + A2**2 + 2*A1*A2*np.cos(phase_diff))
        
        # 计算合成相位
        if A1 + A2*np.cos(phase_diff) != 0:
            composite_phase = np.arctan2(A2*np.sin(phase_diff), A1 + A2*np.cos(phase_diff)) + phi1
        else:
            composite_phase = np.pi/2 + phi1
            
        return composite_amp, composite_phase
    
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
        
        # 确保两个波形的频率保持一致
        if params['omega1'] != params['omega2']:
            self.params_controller.set_param('omega2', params['omega1'])
            self._needs_full_recalculation = True
        
        # 更新时间计数器
        self.time_counter += dt * params['speed']
        t_offset = self.time_counter
        
        # 计算波形和相量
        self.calculate_waves(t_offset)
        self.calculate_phasors(t_offset)
        
        # 计算当前位置
        self.current_position = self.calculate_current_position(t_offset)
        
        # 发送更新信号
        self.update_signal.emit()
    
    def play(self):
        """播放动画"""
        if self.is_paused:
            self.is_paused = False
            self.last_frame_time = time.time()
            if self._monitor_fps:
                self._last_fps_time = time.time()
                self._frame_count = 0
            self.timer.start()
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
        self.timer.stop()
    
    def reset(self):
        """重置动画"""
        # 暂停动画
        self.pause()
        
        # 重置时间和状态
        self.time_counter = 0
        self._needs_full_recalculation = True
        
        # 重新计算初始波形和相量
        self.calculate_waves(0)
        self.calculate_phasors(0)
        self.current_position = self.calculate_current_position(0)
        
        # 发送更新信号
        self.update_signal.emit() 