# -*- coding: utf-8 -*-
import numpy as np
from config import TIME

def calculate_wave_x1(time_offset, A1, omega, phi1):
    """计算第一个波形"""
    return A1 * np.sin(omega * (TIME - time_offset) + phi1)

def calculate_wave_x2(time_offset, A2, omega, phi2):
    """计算第二个波形"""
    return A2 * np.sin(omega * (TIME - time_offset) + phi2)

def calculate_combined_wave(x1, x2):
    """计算合成波"""
    return x1 + x2

def calculate_combined_wave_params(A1, phi1, A2, phi2):
    """计算合成波的振幅和相位"""
    # 同向同频简谐运动合成公式
    # x = A1*sin(ωt + φ1) + A2*sin(ωt + φ2) = A*sin(ωt + φ)
    
    # 计算相位差
    delta_phi = phi2 - phi1
    
    # 使用合成公式计算
    A_squared = A1**2 + A2**2 + 2*A1*A2*np.cos(delta_phi)
    A = np.sqrt(A_squared)
    
    # 计算合成相位
    if A == 0:  # 避免除以零
        phi = 0
    else:
        phi = np.arctan2(A1*np.sin(phi1) + A2*np.sin(phi2), A1*np.cos(phi1) + A2*np.cos(phi2))
    
    return A, phi, delta_phi 