# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 同向不同频（拍现象）主程序
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QColor

from ui_framework import WavePanel, ControlPanel, MatplotlibCanvas, COLORS, get_app_instance
from beat_animation import BeatAnimationController
from params_controller import ParamsController


class BeatWavePanel(QWidget):
    """同向不同频波形显示面板，包含三个独立图形显示两个基础波和合成波"""
    
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标题标签
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 14pt;
            background-color: {color};
            border-radius: 4px;
            padding: 5px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建三个图形的容器
        plots_container = QWidget()
        plots_layout = QVBoxLayout(plots_container)
        plots_layout.setSpacing(10)  # 设置图形之间的间距
        
        # 创建第一个波形画布 - 波形1
        self.canvas1 = MatplotlibCanvas(self)
        self.canvas1.axes.set_xlim(-5, 5)
        self.canvas1.axes.set_ylim(-1.5, 1.5)
        self.canvas1.axes.set_title("波形1", color=COLORS['accent1'], fontsize=12, fontfamily='SimHei')
        self.canvas1.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas1.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas1.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 创建第二个波形画布 - 波形2
        self.canvas2 = MatplotlibCanvas(self)
        self.canvas2.axes.set_xlim(-5, 5)
        self.canvas2.axes.set_ylim(-1.5, 1.5)
        self.canvas2.axes.set_title("波形2", color=COLORS['accent2'], fontsize=12, fontfamily='SimHei')
        self.canvas2.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas2.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas2.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 创建第三个波形画布 - 合成波
        self.canvas3 = MatplotlibCanvas(self)
        self.canvas3.axes.set_xlim(-5, 5)
        self.canvas3.axes.set_ylim(-2.5, 2.5)
        self.canvas3.axes.set_title("合成波", color=COLORS['accent3'], fontsize=12, fontfamily='SimHei')
        self.canvas3.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas3.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas3.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 添加画布到布局
        plots_layout.addWidget(self.canvas1, 1)
        plots_layout.addWidget(self.canvas2, 1)
        plots_layout.addWidget(self.canvas3, 2)  # 合成波图形略大
        
        # 创建公式显示标签
        self.formula_label = QLabel()
        self.formula_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 12pt;
            background-color: rgba(26, 58, 108, 180);
            border: 1px solid {color};
            border-radius: 4px;
            padding: 8px;
        """)
        self.formula_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(plots_container)
        layout.addWidget(self.formula_label)
        
        self.setLayout(layout)
    
    def set_formula(self, formula):
        """设置公式文本"""
        self.formula_label.setText(formula)
    
    def update_waves(self, t, wave1, wave2, composite, envelope_up=None, envelope_down=None, current_t_index=None):
        """更新三个波形图"""
        # 计算新的t值，使波形在-5到5范围内显示
        new_t = t - 5  # 将0-10映射到-5到5
        
        # 查找最接近x=0的数据点索引
        zero_index = np.argmin(np.abs(new_t))
        
        # 获取波形在y轴上的真实值
        if len(wave1) > 0 and zero_index < len(wave1):
            wave1_y = wave1[zero_index]
        else:
            wave1_y = 0
            
        if len(wave2) > 0 and zero_index < len(wave2):
            wave2_y = wave2[zero_index]
        else:
            wave2_y = 0
            
        if len(composite) > 0 and zero_index < len(composite):
            composite_y = composite[zero_index]
        else:
            composite_y = 0
        
        # 更新第一个波形 - 波形1
        self.canvas1.axes.clear()
        self.canvas1.axes.set_xlim(-5, 5)
        self.canvas1.axes.set_ylim(-1.5, 1.5)
        self.canvas1.axes.set_title("波形1", color=COLORS['accent1'], fontsize=12, fontfamily='SimHei')
        self.canvas1.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas1.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas1.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 绘制y轴（加粗显示）
        self.canvas1.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)
        
        if len(wave1) > 0:
            self.canvas1.axes.plot(new_t, wave1, color=COLORS['accent1'], linewidth=2.0)
            # 在y轴处绘制波形1的交点
            if current_t_index is not None:
                self.canvas1.axes.scatter([0], [wave1_y], 
                                 color=COLORS['accent1'], s=100, zorder=3, edgecolor='white', linewidth=1)
        
        # 更新第二个波形 - 波形2
        self.canvas2.axes.clear()
        self.canvas2.axes.set_xlim(-5, 5)
        self.canvas2.axes.set_ylim(-1.5, 1.5)
        self.canvas2.axes.set_title("波形2", color=COLORS['accent2'], fontsize=12, fontfamily='SimHei')
        self.canvas2.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas2.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas2.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 绘制y轴（加粗显示）
        self.canvas2.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)
        
        if len(wave2) > 0:
            self.canvas2.axes.plot(new_t, wave2, color=COLORS['accent2'], linewidth=2.0)
            # 在y轴处绘制波形2的交点
            if current_t_index is not None:
                self.canvas2.axes.scatter([0], [wave2_y], 
                                 color=COLORS['accent2'], s=100, zorder=3, edgecolor='white', linewidth=1)
        
        # 更新第三个波形 - 合成波
        self.canvas3.axes.clear()
        self.canvas3.axes.set_xlim(-5, 5)
        self.canvas3.axes.set_ylim(-2.5, 2.5)
        self.canvas3.axes.set_title("合成波", color=COLORS['accent3'], fontsize=12, fontfamily='SimHei')
        self.canvas3.axes.set_xlabel('时间 (s)', color=COLORS['text'], fontfamily='SimHei')
        self.canvas3.axes.set_ylabel('振幅', color=COLORS['text'], fontfamily='SimHei')
        self.canvas3.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        
        # 绘制y轴（加粗显示）
        self.canvas3.axes.axvline(x=0, color=COLORS['text'], linestyle='-', linewidth=2, alpha=0.7)
        
        if len(composite) > 0:
            self.canvas3.axes.plot(new_t, composite, color=COLORS['accent3'], linewidth=2.0)
            
            # 绘制包络线
            if envelope_up is not None and len(envelope_up) > 0:
                self.canvas3.axes.plot(new_t, envelope_up, color=COLORS['accent5'], linewidth=1.5, linestyle='--')
            
            if envelope_down is not None and len(envelope_down) > 0:
                self.canvas3.axes.plot(new_t, envelope_down, color=COLORS['accent5'], linewidth=1.5, linestyle='--')
            
            # 在y轴处绘制合成波的交点
            if current_t_index is not None:
                self.canvas3.axes.scatter([0], [composite_y], 
                                 color=COLORS['accent4'], s=120, zorder=3, edgecolor='white', linewidth=1)
        
        # 刷新所有画布
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()


class BeatHarmonicWindow(QMainWindow):
    """同向不同频（拍现象）主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("拍现象 - 同向不同频简谐运动")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # 创建参数控制器
        self.params_controller = ParamsController()
        
        # 修改初始参数，使频率更接近，以便清晰观察拍现象
        self.params_controller.set_param('omega1', 5.0)  # 设置较高频率
        self.params_controller.set_param('omega2', 4.7)  # 设置轻微不同的频率
        
        # 创建动画控制器
        self.animation_controller = BeatAnimationController(self.params_controller)
        
        # 创建UI组件
        self.setup_ui()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化动画数据
        self.animation_controller.initialize_data()
        
        # 首次更新波形显示
        self.update_beat_info()
        self.update_plots()
        
        # 默认开始动画 - 自动播放以确保动态效果
        QTimer.singleShot(500, self.animation_controller.play)
        QTimer.singleShot(500, lambda: self.control_panel.play_btn.set_active(True))
    
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
        
        # 调整控制面板，确保频率比控制可见
        freq_ratio_control = self.control_panel.findChild(QGroupBox, "频率比控制")
        
        # 更新控制面板中的标签
        x_params = self.control_panel.findChild(QGroupBox, "X方向参数")
        y_params = self.control_panel.findChild(QGroupBox, "Y方向参数")
        
        if x_params:
            x_params.setTitle("波形1参数")
        if y_params:
            y_params.setTitle("波形2参数")
        
        # 确保频率比按钮组件的可见性
        if freq_ratio_control:
            freq_ratio_control.setVisible(True)
        
        splitter.addWidget(self.control_panel)
        
        # 创建右侧部分
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)  # 增加垂直间距
        
        # 创建波形面板
        self.wave_panel = BeatWavePanel("拍现象波形", COLORS['accent3'])
        self.wave_panel.set_formula("y = A₁sin(ω₁t + φ₁) + A₂sin(ω₂t + φ₂)")
        
        # 创建拍频信息面板
        self.info_panel = QWidget()
        self.info_panel.setMinimumHeight(60)  # 设置最小高度
        self.info_panel.setMaximumHeight(80)  # 设置最大高度，防止过大
        
        info_layout = QHBoxLayout(self.info_panel)
        info_layout.setSpacing(15)  # 增加水平间距
        
        self.beat_freq_label = QLabel("拍频: 0.00 Hz")
        self.beat_period_label = QLabel("拍周期: 0.00 s") 
        self.main_freq_label = QLabel("主频: 0.00 Hz")
        
        for label in [self.beat_freq_label, self.beat_period_label, self.main_freq_label]:
            label.setStyleSheet(f"""
                color: {COLORS['accent5']};
                font-weight: bold;
                font-size: 12pt;
                background-color: rgba(26, 58, 108, 180);
                border: 1px solid {COLORS['accent5']};
                border-radius: 4px;
                padding: 8px;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(self.beat_freq_label, 1)
        info_layout.addWidget(self.beat_period_label, 1)
        info_layout.addWidget(self.main_freq_label, 1)
        
        # 添加到布局
        right_layout.addWidget(self.wave_panel, 1)
        right_layout.addWidget(self.info_panel, 0)  # 固定大小的信息面板
        
        splitter.addWidget(right_widget)
        
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
        from ui_framework import AnimatedButton
        
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
        self.control_panel.w1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('omega1', self.control_panel.w1_slider.get_value()))
        self.control_panel.p1_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi1', self.control_panel.p1_slider.get_value()))
        self.control_panel.a2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('A2', self.control_panel.a2_slider.get_value()))
        self.control_panel.w2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('omega2', self.control_panel.w2_slider.get_value()))
        self.control_panel.p2_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('phi2', self.control_panel.p2_slider.get_value()))
        self.control_panel.speed_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('speed', self.control_panel.speed_slider.get_value()))
        self.control_panel.trail_slider.slider.valueChanged.connect(lambda: self.on_slider_changed('trail_length', int(self.control_panel.trail_slider.get_value())))
        
        # 连接频率比按钮信号
        for ratio_key, btn in self.control_panel.ratio_buttons.items():
            btn.clicked.connect(lambda checked=False, rk=ratio_key: self.on_ratio_button_clicked(rk))
        
        # 连接频率调整模式按钮
        self.control_panel.w1_fixed_btn.clicked.connect(lambda: self.on_ratio_mode_changed('w1'))
        self.control_panel.w2_fixed_btn.clicked.connect(lambda: self.on_ratio_mode_changed('w2'))
        
        # 连接按钮信号
        self.control_panel.play_btn.clicked.connect(self.on_play_clicked)
        self.control_panel.pause_btn.clicked.connect(self.on_pause_clicked)
        self.control_panel.reset_btn.clicked.connect(self.on_reset_clicked)
    
    def update_plots(self):
        """更新波形图"""
        t = self.animation_controller.t
        
        # 计算当前时间指针
        current_t_index = int(len(t) * (self.animation_controller.time_counter % 10) / 10)
        
        # 更新波形面板
        self.wave_panel.update_waves(
            t,
            self.animation_controller.wave1_data,
            self.animation_controller.wave2_data,
            self.animation_controller.composite_data,
            self.animation_controller.envelope_up,
            self.animation_controller.envelope_down,
            current_t_index
        )
    
    def update_beat_info(self):
        """更新拍频信息"""
        beat_freq, beat_period, main_freq = self.animation_controller.calculate_beat_frequency()
        
        self.beat_freq_label.setText(f"拍频: {beat_freq:.3f} Hz")
        
        if beat_period == float('inf'):
            self.beat_period_label.setText("拍周期: ∞ s")
        else:
            self.beat_period_label.setText(f"拍周期: {beat_period:.3f} s")
            
        self.main_freq_label.setText(f"主频: {main_freq:.3f} Hz")
    
    @pyqtSlot()
    def on_params_changed(self):
        """参数变化时更新信息和图形"""
        self.update_beat_info()
        
        # 强制重新计算波形，确保图形更新
        self.animation_controller._needs_full_recalculation = True
        
        if self.animation_controller.is_paused:
            self.animation_controller.calculate_waves(self.animation_controller.time_counter)
            self.animation_controller.current_position = self.animation_controller.calculate_current_position(
                self.animation_controller.time_counter)
            self.update_plots()
    
    @pyqtSlot(str, object)
    def on_slider_changed(self, param_name, value):
        """滑块值变化时的处理"""
        self.params_controller.set_param(param_name, value)
    
    @pyqtSlot(str)
    def on_ratio_button_clicked(self, ratio_key):
        """频率比按钮点击事件处理"""
        print(f"频率比按钮被点击: {ratio_key}")
        
        # 更新按钮状态
        for key, btn in self.control_panel.ratio_buttons.items():
            if key == ratio_key:
                btn.set_active(True)
            else:
                btn.set_active(False)
        
        # 获取参数
        params = self.params_controller.get_params()
        
        # 确保有比率预设
        if 'ratio_presets' not in params:
            from ui_framework import RATIO_PRESETS
            params['ratio_presets'] = RATIO_PRESETS
            self.params_controller.set_param('ratio_presets', RATIO_PRESETS)
        
        # 更新当前比率预设
        self.params_controller.set_param('ratio_preset', ratio_key)
        
        # 获取比率值
        ratio_presets = params['ratio_presets']
        if ratio_key in ratio_presets:
            ratio_values = ratio_presets[ratio_key]
            
            # 确定当前模式 (w1 或 w2)
            ratio_mode = params.get('ratio_mode', 'w2')  # 默认为 w2 模式
            
            # 根据模式应用频率比
            if ratio_mode == 'w1':
                w1_fixed = params['omega2'] * (ratio_values[0] / ratio_values[1])
                self.params_controller.set_param('omega1', w1_fixed)
                print(f"模式: {ratio_mode}, 设置 omega1 = {w1_fixed}")
            else:
                w2_fixed = params['omega1'] * (ratio_values[1] / ratio_values[0])
                self.params_controller.set_param('omega2', w2_fixed)
                print(f"模式: {ratio_mode}, 设置 omega2 = {w2_fixed}")
            
            # 更新滑块UI
            self.control_panel.w1_slider.set_value(params['omega1'])
            self.control_panel.w2_slider.set_value(params['omega2'])
    
    @pyqtSlot(str)
    def on_ratio_mode_changed(self, mode):
        """频率调整模式改变事件处理"""
        print(f"频率调整模式改变: {mode}")
        
        # 更新按钮状态
        if mode == 'w1':
            self.control_panel.w1_fixed_btn.set_active(True)
            self.control_panel.w2_fixed_btn.set_active(False)
        else:
            self.control_panel.w1_fixed_btn.set_active(False)
            self.control_panel.w2_fixed_btn.set_active(True)
        
        # 设置模式参数
        self.params_controller.set_param('ratio_mode', mode)
    
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
        # 恢复我们的自定义参数
        self.params_controller.set_param('omega1', 5.0)
        self.params_controller.set_param('omega2', 4.7)
        self.params_controller.update_ui_from_params(self.control_panel)
        self.animation_controller.reset()
        self.update_beat_info()


def main():
    """程序入口"""
    app = get_app_instance()
    
    # 创建主窗口
    window = BeatHarmonicWindow()
    window.show()
    
    # 只有在直接运行此模块时才执行事件循环
    if __name__ == "__main__":
        sys.exit(app.exec())
        
    # 返回窗口实例，以便启动器能追踪它
    return window


if __name__ == "__main__":
    main() 