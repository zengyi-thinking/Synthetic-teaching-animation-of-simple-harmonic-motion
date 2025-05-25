# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import subprocess

# 如果本地存在ffmpeg，将其添加到系统路径
if os.path.exists('ffmpeg'):
    os.environ["PATH"] += os.pathsep + os.path.abspath("ffmpeg")

# 检查ffmpeg是否安装
has_ffmpeg = False
try:
    result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    has_ffmpeg = (result.returncode == 0)
    if has_ffmpeg:
        print("检测到FFmpeg: 支持保存视频")
except FileNotFoundError:
    print("警告: 未检测到FFmpeg，视频保存功能将被禁用")
    has_ffmpeg = False

# 设置中文字体 - 更健壮的中文字体设置方法
def set_chinese_font():
    # 中文字体列表，按优先级排序
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Heiti TC', 
                    'SimSun', 'WenQuanYi Micro Hei', 'Heiti TC', 'KaiTi', 'Arial Unicode MS']
    
    # 尝试系统字体
    for font in chinese_fonts:
        if font in [f.name for f in fm.fontManager.ttflist]:
            plt.rcParams['font.sans-serif'] = [font]
            # 重要：设置按钮和文本绘制使用的全局字体
            plt.rcParams['font.family'] = 'sans-serif'
            print(f"已设置中文字体: {font}")
            return True
    
    # 如果没有找到中文字体，尝试使用matplotlib内置字体
    try:
        # 检查是否有SimHei字体文件
        simhei_path = None
        for font_path in fm.findSystemFonts():
            if 'simhei' in font_path.lower() or '黑体' in font_path:
                simhei_path = font_path
                break
        
        if simhei_path:
            font_prop = fm.FontProperties(fname=simhei_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            print(f"已设置中文字体(从文件): {font_prop.get_name()}")
            return True
    except:
        pass
    
    # 如果仍然失败，使用默认字体并显示警告
    print("警告: 未能找到中文字体，中文可能显示为方块")
    return False

# 调用字体设置函数
set_chinese_font()

# 确保负号正确显示
plt.rcParams['axes.unicode_minus'] = False

# 优化渲染性能的设置
plt.rcParams['path.simplify'] = True
plt.rcParams['path.simplify_threshold'] = 1.0
plt.rcParams['agg.path.chunksize'] = 10000

# 定义配色方案
BACKGROUND_COLOR = '#0A1929'  # 深蓝黑色背景
GRID_COLOR = '#1E3A5F'  # 网格线颜色
TEXT_COLOR = '#FFFFFF'  # 白色文本
AXIS_COLOR = '#345D8A'  # 轴线颜色
PANEL_COLOR = '#152238'  # 面板背景色

# 波形颜色
WAVE1_COLOR = '#3B82F6'  # 波形1颜色（明亮的蓝色）
WAVE2_COLOR = '#F59E0B'  # 波形2颜色（橙黄色）
COMBINED_WAVE_COLOR = '#10B981'  # 合成波形颜色（翠绿色）
SPEED_COLOR = '#EC4899'  # 速度控制颜色（亮粉色）

# 滑块颜色
SLIDER_COLOR = '#F59E0B'  # 滑块颜色
SLIDER_HANDLE_COLOR = '#FFFFFF'  # 滑块手柄颜色
SLIDER_TRACK_COLOR = '#1E293B'  # 滑块轨道颜色
SLIDER_AX_COLOR = '#1A3A6C'  # 滑块轴背景色

# 按钮颜色
BUTTON_COLOR = '#2563EB'  # 按钮颜色（亮蓝色）
BUTTON_HOVER_COLOR = '#3B82F6'  # 按钮悬停颜色
BUTTON_ACTIVE_COLOR = '#60A5FA'  # 按钮激活颜色
BUTTON_TEXT_COLOR = '#FFFFFF'  # 按钮文本颜色

# 预先计算常用数据以提高性能
T = np.linspace(0, 20, 500)  # 时间序列

# 布局设置
LEFT_MARGIN = 0.22  # 左侧面板宽度
SLIDER_WIDTH = 0.14  # 滑块宽度
BUTTON_WIDTH = 0.14  # 按钮宽度
BUTTON_HEIGHT = 0.06  # 按钮高度

# 初始参数值
INITIAL_PARAMS = {
    'A1': 0.5,
    'omega1': 5.0,
    'phi1': 0.0,
    'A2': 0.5,
    'omega2': 2.0,
    'phi2': 0.0,
    'speed': 1.0
}

# 字体设置
TITLE_FONT = {'fontsize': 16, 'fontweight': 'bold', 'color': TEXT_COLOR}
LABEL_FONT = {'fontsize': 12, 'color': TEXT_COLOR, 'fontweight': 'medium'}
VALUE_FONT1 = {'fontsize': 12, 'color': WAVE1_COLOR, 'fontweight': 'bold'}
VALUE_FONT2 = {'fontsize': 12, 'color': WAVE2_COLOR, 'fontweight': 'bold'}
VALUE_FONT3 = {'fontsize': 12, 'color': COMBINED_WAVE_COLOR, 'fontweight': 'bold'}
SPEED_FONT = {'fontsize': 12, 'color': SPEED_COLOR, 'fontweight': 'bold'} 