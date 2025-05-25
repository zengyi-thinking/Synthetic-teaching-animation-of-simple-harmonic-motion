# -*- coding: utf-8 -*-
import time
import threading
from config import BUTTON_COLOR, BUTTON_ACTIVE_COLOR, TRAJECTORY_COLOR
from lissajous import adjust_frequency_for_ratio

class EventHandlers:
    def __init__(self, animation_controller, params_controller, buttons, sliders, trail_points):
        self.animation = animation_controller
        self.params_controller = params_controller
        self.buttons = buttons
        self.sliders = sliders
        self.trail_points = trail_points
        self.last_update_time = time.time()
        self.update_interval = 0.05  # 50ms更新间隔
        
        # 绑定事件处理函数
        self.bind_events()
    
    def bind_events(self):
        """绑定所有事件处理函数"""
        # 播放控制按钮
        self.buttons['play'].on_clicked(self.toggle_play)
        self.buttons['pause'].on_clicked(self.toggle_pause)
        self.buttons['reset'].on_clicked(self.reset)
        
        # 频率比按钮
        current_params = self.params_controller.get_current_params()
        for i, ratio_key in enumerate(current_params['ratio_presets'].keys()):
            self.buttons['ratio_buttons'][i].on_clicked(
                lambda event, r=ratio_key: self.ratio_button_click(event, r)
            )
        
        # 频率比模式切换按钮
        self.buttons['w1_fixed'].on_clicked(self.toggle_ratio_mode_w1)
        self.buttons['w2_fixed'].on_clicked(self.toggle_ratio_mode_w2)
        
        # 将节流更新函数绑定到所有滑块
        for slider_key, slider in self.sliders.items():
            slider.on_changed(self.throttled_update)
        
        # 使用安全包装器
        for button_key, button in self.buttons.items():
            if button_key not in ['ratio_buttons', 'ratio_button_axes', 'w1_fixed_ax', 'w2_fixed_ax']:
                button.on_clicked = self.safe_click_handler(button.on_clicked)
        
        for button in self.buttons['ratio_buttons']:
            button.on_clicked = self.safe_click_handler(button.on_clicked)
    
    def safe_click_handler(self, original_handler):
        """创建按钮点击安全包装器，避免鼠标抓取冲突"""
        def wrapped_handler(event):
            # 在处理点击事件之前，尝试释放任何现有的鼠标抓取
            if event.canvas.mouse_grabber is not None:
                try:
                    event.canvas.release_mouse(event.canvas.mouse_grabber)
                except:
                    pass  # 忽略释放过程中的错误
            # 调用原始处理函数
            original_handler(event)
        return wrapped_handler
    
    def toggle_play(self, event):
        """切换到播放状态"""
        self.animation.toggle_play()
        self.buttons['play'].color = BUTTON_ACTIVE_COLOR
        self.buttons['pause'].color = BUTTON_COLOR
        
        # 重绘按钮
        self.buttons['play'].ax.figure.canvas.draw_idle()
        self.buttons['pause'].ax.figure.canvas.draw_idle()
    
    def toggle_pause(self, event):
        """切换到暂停状态"""
        self.animation.toggle_pause()
        self.buttons['pause'].color = BUTTON_ACTIVE_COLOR
        self.buttons['play'].color = BUTTON_COLOR
        
        # 重绘按钮
        self.buttons['play'].ax.figure.canvas.draw_idle()
        self.buttons['pause'].ax.figure.canvas.draw_idle()
    
    def reset(self, event):
        """重置所有参数和动画状态"""
        # 重置参数
        self.params_controller.reset_params()
        
        # 重置动画
        self.animation.reset()
        
        # 按钮视觉反馈
        original_color = self.buttons['reset'].color
        self.buttons['reset'].color = BUTTON_ACTIVE_COLOR
        self.buttons['reset'].ax.figure.canvas.draw_idle()
        
        # 安排按钮颜色重置
        def reset_color():
            self.buttons['reset'].color = original_color
            self.buttons['reset'].ax.figure.canvas.draw_idle()
        
        threading.Timer(0.2, reset_color).start()
    
    def ratio_button_click(self, event, ratio_key):
        """处理频率比预设按钮点击事件"""
        # 禁用所有频率比按钮
        for button in self.buttons['ratio_buttons']:
            button.color = '#1E293B'
        
        # 获取被点击的按钮
        for i, key in enumerate(self.params_controller.get_current_params()['ratio_presets'].keys()):
            if key == ratio_key:
                self.buttons['ratio_buttons'][i].color = TRAJECTORY_COLOR
                self.buttons['ratio_buttons'][i].ax.figure.canvas.draw_idle()
        
        # 设置新的频率比
        current_params = self.params_controller.get_current_params()
        ratio_preset = current_params['ratio_presets'][ratio_key]
        
        # 根据所选模式调整频率
        new_w1, new_w2 = adjust_frequency_for_ratio(
            ratio_preset,
            current_params['omega1'], 
            current_params['omega2'], 
            current_params['ratio_mode']
        )
        
        # 更新滑块值
        self.sliders['w1'].set_val(new_w1)
        self.sliders['w2'].set_val(new_w2)
        
        # 存储当前预设
        self.params_controller.set_ratio_preset(ratio_key)
        
        # 清除轨迹，以便使用新参数重新绘制
        self.trail_points[0] = []
        self.trail_points[1] = []
        
        # 重置时间计数器
        self.animation.time_counter = 0
        
        # 立即更新李萨如图形
        self.animation.update_lissajous_figure()
    
    def toggle_ratio_mode_w1(self, event):
        """切换到固定w1模式"""
        # 获取并更新当前参数
        current_params = self.params_controller.get_current_params()
        current_params['ratio_mode'] = 'w1'
        
        # 更新按钮外观
        self.buttons['w1_fixed'].color = TRAJECTORY_COLOR
        self.buttons['w2_fixed'].color = '#1E293B'
        self.buttons['w1_fixed_ax'].figure.canvas.draw_idle()
        self.buttons['w2_fixed_ax'].figure.canvas.draw_idle()
    
    def toggle_ratio_mode_w2(self, event):
        """切换到固定w2模式"""
        # 获取并更新当前参数
        current_params = self.params_controller.get_current_params()
        current_params['ratio_mode'] = 'w2'
        
        # 更新按钮外观
        self.buttons['w2_fixed'].color = TRAJECTORY_COLOR
        self.buttons['w1_fixed'].color = '#1E293B'
        self.buttons['w1_fixed_ax'].figure.canvas.draw_idle()
        self.buttons['w2_fixed_ax'].figure.canvas.draw_idle()
    
    def throttled_update(self, val=None):
        """使用节流技术减少滑块事件处理的频率"""
        current_time = time.time()
        
        # 如果距离上次更新时间小于间隔，则跳过此次更新
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        
        # 存储旧参数，用于检查是否需要重置轨迹
        current_params = self.params_controller.get_current_params()
        old_omega1 = current_params['omega1']
        old_omega2 = current_params['omega2']
        old_phi1 = current_params['phi1']
        old_phi2 = current_params['phi2']
        old_A1 = current_params['A1']
        old_A2 = current_params['A2']
        
        # 更新滑块值
        self.params_controller.update_params_from_sliders()
        
        # 获取更新后的参数
        current_params = self.params_controller.get_current_params()
        
        # 检查是否需要重置轨迹
        # 如果任何参数发生显著变化，则清除轨迹
        if (abs(old_omega1 - current_params['omega1']) > 0.05 or
            abs(old_omega2 - current_params['omega2']) > 0.05 or
            abs(old_phi1 - current_params['phi1']) > 0.05 or
            abs(old_phi2 - current_params['phi2']) > 0.05 or
            abs(old_A1 - current_params['A1']) > 0.05 or
            abs(old_A2 - current_params['A2']) > 0.05):
            
            # 清除轨迹
            self.trail_points[0] = []
            self.trail_points[1] = []
            
            # 更新李萨如图形
            self.animation.update_lissajous_figure() 