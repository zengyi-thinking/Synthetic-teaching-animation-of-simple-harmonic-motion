# -*- coding: utf-8 -*-
import time
from config import INITIAL_PARAMS

class ParamsController:
    """控制和管理波形参数"""
    
    def __init__(self, sliders, text_elements):
        """初始化参数控制器"""
        self.sliders = sliders
        self.text_elements = text_elements
        self.current_params = INITIAL_PARAMS.copy()
        self.last_update_time = time.time()
        self.update_interval = 0.05  # 50ms的更新间隔
    
    def update_params_from_sliders(self, val=None):
        """从滑块更新参数值"""
        # 更新参数值
        self.current_params['A1'] = self.sliders['A1'].val
        self.current_params['omega1'] = self.sliders['w1'].val
        self.current_params['phi1'] = self.sliders['p1'].val
        self.current_params['A2'] = self.sliders['A2'].val
        self.current_params['omega2'] = self.sliders['w2'].val
        self.current_params['phi2'] = self.sliders['p2'].val
        self.current_params['speed'] = self.sliders['speed'].val
        
        # 更新显示的值
        self.update_text_elements()
    
    def update_text_elements(self):
        """更新文本元素显示"""
        # 更新参数显示值
        self.text_elements['A1'].set_text(f"{self.current_params['A1']:.1f}")
        self.text_elements['w1'].set_text(f"{self.current_params['omega1']:.1f}")
        self.text_elements['p1'].set_text(f"{self.current_params['phi1']:.1f}")
        self.text_elements['A2'].set_text(f"{self.current_params['A2']:.1f}")
        self.text_elements['w2'].set_text(f"{self.current_params['omega2']:.1f}")
        self.text_elements['p2'].set_text(f"{self.current_params['phi2']:.1f}")
        self.text_elements['speed'].set_text(f"{self.current_params['speed']:.1f}x")
        
        # 更新公式显示
        self.text_elements['wave1_eq'].set_text(
            f'x1 = {self.current_params["A1"]:.1f}*sin({self.current_params["omega1"]:.1f}*t + {self.current_params["phi1"]:.1f})'
        )
        self.text_elements['wave2_eq'].set_text(
            f'x2 = {self.current_params["A2"]:.1f}*sin({self.current_params["omega2"]:.1f}*t + {self.current_params["phi2"]:.1f})'
        )
        
        # 刷新图形
        self.text_elements['A1'].get_figure().canvas.draw_idle()
    
    def throttled_update(self, val=None):
        """使用节流技术减少滑块事件处理的频率"""
        current_time = time.time()
        
        # 如果距离上次更新时间小于间隔，则跳过此次更新
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        self.update_params_from_sliders()
    
    def reset_params(self):
        """重置参数到初始值"""
        # 重置滑块值
        self.sliders['A1'].set_val(INITIAL_PARAMS['A1'])
        self.sliders['w1'].set_val(INITIAL_PARAMS['omega1'])
        self.sliders['p1'].set_val(INITIAL_PARAMS['phi1'])
        self.sliders['A2'].set_val(INITIAL_PARAMS['A2'])
        self.sliders['w2'].set_val(INITIAL_PARAMS['omega2'])
        self.sliders['p2'].set_val(INITIAL_PARAMS['phi2'])
        self.sliders['speed'].set_val(INITIAL_PARAMS['speed'])
        
        # 恢复初始参数
        self.current_params.update(INITIAL_PARAMS)
    
    def get_current_params(self):
        """获取当前参数值"""
        return self.current_params.copy() 