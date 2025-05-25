# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

# 导入各模块
from config import has_ffmpeg
from ui_components import (
    create_figure, create_equation_boxes, create_plot_elements, 
    create_text_displays, create_sliders, create_buttons
)
from params_controller import ParamsController
from animation_controller import AnimationController
from event_handlers import EventHandlers

def main():
    """主程序入口"""
    # 创建主图形和坐标轴
    fig, ax1, ax2, ax3 = create_figure()
    
    # 添加公式说明框
    create_equation_boxes((ax1, ax2, ax3))
    
    # 创建绘图元素
    lines = create_plot_elements((ax1, ax2, ax3))
    
    # 创建参数显示文本
    text_elements = create_text_displays(fig)
    
    # 创建滑块控件
    sliders = create_sliders(fig)
    
    # 创建按钮控件
    buttons = create_buttons(fig)
    
    # 创建参数控制器
    params_controller = ParamsController(sliders, text_elements)
    
    # 创建动画控制器
    animation_controller = AnimationController(fig, lines, params_controller)
    
    # 创建事件处理器
    event_handlers = EventHandlers(
        animation_controller, params_controller, buttons, sliders
    )

    # 设置更好的交互模式
    plt.rcParams['toolbar'] = 'None'  # 隐藏工具栏以提高性能

    # 启动动画
    animation_controller.start_animation()
    
    # 显示图形
    plt.show()    

if __name__ == '__main__':
    main() 