# -*- coding: utf-8 -*-
import threading
from config import BUTTON_COLOR, BUTTON_ACTIVE_COLOR

class EventHandlers:
    """处理用户交互事件"""
    
    def __init__(self, animation_controller, params_controller, buttons, sliders):
        """初始化事件处理器"""
        self.animation = animation_controller
        self.params_controller = params_controller
        self.buttons = buttons
        self.sliders = sliders
        
        # 绑定事件处理函数
        self.bind_events()
    
    def bind_events(self):
        """绑定所有事件处理函数"""
        # 按钮事件
        self.buttons['play'].on_clicked(self.toggle_play)
        self.buttons['pause'].on_clicked(self.toggle_pause)
        self.buttons['reset'].on_clicked(self.reset)
        
        # 滑块事件
        for slider_key, slider in self.sliders.items():
            slider.on_changed(self.params_controller.throttled_update)
    
    def toggle_play(self, event):
        """切换到播放状态"""
        self.animation.toggle_play()
        self.buttons['play'].color = BUTTON_ACTIVE_COLOR
        self.buttons['pause'].color = BUTTON_COLOR
        
        # 重绘按钮
        self.buttons['play_ax'].figure.canvas.draw_idle()
        self.buttons['pause_ax'].figure.canvas.draw_idle()
    
    def toggle_pause(self, event):
        """切换到暂停状态"""
        self.animation.toggle_pause()
        self.buttons['pause'].color = BUTTON_ACTIVE_COLOR
        self.buttons['play'].color = BUTTON_COLOR
        
        # 重绘按钮
        self.buttons['play_ax'].figure.canvas.draw_idle()
        self.buttons['pause_ax'].figure.canvas.draw_idle()
    
    def reset(self, event):
        """重置所有参数和动画状态"""
        # 重置参数
        self.params_controller.reset_params()
        
        # 重置动画
        self.animation.reset()
        
        # 按钮视觉反馈
        original_color = self.buttons['reset'].color
        self.buttons['reset'].color = BUTTON_ACTIVE_COLOR
        self.buttons['reset_ax'].figure.canvas.draw_idle()
        
        # 安排按钮颜色重置
        def reset_color():
            self.buttons['reset'].color = original_color
            self.buttons['reset_ax'].figure.canvas.draw_idle()
        
        threading.Timer(0.2, reset_color).start() 