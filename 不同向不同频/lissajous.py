# -*- coding: utf-8 -*-
import numpy as np
from config import t

def calculate_wave_x(t_offset, A1, omega1, phi1):
    """计算X方向波形"""
    return A1 * np.sin(omega1 * (t - t_offset) + phi1)

def calculate_wave_y(t_offset, A2, omega2, phi2):
    """计算Y方向波形"""
    return A2 * np.sin(omega2 * (t - t_offset) + phi2)

def calculate_current_position(t_offset, A1, omega1, phi1, A2, omega2, phi2):
    """计算当前点位置"""
    current_x = A1 * np.sin(omega1 * (-t_offset) + phi1)
    current_y = A2 * np.sin(omega2 * (-t_offset) + phi2)
    return current_x, current_y

def calculate_lissajous_figure(A1, omega1, phi1, A2, omega2, phi2):
    """计算完整的李萨如图形"""
    # 根据频率比计算周期
    omega1_int = int(omega1*100)
    omega2_int = int(omega2*100)
    gcd_val = np.gcd(omega1_int, omega2_int)
    period = 2*np.pi * (omega1_int // gcd_val) / omega1
    
    # 计算轨迹
    full_t = np.linspace(0, period, 1000)
    x_full = A1 * np.sin(omega1 * full_t + phi1)
    y_full = A2 * np.sin(omega2 * full_t + phi2)
    
    return x_full, y_full, period

def calculate_frequency_ratio(omega1, omega2):
    """计算并格式化频率比"""
    # 计算最大公约数
    omega1_int = int(omega1*100)
    omega2_int = int(omega2*100)
    gcd_val = np.gcd(omega1_int, omega2_int)
    w1_ratio = omega1_int // gcd_val
    w2_ratio = omega2_int // gcd_val
    
    return w2_ratio, w1_ratio, f'w2:w1 = {w2_ratio}:{w1_ratio}'

def adjust_frequency_for_ratio(ratio_preset, current_omega1, current_omega2, ratio_mode):
    """根据选择的频率比调整频率"""
    w1_val, w2_val = ratio_preset
    
    if ratio_mode == 'w1':
        # 固定w2，调整w1
        new_w1 = current_omega2 * (w1_val / w2_val)
        new_w2 = current_omega2
        # 确保在有效范围内
        new_w1 = max(0.1, min(5.0, new_w1))
    else:
        # 固定w1，调整w2
        new_w1 = current_omega1
        new_w2 = current_omega1 * (w2_val / w1_val)
        # 确保在有效范围内
        new_w2 = max(0.1, min(5.0, new_w2))
        
    return new_w1, new_w2 