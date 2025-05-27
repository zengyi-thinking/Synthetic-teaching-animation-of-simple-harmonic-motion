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
        
        # 时间数据
        self.t = np.linspace(0, 10, 500)
        
        # 初始化动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(20)  # 50 FPS
    
    def initialize_data(self):
        """初始化数据并计算初始波形"""
        # 设置两个波形的频率相同
        params = self.params_controller.get_params()
        self.params_controller.set_param('omega2', params['omega1'])
        self.calculate_waves(0)
        self.calculate_phasors(0)
    
    def calculate_waves(self, t_offset):
        """计算各个波形"""
        params = self.params_controller.get_params()
        
        # 确保两个波形频率相同
        omega = params['omega1']
        
        # 波形移动速度因子 - 更慢的移动使动画更清晰
        move_speed = 0.3
        
        # 计算波形移动的偏移量 - 确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        t_array = self.t - wave_offset
        
        # 第一个简谐振动 - 使波形随时间从左向右移动
        self.wave1_data = params['A1'] * np.sin(omega * t_array + params['phi1'])
        
        # 第二个简谐振动（同频）- 使波形随时间从左向右移动
        self.wave2_data = params['A2'] * np.sin(omega * t_array + params['phi2'])
        
        # 合成波
        self.composite_data = self.wave1_data + self.wave2_data
        
    def calculate_current_position(self, t_offset):
        """计算当前位置"""
        params = self.params_controller.get_params()
        omega = params['omega1']  # 使用相同频率
        # 合成当前位置
        pos1 = params['A1'] * np.sin(omega * (-t_offset) + params['phi1'])
        pos2 = params['A2'] * np.sin(omega * (-t_offset) + params['phi2'])
        return pos1 + pos2
    
    def calculate_phasors(self, t_offset):
        """计算相量图中的向量"""
        params = self.params_controller.get_params()
        omega = params['omega1']
        phase_at_t = omega * (-t_offset)
        
        # 第一个相量
        angle1 = phase_at_t + params['phi1']
        self.phasor1_x = params['A1'] * np.cos(angle1)
        self.phasor1_y = params['A1'] * np.sin(angle1)
        
        # 第二个相量
        angle2 = phase_at_t + params['phi2']
        self.phasor2_x = params['A2'] * np.cos(angle2)
        self.phasor2_y = params['A2'] * np.sin(angle2)
        
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
        speed = params['speed']
        
        # 更新时间
        self.time_counter += dt * speed
        t_offset = self.time_counter
        
        # 计算各波形
        self.calculate_waves(t_offset)
        
        # 计算相量
        self.calculate_phasors(t_offset)
        
        # 计算当前点的位置
        self.current_position = self.calculate_current_position(t_offset)
        
        # 发出更新信号
        self.update_signal.emit()
    
    def play(self):
        """播放动画"""
        if self.is_paused:
            self.is_paused = False
            self.last_frame_time = time.time()
            self.timer.start()
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
        self.timer.stop()
    
    def reset(self):
        """重置动画"""
        self.time_counter = 0
        self.last_frame_time = time.time()
        
        # 如果动画正在播放，更新一帧以显示初始状态
        if not self.is_paused:
            self.update_animation()
        else:
            # 计算初始波形
            self.calculate_waves(0)
            self.calculate_phasors(0)
            self.current_position = self.calculate_current_position(0)
            self.update_signal.emit() 