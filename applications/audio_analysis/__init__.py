# -*- coding: utf-8 -*-
"""
音频分析模块 - 简谐运动教学系统扩展
用于演示音频信号的简谐波合成原理
"""

__version__ = "1.0.0"
__author__ = "简谐运动教学系统"

# 导入核心模块
from .audio_processor import AudioProcessor
from .frequency_analyzer import FrequencyAnalyzer
from .audio_player import AudioPlayer

__all__ = [
    'AudioProcessor',
    'FrequencyAnalyzer', 
    'AudioPlayer'
]
