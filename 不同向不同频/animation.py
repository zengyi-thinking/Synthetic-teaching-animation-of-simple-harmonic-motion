# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.animation as animation
import time
import threading
from config import has_ffmpeg
from lissajous import (
    calculate_wave_x, 
    calculate_wave_y, 
    calculate_current_position, 
    calculate_lissajous_figure
)

class AnimationController:
    def __init__(self, fig, lines, params_controller, trail_points):
        self.fig = fig
        self.line_x, self.line_y, self.line_lissajous, self.point, self.trail = lines
        self.params_controller = params_controller
        self.trail_points = trail_points
        
        # 播放状态控制
        self.is_paused = False
        self.time_counter = 0
        self.last_frame_time = time.time()
        self.need_redraw = False
        
        # 动画对象
        self.ani = None
    
    def init(self):
        """初始化函数"""
        self.line_x.set_data([], [])
        self.line_y.set_data([], [])
        self.line_lissajous.set_data([], [])
        self.point.set_data([], [])
        self.trail.set_data([], [])
        return self.line_x, self.line_y, self.line_lissajous, self.point, self.trail
    
    def animate(self, i):
        """动画更新函数"""
        if self.is_paused:
            return self.line_x, self.line_y, self.line_lissajous, self.point, self.trail
        
        # 计算帧时间差，以保持平滑的动画速度
        current_time = time.time()
        dt = current_time - self.last_frame_time
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
        trail_length = params['trail_length']
        
        # 更新时间
        self.time_counter += dt * speed
        t_offset = self.time_counter
        
        # 计算波形
        x = calculate_wave_x(t_offset, A1, omega1, phi1)
        y = calculate_wave_y(t_offset, A2, omega2, phi2)
        
        # 计算当前点的位置
        current_x, current_y = calculate_current_position(t_offset, A1, omega1, phi1, A2, omega2, phi2)
        
        # 计算完整的李萨如图形
        x_full, y_full, _ = calculate_lissajous_figure(A1, omega1, phi1, A2, omega2, phi2)
        
        # 更新轨迹点
        self.trail_points[0].append(current_x)
        self.trail_points[1].append(current_y)
        
        # 限制轨迹长度
        if len(self.trail_points[0]) > trail_length:
            self.trail_points[0] = self.trail_points[0][-trail_length:]
            self.trail_points[1] = self.trail_points[1][-trail_length:]
        
        # 更新曲线数据
        from config import t
        self.line_x.set_data(t, x)
        self.line_y.set_data(y, t)  # 注意Y和X轴交换
        
        # 始终显示静态轨迹，透明度较低
        self.line_lissajous.set_data(x_full, y_full)
        self.line_lissajous.set_alpha(0.4)  # 静态轨迹的低透明度
            
        self.point.set_data([current_x], [current_y])
        self.trail.set_data(self.trail_points[0], self.trail_points[1])
        
        return self.line_x, self.line_y, self.line_lissajous, self.point, self.trail
    
    def update_lissajous_figure(self):
        """当频率比改变时，立即更新李萨如图形"""
        # 获取当前参数
        params = self.params_controller.get_current_params()
        A1 = params['A1']
        omega1 = params['omega1']
        phi1 = params['phi1']
        A2 = params['A2']
        omega2 = params['omega2']
        phi2 = params['phi2']
        
        # 计算完整的李萨如图形
        x_full, y_full, _ = calculate_lissajous_figure(A1, omega1, phi1, A2, omega2, phi2)
        
        # 更新静态轨迹
        self.line_lissajous.set_data(x_full, y_full)
        self.line_lissajous.set_alpha(0.7)  # 立即更新时的高透明度
        
        # 更新图形
        self.line_lissajous.axes.figure.canvas.draw_idle()
    
    def initialize_lissajous_figure(self):
        """在启动时初始化李萨如图形"""
        self.update_lissajous_figure()
    
    def start_animation(self):
        """启动动画"""
        self.ani = animation.FuncAnimation(
            self.fig, 
            self.animate, 
            frames=None,  # 无限帧
            init_func=self.init, 
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
                self.ani.save('lissajous_animation.mp4', writer=writer)
                print(f"视频已保存为lissajous_animation.mp4")
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
        """重置动画和参数"""
        # 重置轨迹
        self.trail_points[0] = []
        self.trail_points[1] = []
        
        # 重置时间计数器
        self.time_counter = 0
        self.last_frame_time = time.time()
        
        # 清除轨迹
        self.trail.set_data([], [])
        
        # 标记需要重绘
        self.need_redraw = True 