# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.animation as animation
import time
from config import has_ffmpeg, T
from wave_calculations import calculate_wave1, calculate_wave2, calculate_combined_wave

class AnimationController:
    """控制和管理动画"""
    
    def __init__(self, fig, lines, params_controller):
        """初始化动画控制器"""
        self.fig = fig
        self.line1, self.line2, self.line3 = lines
        self.params_controller = params_controller
        
        # 播放状态控制
        self.is_paused = False
        self.time_counter = 0
        self.last_frame_time = time.time()
        self.need_redraw = False
        
        # 动画对象
        self.ani = None
    
    def init_animation(self):
        """初始化动画函数"""
        for line in [self.line1, self.line2, self.line3]:
            line.set_data([], [])
        return self.line1, self.line2, self.line3
    
    def update_animation(self, i):
        """动画更新函数"""
        # 如果暂停，直接返回
        if self.is_paused:
            return self.line1, self.line2, self.line3
        
        # 计算帧间时间差以保持平滑的动画速度
        current_time = time.time()
        time_diff = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 获取当前参数
        params = self.params_controller.get_current_params()
        A1 = params['A1']
        omega1 = params['omega1']
        phi1 = params['phi1']
        A2 = params['A2']
        omega2 = params['omega2']
        phi2 = params['phi2']
        speed = params['speed']
        
        # 更新时间
        self.time_counter += time_diff * speed
        time_offset = self.time_counter
        
        # 计算波形
        x1 = calculate_wave1(time_offset, A1, omega1, phi1)
        x2 = calculate_wave2(time_offset, A2, omega2, phi2)
        x3 = calculate_combined_wave(x1, x2)
        
        # 更新曲线数据
        self.line1.set_data(T, x1)
        self.line2.set_data(T, x2)
        self.line3.set_data(T, x3)
        
        return self.line1, self.line2, self.line3
    
    def start_animation(self):
        """启动动画"""
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_animation,
            frames=None,  # 无限帧
            init_func=self.init_animation,
            interval=25,  # 更高的帧率
            blit=True,
            cache_frame_data=False  # 禁用帧缓存以节省内存
        )
        
        # 如果ffmpeg可用，可以选择保存视频
        self.save_animation_if_ffmpeg_available()
    
    def save_animation_if_ffmpeg_available(self):
        """如果ffmpeg可用，将动画保存为视频"""
        if has_ffmpeg:
            try:
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800)
                print("正在保存视频，请稍候...")
                self.ani.save('harmonic_motion_simulation.mp4', writer=writer)
                print(f"视频已保存为 harmonic_motion_simulation.mp4")
            except Exception as e:
                print(f"保存视频时出错: {e}")
        else:
            print("未检测到FFmpeg，无法保存视频")
    
    def toggle_play(self):
        """播放动画"""
        self.is_paused = False
        self.last_frame_time = time.time()  # 重置时间，避免大跳跃
    
    def toggle_pause(self):
        """暂停动画"""
        self.is_paused = True
    
    def reset(self):
        """重置动画"""
        # 重置时间计数器
        self.time_counter = 0
        self.last_frame_time = time.time()
        
        # 标记需要重绘
        self.need_redraw = True 