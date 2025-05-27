# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 垂直简谐运动（不同向不同频）动画控制器
"""

import numpy as np
import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot


class OrthogonalAnimationController(QObject):
    """
    垂直简谐运动（不同向不同频）动画控制器
    处理X和Y方向上的不同频率简谐运动的合成和李萨如图形的生成
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
        
        # 轨迹数据
        self.trail_points = [[], []]
        
        # 波形和轨迹数据
        self.x_data = []
        self.y_data = []
        self.lissajous_x = []
        self.lissajous_y = []
        self.current_x = 0
        self.current_y = 0
        
        # 时间数据
        self.t = np.linspace(0, 10, 500)
        
        # 添加参数变化检测
        self._last_params = {}
        
        # 初始化动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(20)  # 50 FPS
        
        # 连接参数变化的信号
        self.params_controller.params_changed.connect(self.on_params_changed)
    
    @pyqtSlot()
    def on_params_changed(self):
        """当参数变化时，清除旧轨迹并重新计算李萨如图形"""
        # 检查是否真的有关键参数发生变化
        current_params = self.params_controller.get_params()
        
        # 检查重要参数（振幅、频率、相位）是否有变化
        important_params = ['A1', 'A2', 'omega1', 'omega2', 'phi1', 'phi2']
        params_changed = False
        
        for param in important_params:
            if param not in self._last_params or self._last_params.get(param) != current_params.get(param):
                params_changed = True
                break
        
        if params_changed:
            # 清空轨迹
            self.trail_points = [[], []]
            
            # 重新计算李萨如图形
            self.calculate_lissajous_figure()
            
            # 更新缓存的参数
            self._last_params = current_params.copy()
            
            # 如果动画处于暂停状态，手动触发更新
            if self.is_paused:
                # 计算当前位置
                self.current_x, self.current_y = self.calculate_current_position(self.time_counter)
                self.update_signal.emit()
    
    def initialize_data(self):
        """初始化数据并计算初始图形"""
        self.calculate_lissajous_figure()
        self._last_params = self.params_controller.get_params().copy()
    
    def calculate_wave_x(self, t_offset):
        """计算X方向波形"""
        params = self.params_controller.get_params()
        # 生成一个移动的波形，而不是固定波形
        return params['A1'] * np.sin(params['omega1'] * (self.t - t_offset) + params['phi1'])
    
    def calculate_wave_y(self, t_offset):
        """计算Y方向波形"""
        params = self.params_controller.get_params()
        # 生成一个移动的波形，而不是固定波形
        return params['A2'] * np.sin(params['omega2'] * (self.t - t_offset) + params['phi2'])
    
    def calculate_current_position(self, t_offset):
        """计算当前点的位置"""
        params = self.params_controller.get_params()
        current_x = params['A1'] * np.sin(params['omega1'] * (-t_offset) + params['phi1'])
        current_y = params['A2'] * np.sin(params['omega2'] * (-t_offset) + params['phi2'])
        return current_x, current_y
    
    def calculate_lissajous_figure(self):
        """计算完整的李萨如图形"""
        params = self.params_controller.get_params()
        A1 = params['A1']
        omega1 = params['omega1']
        phi1 = params['phi1']
        A2 = params['A2']
        omega2 = params['omega2']
        phi2 = params['phi2']
        
        # 计算最小公倍周期
        omega1_int = int(omega1 * 100)
        omega2_int = int(omega2 * 100)
        gcd_val = np.gcd(omega1_int, omega2_int)
        period = 2 * np.pi * (omega1_int // gcd_val) / omega1
        
        # 计算轨迹
        full_t = np.linspace(0, period, 1000)
        self.lissajous_x = A1 * np.sin(omega1 * full_t + phi1)
        self.lissajous_y = A2 * np.sin(omega2 * full_t + phi2)
    
    def calculate_frequency_ratio(self):
        """计算并格式化频率比"""
        params = self.params_controller.get_params()
        omega1 = params['omega1']
        omega2 = params['omega2']
        
        # 计算最大公约数
        omega1_int = int(omega1 * 100)
        omega2_int = int(omega2 * 100)
        gcd_val = np.gcd(omega1_int, omega2_int)
        w1_ratio = omega1_int // gcd_val
        w2_ratio = omega2_int // gcd_val
        
        return w2_ratio, w1_ratio, f'ω2:ω1 = {w2_ratio}:{w1_ratio}'
    
    def adjust_frequency_for_ratio(self, ratio_key):
        """根据选择的频率比调整频率"""
        params = self.params_controller.get_params()
        
        # 确保ratio_presets存在
        if 'ratio_presets' not in params:
            print("Error: ratio_presets not found in params")
            return params['omega1'], params['omega2']
            
        ratio_presets = params['ratio_presets']
        
        # 确保选择的比率存在
        if ratio_key not in ratio_presets:
            print(f"Error: ratio key '{ratio_key}' not found in ratio_presets")
            return params['omega1'], params['omega2']
        
        ratio_preset = ratio_presets[ratio_key]
        print(f"Using frequency ratio: {ratio_key} = {ratio_preset}")
        
        w1_val, w2_val = ratio_preset
        
        # 确定当前模式
        ratio_mode = params.get('ratio_mode', 'w2')  # 默认为w2
        
        if ratio_mode == 'w1':
            # 固定w2，调整w1
            new_w1 = params['omega2'] * (w1_val / w2_val)
            new_w2 = params['omega2']
            # 确保在有效范围内
            new_w1 = max(0.1, min(5.0, new_w1))
        else:
            # 固定w1，调整w2
            new_w1 = params['omega1']
            new_w2 = params['omega1'] * (w2_val / w1_val)
            # 确保在有效范围内
            new_w2 = max(0.1, min(5.0, new_w2))
        
        print(f"Adjusted frequencies: omega1={new_w1}, omega2={new_w2}")
        return new_w1, new_w2
    
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
        trail_length = params['trail_length']
        
        # 更新时间
        self.time_counter += dt * speed
        t_offset = self.time_counter
        
        # 计算波形
        self.x_data = self.calculate_wave_x(t_offset)
        self.y_data = self.calculate_wave_y(t_offset)
        
        # 计算当前点的位置
        self.current_x, self.current_y = self.calculate_current_position(t_offset)
        
        # 更新轨迹点
        self.trail_points[0].append(self.current_x)
        self.trail_points[1].append(self.current_y)
        
        # 限制轨迹长度
        if len(self.trail_points[0]) > trail_length:
            self.trail_points[0] = self.trail_points[0][-trail_length:]
            self.trail_points[1] = self.trail_points[1][-trail_length:]
        
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
        
        # 清空轨迹
        self.trail_points = [[], []]
        
        # 如果动画正在播放，更新一帧以显示初始状态
        if not self.is_paused:
            self.update_animation()
        else:
            # 计算初始位置
            self.current_x, self.current_y = self.calculate_current_position(0)
            self.x_data = self.calculate_wave_x(0)
            self.y_data = self.calculate_wave_y(0)
            self.update_signal.emit() 