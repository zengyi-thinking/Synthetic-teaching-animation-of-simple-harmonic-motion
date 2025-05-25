# -*- coding: utf-8 -*-
import numpy as np
from config import INITIAL_PARAMS
from wave_calculations import calculate_combined_wave_params

class ParamsController:
    """控制和管理波形参数"""
    
    def __init__(self, sliders, text_elements):
        """初始化参数控制器"""
        self.sliders = sliders
        self.text_elements = text_elements
        self.current_params = INITIAL_PARAMS.copy()
    
    def update_slider_values(self, val=None):
        """更新参数值，计算合成波参数并刷新显示"""
        # 更新参数值
        self.current_params['A1'] = self.sliders['a1'].val
        self.current_params['phi1'] = self.sliders['p1'].val
        self.current_params['A2'] = self.sliders['a2'].val
        self.current_params['phi2'] = self.sliders['p2'].val
        self.current_params['omega'] = self.sliders['omega'].val
        self.current_params['speed'] = self.sliders['speed'].val
        
        # 计算合成波参数
        A, phi, delta_phi = calculate_combined_wave_params(
            self.current_params['A1'], self.current_params['phi1'],
            self.current_params['A2'], self.current_params['phi2']
        )
        
        # 更新显示的值
        self.text_elements['A1'].set_text(f"{self.current_params['A1']:.1f}")
        self.text_elements['p1'].set_text(f"{self.current_params['phi1']:.2f}")
        self.text_elements['A2'].set_text(f"{self.current_params['A2']:.1f}")
        self.text_elements['p2'].set_text(f"{self.current_params['phi2']:.2f}")
        self.text_elements['omega'].set_text(f"{self.current_params['omega']:.1f}")
        self.text_elements['speed'].set_text(f"{self.current_params['speed']:.1f}x")
        
        # 更新合成波参数
        self.text_elements['A'].set_text(f"{A:.1f}")
        self.text_elements['phi'].set_text(f"{phi:.2f}")
        self.text_elements['delta_phi'].set_text(f"{delta_phi:.2f}")
        
        # 更新方程文本
        omega_str = f"{self.current_params['omega']:.1f}"
        self.text_elements['wave1_eq'].set_text(
            f"x1 = {self.current_params['A1']:.1f}*sin({omega_str}t + {self.current_params['phi1']:.2f})"
        )
        self.text_elements['wave2_eq'].set_text(
            f"x2 = {self.current_params['A2']:.1f}*sin({omega_str}t + {self.current_params['phi2']:.2f})"
        )
        self.text_elements['wave3_eq'].set_text(
            f"x = {A:.1f}*sin({omega_str}t + {phi:.2f})"
        )
        
        # 刷新图形
        self.text_elements['A1'].get_figure().canvas.draw_idle()
    
    def reset_params(self):
        """重置参数到初始值"""
        # 重置滑块
        for param_name, slider in self.sliders.items():
            param_key = self._slider_name_to_param_key(param_name)
            if param_key in INITIAL_PARAMS:
                slider.set_val(INITIAL_PARAMS[param_key])
        
        # 更新显示的值
        self.update_slider_values()
    
    def set_phase_difference(self, phase_value):
        """设置相位差，保持相位1不变，调整相位2"""
        # 保持相位1不变，调整相位2
        current_phi1 = self.sliders['p1'].val
        new_phi2 = current_phi1 + phase_value
        
        # 确保相位2在滑块范围内
        if new_phi2 > np.pi:
            new_phi2 = new_phi2 - 2*np.pi
        elif new_phi2 < -np.pi:
            new_phi2 = new_phi2 + 2*np.pi
        
        # 设置相位2滑块的值
        self.sliders['p2'].set_val(new_phi2)
        
        # 更新显示的值
        self.update_slider_values()
        
    def get_current_params(self):
        """获取当前参数值"""
        return self.current_params.copy()
    
    def _slider_name_to_param_key(self, slider_name):
        """将滑块名称转换为参数键名"""
        # 映射滑块名称到参数键
        mapping = {
            'a1': 'A1',
            'p1': 'phi1',
            'a2': 'A2', 
            'p2': 'phi2',
            'omega': 'omega',
            'speed': 'speed'
        }
        return mapping.get(slider_name, slider_name) 