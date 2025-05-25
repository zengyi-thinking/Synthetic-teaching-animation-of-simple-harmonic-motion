# -*- coding: utf-8 -*-
import numpy as np
from config import BUTTON_COLOR, BUTTON_ACTIVE_COLOR

class EventHandlers:
    """处理用户界面的事件"""
    
    def __init__(self, animation_controller, params_controller):
        """初始化事件处理器"""
        self.animation_controller = animation_controller
        self.params_controller = params_controller
        
    def connect_events(self, buttons, sliders, phase_buttons):
        """连接所有事件处理函数"""
        # 连接主控制按钮
        buttons['play'].on_clicked(self.toggle_play)
        buttons['pause'].on_clicked(self.toggle_pause)
        buttons['reset'].on_clicked(self.reset)
        
        # 连接滑块
        for name, slider in sliders.items():
            slider.on_changed(self.params_controller.update_slider_values)
        
        # 连接相位差预设按钮
        for btn, value in phase_buttons:
            # 使用闭包创建有正确值捕获的回调
            btn.on_clicked(self._create_phase_difference_callback(value))
    
    def toggle_play(self, event):
        """播放动画"""
        self.animation_controller.resume()
        # 更新按钮状态
        self._update_play_button_state(True)
    
    def toggle_pause(self, event):
        """暂停动画"""
        self.animation_controller.pause()
        # 更新按钮状态
        self._update_play_button_state(False)
    
    def reset(self, event):
        """重置参数到初始值"""
        # 重置滑块和参数
        self.params_controller.reset_params()
        
        # 短暂改变按钮颜色以指示操作
        original_color = event.inaxes.patches[0].get_facecolor()
        event.inaxes.patches[0].set_facecolor(BUTTON_ACTIVE_COLOR)
        event.canvas.draw_idle()
        
        # 使用计时器在短时间后恢复按钮颜色
        timer = event.canvas.new_timer(interval=200)  # 200毫秒后恢复
        
        def reset_color():
            event.inaxes.patches[0].set_facecolor(original_color)
            event.canvas.draw_idle()
        
        timer.add_callback(reset_color)
        timer.start()
    
    def _create_phase_difference_callback(self, phase_value):
        """创建相位差预设按钮的回调函数"""
        def set_phase_difference(event):
            self.params_controller.set_phase_difference(phase_value)
        return set_phase_difference
    
    def _update_play_button_state(self, is_playing):
        """更新播放/暂停按钮的状态"""
        play_button = self.params_controller.buttons['play']
        pause_button = self.params_controller.buttons['pause']
        
        # 根据是否正在播放设置按钮颜色
        play_button.color = BUTTON_ACTIVE_COLOR if is_playing else BUTTON_COLOR
        pause_button.color = BUTTON_COLOR if is_playing else BUTTON_ACTIVE_COLOR
        
        # 刷新按钮
        play_button.ax.figure.canvas.draw_idle()
        pause_button.ax.figure.canvas.draw_idle() 