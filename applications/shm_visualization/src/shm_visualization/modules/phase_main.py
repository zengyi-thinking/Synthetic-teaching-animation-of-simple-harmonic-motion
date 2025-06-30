# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 同向同频（相位差合成）主程序
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from matplotlib.patches import Circle, Arrow, Arc

from ..ui.ui_framework import WavePanel, PhaseControlPanel, MatplotlibCanvas, COLORS, get_app_instance
from ..animations.phase_animation import PhaseAnimationController
from ..ui.params_controller import ParamsController


class PhasorPanel(QWidget):
    """相量图显示面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标题标签
        self.title_label = QLabel("相量图")
        self.title_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 14pt; background-color: {COLORS['accent3']}; border-radius: 4px; padding: 5px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建画布
        self.canvas = MatplotlibCanvas(self)
        self.canvas.axes.set_aspect('equal')
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(-2.5, 2.5)
        self.canvas.axes.set_ylim(-2.5, 2.5)
        self.canvas.axes.set_xlabel('实部', color=COLORS['text'])
        self.canvas.axes.set_ylabel('虚部', color=COLORS['text'])
        
        # 绘制坐标轴
        self.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', alpha=0.3)
        self.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', alpha=0.3)
        
        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.canvas)
        
        # 创建振幅和相位信息标签
        self.info_label = QLabel("合成振幅: 1.0   合成相位: 0.0")
        self.info_label.setStyleSheet(f"color: {COLORS['accent3']}; font-weight: bold; font-size: 12pt; background-color: rgba(26, 58, 108, 180); border: 1px solid {COLORS['accent3']}; border-radius: 4px; padding: 8px;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.info_label)
        self.setLayout(layout)
    
    def update_phasors(self, phasor1_x, phasor1_y, phasor2_x, phasor2_y, composite_x, composite_y):
        """更新相量图 - 优化版本，解决遮挡问题"""
        self.canvas.axes.clear()

        # 重新设置坐标轴属性
        self.canvas.axes.set_xlim(-2.5, 2.5)
        self.canvas.axes.set_ylim(-2.5, 2.5)
        self.canvas.axes.set_xlabel('实部', color=COLORS['text'], fontsize=10)
        self.canvas.axes.set_ylabel('虚部', color=COLORS['text'], fontsize=10)

        # 绘制坐标轴
        self.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', alpha=0.3)
        self.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', alpha=0.3)
        self.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.2)

        # 绘制单位圆
        circle = Circle((0, 0), 1, fill=False, color=COLORS['text'], linestyle='--', alpha=0.4)
        self.canvas.axes.add_patch(circle)

        # 绘制第一个相量向量
        self.canvas.axes.arrow(0, 0, phasor1_x, phasor1_y, head_width=0.08, head_length=0.08,
                      fc=COLORS['accent1'], ec=COLORS['accent1'], linewidth=2.5, zorder=2)

        # 绘制第二个相量向量（从原点出发）
        self.canvas.axes.arrow(0, 0, phasor2_x, phasor2_y, head_width=0.08, head_length=0.08,
                      fc=COLORS['accent2'], ec=COLORS['accent2'], linewidth=2.5, zorder=2)

        # 绘制合成相量向量
        self.canvas.axes.arrow(0, 0, composite_x, composite_y, head_width=0.1, head_length=0.1,
                      fc=COLORS['accent3'], ec=COLORS['accent3'], linewidth=3.5, zorder=4)

        # 绘制向量相加路径（虚线）- 从第一个向量端点到合成向量端点
        self.canvas.axes.plot([phasor1_x, composite_x], [phasor1_y, composite_y],
                    color=COLORS['accent2'], linestyle='--', alpha=0.6, linewidth=1.5, zorder=1)

        # 添加向量标签，避免遮挡
        # 计算标签位置，避开向量箭头
        label_offset = 0.15

        # 波形1标签
        if abs(phasor1_x) > 0.1 or abs(phasor1_y) > 0.1:
            label1_x = phasor1_x + label_offset * (1 if phasor1_x >= 0 else -1)
            label1_y = phasor1_y + label_offset * (1 if phasor1_y >= 0 else -1)
            self.canvas.axes.text(label1_x, label1_y, 'A₁', color=COLORS['accent1'],
                         fontsize=9, fontweight='bold', ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor=COLORS['accent1']))

        # 波形2标签
        if abs(phasor2_x) > 0.1 or abs(phasor2_y) > 0.1:
            label2_x = phasor2_x + label_offset * (1 if phasor2_x >= 0 else -1)
            label2_y = phasor2_y + label_offset * (1 if phasor2_y >= 0 else -1)
            self.canvas.axes.text(label2_x, label2_y, 'A₂', color=COLORS['accent2'],
                         fontsize=9, fontweight='bold', ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor=COLORS['accent2']))

        # 合成向量标签
        if abs(composite_x) > 0.1 or abs(composite_y) > 0.1:
            label_comp_x = composite_x + label_offset * 1.5 * (1 if composite_x >= 0 else -1)
            label_comp_y = composite_y + label_offset * 1.5 * (1 if composite_y >= 0 else -1)
            self.canvas.axes.text(label_comp_x, label_comp_y, 'A合成', color=COLORS['accent3'],
                         fontsize=9, fontweight='bold', ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor=COLORS['accent3']))

        # 添加简化的图例，放在左下角避免遮挡
        legend_elements = [
            plt.Line2D([0], [0], color=COLORS['accent1'], lw=2, label='波形1'),
            plt.Line2D([0], [0], color=COLORS['accent2'], lw=2, label='波形2'),
            plt.Line2D([0], [0], color=COLORS['accent3'], lw=3, label='合成波'),
            plt.Line2D([0], [0], color=COLORS['accent2'], lw=1, linestyle='--', label='向量和')
        ]
        self.canvas.axes.legend(handles=legend_elements, loc='lower left',
                       framealpha=0.9, fontsize=8, fancybox=True, shadow=True)

        # 刷新画布
        self.canvas.draw()
    
    def set_info(self, amplitude, phase):
        """设置振幅和相位信息"""
        self.info_label.setText(f"合成振幅: {amplitude:.2f}   合成相位: {phase:.2f} rad")


class PhaseCompositePanel(QWidget):
    """同向同频波形显示面板，包含原波形和合成波形"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 14pt; background-color: {COLORS['accent3']}; border-radius: 4px; padding: 5px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建画布
        self.canvas = MatplotlibCanvas(self)
        # 修改x轴范围，使y轴位于中间
        self.canvas.axes.set_xlim(-5, 5)
        self.canvas.axes.set_ylim(-2.5, 2.5)
        
        # 创建公式显示标签
        self.formula_label = QLabel("y = A₁sin(ωt + φ₁) + A₂sin(ωt + φ₂)")
        self.formula_label.setStyleSheet(f"color: {COLORS['accent3']}; font-weight: bold; font-size: 12pt; background-color: rgba(26, 58, 108, 180); border: 1px solid {COLORS['accent3']}; border-radius: 4px; padding: 8px;")
        self.formula_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.formula_label)
        
        self.setLayout(layout)
    
    def update_waves(self, t, wave1, wave2, composite, current_t_index=None):
        """更新波形显示"""
        self.canvas.axes.clear()
        # 修改x轴范围，使y轴位于中间
        self.canvas.axes.set_xlim(-5, 5)
        self.canvas.axes.set_ylim(-2.5, 2.5)
        self.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'])
        self.canvas.axes.set_ylabel('振幅', color=COLORS['text'])
        self.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 计算新的t值，使波形在-5到5范围内显示
        new_t = t - 5  # 将0-10映射到-5到5
        
        # 查找最接近x=0的数据点索引
        zero_index = np.argmin(np.abs(new_t))
        
        # 绘制第一个波形
        if len(wave1) > 0:
            self.canvas.axes.plot(new_t, wave1, color=COLORS['accent1'], linewidth=1.5, alpha=0.6, label='波形1')
        
        # 绘制第二个波形
        if len(wave2) > 0:
            self.canvas.axes.plot(new_t, wave2, color=COLORS['accent2'], linewidth=1.5, alpha=0.6, label='波形2')
        
        # 绘制合成波形
        if len(composite) > 0:
            self.canvas.axes.plot(new_t, composite, color=COLORS['accent3'], linewidth=2.0, label='合成波')
        
        # 绘制y轴（加粗显示）
        self.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)
        
        # 绘制当前位置 - 显示所有波形与y轴的交点
        if current_t_index is not None and current_t_index < len(t) and len(composite) > 0:
            # 使用波形当前计算得到的x=0处的真实值
            wave1_y = wave1[zero_index]
            wave2_y = wave2[zero_index]
            composite_y = composite[zero_index]
            
            # 显示波形1与y轴的交点
            self.canvas.axes.scatter([0], [wave1_y], 
                            color=COLORS['accent1'], s=80, zorder=4, edgecolor='white', linewidth=1)
            
            # 显示波形2与y轴的交点
            self.canvas.axes.scatter([0], [wave2_y], 
                            color=COLORS['accent2'], s=80, zorder=4, edgecolor='white', linewidth=1)
            
            # 显示合成波与y轴的交点（略大一些）
            self.canvas.axes.scatter([0], [composite_y], 
                            color=COLORS['accent4'], s=120, zorder=5, edgecolor='white', linewidth=1)
        
        # 添加图例
        self.canvas.axes.legend(loc='upper right', framealpha=0.7)
        
        # 刷新画布
        self.canvas.draw()


class PhaseHarmonicWindow(QMainWindow):
    """同向同频（相位差合成）主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("相位合成 - 同向同频简谐运动")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # 创建参数控制器
        self.params_controller = ParamsController()
        
        # 修改初始参数，设置相位差
        self.params_controller.set_param('phi2', np.pi/2)  # 设置90度相位差
        self.params_controller.set_param('omega1', 1.0)    # 设置频率为1.0
        self.params_controller.set_param('omega2', 1.0)    # 设置频率为1.0
        
        # 创建动画控制器
        self.animation_controller = PhaseAnimationController(self.params_controller)
        
        # 创建UI组件
        self.setup_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化动画数据
        self.animation_controller.initialize_data()
        
        # 首次更新波形显示
        self.update_plots()
    
    def setup_ui(self):
        """设置UI布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分隔器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 使用新的相位差专用控制面板
        self.control_panel = PhaseControlPanel()
        
        # 锁定频率滑块，防止用户修改
        self.control_panel.w1_slider.slider.setEnabled(False)
        self.control_panel.w2_slider.slider.setEnabled(False)
        
        # 添加频率锁定指示器
        freq_lock_label = QLabel("频率已锁定: ω1 = ω2 = 1.0")
        freq_lock_label.setStyleSheet(f"color: {COLORS['text']}; background-color: {COLORS['accent3']}; font-weight: bold; font-size: 12pt; padding: 5px; margin: 5px;")
        freq_lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.control_panel.layout().insertWidget(1, freq_lock_label)
        
        splitter.addWidget(self.control_panel)
        
        # 创建右侧部分
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建波形显示面板
        self.wave_panel = PhaseCompositePanel("相位差合成波形")
        
        # 创建相量图面板
        self.phasor_panel = PhasorPanel()
        
        # 添加到布局
        right_layout.addWidget(self.wave_panel, 3)
        right_layout.addWidget(self.phasor_panel, 2)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # 设置分隔器大小策略
        splitter.setSizes([300, 900])
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {COLORS['border']}; }}")
        
        main_layout.addWidget(splitter)
        
        # 添加退出按钮
        from ui.ui_framework import AnimatedButton
        
        # 创建退出按钮
        self.exit_btn = AnimatedButton("退出", COLORS['accent5'])
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setFixedSize(100, 40)
        self.exit_btn.setStyleSheet(f"""
            font-weight: bold; 
            font-size: 14px;
            border: none;
            border-radius: 5px;
        """)
        
        # 将退出按钮添加到控制面板的底部
        self.control_panel.layout().addWidget(self.exit_btn)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接参数控制器信号
        self.params_controller.params_changed.connect(self.on_params_changed)
        
        # 连接动画控制器信号
        self.animation_controller.update_signal.connect(self.update_plots)
        
        # 连接控制面板的滑块信号
        self.control_panel.a1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('A1', self.control_panel.a1_slider.get_value()))
        self.control_panel.w1_slider.slider.valueChanged.connect(self.on_omega_changed)  # 特殊处理保持同频
        self.control_panel.p1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi1', self.control_panel.p1_slider.get_value()))
        self.control_panel.a2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('A2', self.control_panel.a2_slider.get_value()))
        self.control_panel.p2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi2', self.control_panel.p2_slider.get_value()))
        self.control_panel.speed_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('speed', self.control_panel.speed_slider.get_value()))
        self.control_panel.trail_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('trail_length', int(self.control_panel.trail_slider.get_value())))
        
        # 连接按钮信号
        self.control_panel.play_btn.clicked.connect(self.on_play_clicked)
        self.control_panel.pause_btn.clicked.connect(self.on_pause_clicked)
        self.control_panel.reset_btn.clicked.connect(self.on_reset_clicked)
    
    def update_plots(self):
        """更新波形图和相量图"""
        t = self.animation_controller.t
        
        # 计算当前时间指针
        current_t_index = int(len(t) * (self.animation_controller.time_counter % 10) / 10)
        
        # 更新波形面板
        self.wave_panel.update_waves(
            t,
            self.animation_controller.wave1_data,
            self.animation_controller.wave2_data,
            self.animation_controller.composite_data,
            current_t_index
        )
        
        # 更新相量图
        self.phasor_panel.update_phasors(
            self.animation_controller.phasor1_x,
            self.animation_controller.phasor1_y,
            self.animation_controller.phasor2_x,
            self.animation_controller.phasor2_y,
            self.animation_controller.composite_x,
            self.animation_controller.composite_y
        )
        
        # 更新振幅和相位信息
        amplitude, phase = self.animation_controller.calculate_composite_amplitude()
        self.phasor_panel.set_info(amplitude, phase)
    
    @pyqtSlot()
    def on_params_changed(self):
        """参数变化时更新波形"""
        # 强制保持频率相等
        params = self.params_controller.get_params()
        if params['omega1'] != 1.0 or params['omega2'] != 1.0:
            self.params_controller.set_param('omega1', 1.0)
            self.params_controller.set_param('omega2', 1.0)
            # 更新滑块位置
            self.control_panel.w1_slider.set_value(1.0)
            self.control_panel.w2_slider.set_value(1.0)
        
        if self.animation_controller.is_paused:
            self.animation_controller.calculate_waves(self.animation_controller.time_counter)
            self.animation_controller.current_position = self.animation_controller.calculate_current_position(
                self.animation_controller.time_counter)
            self.update_plots()
    
    def on_omega_changed(self):
        """频率变化时保持两个波形频率相同"""
        value = self.control_panel.w1_slider.get_value()
        self.params_controller.set_param('omega1', value)
        self.params_controller.set_param('omega2', value)  # 同步更新第二个波的频率
    
    @pyqtSlot(str, object)
    def on_slider_changed(self, param_name, value):
        """滑块值变化时的处理"""
        self.params_controller.set_param(param_name, value)
    
    @pyqtSlot()
    def on_play_clicked(self):
        """播放按钮点击事件"""
        self.animation_controller.play()
        self.control_panel.play_btn.set_active(True)
        self.control_panel.pause_btn.set_active(False)
    
    @pyqtSlot()
    def on_pause_clicked(self):
        """暂停按钮点击事件"""
        self.animation_controller.pause()
        self.control_panel.play_btn.set_active(False)
        self.control_panel.pause_btn.set_active(True)
    
    @pyqtSlot()
    def on_reset_clicked(self):
        """重置按钮点击事件"""
        self.params_controller.reset_params()
        # 确保频率始终为1.0
        self.params_controller.set_param('omega1', 1.0)
        self.params_controller.set_param('omega2', 1.0)
        # 恢复相位差设置
        self.params_controller.set_param('phi2', np.pi/2)
        self.params_controller.update_ui_from_params(self.control_panel)
        # 重新禁用频率滑块
        self.control_panel.w1_slider.slider.setEnabled(False)
        self.control_panel.w2_slider.slider.setEnabled(False)
        self.animation_controller.reset()


def main():
    """程序入口"""
    app = get_app_instance()
    
    # 创建主窗口
    window = PhaseHarmonicWindow()
    window.show()
    
    # 只有在直接运行此模块时才执行事件循环
    if __name__ == "__main__":
        sys.exit(app.exec())
        
    # 返回窗口实例，以便启动器能追踪它
    return window 