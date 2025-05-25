# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

# 导入自定义模块
from config import (
    INITIAL_PARAMS, ratio_presets, trail_length, plt, has_ffmpeg
)
from ui_components import (
    create_figure, create_ui_panels, add_equation_boxes,
    create_parameter_displays, create_sliders, create_buttons,
    create_plot_elements
)
from animation import AnimationController
from event_handlers import EventHandlers

def main():
    """主程序入口"""
    # 创建主图形和坐标轴
    fig, ax_x, ax_y, ax_lissajous = create_figure()
    
    # 创建UI面板
    create_ui_panels(fig)
    
    # 添加公式说明框
    add_equation_boxes(ax_x, ax_y, ax_lissajous)
    
    # 创建参数显示文本
    text_elements = create_parameter_displays(fig)
    
    # 创建滑块控件
    sliders = create_sliders(fig)
    
    # 创建按钮控件
    buttons = create_buttons(fig)
    
    # 创建图形元素
    lines = create_plot_elements(ax_x, ax_y, ax_lissajous)
    
    # 存储轨迹点
    trail_points = [[], []]
    
    # 创建当前参数对象，包含所有初始参数值
    current_params = INITIAL_PARAMS.copy()
    current_params['ratio_presets'] = ratio_presets
    
    # 创建动画控制器
    animation_controller = AnimationController(
        fig, lines, current_params, trail_points, text_elements, sliders
    )
    
    # 创建事件处理器
    event_handlers = EventHandlers(
        animation_controller, buttons, sliders, current_params, trail_points
    )
    
    # 在启动时初始化李萨如图形
    animation_controller.initialize_lissajous_figure()
    
    # 鼠标关闭事件处理
    def on_close(event):
        """当图形关闭时，清理鼠标抓取状态"""
        # 释放所有鼠标抓取
        event.canvas.mpl_disconnect(cid_close)
        event.canvas.stop_event_loop()
        for ax in fig.axes:
            if event.canvas.mouse_grabber is ax:
                event.canvas.release_mouse(ax)

    # 连接关闭事件处理函数
    cid_close = fig.canvas.mpl_connect('close_event', on_close)
    
    # 设置更好的交互模式
    plt.rcParams['toolbar'] = 'None'  # 隐藏工具栏以提高性能
    
    # 启动动画
    animation_controller.start_animation()
    
    # 显示图形
    plt.show()

if __name__ == '__main__':
    main()
