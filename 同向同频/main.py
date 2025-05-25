# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

# 导入各模块
from config import has_ffmpeg
from ui_components import (
    create_figure, create_equation_boxes, create_plot_elements,
    create_text_labels, create_sliders, create_buttons, create_phase_buttons
)
from params_controller import ParamsController
from animation_controller import AnimationController
from event_handlers import EventHandlers

def main():
    """主程序入口"""
    # 创建主图形和坐标轴
    fig, ax1, ax2, ax3 = create_figure()
    axes = (ax1, ax2, ax3)
    
    # 添加公式说明框
    create_equation_boxes(axes)
    
    # 创建波形线条
    lines = create_plot_elements(axes)
    
    # 创建文本标签
    text_elements = create_text_labels(fig)
    
    # 创建控制元素
    sliders = create_sliders(fig)
    buttons = create_buttons(fig)
    phase_buttons = create_phase_buttons(fig)
    
    # 创建参数控制器
    params_controller = ParamsController(sliders, text_elements)
    
    # 创建动画控制器
    animation_controller = AnimationController(fig, lines, params_controller)
    
    # 创建事件处理器
    event_handlers = EventHandlers(
        animation_controller, params_controller, buttons, sliders, phase_buttons
    )
    
    # 鼠标关闭事件处理
    def on_close(event):
        """当图形关闭时，清理鼠标抓取状态"""
        event.canvas.mpl_disconnect(cid_close)
        event.canvas.stop_event_loop()
        for ax in fig.axes:
            if event.canvas.mouse_grabber is ax:
                event.canvas.release_mouse(ax)

    # 连接关闭事件处理函数
    cid_close = fig.canvas.mpl_connect('close_event', on_close)
    
    # 设置更好的交互模式
    plt.rcParams['toolbar'] = 'None'  # 隐藏工具栏以提高性能
    
    # 初始化参数
    params_controller.update_slider_values()
    
    # 启动动画
    animation_controller.start_animation()
    
    # 显示图形
    plt.show()

if __name__ == '__main__':
    main() 