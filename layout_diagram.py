#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成L型布局示意图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_layout_diagram():
    """创建L型布局示意图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 设置坐标范围
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    
    # 控制面板
    control_panel = patches.Rectangle((0.5, 1), 2.5, 6, 
                                    linewidth=2, edgecolor='blue', 
                                    facecolor='lightblue', alpha=0.7)
    ax.add_patch(control_panel)
    ax.text(1.75, 4, '控制面板\n参数调节', ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # Y方向波形面板（左上）
    y_wave_panel = patches.Rectangle((3.5, 4.5), 3, 2.5, 
                                   linewidth=2, edgecolor='orange', 
                                   facecolor='lightyellow', alpha=0.7)
    ax.add_patch(y_wave_panel)
    ax.text(5, 5.75, 'Y方向波形\n(垂直显示)', ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # 李萨如图形面板（右上）
    lissajous_panel = patches.Rectangle((7, 4.5), 4, 2.5, 
                                      linewidth=2, edgecolor='green', 
                                      facecolor='lightgreen', alpha=0.7)
    ax.add_patch(lissajous_panel)
    ax.text(9, 5.75, '李萨如图形\n(主显示区)', ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # 空白占位符（左下）
    placeholder = patches.Rectangle((3.5, 1), 3, 2.5, 
                                  linewidth=2, edgecolor='gray', 
                                  facecolor='lightgray', alpha=0.5)
    ax.add_patch(placeholder)
    ax.text(5, 2.25, '空白区域', ha='center', va='center', 
            fontsize=10, style='italic')
    
    # X方向波形面板（右下）
    x_wave_panel = patches.Rectangle((7, 1), 4, 2.5, 
                                   linewidth=2, edgecolor='red', 
                                   facecolor='lightcoral', alpha=0.7)
    ax.add_patch(x_wave_panel)
    ax.text(9, 2.25, 'X方向波形\n(水平显示)', ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # 添加箭头显示对应关系
    # Y波形到李萨如图形的对应关系
    ax.annotate('', xy=(7, 5.75), xytext=(6.5, 5.75),
                arrowprops=dict(arrowstyle='<->', color='orange', lw=2))
    ax.text(6.75, 6.1, 'Y轴对齐', ha='center', va='bottom', 
            fontsize=8, color='orange')
    
    # X波形到李萨如图形的对应关系
    ax.annotate('', xy=(9, 4.5), xytext=(9, 3.5),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(9.5, 4, 'X轴对齐', ha='left', va='center', 
            fontsize=8, color='red', rotation=90)
    
    # 添加标题和说明
    ax.set_title('简谐运动可视化系统 - L型布局设计', fontsize=16, weight='bold', pad=20)
    
    # 添加说明文字
    explanation = """
    布局特点：
    • Y波形图位于李萨如图形左侧，Y轴对齐
    • X波形图位于李萨如图形下方，X轴对齐
    • 形成L型布局，增强视觉对应关系
    • 控制面板保持在最左侧位置
    """
    ax.text(0.5, 0.5, explanation, fontsize=9, va='top', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8))
    
    # 移除坐标轴
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('L_layout_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    create_layout_diagram()
