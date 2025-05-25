# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import subprocess

# 如果本地存在ffmpeg，将其添加到系统路径中
if os.path.exists('ffmpeg'):
    os.environ["PATH"] += os.pathsep + os.path.abspath("ffmpeg")

# 检查是否安装了ffmpeg
has_ffmpeg = False
try:
    result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    has_ffmpeg = (result.returncode == 0)
    if has_ffmpeg:
        print("检测到FFmpeg: 支持视频保存")
except FileNotFoundError:
    print("警告: 未检测到FFmpeg，视频保存功能将被禁用")
    has_ffmpeg = False

# 尝试设置更美观的字体 - 优先选择现代无衬线字体
modern_fonts = ['Microsoft YaHei', 'SimHei', 'Segoe UI', 'Arial', 'Helvetica Neue', 'Calibri']
for font in modern_fonts:
    if font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
        plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
        break

# 备用方案 - 使用SimHei支持中文显示
if 'SimHei' not in plt.rcParams['font.sans-serif']:
    plt.rcParams['font.sans-serif'] = ['SimHei'] + plt.rcParams['font.sans-serif']

plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 性能优化设置
plt.rcParams['path.simplify'] = True
plt.rcParams['path.simplify_threshold'] = 1.0
plt.rcParams['agg.path.chunksize'] = 10000

# 定义配色方案 - 现代深色主题
BACKGROUND_COLOR = '#0A1929'  # 深蓝黑色背景
GRID_COLOR = '#1E3A5F'        # 网格线颜色
TEXT_COLOR = '#FFFFFF'        # 纯白色文本
AXIS_COLOR = '#345D8A'        # 坐标轴颜色
PANEL_COLOR = '#152238'       # 控制面板背景

# 波形和轨迹颜色 - 更明亮的颜色
WAVE_X_COLOR = '#4F9BFF'      # X方向波形（更亮的蓝色）
WAVE_Y_COLOR = '#FFB938'      # Y方向波形（更亮的橙黄色）
TRAJECTORY_COLOR = '#2EE59D'  # 李萨如图形轨迹（更亮的青绿色）
POINT_COLOR = '#FF6EB4'       # 移动点颜色（更亮的粉红色）
TRAIL_COLOR = '#B566FF'       # 轨迹颜色（更亮的紫色）

# 滑块颜色
SLIDER_COLOR = '#FFB938'      # 橙黄色
SLIDER_HANDLE_COLOR = '#FFFFFF'
SLIDER_TRACK_COLOR = '#1E293B'

# 按钮颜色
BUTTON_COLOR = '#3877FF'      # 亮蓝色
BUTTON_HOVER_COLOR = '#5C9AFF'
BUTTON_ACTIVE_COLOR = '#82BCFF'
BUTTON_TEXT_COLOR = '#FFFFFF'

# 定义不同区域的颜色，以便更好地视觉区分
SECTION_X_COLOR = '#1A3A6C'     # X参数区域
SECTION_Y_COLOR = '#1A3A6C'     # Y参数区域
SECTION_RATIO_COLOR = '#1A4A4A' # 频率比区域
SECTION_CONTROL_COLOR = '#1A3A6C' # 控制区域
SECTION_HEADER_COLOR = '#345D8A' # 区域标题背景色
BORDER_COLOR = '#345D8A'        # 区域边框颜色

# 预计算常用数据以提高性能
t = np.linspace(0, 10, 500)  # 时间序列
trail_length = 100           # 轨迹长度

# 定义李萨如图形的常用频率比预设
ratio_presets = {
    "1:1": (1.0, 1.0),   # 圆形/椭圆形
    "1:2": (1.0, 2.0),   # 8字形
    "2:3": (2.0, 3.0),   # 三瓣形
    "3:4": (3.0, 4.0),   # 四瓣形
    "3:5": (3.0, 5.0),   # 五瓣形
    "4:5": (4.0, 5.0)    # 复杂形状
}

# 标题和布局设置
TITLE = '李萨如图形 - 垂直简谐运动'
TITLE_FONTSIZE = 24
LEFT_MARGIN = 0.38  # 增加左侧面板宽度，从0.35增加到0.38

# 滑块和按钮尺寸
SLIDER_WIDTH = 0.25  # 增加滑块宽度，从0.23增加到0.25
SLIDER_HEIGHT = 0.015
BUTTON_WIDTH = 0.09
BUTTON_HEIGHT = 0.04
RATIO_BUTTON_WIDTH = 0.07
RATIO_BUTTON_HEIGHT = 0.035
RATIO_MODE_WIDTH = 0.12
RATIO_MODE_HEIGHT = 0.035

# 初始参数值
INITIAL_PARAMS = {
    'A1': 1.0,
    'omega1': 1.0,
    'phi1': 0.0,
    'A2': 1.0,
    'omega2': 2.0, 
    'phi2': 0.0,
    'speed': 1.0,
    'trail_length': trail_length,
    'ratio_mode': 'w2',  # 当频率比改变时，调整哪个频率 ('w1' 或 'w2')
    'ratio_preset': '1:2'  # 当前预设频率比
}

# 字体设置
TITLE_FONT = {'fontsize': 18, 'fontweight': 'bold', 'color': TEXT_COLOR, 
              'family': plt.rcParams['font.sans-serif'][0]}
LABEL_FONT = {'fontsize': 12, 'color': TEXT_COLOR, 'fontweight': 'medium', 
              'family': plt.rcParams['font.sans-serif'][0]}
VALUE_FONT_X = {'fontsize': 12, 'color': WAVE_X_COLOR, 'fontweight': 'bold', 
               'family': plt.rcParams['font.sans-serif'][0]}
VALUE_FONT_Y = {'fontsize': 12, 'color': WAVE_Y_COLOR, 'fontweight': 'bold', 
               'family': plt.rcParams['font.sans-serif'][0]}
SPEED_FONT = {'fontsize': 12, 'color': POINT_COLOR, 'fontweight': 'bold', 
              'family': plt.rcParams['font.sans-serif'][0]}
TRAIL_FONT = {'fontsize': 12, 'color': TRAIL_COLOR, 'fontweight': 'bold',
             'family': plt.rcParams['font.sans-serif'][0]} 