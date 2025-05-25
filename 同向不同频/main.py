# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button
import subprocess
import sys
import os
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
import time

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
    chinese_fonts = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'Microsoft YaHei', 
                    'SimSun', 'WenQuanYi Micro Hei', 'Heiti TC', 'KaiTi']
    
    # 尝试系统字体
    for font in chinese_fonts:
        if font in [f.name for f in fm.fontManager.ttflist]:
            plt.rcParams['font.sans-serif'] = [font]
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

# 定义配色方案 - 改进的深色主题，具有更好的对比度和现代感
background_color = '#0A1929'  # 更深的蓝黑色背景
grid_line_color = '#1E3A5F'  # 更亮的网格线颜色
text_color = '#FFFFFF'  # 纯白色文本
axis_color = '#345D8A'  # 更亮的轴线颜色
panel_background_color = '#152238'  # 稍微亮一点的面板背景

# 波形颜色，饱和度更高，对比度更好
wave1_color = '#3B82F6'  # 明亮的蓝色
wave2_color = '#F59E0B'  # 橙黄色
combined_wave_color = '#10B981'  # 翠绿色
speed_control_color = '#EC4899'  # 亮粉色用于速度控制

# 滑块颜色
slider_color = '#F59E0B'  # 橙黄色
slider_handle_color = '#FFFFFF'
slider_track_color = '#1E293B'

# 按钮颜色
button_color = '#2563EB'  # 亮蓝色
button_hover_color = '#3B82F6'
button_active_color = '#60A5FA'
button_text_color = '#FFFFFF'

# 预先计算常用数据以提高性能
t = np.linspace(0, 20, 500)  # 减少点数以提高性能

# 创建带有深色背景的图形
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 9), facecolor=background_color)
fig.patch.set_alpha(1.0)  # 确保背景完全不透明

# 为图形添加标题，优化字体显示
fig.suptitle('简谐运动合成', fontsize=24, fontweight='bold', color=text_color, y=0.98)

# 扩大左侧面板宽度，为控制元素留出更多空间
left_margin = 0.22

# 创建更好的布局，清晰区分控制区和绘图区
grid_layout = GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.15)

# 创建主绘图轴，左侧为控制区留出更多空间
ax1 = fig.add_subplot(grid_layout[0])
ax2 = fig.add_subplot(grid_layout[1])
ax3 = fig.add_subplot(grid_layout[2])

# 配置绘图轴的外观
for ax in [ax1, ax2, ax3]:
    ax.set_facecolor(background_color)
    ax.set_xlim(0, 20)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True, color=grid_line_color, linestyle='-', alpha=0.5, linewidth=0.5)
    ax.tick_params(axis='y', colors=text_color, direction='out', length=6, width=1, labelsize=10)
    ax.tick_params(axis='x', colors=text_color, direction='out', length=6, width=1, labelsize=10)

    # 添加次要网格线以提高可读性
    ax.grid(which='minor', color=grid_line_color, linestyle='-', alpha=0.2, linewidth=0.25)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))

    # 仅在底部绘图显示x轴标签
    if ax != ax3:
        ax.set_xticklabels([])
    else:
        ax.set_xlabel('时间 (秒)', color=text_color, fontsize=12, fontweight='medium')

    # 设置轴线颜色
    for spine in ax.spines.values():
        spine.set_color(axis_color)
        spine.set_linewidth(1.5)

    # 添加Y轴标签
    ax.set_ylabel('振幅', color=text_color, fontsize=12, fontweight='medium')

# 创建左侧控制面板背景，带有圆角和微妙阴影
# 通过叠加多个矩形实现渐变效果
def create_panel(y_pos, height, transparency=0.9):
    # 主面板 - 使用FancyBboxPatch创建圆角面板
    rect = FancyBboxPatch((0.005, y_pos), left_margin - 0.02, height,
                      transform=fig.transFigure, facecolor=panel_background_color,
                      edgecolor=axis_color, linewidth=1, alpha=transparency, zorder=-1,
                      boxstyle="round,pad=0.01,rounding_size=0.02")

    # 顶部高亮（渐变效果）
    highlight_rect = plt.Rectangle((0.005, y_pos + height - 0.02), left_margin - 0.02, 0.02,
                           transform=fig.transFigure, facecolor='#1A3A6C',
                           edgecolor=None, alpha=0.4, zorder=-0.9)

    # 底部阴影
    shadow_rect = plt.Rectangle((0.005, y_pos), left_margin - 0.02, 0.02,
                         transform=fig.transFigure, facecolor='#050A14',
                         edgecolor=None, alpha=0.4, zorder=-0.9)

    return [rect, highlight_rect, shadow_rect]

# 创建三个带有阴影效果的面板
panel_elements = []
panel_elements.extend(create_panel(0.67, 0.31))
panel_elements.extend(create_panel(0.34, 0.33))
panel_elements.extend(create_panel(0.01, 0.33))

fig.patches.extend(panel_elements)

# 初始化波形绘图，使用更好的线条样式
line1, = ax1.plot([], [], color=wave1_color, lw=2.5, animated=True)
line2, = ax2.plot([], [], color=wave2_color, lw=2.5, animated=True)
line3, = ax3.plot([], [], color=combined_wave_color, lw=2.5, animated=True)

# 创建图例，显示各个波形的方程式
def create_equation_box(ax, y_pos, equation, color):
    # 创建文本方框背景
    box_props = dict(boxstyle='round,pad=0.5', facecolor='#1A3A6C', alpha=0.7, edgecolor=color)
    # 在右上角添加方程文本
    ax.text(0.98, y_pos, equation, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', horizontalalignment='right',
            bbox=box_props, color=color, fontweight='bold')

# 为每个波形图添加方程式说明
create_equation_box(ax1, 0.9, "x1 = A1*sin(w1*t + p1)", wave1_color)
create_equation_box(ax2, 0.9, "x2 = A2*sin(w2*t + p2)", wave2_color)
create_equation_box(ax3, 0.9, "x = x1 + x2", combined_wave_color)

# 添加波形标题和标签，优化样式
title_font = {'fontsize': 16, 'fontweight': 'bold', 'color': text_color}
label_font = {'fontsize': 12, 'color': text_color, 'fontweight': 'medium'}
value_font1 = {'fontsize': 12, 'color': wave1_color, 'fontweight': 'bold'}
value_font2 = {'fontsize': 12, 'color': wave2_color, 'fontweight': 'bold'}
value_font3 = {'fontsize': 12, 'color': combined_wave_color, 'fontweight': 'bold'}
speed_font = {'fontsize': 12, 'color': speed_control_color, 'fontweight': 'bold'}

# 调整左侧文本垂直位置，避免重叠
# 波形1方程式和标签 - 增加垂直间距
wave1_equation_text = fig.text(0.11, 0.95, 'x1 = A1*sin(w1*t + p1)', ha='center', **value_font1)
fig.text(0.11, 0.90, '波形1', ha='center', **title_font)
fig.text(0.04, 0.85, '振幅1:', **label_font)
fig.text(0.04, 0.78, '频率1:', **label_font)
fig.text(0.04, 0.71, '相位1:', **label_font)

# 波形1的值 - 放在标签右侧显示
text_A1 = fig.text(0.15, 0.85, "0.5", **value_font1)
text_w1 = fig.text(0.15, 0.78, "5.0", **value_font1)
text_p1 = fig.text(0.15, 0.71, "0.0", **value_font1)

# 波形2方程式和标签 - 增加垂直间距
wave2_equation_text = fig.text(0.11, 0.62, 'x2 = A2*sin(w2*t + p2)', ha='center', **value_font2)
fig.text(0.11, 0.57, '波形2', ha='center', **title_font)
fig.text(0.04, 0.52, '振幅2:', **label_font)
fig.text(0.04, 0.45, '频率2:', **label_font)
fig.text(0.04, 0.38, '相位2:', **label_font)

# 波形2的值
text_A2 = fig.text(0.15, 0.52, "0.5", **value_font2)
text_w2 = fig.text(0.15, 0.45, "2.0", **value_font2)
text_p2 = fig.text(0.15, 0.38, "0.0", **value_font2)

# 合成波形方程式
wave3_equation_text = fig.text(0.11, 0.29, 'x = x1 + x2', ha='center', **value_font3)
fig.text(0.11, 0.24, '合成波形', ha='center', **title_font)

# 添加速度控制标签
fig.text(0.11, 0.19, '速度控制', ha='center', color=speed_control_color, fontsize=14, fontweight='bold')
text_speed = fig.text(0.15, 0.14, "1.0x", **speed_font)
fig.text(0.04, 0.14, '速度:', **label_font)

# 存储当前参数值，避免不必要的重新计算
current_params = {
    'A1': 0.5,
    'omega1': 5.0,
    'phi1': 0.0,
    'A2': 0.5,
    'omega2': 2.0,
    'phi2': 0.0,
    'speed': 1.0
}

# 创建滑块轴，优化视觉样式
A1_slider_ax = fig.add_axes([0.05, 0.83, 0.14, 0.02], facecolor=slider_track_color)
w1_slider_ax = fig.add_axes([0.05, 0.76, 0.14, 0.02], facecolor=slider_track_color)
p1_slider_ax = fig.add_axes([0.05, 0.69, 0.14, 0.02], facecolor=slider_track_color)

A2_slider_ax = fig.add_axes([0.05, 0.50, 0.14, 0.02], facecolor=slider_track_color)
w2_slider_ax = fig.add_axes([0.05, 0.43, 0.14, 0.02], facecolor=slider_track_color)
p2_slider_ax = fig.add_axes([0.05, 0.36, 0.14, 0.02], facecolor=slider_track_color)

# 添加速度控制滑块
speed_slider_ax = fig.add_axes([0.05, 0.12, 0.14, 0.02], facecolor=slider_track_color)

# 创建样式化的滑块，增强可见性 - 修复手柄样式参数
slider_props = {
    'color': slider_color,
    'valstep': None,
    'initcolor': 'none',
    'handle_style': {'facecolor': slider_handle_color, 'edgecolor': None, 'size': 12}
}

# 速度滑块的样式
speed_slider_props = {
    'color': speed_control_color,
    'valstep': None,
    'initcolor': 'none',
    'handle_style': {'facecolor': slider_handle_color, 'edgecolor': None, 'size': 12}
}

A1_slider = Slider(A1_slider_ax, '', 0.1, 1.0, valinit=0.5, **slider_props)
w1_slider = Slider(w1_slider_ax, '', 0.5, 10.0, valinit=5.0, **slider_props)
p1_slider = Slider(p1_slider_ax, '', 0, 2*np.pi, valinit=0, **slider_props)

A2_slider = Slider(A2_slider_ax, '', 0.1, 1.0, valinit=0.5, **slider_props)
w2_slider = Slider(w2_slider_ax, '', 0.5, 10.0, valinit=2.0, **slider_props)
p2_slider = Slider(p2_slider_ax, '', 0, 2*np.pi, valinit=0, **slider_props)

# 创建速度控制滑块（0.1x 到 3.0x 的速度范围）
speed_slider = Slider(speed_slider_ax, '', 0.1, 3.0, valinit=1.0, **speed_slider_props)

# 自定义滑块外观
for slider in [A1_slider, w1_slider, p1_slider, A2_slider, w2_slider, p2_slider, speed_slider]:
    slider.valtext.set_visible(False)  # 使用自定义的值显示
    slider.label.set_visible(False)

# 创建现代、更具吸引力的按钮，带有渐变效果
button_width = 0.14
button_height = 0.06
button_props = {
    'color': button_color,
    'hovercolor': button_hover_color
}

# 创建样式化的按钮，优化位置和样式
play_button_ax = fig.add_axes([0.04, 0.05, button_width/2-0.01, button_height])
pause_button_ax = fig.add_axes([0.04+button_width/2, 0.05, button_width/2-0.01, button_height])
reset_button_ax = fig.add_axes([0.04, 0.05-button_height-0.01, button_width, button_height])

play_button = Button(play_button_ax, '播放', **button_props)
pause_button = Button(pause_button_ax, '暂停', **button_props)
reset_button = Button(reset_button_ax, '重置', **button_props)

# 增强按钮样式
for button in [play_button, pause_button, reset_button]:
    button.label.set_color(button_text_color)
    button.label.set_fontweight('bold')
    button.label.set_fontsize(14)

# 播放状态控制
is_paused = [False]
needs_redraw = [False]  # 标记是否需要重绘图形

def toggle_play(event):
    is_paused[0] = False
    play_button.color = button_active_color
    pause_button.color = button_color

    # 重绘按钮
    play_button_ax.figure.canvas.draw_idle()
    pause_button_ax.figure.canvas.draw_idle()

def toggle_pause(event):
    is_paused[0] = True
    pause_button.color = button_active_color
    play_button.color = button_color

    # 重绘按钮
    play_button_ax.figure.canvas.draw_idle()
    pause_button_ax.figure.canvas.draw_idle()

def reset(event):
    # 重置滑块值
    A1_slider.set_val(0.5)
    w1_slider.set_val(5.0)
    p1_slider.set_val(0)
    A2_slider.set_val(0.5)
    w2_slider.set_val(2.0)
    p2_slider.set_val(0)
    speed_slider.set_val(1.0)

    # 更新存储的参数
    current_params['A1'] = 0.5
    current_params['omega1'] = 5.0
    current_params['phi1'] = 0.0
    current_params['A2'] = 0.5
    current_params['omega2'] = 2.0
    current_params['phi2'] = 0.0
    current_params['speed'] = 1.0

    # 按钮按下的视觉反馈
    original_color = reset_button.color
    reset_button.color = button_active_color
    reset_button_ax.figure.canvas.draw_idle()

    # 安排按钮颜色重置
    import threading
    def reset_color():
        reset_button.color = original_color
        reset_button_ax.figure.canvas.draw_idle()

    threading.Timer(0.2, reset_color).start()

    # 标记需要重绘
    needs_redraw[0] = True

play_button.on_clicked(toggle_play)
pause_button.on_clicked(toggle_pause)
reset_button.on_clicked(reset)

# 初始化函数
def init():
    for line in [line1, line2, line3]:
        line.set_data([], [])
    return line1, line2, line3

# 使用基于时间的动画控制
last_frame_time = time.time()
time_counter = [0]

# 优化的动画更新函数
def update_animation(i):
    global last_frame_time

    if is_paused[0]:
        return line1, line2, line3

    # 计算帧间时间差以保持平滑的动画速度
    current_time = time.time()
    time_diff = current_time - last_frame_time
    last_frame_time = current_time

    # 获取当前参数
    A1 = current_params['A1']
    omega1 = current_params['omega1']
    phi1 = current_params['phi1']
    A2 = current_params['A2']
    omega2 = current_params['omega2']
    phi2 = current_params['phi2']
    speed = current_params['speed']

    # 更新时间
    time_counter[0] += time_diff * speed
    time_offset = time_counter[0]

    # 计算波形
    x1 = A1 * np.sin(omega1 * (t - time_offset) + phi1)
    x2 = A2 * np.sin(omega2 * (t - time_offset) + phi2)
    x3 = x1 + x2

    # 更新曲线数据
    line1.set_data(t, x1)
    line2.set_data(t, x2)
    line3.set_data(t, x3)

    return line1, line2, line3

# 优化滑块更新函数，避免过于频繁的更新
def update_slider_values():
    # 更新参数值
    current_params['A1'] = A1_slider.val
    current_params['omega1'] = w1_slider.val
    current_params['phi1'] = p1_slider.val
    current_params['A2'] = A2_slider.val
    current_params['omega2'] = w2_slider.val
    current_params['phi2'] = p2_slider.val
    current_params['speed'] = speed_slider.val

    # 更新显示的值
    text_A1.set_text(f"{current_params['A1']:.1f}")
    text_w1.set_text(f"{current_params['omega1']:.1f}")
    text_p1.set_text(f"{current_params['phi1']:.1f}")
    text_A2.set_text(f"{current_params['A2']:.1f}")
    text_w2.set_text(f"{current_params['omega2']:.1f}")
    text_p2.set_text(f"{current_params['phi2']:.1f}")
    text_speed.set_text(f"{current_params['speed']:.1f}x")

    # 更新方程显示
    wave1_equation_text.set_text(f'x1 = {current_params["A1"]:.1f}*sin({current_params["omega1"]:.1f}*t + {current_params["phi1"]:.1f})')
    wave2_equation_text.set_text(f'x2 = {current_params["A2"]:.1f}*sin({current_params["omega2"]:.1f}*t + {current_params["phi2"]:.1f})')

    # 只重绘文本区域而不是整个图形
    fig.canvas.draw_idle()

# 使用节流技术减少滑块事件的处理频率
last_update_time = time.time()
update_interval = 0.05  # 50ms的更新间隔

def throttled_update(val=None):
    global last_update_time
    current_time = time.time()

    # 如果距离上次更新不到指定间隔，则跳过此次更新
    if current_time - last_update_time < update_interval:
        return

    last_update_time = current_time
    update_slider_values()

# 为所有滑块绑定节流更新函数
A1_slider.on_changed(throttled_update)
w1_slider.on_changed(throttled_update)
p1_slider.on_changed(throttled_update)
A2_slider.on_changed(throttled_update)
w2_slider.on_changed(throttled_update)
p2_slider.on_changed(throttled_update)
speed_slider.on_changed(throttled_update)

# 为滑块添加文本标签，提高可用性
fig.text(0.03, 0.83, "最小值", fontsize=8, color=text_color, ha='left', va='center')
fig.text(0.19, 0.83, "最大值", fontsize=8, color=text_color, ha='right', va='center')
fig.text(0.03, 0.50, "最小值", fontsize=8, color=text_color, ha='left', va='center')
fig.text(0.19, 0.50, "最大值", fontsize=8, color=text_color, ha='right', va='center')
fig.text(0.03, 0.12, "慢", fontsize=8, color=text_color, ha='left', va='center')
fig.text(0.19, 0.12, "快", fontsize=8, color=text_color, ha='right', va='center')

# 调整图形边距以适应控制面板
plt.subplots_adjust(top=0.92, bottom=0.08, left=left_margin, right=0.98)

# 更新初始参数值
update_slider_values()

# 使用更高效的动画设置
animation = animation.FuncAnimation(
    fig,
    update_animation,
    frames=None,  # 无限帧
    init_func=init,
    interval=25,  # 更高的帧率
    blit=True,
    cache_frame_data=False  # 禁用帧缓存以节省内存
)

# 设置更好的交互模式
plt.rcParams['toolbar'] = 'None'  # 隐藏工具栏以提高性能

# 保存为视频文件（如果ffmpeg可用）
if has_ffmpeg:
    try:
        writer_class = animation.writers['ffmpeg']
        writer = writer_class(fps=30, metadata=dict(artist='Me'), bitrate=1800)
        print("正在保存视频，请稍候...")
        animation.save('harmonic_motion_simulation.mp4', writer=writer)
        print(f"视频已保存为 harmonic_motion_simulation.mp4")
    except Exception as e:
        print(f"保存视频时出错: {e}")
else:
    print("未安装FFmpeg，视频保存功能禁用")

# 显示动画
plt.show()    