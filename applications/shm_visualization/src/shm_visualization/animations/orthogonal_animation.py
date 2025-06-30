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
        
        # 时间数据 - 优化采样点减少计算量
        self.t = np.linspace(0, 10, 300)  # 从400减少到300点
        
        # 添加参数变化检测
        self._last_params = {}
        
        # 添加性能优化变量
        self._needs_full_recalculation = True
        self._next_frame_data = None
        self._use_double_buffering = True
        self._precomputed_lissajous = False
        self._lissajous_cache = {}
        
        # 初始化动画定时器 - 优化流畅度
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(12)  # 约83 FPS (1000/12) - 提高流畅度
        
        # 帧率监控
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_fps = 0
        self._monitor_fps = True  # 启用帧率监控
        
        # 抗锯齿和高质量渲染
        self._high_quality = True
        
        # 连接参数变化的信号
        self.params_controller.params_changed.connect(self.on_params_changed)
        
        print("动画控制器初始化完成")
    
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
            self._precomputed_lissajous = False
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
        
        # 使用预计算数据（如有）
        if not self._needs_full_recalculation and self._next_frame_data is not None:
            x_data, _ = self._next_frame_data
            self._next_frame_data = None
            return x_data
            
        # 波形移动速度因子 - 更慢的移动使动画更清晰
        move_speed = 0.3
        
        # 计算波形移动的偏移量 - 确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        # 使用-5到5的范围，与波形图中的设置匹配
        t_array = self.t - wave_offset
        
        # 使用向量化操作生成波形，提高效率
        return params['A1'] * np.sin(params['omega1'] * t_array + params['phi1'])
    
    def calculate_wave_y(self, t_offset):
        """计算Y方向波形"""
        params = self.params_controller.get_params()
        
        # 使用预计算数据（如有）
        if not self._needs_full_recalculation and self._next_frame_data is not None:
            _, y_data = self._next_frame_data
            return y_data
            
        # 波形移动速度因子 - 更慢的移动使动画更清晰
        move_speed = 0.3
        
        # 计算波形移动的偏移量 - 确保在视窗内循环
        wave_offset = (t_offset * move_speed) % 10
        
        # 为了确保波形从左向右移动，我们需要减去这个偏移量
        # 使用-5到5的范围，与波形图中的设置匹配
        t_array = self.t - wave_offset
        
        # 使用向量化操作生成波形，提高效率
        return params['A2'] * np.sin(params['omega2'] * t_array + params['phi2'])
    
    def _precompute_next_frame(self, next_t_offset):
        """预计算下一帧的波形数据"""
        params = self.params_controller.get_params()
        A1 = params['A1']
        omega1 = params['omega1']
        phi1 = params['phi1']
        A2 = params['A2']
        omega2 = params['omega2']
        phi2 = params['phi2']
        
        # 波形移动速度因子
        move_speed = 0.3
        
        # 计算波形移动的偏移量
        next_wave_offset = (next_t_offset * move_speed) % 10
        
        # 计算时间数组
        next_t_array = self.t - next_wave_offset
        
        # 一次性计算下一帧的X和Y波形
        next_x_data = A1 * np.sin(omega1 * next_t_array + phi1)
        next_y_data = A2 * np.sin(omega2 * next_t_array + phi2)
        
        # 存储预计算结果
        self._next_frame_data = (next_x_data, next_y_data)
    
    def calculate_current_position(self, t_offset):
        """计算当前点的位置"""
        params = self.params_controller.get_params()
        
        # 直接计算当前时刻的x和y位置，无需关心波形
        current_x = params['A1'] * np.sin(params['omega1'] * t_offset + params['phi1'])
        current_y = params['A2'] * np.sin(params['omega2'] * t_offset + params['phi2'])
        
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
        
        # 检查缓存中是否已有相同参数的李萨如图形
        cache_key = f"{A1:.2f}_{A2:.2f}_{omega1:.2f}_{omega2:.2f}_{phi1:.2f}_{phi2:.2f}"
        if cache_key in self._lissajous_cache and self._precomputed_lissajous:
            self.lissajous_x, self.lissajous_y = self._lissajous_cache[cache_key]
            return
        
        # 计算最小公倍周期，确保图形闭合
        omega1_int = int(omega1 * 100)
        omega2_int = int(omega2 * 100)
        gcd_val = np.gcd(omega1_int, omega2_int)
        period = 2 * np.pi * (omega1_int // gcd_val) / omega1
        
        # 优化李萨如图形计算的采样点数量
        num_points = min(2000, max(500, int((omega1_int + omega2_int) * 5)))
        
        # 计算轨迹
        full_t = np.linspace(0, period, num_points)
        self.lissajous_x = A1 * np.sin(omega1 * full_t + phi1)
        self.lissajous_y = A2 * np.sin(omega2 * full_t + phi2)
        
        # 缓存计算结果
        self._lissajous_cache[cache_key] = (self.lissajous_x, self.lissajous_y)
        self._precomputed_lissajous = True
        
        # 限制缓存大小
        if len(self._lissajous_cache) > 20:  # 最多保存20组不同参数的图形
            # 移除最早添加的项
            oldest_key = next(iter(self._lissajous_cache))
            del self._lissajous_cache[oldest_key]
    
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
            print(f"Error: ratio key '{ratio_key}' not found in presets")
            return params['omega1'], params['omega2']
        
        # 获取频率比
        ratio_x, ratio_y = ratio_presets[ratio_key]
        
        # 根据用户选择的比率模式决定如何调整频率
        ratio_mode = params.get('ratio_mode', 'w2')
        
        if ratio_mode == 'w1':
            # 保持omega2不变，调整omega1使其符合比例
            omega2 = params['omega2']
            omega1 = (ratio_x / ratio_y) * omega2
            return omega1, omega2
        else:  # 默认为'w2'模式
            # 保持omega1不变，调整omega2使其符合比例
            omega1 = params['omega1']
            omega2 = (ratio_y / ratio_x) * omega1
            return omega1, omega2
    
    @pyqtSlot()
    def update_animation(self):
        """更新动画帧"""
        if self.is_paused:
            return
        
        # 高精度计时以保持平滑的动画速度
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 获取当前参数
        params = self.params_controller.get_params()
        
        # 更新时间计数器
        self.time_counter += dt * params['speed']
        t_offset = self.time_counter
        
        # 计算当前波形 - 每帧都需要更新波形以实现移动效果
        self.x_data = self.calculate_wave_x(t_offset)
        self.y_data = self.calculate_wave_y(t_offset)
        
        # 计算当前时刻波形与y轴的交点 - 这仅用于初始化当前位置
        # 在UI层会根据实际波形数据重新计算并更新这些值
        self.current_x, self.current_y = self.get_zero_point_value(t_offset)
        
        # 注意：轨迹点的添加将在UI层进行，以确保使用正确的交点值
        # 此处不再主动添加轨迹点，而是在UI的update_plots方法中添加
        
        # 帧率监控
        if self._monitor_fps:
            self._frame_count += 1
            elapsed = current_time - self._last_fps_time
            if elapsed >= 1.0:
                self._current_fps = self._frame_count / elapsed
                self._frame_count = 0
                self._last_fps_time = current_time
                print(f"李萨如动画FPS: {self._current_fps:.1f}")
        
        # 每隔100帧打印一次当前状态
        if self._frame_count % 100 == 0:
            print(f"动画更新 - 时间: {t_offset:.2f}, 坐标: ({self.current_x:.2f}, {self.current_y:.2f})")
            print(f"波形偏移: {(t_offset * 0.3) % 10:.2f}")
        
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
            print(f"动画开始播放 - 时间计数器: {self.time_counter:.2f}")
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
        self.timer.stop()
        print(f"动画已暂停 - 时间计数器: {self.time_counter:.2f}")
    
    def reset(self):
        """重置动画"""
        # 暂停动画
        self.pause()
        
        # 重置状态
        self.time_counter = 0
        self.trail_points = [[], []]  # 清空轨迹
        
        # 重新计算初始波形
        self.x_data = self.calculate_wave_x(0)
        self.y_data = self.calculate_wave_y(0)
        
        # 使用与视图显示一致的方法计算初始位置
        self.current_x, self.current_y = self.get_zero_point_value(0)
        
        # 发送更新信号
        self.update_signal.emit()
        print("动画已重置")
    
    def set_high_quality(self, enabled=True):
        """设置是否启用高质量渲染"""
        self._high_quality = enabled
        # 高质量模式下使用双缓冲和更多的李萨如图形采样点
        if enabled and not self._use_double_buffering:
            self._use_double_buffering = True
            self._precomputed_lissajous = False
            self.calculate_lissajous_figure()  # 重新计算更高质量的图形

    def get_zero_point_value(self, t_offset):
        """计算波形与y轴(x=0处)的交点值"""
        params = self.params_controller.get_params()
        A1 = params['A1']
        omega1 = params['omega1']
        phi1 = params['phi1']
        A2 = params['A2']
        omega2 = params['omega2']
        phi2 = params['phi2']
        
        # 波形移动速度因子
        move_speed = 0.3
        
        # 计算波形移动的偏移量
        wave_offset = (t_offset * move_speed) % 10
        
        # 查找波形数组中最接近纵轴(x=0)的点
        # 在波形图中，我们显示的是[-5,5]的范围，因此纵轴(x=0)对应的是第5*len(self.t)/10个点
        mid_index = len(self.t) // 2
        
        # 使用当前计算的波形直接获取交点值
        # 这确保了小球位置与实际绘制的波形完全匹配
        try:
            if len(self.x_data) > 0 and mid_index < len(self.x_data):
                x_value = self.x_data[mid_index]
            else:
                # 如果波形数据还没准备好，使用公式计算
                t_at_zero = 5.0 + wave_offset  # 纵轴对应的时间点
                if t_at_zero >= 10:
                    t_at_zero -= 10
                x_value = A1 * np.sin(omega1 * t_at_zero + phi1)
                
            if len(self.y_data) > 0 and mid_index < len(self.y_data):
                y_value = self.y_data[mid_index]
            else:
                # 如果波形数据还没准备好，使用公式计算
                t_at_zero = 5.0 + wave_offset  # 纵轴对应的时间点
                if t_at_zero >= 10:
                    t_at_zero -= 10
                y_value = A2 * np.sin(omega2 * t_at_zero + phi2)
                
            print(f"交点计算: wave_offset={wave_offset:.2f}, 坐标=({x_value:.2f}, {y_value:.2f})")
            return x_value, y_value
        except Exception as e:
            print(f"交点计算错误: {e}")
            # 如果出错，使用公式计算
            return A1 * np.sin(omega1 * t_offset + phi1), A2 * np.sin(omega2 * t_offset + phi2) 