# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator

from config import (
    BACKGROUND_COLOR, GRID_COLOR, TEXT_COLOR, AXIS_COLOR, PANEL_COLOR,
    WAVE1_COLOR, WAVE2_COLOR, COMBINED_WAVE_COLOR, SPEED_COLOR,
    SLIDER_COLOR, SLIDER_HANDLE_COLOR, SLIDER_TRACK_COLOR, SLIDER_AX_COLOR,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, BUTTON_ACTIVE_COLOR,
    LEFT_MARGIN, SLIDER_WIDTH, BUTTON_WIDTH, BUTTON_HEIGHT,
    TITLE_FONT, LABEL_FONT, VALUE_FONT1, VALUE_FONT2, VALUE_FONT3, SPEED_FONT,
    INITIAL_PARAMS
)

def create_figure():
    """创建主图形和坐标轴"""
    # 创建带有深色背景的图形
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 9), facecolor=BACKGROUND_COLOR)
    fig.patch.set_alpha(1.0)  # 确保背景完全不透明
    
    # 为图形添加标题
    fig.suptitle('简谐运动合成', fontsize=24, fontweight='bold', color=TEXT_COLOR, y=0.98)
    
    # 创建布局，清晰区分控制区和绘图区
    grid_layout = GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.15)
    
    # 创建主绘图轴，左侧为控制区留出更多空间
    ax1 = fig.add_subplot(grid_layout[0])
    ax2 = fig.add_subplot(grid_layout[1])
    ax3 = fig.add_subplot(grid_layout[2])
    
    # 配置绘图轴的外观
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(BACKGROUND_COLOR)
        ax.set_xlim(0, 20)
        ax.set_ylim(-1.2, 1.2)
        ax.grid(True, color=GRID_COLOR, linestyle='-', alpha=0.5, linewidth=0.5)
        ax.tick_params(axis='y', colors=TEXT_COLOR, direction='out', length=6, width=1, labelsize=10)
        ax.tick_params(axis='x', colors=TEXT_COLOR, direction='out', length=6, width=1, labelsize=10)
    
        # 添加次要网格线以提高可读性
        ax.grid(which='minor', color=GRID_COLOR, linestyle='-', alpha=0.2, linewidth=0.25)
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    
        # 仅在底部绘图显示x轴标签
        if ax != ax3:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel('时间 (秒)', color=TEXT_COLOR, fontsize=12, fontweight='medium')
    
        # 设置轴线颜色
        for spine in ax.spines.values():
            spine.set_color(AXIS_COLOR)
            spine.set_linewidth(1.5)
    
        # 添加Y轴标签
        ax.set_ylabel('振幅', color=TEXT_COLOR, fontsize=12, fontweight='medium')
    
    # 调整图形边距以适应控制面板
    plt.subplots_adjust(top=0.92, bottom=0.08, left=LEFT_MARGIN, right=0.98)
    
    # 创建控制面板背景
    create_control_panels(fig)
    
    return fig, ax1, ax2, ax3

def create_control_panels(fig):
    """创建左侧控制面板背景，带有圆角和微妙阴影"""
    # 通过叠加多个矩形实现渐变效果
    def create_panel(y_pos, height, transparency=0.9):
        # 主面板 - 使用FancyBboxPatch创建圆角面板
        rect = FancyBboxPatch(
            (0.005, y_pos), LEFT_MARGIN - 0.02, height,
            transform=fig.transFigure, facecolor=PANEL_COLOR,
            edgecolor=AXIS_COLOR, linewidth=1, alpha=transparency, zorder=-1,
            boxstyle="round,pad=0.01,rounding_size=0.02"
        )
    
        # 顶部高亮（渐变效果）
        highlight_rect = plt.Rectangle(
            (0.005, y_pos + height - 0.02), LEFT_MARGIN - 0.02, 0.02,
            transform=fig.transFigure, facecolor='#1A3A6C',
            edgecolor=None, alpha=0.4, zorder=-0.9
        )
    
        # 底部阴影
        shadow_rect = plt.Rectangle(
            (0.005, y_pos), LEFT_MARGIN - 0.02, 0.02,
            transform=fig.transFigure, facecolor='#050A14',
            edgecolor=None, alpha=0.4, zorder=-0.9
        )
    
        return [rect, highlight_rect, shadow_rect]
    
    # 创建三个带有阴影效果的面板
    panel_elements = []
    panel_elements.extend(create_panel(0.67, 0.31))  # 波形1区域
    panel_elements.extend(create_panel(0.34, 0.33))  # 波形2区域
    panel_elements.extend(create_panel(0.01, 0.33))  # 合成波形和速度控制区域
    
    fig.patches.extend(panel_elements)

def create_equation_boxes(axes):
    """创建方程式说明框"""
    ax1, ax2, ax3 = axes
    
    def create_equation_box(ax, y_pos, equation, color):
        # 创建文本方框背景
        box_props = dict(boxstyle='round,pad=0.5', facecolor='#1A3A6C', alpha=0.7, edgecolor=color)
        # 在右上角添加方程文本
        ax.text(0.98, y_pos, equation, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', horizontalalignment='right',
                bbox=box_props, color=color, fontweight='bold')
    
    # 为每个波形图添加方程式说明
    create_equation_box(ax1, 0.9, "x1 = A1*sin(w1*t + p1)", WAVE1_COLOR)
    create_equation_box(ax2, 0.9, "x2 = A2*sin(w2*t + p2)", WAVE2_COLOR)
    create_equation_box(ax3, 0.9, "x = x1 + x2", COMBINED_WAVE_COLOR)

def create_plot_elements(axes):
    """创建绘图元素"""
    ax1, ax2, ax3 = axes
    
    # 初始化波形绘图
    line1, = ax1.plot([], [], color=WAVE1_COLOR, lw=2.5, animated=True)
    line2, = ax2.plot([], [], color=WAVE2_COLOR, lw=2.5, animated=True)
    line3, = ax3.plot([], [], color=COMBINED_WAVE_COLOR, lw=2.5, animated=True)
    
    return line1, line2, line3

def create_text_displays(fig):
    """创建参数显示文本"""
    # 波形1方程式和标签 - 增加垂直间距
    wave1_equation_text = fig.text(0.11, 0.96, 'x1 = A1*sin(w1*t + p1)', ha='center', **VALUE_FONT1)
    fig.text(0.11, 0.92, '波形1', ha='center', **TITLE_FONT)
    fig.text(0.04, 0.87, '振幅1:', **LABEL_FONT)
    fig.text(0.04, 0.80, '频率1:', **LABEL_FONT)
    fig.text(0.04, 0.73, '相位1:', **LABEL_FONT)
    
    # 波形1的值
    text_A1 = fig.text(0.16, 0.87, f"{INITIAL_PARAMS['A1']:.1f}", **VALUE_FONT1)
    text_w1 = fig.text(0.16, 0.80, f"{INITIAL_PARAMS['omega1']:.1f}", **VALUE_FONT1)
    text_p1 = fig.text(0.16, 0.73, f"{INITIAL_PARAMS['phi1']:.1f}", **VALUE_FONT1)
    
    # 波形2方程式和标签
    wave2_equation_text = fig.text(0.11, 0.62, 'x2 = A2*sin(w2*t + p2)', ha='center', **VALUE_FONT2)
    fig.text(0.11, 0.58, '波形2', ha='center', **TITLE_FONT)
    fig.text(0.04, 0.53, '振幅2:', **LABEL_FONT)
    fig.text(0.04, 0.46, '频率2:', **LABEL_FONT)
    fig.text(0.04, 0.39, '相位2:', **LABEL_FONT)
    
    # 波形2的值
    text_A2 = fig.text(0.16, 0.53, f"{INITIAL_PARAMS['A2']:.1f}", **VALUE_FONT2)
    text_w2 = fig.text(0.16, 0.46, f"{INITIAL_PARAMS['omega2']:.1f}", **VALUE_FONT2)
    text_p2 = fig.text(0.16, 0.39, f"{INITIAL_PARAMS['phi2']:.1f}", **VALUE_FONT2)
    
    # 合成波形方程式
    wave3_equation_text = fig.text(0.11, 0.29, 'x = x1 + x2', ha='center', **VALUE_FONT3)
    fig.text(0.11, 0.25, '合成波形', ha='center', **TITLE_FONT)
    
    # 添加速度控制标签
    fig.text(0.11, 0.20, '速度控制', ha='center', color=SPEED_COLOR, fontsize=14, fontweight='bold')
    text_speed = fig.text(0.16, 0.15, f"{INITIAL_PARAMS['speed']:.1f}x", **SPEED_FONT)
    fig.text(0.04, 0.15, '速度:', **LABEL_FONT)
    
    # 添加滑块最大/最小值标签 - 调整位置以避免重叠
    fig.text(0.03, 0.85, "最小值", fontsize=8, color=TEXT_COLOR, ha='left', va='center')
    fig.text(0.19, 0.85, "最大值", fontsize=8, color=TEXT_COLOR, ha='right', va='center')
    fig.text(0.03, 0.51, "最小值", fontsize=8, color=TEXT_COLOR, ha='left', va='center')
    fig.text(0.19, 0.51, "最大值", fontsize=8, color=TEXT_COLOR, ha='right', va='center')
    fig.text(0.03, 0.13, "慢", fontsize=8, color=TEXT_COLOR, ha='left', va='center')
    fig.text(0.19, 0.13, "快", fontsize=8, color=TEXT_COLOR, ha='right', va='center')
    
    # 返回需要更新的文本对象
    text_elements = {
        'wave1_eq': wave1_equation_text,
        'wave2_eq': wave2_equation_text,
        'wave3_eq': wave3_equation_text,
        'A1': text_A1,
        'w1': text_w1,
        'p1': text_p1,
        'A2': text_A2,
        'w2': text_w2,
        'p2': text_p2,
        'speed': text_speed
    }
    
    return text_elements

def create_sliders(fig):
    """创建滑块控件"""
    # 滑块属性
    slider_props = {
        'color': SLIDER_COLOR,
        'valstep': None,
        'initcolor': 'none',
        'handle_style': {'facecolor': SLIDER_HANDLE_COLOR, 'edgecolor': None, 'size': 12}
    }
    
    # 速度滑块的样式
    speed_slider_props = {
        'color': SPEED_COLOR,
        'valstep': None,
        'initcolor': 'none', 
        'handle_style': {'facecolor': SLIDER_HANDLE_COLOR, 'edgecolor': None, 'size': 12}
    }
    
    # 创建波形1滑块
    A1_slider_ax = plt.axes([0.05, 0.85, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    A1_slider = Slider(A1_slider_ax, '', 0.1, 1.0, valinit=INITIAL_PARAMS['A1'], **slider_props)
    
    w1_slider_ax = plt.axes([0.05, 0.78, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    w1_slider = Slider(w1_slider_ax, '', 0.5, 10.0, valinit=INITIAL_PARAMS['omega1'], **slider_props)
    
    p1_slider_ax = plt.axes([0.05, 0.71, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    p1_slider = Slider(p1_slider_ax, '', 0, 2*np.pi, valinit=INITIAL_PARAMS['phi1'], **slider_props)
    
    # 创建波形2滑块
    A2_slider_ax = plt.axes([0.05, 0.51, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    A2_slider = Slider(A2_slider_ax, '', 0.1, 1.0, valinit=INITIAL_PARAMS['A2'], **slider_props)
    
    w2_slider_ax = plt.axes([0.05, 0.44, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    w2_slider = Slider(w2_slider_ax, '', 0.5, 10.0, valinit=INITIAL_PARAMS['omega2'], **slider_props)
    
    p2_slider_ax = plt.axes([0.05, 0.37, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    p2_slider = Slider(p2_slider_ax, '', 0, 2*np.pi, valinit=INITIAL_PARAMS['phi2'], **slider_props)
    
    # 创建速度控制滑块
    speed_slider_ax = plt.axes([0.05, 0.13, SLIDER_WIDTH, 0.02], facecolor=SLIDER_TRACK_COLOR)
    speed_slider = Slider(speed_slider_ax, '', 0.1, 3.0, valinit=INITIAL_PARAMS['speed'], **speed_slider_props)
    
    # 隐藏滑块默认的值显示
    for slider in [A1_slider, w1_slider, p1_slider, A2_slider, w2_slider, p2_slider, speed_slider]:
        slider.valtext.set_visible(False)
        slider.label.set_visible(False)
    
    # 返回滑块字典
    sliders = {
        'A1': A1_slider,
        'w1': w1_slider,
        'p1': p1_slider,
        'A2': A2_slider,
        'w2': w2_slider,
        'p2': p2_slider,
        'speed': speed_slider
    }
    
    return sliders

def create_buttons(fig):
    """创建按钮控件"""
    # 按钮属性
    button_props = {
        'color': BUTTON_COLOR,
        'hovercolor': BUTTON_HOVER_COLOR
    }
    
    # 创建按钮 - 修改位置以避免重叠
    play_button_ax = plt.axes([0.04, 0.06, BUTTON_WIDTH/2-0.01, BUTTON_HEIGHT])
    pause_button_ax = plt.axes([0.04+BUTTON_WIDTH/2, 0.06, BUTTON_WIDTH/2-0.01, BUTTON_HEIGHT])
    reset_button_ax = plt.axes([0.04, 0.01, BUTTON_WIDTH, BUTTON_HEIGHT])
    
    play_button = Button(play_button_ax, '播放', **button_props)
    pause_button = Button(pause_button_ax, '暂停', **button_props)
    reset_button = Button(reset_button_ax, '重置', **button_props)
    
    # 增强按钮样式
    for button in [play_button, pause_button, reset_button]:
        button.label.set_color(BUTTON_TEXT_COLOR)
        button.label.set_fontweight('bold')
        button.label.set_fontsize(14)
    
    # 返回按钮字典
    buttons = {
        'play': play_button,
        'play_ax': play_button_ax,
        'pause': pause_button,
        'pause_ax': pause_button_ax,
        'reset': reset_button,
        'reset_ax': reset_button_ax
    }
    
    return buttons 