# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 垂直简谐运动（不同向不同频）主程序
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

from ui.ui_framework import WavePanel, LissajousPanel, ControlPanel, COLORS, get_app_instance, AnimatedButton
from animations.orthogonal_animation import OrthogonalAnimationController
from ui.params_controller import ParamsController


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
        """设置UI布局 - L型布局设计"""
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

        # 创建绘图部分的容器，使用网格布局实现L型排列
        plots_container = QWidget()
        plots_layout = QGridLayout(plots_container)
        plots_layout.setSpacing(5)  # 设置间距

        # 创建Y方向波形面板（左侧，垂直显示）
        self.y_wave_panel = WavePanel("Y方向振动", COLORS['accent2'])
        self.y_wave_panel.set_formula("y = A₂sin(ω₂t + φ₂)")
        # Y方向波形需要旋转90度显示，时间轴变为垂直方向
        self.y_wave_panel.canvas.axes.set_xlim(-1.2, 1.2)  # X轴现在表示Y振幅
        self.y_wave_panel.canvas.axes.set_ylim(-5, 5)      # Y轴现在表示时间
        self.y_wave_panel.canvas.axes.set_xlabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')
        self.y_wave_panel.canvas.axes.set_ylabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        # 绘制时间轴中心线（水平线，y=0）
        self.y_wave_panel.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)

        # 创建李萨如图形面板（右上角）
        self.lissajous_panel = LissajousPanel()
        self.lissajous_panel.set_ratio("ω₂:ω₁ = 2:1")
        self.lissajous_panel.canvas.axes.set_xlim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_ylim(-1.2, 1.2)

        # 添加坐标轴
        self.lissajous_panel.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', alpha=0.5)
        self.lissajous_panel.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', alpha=0.5)
        self.lissajous_panel.canvas.axes.set_xlabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        self.lissajous_panel.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')

        # 创建X方向波形面板（下方）
        self.x_wave_panel = WavePanel("X方向振动", COLORS['accent1'])
        self.x_wave_panel.set_formula("x = A₁sin(ω₁t + φ₁)")
        self.x_wave_panel.canvas.axes.set_xlim(-5, 5)      # X轴表示时间
        self.x_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)  # Y轴表示X振幅
        self.x_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.x_wave_panel.canvas.axes.set_ylabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        # 绘制时间轴中心线（垂直线，x=0）
        self.x_wave_panel.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)

        # 创建空白占位符（左下角）
        placeholder = QWidget()
        placeholder.setMinimumSize(50, 50)
        placeholder.setStyleSheet(f"background-color: {COLORS['background']};")

        # 使用网格布局排列组件，形成L型布局
        # 第0行：Y波形面板(0,0) + 李萨如图形面板(0,1)
        # 第1行：占位符(1,0) + X波形面板(1,1)
        plots_layout.addWidget(self.y_wave_panel, 0, 0)
        plots_layout.addWidget(self.lissajous_panel, 0, 1)
        plots_layout.addWidget(placeholder, 1, 0)
        plots_layout.addWidget(self.x_wave_panel, 1, 1)

        # 设置行列比例，确保李萨如图形和波形图有合适的大小
        plots_layout.setRowStretch(0, 2)  # 上行占2/3
        plots_layout.setRowStretch(1, 1)  # 下行占1/3
        plots_layout.setColumnStretch(0, 1)  # 左列占1/3
        plots_layout.setColumnStretch(1, 2)  # 右列占2/3

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
        
        # 添加退出按钮
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
        """更新所有图表 - L型布局版本"""
        t = self.animation_controller.t
        x_data = self.animation_controller.x_data
        y_data = self.animation_controller.y_data

        # 获取当前时间和李萨如坐标点
        current_t = self.animation_controller.time_counter
        current_x = self.animation_controller.current_x
        current_y = self.animation_controller.current_y

        # 计算新的t值，使波形在-5到5范围内显示
        new_t = t - 5  # 将0-10映射到-5到5

        # 查找最接近纵轴(x=0)的点索引
        zero_index = np.argmin(np.abs(new_t))

        # 确保使用波形图上的实际交点值
        if len(x_data) > 0 and zero_index < len(x_data):
            x_at_zero = x_data[zero_index]
        else:
            x_at_zero = current_x

        if len(y_data) > 0 and zero_index < len(y_data):
            y_at_zero = y_data[zero_index]
        else:
            y_at_zero = current_y

        # 确保动画控制器中的当前点与波形上的交点一致
        self.animation_controller.current_x = x_at_zero
        self.animation_controller.current_y = y_at_zero

        # 添加当前点到轨迹
        params = self.params_controller.get_params()
        max_trail_length = int(params.get('trail_length', 100))

        # 只有在动画播放状态才添加轨迹点
        if not self.animation_controller.is_paused:
            self.animation_controller.trail_points[0].append(x_at_zero)
            self.animation_controller.trail_points[1].append(y_at_zero)

            # 裁剪轨迹长度
            if len(self.animation_controller.trail_points[0]) > max_trail_length:
                self.animation_controller.trail_points[0] = self.animation_controller.trail_points[0][-max_trail_length:]
                self.animation_controller.trail_points[1] = self.animation_controller.trail_points[1][-max_trail_length:]
        
        # 更新X方向波形（下方，水平显示）
        self.x_wave_panel.canvas.axes.clear()
        self.x_wave_panel.canvas.axes.set_xlim(-5, 5)
        self.x_wave_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.x_wave_panel.canvas.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.x_wave_panel.canvas.axes.set_ylabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        self.x_wave_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)

        # 绘制时间轴中心线（垂直线，x=0）
        self.x_wave_panel.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=1.5, alpha=0.7)

        # 绘制X方向波形
        if len(x_data) > 0:
            self.x_wave_panel.canvas.axes.plot(new_t, x_data, color=COLORS['accent1'], linewidth=2.0)

            # 在时间轴处显示当前点 - 使用实际波形数据上的交点
            self.x_wave_panel.canvas.axes.scatter([0], [x_at_zero], color=COLORS['accent4'], s=100, zorder=3)

            # 绘制从当前点到李萨如图形的辅助线（水平投影）
            # 这条线表示当前X振幅值对应到李萨如图形的X坐标
            self.x_wave_panel.canvas.axes.axhline(y=x_at_zero, color=COLORS['accent1'], linestyle='--', alpha=0.5, linewidth=1)
        
        # 更新Y方向波形（左侧，垂直显示）
        self.y_wave_panel.canvas.axes.clear()
        self.y_wave_panel.canvas.axes.set_xlim(-1.2, 1.2)  # X轴现在表示Y振幅
        self.y_wave_panel.canvas.axes.set_ylim(-5, 5)      # Y轴现在表示时间
        self.y_wave_panel.canvas.axes.set_xlabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')
        self.y_wave_panel.canvas.axes.set_ylabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.y_wave_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)

        # 绘制时间轴中心线（水平线，y=0）
        self.y_wave_panel.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', linewidth=1.5, alpha=0.7)

        # 绘制Y方向波形（旋转90度：Y振幅作为X坐标，时间作为Y坐标）
        if len(y_data) > 0:
            self.y_wave_panel.canvas.axes.plot(y_data, new_t, color=COLORS['accent2'], linewidth=2.0)

            # 在时间轴处显示当前点 - 使用实际波形数据上的交点
            self.y_wave_panel.canvas.axes.scatter([y_at_zero], [0], color=COLORS['accent4'], s=100, zorder=3)

            # 绘制从当前点到李萨如图形的辅助线（垂直投影）
            # 这条线表示当前Y振幅值对应到李萨如图形的Y坐标
            self.y_wave_panel.canvas.axes.axvline(x=y_at_zero, color=COLORS['accent2'], linestyle='--', alpha=0.5, linewidth=1)
        
        # 更新李萨如图形（右上角）
        self.lissajous_panel.canvas.axes.clear()
        self.lissajous_panel.canvas.axes.set_xlim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_ylim(-1.2, 1.2)
        self.lissajous_panel.canvas.axes.set_xlabel('X振幅', color=COLORS['text'], fontfamily='SimHei')
        self.lissajous_panel.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'], fontfamily='SimHei')
        self.lissajous_panel.canvas.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)

        # 绘制坐标轴
        self.lissajous_panel.canvas.axes.axhline(y=0, color=COLORS['text'], linestyle='-', alpha=0.5)
        self.lissajous_panel.canvas.axes.axvline(x=0, color=COLORS['text'], linestyle='-', alpha=0.5)

        # 绘制李萨如图形轨迹 - 静态曲线
        lissajous_x = self.animation_controller.lissajous_x
        lissajous_y = self.animation_controller.lissajous_y

        if len(lissajous_x) > 0 and len(lissajous_y) > 0:
            self.lissajous_panel.canvas.axes.plot(lissajous_x, lissajous_y, color=COLORS['accent3'], alpha=0.3, linewidth=1.0)

        # 绘制动态轨迹
        trail_x = self.animation_controller.trail_points[0]
        trail_y = self.animation_controller.trail_points[1]

        if len(trail_x) > 0 and len(trail_y) > 0:
            # 绘制完整轨迹
            self.lissajous_panel.canvas.axes.plot(trail_x, trail_y, color=COLORS['accent5'], alpha=0.7, linewidth=1.5)

            # 让最新部分的轨迹更亮
            if len(trail_x) > 5:
                self.lissajous_panel.canvas.axes.plot(
                    trail_x[-5:],
                    trail_y[-5:],
                    color=COLORS['accent5'],
                    alpha=1.0,
                    linewidth=2.0
                )

        # 绘制当前点 - 使用波形与时间轴的交点值
        self.lissajous_panel.canvas.axes.scatter([x_at_zero], [y_at_zero], color=COLORS['accent4'], s=120, zorder=4, edgecolor='white', linewidth=1)

        # 绘制增强的辅助线，显示与波形图的对应关系
        # X方向投影线（垂直虚线，连接到下方X波形图）
        self.lissajous_panel.canvas.axes.axvline(x=x_at_zero, color=COLORS['accent1'], linestyle='--', alpha=0.7, linewidth=1.5)
        # Y方向投影线（水平虚线，连接到左侧Y波形图）
        self.lissajous_panel.canvas.axes.axhline(y=y_at_zero, color=COLORS['accent2'], linestyle='--', alpha=0.7, linewidth=1.5)

        # 绘制坐标指示线（从原点到当前点的投影）
        self.lissajous_panel.canvas.axes.plot([x_at_zero, x_at_zero], [-1.2, 0], color=COLORS['accent1'], alpha=0.3, linewidth=1)
        self.lissajous_panel.canvas.axes.plot([-1.2, 0], [y_at_zero, y_at_zero], color=COLORS['accent2'], alpha=0.3, linewidth=1)
        
        # 刷新所有画布
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
        
        # 清空轨迹数据，避免出现不必要的连线
        self.animation_controller.trail_points = [[], []]
        
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
        print("动画播放中...")  # 添加调试输出
    
    @pyqtSlot()
    def on_pause_clicked(self):
        """暂停按钮点击事件"""
        self.animation_controller.pause()
        self.control_panel.play_btn.set_active(False)
        self.control_panel.pause_btn.set_active(True)
        print("动画已暂停")  # 添加调试输出
    
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
        
        # 清空轨迹数据，避免出现不必要的连线
        self.animation_controller.trail_points = [[], []]
        
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