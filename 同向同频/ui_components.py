# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator
from config import (
    BACKGROUND_COLOR, GRID_COLOR, TEXT_COLOR, AXIS_COLOR, PANEL_COLOR,
    WAVE1_COLOR, WAVE2_COLOR, COMBINED_WAVE_COLOR, PHASE_DIFF_COLOR,
    SLIDER_AX_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, LEFT_MARGIN,
    SLIDER_WIDTH, TITLE_FONT, LABEL_FONT, VALUE_FONT1, VALUE_FONT2, 
    VALUE_FONT3, PHASE_FONT, PHASE_LABELS, PHASE_VALUES, INITIAL_PARAMS
)

def create_figure():
    """创建主图形和坐标轴"""
    # 创建带有深色背景的图形
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 9), facecolor=BACKGROUND_COLOR)
    fig.patch.set_alpha(1.0)  # 确保背景完全不透明
    
    # 为图形添加标题
    fig.suptitle('同向同频简谐运动合成', fontsize=24, fontweight='bold', color=TEXT_COLOR, y=0.98)
    
    # 创建布局，清晰区分控制区和绘图区
    grid_layout = GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.15, left=LEFT_MARGIN, right=0.98)
    
    # 创建主绘图轴
    ax1 = fig.add_subplot(grid_layout[0])  # 波形1
    ax2 = fig.add_subplot(grid_layout[1])  # 波形2
    ax3 = fig.add_subplot(grid_layout[2])  # 合成波形
    
    # 配置绘图轴的外观
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(BACKGROUND_COLOR)
        ax.set_xlim(0, 20)
        ax.set_ylim(-2.5, 2.5)  # 增大振幅范围，以容纳合成波的可能最大振幅
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
    
    # 创建控制面板背景
    create_control_panels(fig)
    
    return fig, ax1, ax2, ax3

def create_control_panels(fig):
    """创建左侧控制面板背景"""
    # 通过叠加多个矩形实现渐变效果
    def create_panel(y_pos, height, transparency=0.9):
        # 主面板 - 使用FancyBboxPatch创建圆角面板
        rect = FancyBboxPatch(
            (0.005, y_pos), LEFT_MARGIN - 0.015, height,
            transform=fig.transFigure, facecolor=PANEL_COLOR,
            edgecolor=AXIS_COLOR, linewidth=1, alpha=transparency, zorder=-1,
            boxstyle="round,pad=0.01,rounding_size=0.02"
        )
    
        # 顶部高亮（渐变效果）
        highlight_rect = plt.Rectangle(
            (0.005, y_pos + height - 0.02), LEFT_MARGIN - 0.015, 0.02,
            transform=fig.transFigure, facecolor='#1A3A6C',
            edgecolor=None, alpha=0.4, zorder=-0.9
        )
    
        # 底部阴影
        shadow_rect = plt.Rectangle(
            (0.005, y_pos), LEFT_MARGIN - 0.015, 0.02,
            transform=fig.transFigure, facecolor='#050A14',
            edgecolor=None, alpha=0.4, zorder=-0.9
        )
    
        return [rect, highlight_rect, shadow_rect]
    
    panel_elements = []
    panel_elements.extend(create_panel(0.73, 0.25))   # 波形1区域
    panel_elements.extend(create_panel(0.54, 0.19))   # 波形2区域
    panel_elements.extend(create_panel(0.39, 0.15))   # 相位差预设区域（新增）
    panel_elements.extend(create_panel(0.20, 0.19))   # 公共参数区域
    panel_elements.extend(create_panel(0.01, 0.19))   # 合成波形区域
    
    fig.patches.extend(panel_elements)

def create_equation_boxes(axes):
    """创建公式说明框"""
    ax1, ax2, ax3 = axes
    
    def create_equation_box(ax, y_pos, equation, color):
        # 创建文本方框背景
        box_props = dict(boxstyle='round,pad=0.5', facecolor='#1A3A6C', alpha=0.7, edgecolor=color)
        # 在右上角添加方程文本
        ax.text(0.98, y_pos, equation, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', horizontalalignment='right',
                bbox=box_props, color=color, fontweight='bold')
    
    # 为每个波形图添加方程式说明
    create_equation_box(ax1, 0.9, "x1 = A1*sin(ωt + φ1)", WAVE1_COLOR)
    create_equation_box(ax2, 0.9, "x2 = A2*sin(ωt + φ2)", WAVE2_COLOR)
    create_equation_box(ax3, 0.9, "x = x1 + x2 = A*sin(ωt + φ)", COMBINED_WAVE_COLOR)

def create_plot_elements(axes):
    """创建绘图元素"""
    ax1, ax2, ax3 = axes
    
    # 初始化波形绘图，使用更好的线条样式
    line1, = ax1.plot([], [], color=WAVE1_COLOR, lw=2.5, animated=True)
    line2, = ax2.plot([], [], color=WAVE2_COLOR, lw=2.5, animated=True)
    line3, = ax3.plot([], [], color=COMBINED_WAVE_COLOR, lw=2.5, animated=True)
    
    return line1, line2, line3

def create_text_labels(fig):
    """创建文本标签"""
    # ========= 波形1部分 =========
    wave1_equation_text = fig.text(0.15, 0.95, 'x1 = A1*sin(ωt + φ1)', ha='center', **VALUE_FONT1)
    fig.text(0.15, 0.91, '波形1', ha='center', **TITLE_FONT)
    fig.text(0.05, 0.87, '振幅1:', **LABEL_FONT)
    fig.text(0.05, 0.81, '相位1:', **LABEL_FONT)
    
    # 波形1的值
    text_A1 = fig.text(0.22, 0.87, f"{INITIAL_PARAMS['A1']:.1f}", **VALUE_FONT1)
    text_p1 = fig.text(0.22, 0.81, f"{INITIAL_PARAMS['phi1']:.2f}", **VALUE_FONT1)
    
    # ========= 波形2部分 =========
    wave2_equation_text = fig.text(0.15, 0.71, 'x2 = A2*sin(ωt + φ2)', ha='center', **VALUE_FONT2)
    fig.text(0.15, 0.67, '波形2', ha='center', **TITLE_FONT)
    fig.text(0.05, 0.63, '振幅2:', **LABEL_FONT)
    fig.text(0.05, 0.57, '相位2:', **LABEL_FONT)
    
    # 波形2的值
    text_A2 = fig.text(0.22, 0.63, f"{INITIAL_PARAMS['A2']:.1f}", **VALUE_FONT2)
    text_p2 = fig.text(0.22, 0.57, f"{INITIAL_PARAMS['phi2']:.2f}", **VALUE_FONT2)
    
    # ========= 相位差预设部分 =========
    fig.text(0.15, 0.51, '相位差预设', ha='center', **TITLE_FONT)
    
    # ========= 公共参数部分 =========
    fig.text(0.15, 0.36, '公共参数', ha='center', **TITLE_FONT)
    fig.text(0.05, 0.32, '频率ω:', **LABEL_FONT)
    text_omega = fig.text(0.22, 0.32, f"{INITIAL_PARAMS['omega']:.1f}", **PHASE_FONT)
    
    # ========= 合成波形部分 =========
    wave3_equation_text = fig.text(0.15, 0.17, 'x = A*sin(ωt + φ)', ha='center', **VALUE_FONT3)
    fig.text(0.15, 0.14, '合成波形', ha='center', **TITLE_FONT)
    fig.text(0.05, 0.11, '合成振幅 A:', **LABEL_FONT)
    fig.text(0.05, 0.08, '合成相位 φ:', **LABEL_FONT)
    fig.text(0.05, 0.05, '相位差 Δφ:', **LABEL_FONT)
    
    # 合成波参数的显示值
    text_A = fig.text(0.22, 0.11, "2.0", **VALUE_FONT3)
    text_phi = fig.text(0.22, 0.08, "0.0", **VALUE_FONT3)
    text_delta_phi = fig.text(0.22, 0.05, "0.0", **PHASE_FONT)
    
    # ========= 速度控制部分 =========
    fig.text(0.15, 0.02, '速度控制', ha='center', color=PHASE_DIFF_COLOR, fontsize=12, fontweight='bold')
    text_speed = fig.text(0.22, 0.01, f"{INITIAL_PARAMS['speed']:.1f}x", **PHASE_FONT)
    fig.text(0.07, 0.01, '速度:', **LABEL_FONT)
    
    # 返回需要更新的文本对象
    text_elements = {
        'wave1_eq': wave1_equation_text,
        'wave2_eq': wave2_equation_text,
        'wave3_eq': wave3_equation_text,
        'A1': text_A1,
        'p1': text_p1,
        'A2': text_A2,
        'p2': text_p2,
        'omega': text_omega,
        'A': text_A,
        'phi': text_phi,
        'delta_phi': text_delta_phi,
        'speed': text_speed
    }
    
    return text_elements

def create_sliders(fig):
    """创建滑块控件"""
    # 振幅1滑块
    amp1_slider_ax = plt.axes([0.08, 0.85, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    amp1_slider = Slider(
        amp1_slider_ax, '', 0.0, 2.0,
        valinit=INITIAL_PARAMS['A1'], valfmt='%.1f',
        color=WAVE1_COLOR, initcolor=WAVE1_COLOR
    )
    amp1_slider.valtext.set_visible(False)
    
    # 相位1滑块
    phase1_slider_ax = plt.axes([0.08, 0.79, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    phase1_slider = Slider(
        phase1_slider_ax, '', -np.pi, np.pi,
        valinit=INITIAL_PARAMS['phi1'], valfmt='%.1f',
        color=WAVE1_COLOR, initcolor=WAVE1_COLOR
    )
    phase1_slider.valtext.set_visible(False)
    
    # 振幅2滑块
    amp2_slider_ax = plt.axes([0.08, 0.61, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    amp2_slider = Slider(
        amp2_slider_ax, '', 0.0, 2.0,
        valinit=INITIAL_PARAMS['A2'], valfmt='%.1f',
        color=WAVE2_COLOR, initcolor=WAVE2_COLOR
    )
    amp2_slider.valtext.set_visible(False)
    
    # 相位2滑块
    phase2_slider_ax = plt.axes([0.08, 0.55, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    phase2_slider = Slider(
        phase2_slider_ax, '', -np.pi, np.pi,
        valinit=INITIAL_PARAMS['phi2'], valfmt='%.1f',
        color=WAVE2_COLOR, initcolor=WAVE2_COLOR
    )
    phase2_slider.valtext.set_visible(False)
    
    # 频率滑块
    omega_slider_ax = plt.axes([0.08, 0.30, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    omega_slider = Slider(
        omega_slider_ax, '', 0.1, 3.0,
        valinit=INITIAL_PARAMS['omega'], valfmt='%.1f',
        color=PHASE_DIFF_COLOR, initcolor=PHASE_DIFF_COLOR
    )
    omega_slider.valtext.set_visible(False)
    
    # 速度控制滑块
    speed_slider_ax = plt.axes([0.08, 0.01, SLIDER_WIDTH, 0.02], facecolor=SLIDER_AX_COLOR)
    speed_slider = Slider(
        speed_slider_ax, '', 0.1, 3.0,
        valinit=INITIAL_PARAMS['speed'], valfmt='%.1fx',
        color=PHASE_DIFF_COLOR, initcolor=PHASE_DIFF_COLOR
    )
    speed_slider.valtext.set_visible(False)
    
    sliders = {
        'a1': amp1_slider,
        'p1': phase1_slider,
        'a2': amp2_slider,
        'p2': phase2_slider,
        'omega': omega_slider,
        'speed': speed_slider
    }
    
    return sliders

def create_buttons(fig):
    """创建按钮控件"""
    # 创建按钮区域
    button_ax_play = plt.axes([0.08, 0.22, 0.07, 0.04])
    button_ax_pause = plt.axes([0.17, 0.22, 0.07, 0.04])
    button_ax_reset = plt.axes([0.12, 0.26, 0.09, 0.04])
    
    # 创建按钮，确保使用fontproperties支持中文
    button_play = Button(button_ax_play, '▶', color=BUTTON_COLOR, hovercolor=BUTTON_HOVER_COLOR)
    button_pause = Button(button_ax_pause, '⏸', color=BUTTON_COLOR, hovercolor=BUTTON_HOVER_COLOR)
    button_reset = Button(button_ax_reset, '重置', color=BUTTON_COLOR, hovercolor=BUTTON_HOVER_COLOR)
    
    # 手动设置按钮中的中文字体
    for button, label in [(button_reset, '重置')]:
        button.label.set_fontsize(12)  # 设置字体大小
        
    buttons = {
        'play': button_play,
        'pause': button_pause,
        'reset': button_reset
    }
    
    return buttons

def create_phase_buttons(fig):
    """创建相位差预设按钮"""
    # 参数设置
    row1_y = 0.47  # 第一行按钮位置
    row2_y = 0.42  # 第二行按钮位置，与第一行有足够间距
    button_width = 0.055  # 按钮宽度
    button_height = 0.03  # 按钮高度
    button_spacing = 0.026  # 按钮之间的间距
    
    # 定义每个按钮的位置
    button_positions = [
        # 第一行按钮 - 0°, 30°, 60°
        [0.03, row1_y, button_width, button_height],
        [0.03 + button_width + button_spacing, row1_y, button_width, button_height],
        [0.03 + 2*(button_width + button_spacing), row1_y, button_width, button_height],
        
        # 第二行按钮 - 90°, 120°, 180°
        [0.03, row2_y, button_width, button_height],
        [0.03 + button_width + button_spacing, row2_y, button_width, button_height],
        [0.03 + 2*(button_width + button_spacing), row2_y, button_width, button_height]
    ]
    
    phase_buttons = []
    
    # 创建按钮
    for i, (pos, label, value) in enumerate(zip(button_positions, PHASE_LABELS, PHASE_VALUES)):
        btn_ax = plt.axes(pos)
        btn = Button(btn_ax, label, color=BUTTON_COLOR, hovercolor=BUTTON_HOVER_COLOR)
        # 设置按钮标签文本的字体属性
        btn.label.set_fontsize(10)  # 设置字体大小
        phase_buttons.append((btn, value))
    
    return phase_buttons 