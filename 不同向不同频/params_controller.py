# -*- coding: utf-8 -*-
import numpy as np
from config import INITIAL_PARAMS, ratio_presets
from lissajous import calculate_frequency_ratio

class ParamsController:
    """控制和管理波形参数"""
    
    def __init__(self, sliders, text_elements):
        """初始化参数控制器"""
        self.sliders = sliders
        self.text_elements = text_elements
        self.current_params = INITIAL_PARAMS.copy()
        self.current_params['ratio_presets'] = ratio_presets
    
    def update_params_from_sliders(self, val=None):
        """从滑块更新参数值"""
        # 更新参数值
        self.current_params['A1'] = self.sliders['a1'].val
        self.current_params['omega1'] = self.sliders['w1'].val
        self.current_params['phi1'] = self.sliders['p1'].val
        self.current_params['A2'] = self.sliders['a2'].val
        self.current_params['omega2'] = self.sliders['w2'].val
        self.current_params['phi2'] = self.sliders['p2'].val
        self.current_params['speed'] = self.sliders['speed'].val
        self.current_params['trail_length'] = int(self.sliders['trail'].val)
        
        # 更新显示的值
        self.update_text_elements()
        
    def update_text_elements(self):
        """更新文本元素显示"""
        # 更新参数显示值
        self.text_elements['a1'].set_text(f"{self.current_params['A1']:.1f}")
        self.text_elements['w1'].set_text(f"{self.current_params['omega1']:.1f}")
        self.text_elements['p1'].set_text(f"{self.current_params['phi1']:.1f}")
        self.text_elements['a2'].set_text(f"{self.current_params['A2']:.1f}")
        self.text_elements['w2'].set_text(f"{self.current_params['omega2']:.1f}")
        self.text_elements['p2'].set_text(f"{self.current_params['phi2']:.1f}")
        self.text_elements['speed'].set_text(f"{self.current_params['speed']:.1f}x")
        self.text_elements['trail'].set_text(f"{int(self.current_params['trail_length'])}")
        
        # 更新频率比显示
        w2_ratio, w1_ratio, ratio_text = calculate_frequency_ratio(
            self.current_params["omega1"], 
            self.current_params["omega2"]
        )
        self.text_elements['ratio'].set_text(ratio_text)
        
        # 刷新图形
        self.text_elements['a1'].get_figure().canvas.draw_idle()
    
    def reset_params(self):
        """重置参数到初始值"""
        # 重置滑块值
        for slider_key, initial_value in [
            ('a1', INITIAL_PARAMS['A1']), 
            ('w1', INITIAL_PARAMS['omega1']), 
            ('p1', INITIAL_PARAMS['phi1']),
            ('a2', INITIAL_PARAMS['A2']), 
            ('w2', INITIAL_PARAMS['omega2']), 
            ('p2', INITIAL_PARAMS['phi2']),
            ('speed', INITIAL_PARAMS['speed']), 
            ('trail', INITIAL_PARAMS['trail_length'])
        ]:
            self.sliders[slider_key].set_val(initial_value)
        
        # 恢复初始参数
        self.current_params.update(INITIAL_PARAMS)
        # 重新添加ratio_presets，因为它不在INITIAL_PARAMS中
        self.current_params['ratio_presets'] = ratio_presets
    
    def get_current_params(self):
        """获取当前参数值"""
        return self.current_params.copy()
        
    def set_ratio_preset(self, ratio_key):
        """设置频率比预设"""
        self.current_params['ratio_preset'] = ratio_key 