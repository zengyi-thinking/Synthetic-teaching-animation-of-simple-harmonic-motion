# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 垂直简谐运动（不同向不同频）主程序
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

from ui_framework import WavePanel, LissajousPanel, ControlPanel, COLORS, get_app_instance
from orthogonal_animation import OrthogonalAnimationController
from params_controller import ParamsController


class OrthogonalHarmonicWindow(QMainWindow):
    """垂直简谐运动（不同向不同频）主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("李萨如图形 - 不同向不同频简谐运动")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # 创建参数控制器
        self.params_controller = ParamsController()
        
        # 创建动画控制器
        self.animation_controller = OrthogonalAnimationController(self.params_controller)
        
        # 创建UI组件
        self.setup_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化动画数据
        self.animation_controller.initialize_data()
        self.update_plots()
        
        # 更新频率比显示
        self.update_ratio_display()
    
    def setup_ui(self):
        """设置UI布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分隔器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建控制面板
        self.control_panel = ControlPanel()
        splitter.addWidget(self.control_panel)
        
        # 创建绘图部分的容器
        plots_container = QWidget()
        plots_layout = QHBoxLayout(plots_container)
        
        # 创建垂直分隔器用于放置X和Y波形图
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 创建X方向波形面板
        self.x_wave_panel = WavePanel("X方向振动", COLORS['accent1'])
        self.x_wave_panel.set_formula("x = A₁sin(ω₁t + φ₁)")
        self.x_wave_panel.canvas.axes.set_xlim(0, 10)
        self.x_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.x_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'])
        self.x_wave_panel.canvas.axes.set_ylabel('X振幅', color=COLORS['text'])
        
        # 创建Y方向波形面板
        self.y_wave_panel = WavePanel("Y方向振动", COLORS['accent2'])
        self.y_wave_panel.set_formula("y = A₂sin(ω₂t + φ₂)")
        self.y_wave_panel.canvas.axes.set_xlim(0, 10)
        self.y_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.y_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'])
        self.y_wave_panel.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'])
        
        vertical_splitter.addWidget(self.x_wave_panel)
        vertical_splitter.addWidget(self.y_wave_panel)
        
        # 创建李萨如图形面板
        self.lissajous_panel = LissajousPanel()
        self.lissajous_panel.set_ratio("ω₂:ω₁ = 2:1")
        self.lissajous_panel.canvas.axes.set_xlim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_ylim(-1.2, 1.2)
        
        # 添加到布局
        plots_layout.addWidget(vertical_splitter, 1)
        plots_layout.addWidget(self.lissajous_panel, 1)
        
        splitter.addWidget(plots_container)
        
        # 设置分隔器大小策略
        splitter.setSizes([300, 900])
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['border']};
            }}
        """)
        
        main_layout.addWidget(splitter)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接参数控制器信号
        self.params_controller.params_changed.connect(self.on_params_changed)
        self.params_controller.ratio_changed.connect(self.on_ratio_changed)
        
        # 连接动画控制器信号
        self.animation_controller.update_signal.connect(self.update_plots)
        
        # 连接控制面板的滑块信号
        self.control_panel.a1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('A1', self.control_panel.a1_slider.get_value()))
        self.control_panel.w1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('omega1', self.control_panel.w1_slider.get_value()))
        self.control_panel.p1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi1', self.control_panel.p1_slider.get_value()))
        self.control_panel.a2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('A2', self.control_panel.a2_slider.get_value()))
        self.control_panel.w2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('omega2', self.control_panel.w2_slider.get_value()))
        self.control_panel.p2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi2', self.control_panel.p2_slider.get_value()))
        self.control_panel.speed_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('speed', self.control_panel.speed_slider.get_value()))
        self.control_panel.trail_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('trail_length', int(self.control_panel.trail_slider.get_value())))
        
        # 连接按钮信号
        self.control_panel.play_btn.clicked.connect(self.on_play_clicked)
        self.control_panel.pause_btn.clicked.connect(self.on_pause_clicked)
        self.control_panel.reset_btn.clicked.connect(self.on_reset_clicked)
        self.control_panel.w1_fixed_btn.clicked.connect(lambda: self.on_ratio_mode_changed('w1'))
        self.control_panel.w2_fixed_btn.clicked.connect(lambda: self.on_ratio_mode_changed('w2'))
        
        # 连接频率比预设按钮
        for ratio_key, button in self.control_panel.ratio_buttons.items():
            button.clicked.connect(lambda checked=False, r=ratio_key: self.on_ratio_button_clicked(r))
    
    @pyqtSlot()
    def update_plots(self):
        """更新所有图表"""
        # 更新X方向波形
        self.x_wave_panel.canvas.axes.clear()
        self.x_wave_panel.canvas.axes.set_xlim(0, 10)
        self.x_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.x_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.x_wave_panel.canvas.axes.set_ylabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        self.x_wave_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        t = self.animation_controller.t
        if len(self.animation_controller.x_data) > 0:
            self.x_wave_panel.canvas.axes.plot(t, self.animation_controller.x_data, color=COLORS['accent1'], linewidth=2.0)
            current_t_index = int(len(t) * (self.animation_controller.time_counter % 10) / 10)
            if current_t_index < len(t):
                self.x_wave_panel.canvas.axes.scatter(t[current_t_index], self.animation_controller.x_data[current_t_index], 
                                               color=COLORS['accent4'], s=80, zorder=3)
        
        # 更新Y方向波形
        self.y_wave_panel.canvas.axes.clear()
        self.y_wave_panel.canvas.axes.set_xlim(0, 10)
        self.y_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.y_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.y_wave_panel.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')
        self.y_wave_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        if len(self.animation_controller.y_data) > 0:
            self.y_wave_panel.canvas.axes.plot(t, self.animation_controller.y_data, color=COLORS['accent2'], linewidth=2.0)
            current_t_index = int(len(t) * (self.animation_controller.time_counter % 10) / 10)
            if current_t_index < len(t):
                self.y_wave_panel.canvas.axes.scatter(t[current_t_index], self.animation_controller.y_data[current_t_index], 
                                               color=COLORS['accent4'], s=80, zorder=3)
        
        # 更新李萨如图形
        self.lissajous_panel.canvas.axes.clear()
        self.lissajous_panel.canvas.axes.set_xlim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_xlabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        self.lissajous_panel.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')
        self.lissajous_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        self.lissajous_panel.canvas.axes.set_aspect('equal')
        
        # 绘制完整李萨如图形
        if len(self.animation_controller.lissajous_x) > 0:
            self.lissajous_panel.canvas.axes.plot(self.animation_controller.lissajous_x, 
                                           self.animation_controller.lissajous_y, 
                                           color=COLORS['accent3'], linewidth=1.5, alpha=0.5)
        
        # 绘制轨迹
        if len(self.animation_controller.trail_points[0]) > 0:
            self.lissajous_panel.canvas.axes.plot(self.animation_controller.trail_points[0], 
                                           self.animation_controller.trail_points[1], 
                                           color=COLORS['accent5'], linewidth=2.0)
        
        # 绘制当前点
        self.lissajous_panel.canvas.axes.scatter([self.animation_controller.current_x], 
                                          [self.animation_controller.current_y], 
                                          color=COLORS['accent4'], s=100, zorder=3)
        
        # 刷新画布
        self.x_wave_panel.canvas.draw()
        self.y_wave_panel.canvas.draw()
        self.lissajous_panel.canvas.draw()
    
    @pyqtSlot()
    def on_params_changed(self):
        """参数变化时更新图形"""
        self.animation_controller.calculate_lissajous_figure()
        self.update_ratio_display()
        if self.animation_controller.is_paused:
            self.animation_controller.current_x, self.animation_controller.current_y = self.animation_controller.calculate_current_position(self.animation_controller.time_counter)
            self.animation_controller.x_data = self.animation_controller.calculate_wave_x(self.animation_controller.time_counter)
            self.animation_controller.y_data = self.animation_controller.calculate_wave_y(self.animation_controller.time_counter)
            self.update_plots()
    
    def update_ratio_display(self):
        """更新频率比显示"""
        w2_ratio, w1_ratio, ratio_text = self.animation_controller.calculate_frequency_ratio()
        self.lissajous_panel.set_ratio(ratio_text)
    
    @pyqtSlot(str)
    def on_ratio_changed(self, ratio_key):
        """频率比预设变化时的处理"""
        # 打印调试信息
        print(f"频率比变化: {ratio_key}")
        
        # 更新按钮状态
        for key, button in self.control_panel.ratio_buttons.items():
            if key == ratio_key:
                button.set_background_color(COLORS['accent3'])
            else:
                button.set_background_color(COLORS['panel'])
        
        # 调整频率
        new_w1, new_w2 = self.animation_controller.adjust_frequency_for_ratio(ratio_key)
        
        # 更新滑块和参数
        self.control_panel.w1_slider.set_value(new_w1)
        self.control_panel.w2_slider.set_value(new_w2)
        self.params_controller.set_param('omega1', new_w1)
        self.params_controller.set_param('omega2', new_w2)
        
        # 强制重新计算李萨如图形
        self.animation_controller.calculate_lissajous_figure()
        self.update_ratio_display()
        self.update_plots()
    
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
        self.params_controller.update_ui_from_params(self.control_panel)
        self.animation_controller.reset()
        self.update_ratio_display()
        
        # 更新比率按钮
        for key, button in self.control_panel.ratio_buttons.items():
            if key == self.params_controller.params['ratio_preset']:
                button.set_background_color(COLORS['accent3'])
            else:
                button.set_background_color(COLORS['panel'])
        
        # 更新模式按钮
        if self.params_controller.params['ratio_mode'] == 'w1':
            self.control_panel.w1_fixed_btn.set_active(True)
            self.control_panel.w2_fixed_btn.set_active(False)
        else:
            self.control_panel.w1_fixed_btn.set_active(False)
            self.control_panel.w2_fixed_btn.set_active(True)
    
    @pyqtSlot(str)
    def on_ratio_button_clicked(self, ratio_key):
        """频率比按钮点击事件"""
        print(f"点击频率比按钮: {ratio_key}")
        
        # 更新所有按钮状态
        for key, button in self.control_panel.ratio_buttons.items():
            if key == ratio_key:
                button.set_background_color(COLORS['accent3'])
            else:
                button.set_background_color(COLORS['panel'])
        
        # 设置频率比预设并触发相应事件
        self.params_controller.set_ratio_preset(ratio_key)
        
        # 如果信号没有正确触发，直接调用处理函数
        self.on_ratio_changed(ratio_key)
    
    @pyqtSlot(str)
    def on_ratio_mode_changed(self, mode):
        """频率比模式切换事件"""
        self.params_controller.set_ratio_mode(mode)
        if mode == 'w1':
            self.control_panel.w1_fixed_btn.set_active(True)
            self.control_panel.w2_fixed_btn.set_active(False)
        else:
            self.control_panel.w1_fixed_btn.set_active(False)
            self.control_panel.w2_fixed_btn.set_active(True)


def main():
    """程序入口"""
    app = get_app_instance()
    
    # 创建主窗口
    window = OrthogonalHarmonicWindow()
    window.show()
    
    # 只有在直接运行此模块时才执行事件循环
    if __name__ == "__main__":
        sys.exit(app.exec())
        
    # 返回窗口实例，以便启动器能追踪它
    return window


if __name__ == "__main__":
    main() 