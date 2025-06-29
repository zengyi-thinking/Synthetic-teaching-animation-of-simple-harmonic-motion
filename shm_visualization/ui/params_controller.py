# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 参数控制器
管理和更新简谐运动动画的参数
"""

from PyQt6.QtCore import QObject, pyqtSignal
from ui.ui_framework import INITIAL_PARAMS, RATIO_PRESETS


class ParamsController(QObject):
    """参数控制器，管理和更新动画参数"""
    
    # 参数更新信号
    params_changed = pyqtSignal()
    ratio_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 复制初始参数
        self.params = INITIAL_PARAMS.copy()
        # 添加频率比预设
        self.params['ratio_presets'] = RATIO_PRESETS
    
    def get_params(self):
        """获取当前参数的副本"""
        return self.params.copy()
    
    def set_param(self, name, value):
        """设置单个参数的值"""
        if name in self.params:
            self.params[name] = value
            self.params_changed.emit()
    
    def reset_params(self):
        """重置所有参数到初始值"""
        self.params = INITIAL_PARAMS.copy()
        self.params['ratio_presets'] = RATIO_PRESETS
        self.params_changed.emit()
    
    def update_from_control_panel(self, control_panel):
        """从控制面板更新所有参数"""
        # 获取所有滑块值
        self.params['A1'] = control_panel.a1_slider.get_value()
        self.params['omega1'] = control_panel.w1_slider.get_value()
        self.params['phi1'] = control_panel.p1_slider.get_value()
        self.params['A2'] = control_panel.a2_slider.get_value()
        self.params['omega2'] = control_panel.w2_slider.get_value()
        self.params['phi2'] = control_panel.p2_slider.get_value()
        self.params['speed'] = control_panel.speed_slider.get_value()
        self.params['trail_length'] = int(control_panel.trail_slider.get_value())
        
        self.params_changed.emit()
    
    def update_ui_from_params(self, control_panel):
        """根据当前参数更新UI控件"""
        # 更新所有滑块
        control_panel.a1_slider.set_value(self.params['A1'])
        control_panel.w1_slider.set_value(self.params['omega1'])
        control_panel.p1_slider.set_value(self.params['phi1'])
        control_panel.a2_slider.set_value(self.params['A2'])
        control_panel.w2_slider.set_value(self.params['omega2'])
        control_panel.p2_slider.set_value(self.params['phi2'])
        control_panel.speed_slider.set_value(self.params['speed'])
        control_panel.trail_slider.set_value(self.params['trail_length'])
    
    def set_ratio_mode(self, mode):
        """设置频率比模式"""
        if mode in ['w1', 'w2']:
            self.params['ratio_mode'] = mode
            self.params_changed.emit()
    
    def set_ratio_preset(self, ratio_key):
        """设置频率比预设"""
        if ratio_key in self.params['ratio_presets']:
            self.params['ratio_preset'] = ratio_key
            self.ratio_changed.emit(ratio_key) 