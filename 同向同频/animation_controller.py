# -*- coding: utf-8 -*-
import time
import numpy as np
import matplotlib.animation as animation
from config import TIME, has_ffmpeg
from wave_calculations import (
    calculate_wave_x1, calculate_wave_x2, calculate_combined_wave
)

class AnimationController:
    """控制动画播放和更新"""
    
    def __init__(self, fig, lines, params_controller):
        """初始化动画控制器"""
        self.fig = fig
        self.line1, self.line2, self.line3 = lines
        self.params_controller = params_controller
        
        # 动画状态
        self.time_counter = 0
        self.is_paused = False
        self.last_frame_time = time.time()
        self.animation = None
    
    def init_animation(self):
        """初始化动画"""
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.line3.set_data([], [])
        return self.line1, self.line2, self.line3
    
    def update_animation(self, i):
        """更新动画帧"""
        if self.is_paused:
            return self.line1, self.line2, self.line3
        
        # 计算帧时间差，以保持平滑的动画速度
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 获取当前参数
        params = self.params_controller.get_current_params()
        
        # 更新时间
        self.time_counter += dt * params['speed']
        t_offset = self.time_counter
        
        # 计算波形
        x1 = calculate_wave_x1(t_offset, params['A1'], params['omega'], params['phi1'])
        x2 = calculate_wave_x2(t_offset, params['A2'], params['omega'], params['phi2'])
        x3 = calculate_combined_wave(x1, x2)
        
        # 更新曲线数据
        self.line1.set_data(TIME, x1)
        self.line2.set_data(TIME, x2)
        self.line3.set_data(TIME, x3)
        
        return self.line1, self.line2, self.line3
    
    def start_animation(self):
        """启动动画"""
        # 创建动画对象
        self.animation = animation.FuncAnimation(
            self.fig, self.update_animation, frames=None,
            init_func=self.init_animation, interval=25,
            blit=True, cache_frame_data=False
        )
        
        # 如果ffmpeg可用，可以选择保存视频
        if has_ffmpeg:
            try:
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800)
                print("正在保存视频，请稍候...")
                self.animation.save('同向同频.mp4', writer=writer)
                print(f"视频已保存为同向同频.mp4")
            except Exception as e:
                print(f"保存视频时出错: {e}")
    
    def pause(self):
        """暂停动画"""
        self.is_paused = True
    
    def resume(self):
        """继续播放动画"""
        self.is_paused = False
        self.last_frame_time = time.time()  # 重置时间，避免大跳跃 