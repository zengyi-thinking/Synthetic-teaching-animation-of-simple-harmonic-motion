# -*- coding: utf-8 -*-
import numpy as np
from config import T

def calculate_wave1(time_offset, A1, omega1, phi1):
    """计算第一个波形"""
    return A1 * np.sin(omega1 * (T - time_offset) + phi1)

def calculate_wave2(time_offset, A2, omega2, phi2):
    """计算第二个波形"""
    return A2 * np.sin(omega2 * (T - time_offset) + phi2)

def calculate_combined_wave(x1, x2):
    """计算合成波"""
    return x1 + x2 