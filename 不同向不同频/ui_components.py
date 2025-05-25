# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
from config import *

def create_figure():
    """创建主图形和布局"""
    # 创建带有深色背景的图形
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10), facecolor=BACKGROUND_COLOR)
    fig.patch.set_alpha(1.0)  # 确保背景完全不透明

    # 添加标题
    fig.suptitle(TITLE, fontsize=TITLE_FONTSIZE, fontweight='bold', color=TEXT_COLOR, y=0.98, 
                family=plt.rcParams['font.sans-serif'][0])

    # 创建布局网格 - 增加间距
    gs = GridSpec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1], hspace=0.35, wspace=0.35)

    # 创建主绘图区域
    ax_x = fig.add_subplot(gs[0, 1:])                # X方向振动图
    ax_y = fig.add_subplot(gs[1:, 1])                # Y方向振动图
    ax_lissajous = fig.add_subplot(gs[1:, 2])        # 李萨如图形

    # 配置绘图区域外观
    for ax in [ax_x, ax_y, ax_lissajous]:
        ax.set_facecolor(BACKGROUND_COLOR)
        ax.grid(True, color=GRID_COLOR, linestyle='-', alpha=0.6, linewidth=0.6)
        ax.tick_params(axis='both', colors=TEXT_COLOR, direction='out', length=6, width=1, labelsize=10)
        
        # 添加次要网格线
        ax.grid(which='minor', color=GRID_COLOR, linestyle='-', alpha=0.3, linewidth=0.3)
        ax.xaxis.set_minor_locator(plt.MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.5))
        
        # 设置坐标轴颜色
        for spine in ax.spines.values():
            spine.set_color(AXIS_COLOR)
            spine.set_linewidth(2.0)

    # 配置X方向振动图
    ax_x.set_xlim(0, 10)
    ax_x.set_ylim(-1.2, 1.2)
    ax_x.set_ylabel('X振幅', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                family=plt.rcParams['font.sans-serif'][0])
    ax_x.set_xlabel('t (s)', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                family=plt.rcParams['font.sans-serif'][0])

    # 配置Y方向振动图
    ax_y.set_xlim(-1.2, 1.2)
    ax_y.set_ylim(0, 10)
    ax_y.set_xlabel('Y振幅', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                family=plt.rcParams['font.sans-serif'][0])
    ax_y.set_ylabel('t (s)', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                family=plt.rcParams['font.sans-serif'][0])

    # 配置李萨如图形
    ax_lissajous.set_xlim(-1.2, 1.2)
    ax_lissajous.set_ylim(-1.2, 1.2)
    ax_lissajous.set_xlabel('X振幅', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                        family=plt.rcParams['font.sans-serif'][0])
    ax_lissajous.set_ylabel('Y振幅', color=TEXT_COLOR, fontsize=14, fontweight='bold',
                        family=plt.rcParams['font.sans-serif'][0])
    ax_lissajous.set_aspect('equal')  # 确保图形为正方形，保持X和Y比例相同

    # 调整图形边距 - 更新左侧边距，增加顶部和底部边距
    plt.subplots_adjust(top=0.92, bottom=0.09, left=LEFT_MARGIN, right=0.98)

    return fig, ax_x, ax_y, ax_lissajous

def create_section_panel(fig, y_pos, height, title, color=SECTION_X_COLOR):
    """创建带有标题的面板区域"""
    # 主面板和标题栏
    panel_height = height - 0.03  # 预留标题栏空间
    main_panel = FancyBboxPatch((0.01, y_pos), LEFT_MARGIN - 0.025, panel_height, 
                      transform=fig.transFigure, facecolor=color, 
                      edgecolor=BORDER_COLOR, linewidth=2.0, alpha=0.95, zorder=-1,
                      boxstyle="round,pad=0.03,rounding_size=0.02")
    
    # 标题栏，使用不同颜色
    header = FancyBboxPatch((0.01, y_pos + panel_height), LEFT_MARGIN - 0.025, 0.03, 
                     transform=fig.transFigure, facecolor=SECTION_HEADER_COLOR, 
                     edgecolor=BORDER_COLOR, linewidth=2.0, alpha=0.95, zorder=-1,
                     boxstyle="round,pad=0.01,rounding_size=0.02")
    
    # 添加标题文本
    title_text = fig.text(LEFT_MARGIN/2, y_pos + panel_height + 0.015, title, 
                  ha='center', va='center', fontsize=12, fontweight='bold', color=TEXT_COLOR)
    
    return [main_panel, header, title_text]

def create_ui_panels(fig):
    """创建所有UI面板区域"""
    panel_elements = []
    panel_elements.extend(create_section_panel(fig, 0.82, 0.16, "X方向参数", SECTION_X_COLOR))
    panel_elements.extend(create_section_panel(fig, 0.62, 0.16, "Y方向参数", SECTION_Y_COLOR))
    panel_elements.extend(create_section_panel(fig, 0.36, 0.22, "频率比控制", SECTION_RATIO_COLOR))
    panel_elements.extend(create_section_panel(fig, 0.09, 0.25, "播放控制", SECTION_CONTROL_COLOR))

    fig.patches.extend(panel_elements[:8])  # 仅添加面板图形，不添加文本元素
    return panel_elements

def create_equation_box(ax, y_pos, equation, color):
    """创建公式显示框"""
    props = dict(boxstyle='round,pad=0.6', facecolor='#1A3A6C', alpha=0.8, edgecolor=color, linewidth=1.5)
    ax.text(0.98, y_pos, equation, transform=ax.transAxes, fontsize=13,
            verticalalignment='top', horizontalalignment='right',
            bbox=props, color=color, fontweight='bold', 
            family=plt.rcParams['font.sans-serif'][0])

def add_equation_boxes(ax_x, ax_y, ax_lissajous):
    """添加公式说明框"""
    create_equation_box(ax_x, 0.9, "x = A1*sin(w1*t + p1)", WAVE_X_COLOR)
    create_equation_box(ax_y, 0.9, "y = A2*sin(w2*t + p2)", WAVE_Y_COLOR)
    create_equation_box(ax_lissajous, 0.9, "李萨如图形", TRAJECTORY_COLOR)

def create_parameter_displays(fig):
    """创建参数显示文本"""
    # X方向参数显示 - 调整位置和对齐方式
    wave_x_eq_text = fig.text(0.19, 0.95, 'x = A1*sin(w1*t + p1)', ha='center', **VALUE_FONT_X)
    fig.text(0.08, 0.90, 'A1:', ha='left', **LABEL_FONT)
    fig.text(0.08, 0.86, 'w1:', ha='left', **LABEL_FONT)
    fig.text(0.08, 0.82, 'p1:', ha='left', **LABEL_FONT)

    # X方向参数值 - 增加右侧间距
    text_a1 = fig.text(0.32, 0.90, "1.0", ha='right', **VALUE_FONT_X)
    text_w1 = fig.text(0.32, 0.86, "1.0", ha='right', **VALUE_FONT_X)
    text_p1 = fig.text(0.32, 0.82, "0.0", ha='right', **VALUE_FONT_X)

    # Y方向参数显示 - 调整位置
    wave_y_eq_text = fig.text(0.19, 0.75, 'y = A2*sin(w2*t + p2)', ha='center', **VALUE_FONT_Y)
    fig.text(0.08, 0.70, 'A2:', ha='left', **LABEL_FONT)
    fig.text(0.08, 0.66, 'w2:', ha='left', **LABEL_FONT)
    fig.text(0.08, 0.62, 'p2:', ha='left', **LABEL_FONT)

    # Y方向参数值 - 增加右侧间距
    text_a2 = fig.text(0.32, 0.70, "1.0", ha='right', **VALUE_FONT_Y)
    text_w2 = fig.text(0.32, 0.66, "2.0", ha='right', **VALUE_FONT_Y) 
    text_p2 = fig.text(0.32, 0.62, "0.0", ha='right', **VALUE_FONT_Y)

    # 频率比显示 - 调整位置
    ratio_text = fig.text(0.19, 0.55, 'w2:w1 = 2:1', ha='center', color=TRAJECTORY_COLOR, 
                        fontsize=13, fontweight='bold', family=plt.rcParams['font.sans-serif'][0])

    # 速度和轨迹长度控制 - 增加垂直间距
    fig.text(0.08, 0.25, '速度:', ha='left', **LABEL_FONT)
    text_speed = fig.text(0.32, 0.25, "1.0x", ha='right', **SPEED_FONT)

    fig.text(0.08, 0.21, '轨迹长度:', ha='left', **LABEL_FONT)
    text_trail = fig.text(0.32, 0.21, f"{trail_length}", ha='right', **TRAIL_FONT)

    # 滑块标签 - 调整透明度和位置
    # X滑块标签 - 使用半透明背景
    for pos_y, label in [(0.88, "最小"), (0.84, "最小"), (0.80, "0")]:
        text = fig.text(0.08, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='left', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))
        
    for pos_y, label in [(0.88, "最大"), (0.84, "最大"), (0.80, "2π")]:
        text = fig.text(0.33, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='right', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))

    # Y滑块标签 - 使用半透明背景
    for pos_y, label in [(0.68, "最小"), (0.64, "最小"), (0.60, "0")]:
        text = fig.text(0.08, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='left', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))
        
    for pos_y, label in [(0.68, "最大"), (0.64, "最大"), (0.60, "2π")]:
        text = fig.text(0.33, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='right', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))

    # 控制滑块标签 - 使用半透明背景
    for pos_y, label in [(0.23, "慢"), (0.19, "短")]:
        text = fig.text(0.08, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='left', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))
        
    for pos_y, label in [(0.23, "快"), (0.19, "长")]:
        text = fig.text(0.33, pos_y, label, fontsize=8, color=TEXT_COLOR, ha='right', va='bottom', alpha=0.7)
        text.set_bbox(dict(facecolor=BACKGROUND_COLOR, alpha=0.5, edgecolor='none', pad=1))

    return {
        'wave_x_eq': wave_x_eq_text,
        'wave_y_eq': wave_y_eq_text,
        'ratio': ratio_text,
        'a1': text_a1,
        'w1': text_w1,
        'p1': text_p1,
        'a2': text_a2,
        'w2': text_w2,
        'p2': text_p2,
        'speed': text_speed,
        'trail': text_trail
    }

def create_sliders(fig):
    """创建所有滑块控件"""
    # X参数滑块 - 调整位置和宽度
    a1_slider_ax = fig.add_axes([0.08, 0.88, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)
    w1_slider_ax = fig.add_axes([0.08, 0.84, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)
    p1_slider_ax = fig.add_axes([0.08, 0.80, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)

    # Y参数滑块 - 调整位置和宽度
    a2_slider_ax = fig.add_axes([0.08, 0.68, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)
    w2_slider_ax = fig.add_axes([0.08, 0.64, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)
    p2_slider_ax = fig.add_axes([0.08, 0.60, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)

    # 速度和轨迹滑块 - 调整位置和垂直间距
    speed_slider_ax = fig.add_axes([0.08, 0.23, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)
    trail_slider_ax = fig.add_axes([0.08, 0.19, SLIDER_WIDTH, SLIDER_HEIGHT], facecolor=SLIDER_TRACK_COLOR)

    # 滑块样式
    slider_props = {
        'color': SLIDER_COLOR,
        'valstep': None,
        'initcolor': 'none',
        'handle_style': {'facecolor': SLIDER_HANDLE_COLOR, 'edgecolor': WAVE_X_COLOR, 'size': 14}
    }

    # 速度滑块样式
    speed_slider_props = {
        'color': POINT_COLOR,
        'valstep': None,
        'initcolor': 'none',
        'handle_style': {'facecolor': SLIDER_HANDLE_COLOR, 'edgecolor': POINT_COLOR, 'size': 14}
    }

    # 轨迹长度滑块样式
    trail_slider_props = {
        'color': TRAIL_COLOR,
        'valstep': 1,  # 轨迹长度为整数
        'initcolor': 'none',
        'handle_style': {'facecolor': SLIDER_HANDLE_COLOR, 'edgecolor': TRAIL_COLOR, 'size': 14}
    }

    # 创建滑块
    a1_slider = Slider(a1_slider_ax, '', 0.1, 1.0, valinit=INITIAL_PARAMS['A1'], **slider_props)
    w1_slider = Slider(w1_slider_ax, '', 0.1, 5.0, valinit=INITIAL_PARAMS['omega1'], **slider_props)
    p1_slider = Slider(p1_slider_ax, '', 0, 2*np.pi, valinit=INITIAL_PARAMS['phi1'], **slider_props)

    a2_slider = Slider(a2_slider_ax, '', 0.1, 1.0, valinit=INITIAL_PARAMS['A2'], **slider_props)
    w2_slider = Slider(w2_slider_ax, '', 0.1, 5.0, valinit=INITIAL_PARAMS['omega2'], **slider_props)
    p2_slider = Slider(p2_slider_ax, '', 0, 2*np.pi, valinit=INITIAL_PARAMS['phi2'], **slider_props)

    # 创建速度控制滑块
    speed_slider = Slider(speed_slider_ax, '', 0.1, 3.0, valinit=INITIAL_PARAMS['speed'], **speed_slider_props)

    # 创建轨迹长度控制滑块
    trail_slider = Slider(trail_slider_ax, '', 10, 200, valinit=INITIAL_PARAMS['trail_length'], **trail_slider_props)

    # 自定义滑块外观
    for slider in [a1_slider, w1_slider, p1_slider, a2_slider, w2_slider, p2_slider, speed_slider, trail_slider]:
        slider.valtext.set_visible(False)  # 使用自定义值显示
        slider.label.set_visible(False)

    return {
        'a1': a1_slider,
        'w1': w1_slider,
        'p1': p1_slider,
        'a2': a2_slider,
        'w2': w2_slider,
        'p2': p2_slider,
        'speed': speed_slider,
        'trail': trail_slider
    }

def create_buttons(fig):
    """创建所有按钮控件"""
    button_props = {
        'color': BUTTON_COLOR,
        'hovercolor': BUTTON_HOVER_COLOR
    }

    # 播放控制按钮 - 增加间距和位置调整
    play_button_ax = fig.add_axes([0.05, 0.12, BUTTON_WIDTH, BUTTON_HEIGHT])
    pause_button_ax = fig.add_axes([0.17, 0.12, BUTTON_WIDTH, BUTTON_HEIGHT])
    reset_button_ax = fig.add_axes([0.29, 0.12, BUTTON_WIDTH, BUTTON_HEIGHT])

    play_button = Button(play_button_ax, '播放', **button_props)
    pause_button = Button(pause_button_ax, '暂停', **button_props)
    reset_button = Button(reset_button_ax, '重置', **button_props)

    # 创建频率比预设按钮 - 优化网格布局和间距
    ratio_button_width = RATIO_BUTTON_WIDTH
    ratio_button_height = RATIO_BUTTON_HEIGHT
    button_margin = 0.018  # 增加按钮间距
    ratio_buttons = []
    ratio_button_axes = []

    # 创建频率比预设按钮，采用3x2网格布局，增加水平和垂直间距
    for i, ratio in enumerate(ratio_presets.keys()):
        row = i // 3
        col = i % 3
        x_pos = 0.06 + col * (ratio_button_width + button_margin)
        y_pos = 0.51 - row * (ratio_button_height + button_margin)
        
        ratio_button_ax = fig.add_axes([x_pos, y_pos, ratio_button_width, ratio_button_height])
        ratio_button_axes.append(ratio_button_ax)
        
        button = Button(ratio_button_ax, ratio, 
                      color=TRAJECTORY_COLOR if ratio == INITIAL_PARAMS['ratio_preset'] else '#1E293B',
                      hovercolor=BUTTON_HOVER_COLOR)
        ratio_buttons.append(button)

    # 添加频率比模式切换按钮 - 调整位置增加间距
    w1_fixed_ax = fig.add_axes([0.07, 0.42, RATIO_MODE_WIDTH, RATIO_MODE_HEIGHT])
    w2_fixed_ax = fig.add_axes([0.21, 0.42, RATIO_MODE_WIDTH, RATIO_MODE_HEIGHT])

    w1_fixed_button = Button(w1_fixed_ax, '固定w1', 
                            color='#1E293B' if INITIAL_PARAMS['ratio_mode'] == 'w2' else TRAJECTORY_COLOR, 
                            hovercolor=BUTTON_HOVER_COLOR)
    w2_fixed_button = Button(w2_fixed_ax, '固定w2', 
                            color=TRAJECTORY_COLOR if INITIAL_PARAMS['ratio_mode'] == 'w2' else '#1E293B', 
                            hovercolor=BUTTON_HOVER_COLOR)

    # 增强按钮样式
    for button in [play_button, pause_button, reset_button, w1_fixed_button, w2_fixed_button] + ratio_buttons:
        button.label.set_color(BUTTON_TEXT_COLOR)
        button.label.set_fontweight('bold')
        button.label.set_fontsize(11 if button in ratio_buttons else 12)
        button.label.set_family(plt.rcParams['font.sans-serif'][0])

    return {
        'play': play_button,
        'pause': pause_button,
        'reset': reset_button,
        'ratio_buttons': ratio_buttons,
        'ratio_button_axes': ratio_button_axes,
        'w1_fixed': w1_fixed_button,
        'w2_fixed': w2_fixed_button,
        'w1_fixed_ax': w1_fixed_ax,
        'w2_fixed_ax': w2_fixed_ax
    }

def create_plot_elements(ax_x, ax_y, ax_lissajous):
    """创建波形和轨迹图形元素"""
    line_x, = ax_x.plot([], [], color=WAVE_X_COLOR, lw=3.0, animated=True)
    line_y, = ax_y.plot([], [], color=WAVE_Y_COLOR, lw=3.0, animated=True, alpha=0.85)
    line_lissajous, = ax_lissajous.plot([], [], color=TRAJECTORY_COLOR, lw=1.8, animated=True)
    point, = ax_lissajous.plot([], [], 'o', color=POINT_COLOR, ms=10, animated=True)
    trail, = ax_lissajous.plot([], [], '-', color=TRAIL_COLOR, lw=1.8, alpha=0.75, animated=True)

    return line_x, line_y, line_lissajous, point, trail 