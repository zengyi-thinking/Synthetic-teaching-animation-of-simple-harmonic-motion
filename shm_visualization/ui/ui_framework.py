# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 基础UI框架
使用PyQt6和Matplotlib实现高质量的简谐运动可视化
"""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QRect
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QLinearGradient, QGradient, QPainter, QBrush
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QPushButton, QGroupBox, QFrame, QGridLayout,
    QSpacerItem, QSizePolicy
)
import numpy as np
import matplotlib
try:
    matplotlib.use('Qt5Agg')
except Exception as e:
    print(f"设置Matplotlib后端失败: {e}")
    # 尝试其他后端
    try:
        matplotlib.use('Agg')
        print("使用备用后端Agg")
    except:
        print("无法设置Matplotlib后端")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys

# 配置matplotlib支持中文显示
try:
    # 检查系统中文字体
    fonts_path = 'C:/Windows/Fonts'  # Windows字体目录
    
    # 常见中文字体优先级
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi', 'Arial Unicode MS']
    
    # 检查并添加找到的中文字体
    found_font = None
    for font_name in chinese_fonts:
        font_path = os.path.join(fonts_path, f"{font_name}.ttf")
        if os.path.exists(font_path):
            # 添加字体
            font_path = fm.fontManager.addfont(font_path)
            found_font = font_name
            break
    
    if found_font:
        plt.rcParams['font.sans-serif'] = [found_font, 'DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
    else:
        # 如果没找到，使用通用设置
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    # 确保中文标题正常显示
    plt.rcParams['font.size'] = 10
except Exception as e:
    print(f"字体配置错误: {e}")

# 配色方案 - 现代深色主题
COLORS = {
    'background': '#0A1929',    # 深蓝黑色背景
    'panel': '#152238',         # 控制面板背景
    'accent1': '#4F9BFF',       # X方向波形（亮蓝色）
    'accent2': '#FFB938',       # Y方向波形（橙黄色）
    'accent3': '#2EE59D',       # 李萨如图形轨迹（青绿色）
    'accent4': '#FF6EB4',       # 移动点颜色（粉红色）
    'accent5': '#B566FF',       # 轨迹颜色（紫色）
    'text': '#FFFFFF',          # 文本颜色
    'grid': '#1E3A5F',          # 网格线颜色
    'button': '#3877FF',        # 按钮颜色 
    'button_hover': '#5C9AFF',  # 按钮悬停色
    'button_active': '#82BCFF', # 按钮激活色
    'slider_track': '#1E293B',  # 滑块轨道色
    'slider_handle': '#FFFFFF', # 滑块手柄色
    'border': '#345D8A',        # 边框颜色
}

# 初始参数值
INITIAL_PARAMS = {
    'A1': 1.0,
    'omega1': 1.0,
    'phi1': 0.0,
    'A2': 1.0,
    'omega2': 1.0,  # 确保初始值为1.0
    'phi2': 0.0,
    'speed': 1.0,
    'trail_length': 100,
    'ratio_mode': 'w2',  # 当频率比改变时，调整哪个频率 ('w1' 或 'w2')
    'ratio_preset': '1:1'  # 确保默认频率比为1:1
}

# 李萨如图形的常用频率比预设
RATIO_PRESETS = {
    "1:1": (1.0, 1.0),   # 圆形/椭圆形
    "1:2": (1.0, 2.0),   # 8字形
    "2:3": (2.0, 3.0),   # 三瓣形
    "3:4": (3.0, 4.0),   # 四瓣形
    "3:5": (3.0, 5.0),   # 五瓣形
    "4:5": (4.0, 5.0)    # 复杂形状
}

# 全局QApplication实例
_app = None

def get_app_instance():
    """获取或创建全局QApplication实例"""
    global _app
    if _app is None or not isinstance(_app, QApplication):
        if QApplication.instance() is None:
            _app = QApplication([])
            
            # 设置应用样式
            _app.setStyle('Fusion')
            
            # 设置默认字体
            font = QFont()
            font.setPointSize(10)
            _app.setFont(font)
        else:
            _app = QApplication.instance()
    return _app

class AnimatedSlider(QWidget):
    """带有动画和现代外观的滑块控件"""
    
    def __init__(self, title, min_val, max_val, initial_val, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.value = initial_val
        self.setup_ui(title, min_val, max_val, initial_val)
        
    def setup_ui(self, title, min_val, max_val, initial_val):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题和值显示
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold;")
        
        self.value_label = QLabel(f"{initial_val:.1f}")
        self.value_label.setStyleSheet(f"color: {self.color.name()}; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.value_label)
        
        layout.addLayout(title_layout)
        
        # 滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(min_val * 100))  # 使用整数以避免浮点精度问题
        self.slider.setMaximum(int(max_val * 100))
        self.slider.setValue(int(initial_val * 100))
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['slider_track']};
                height: 8px;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background: {COLORS['slider_handle']};
                border: 2px solid {self.color.name()};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            
            QSlider::add-page:horizontal {{
                background: {COLORS['slider_track']};
                border-radius: 4px;
            }}
            
            QSlider::sub-page:horizontal {{
                background: {self.color.name()};
                border-radius: 4px;
            }}
        """)
        
        self.slider.valueChanged.connect(self.update_value)
        layout.addWidget(self.slider)
        
        # 最小/最大标签
        labels_layout = QHBoxLayout()
        min_label = QLabel(f"{min_val}")
        min_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 8pt;")
        
        max_label = QLabel(f"{max_val}")
        max_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 8pt;")
        max_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        labels_layout.addWidget(min_label)
        labels_layout.addWidget(max_label)
        
        layout.addLayout(labels_layout)
        self.setLayout(layout)
        
    def update_value(self):
        """更新显示的值"""
        self.value = self.slider.value() / 100.0
        self.value_label.setText(f"{self.value:.1f}")
        
    def get_value(self):
        """获取当前值"""
        return self.value
        
    def set_value(self, value):
        """设置当前值"""
        self.slider.setValue(int(value * 100))


class AnimatedButton(QPushButton):
    """带有动画效果的按钮"""
    
    def __init__(self, text, color=COLORS['button'], parent=None):
        super().__init__(text, parent)
        self.color = QColor(color)
        self.hover_color = QColor(COLORS['button_hover'])
        self.active_color = QColor(COLORS['button_active'])
        self.current_color = self.color.name()
        
        # 设置样式
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                color: {COLORS['text']};
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self.hover_color.name()};
            }}
            
            QPushButton:pressed {{
                background-color: {self.active_color.name()};
            }}
        """)
        
        # 设置动画
        self.animation = QPropertyAnimation(self, b"backgroundColor")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def set_active(self, active=True):
        """设置按钮状态"""
        if active:
            self.animation.setStartValue(self.color.name())
            self.animation.setEndValue(self.active_color.name())
            self.current_color = self.active_color.name()
        else:
            self.animation.setStartValue(self.active_color.name())
            self.animation.setEndValue(self.color.name())
            self.current_color = self.color.name()
        self.animation.start()
        
    def get_background_color(self):
        """获取背景颜色"""
        return self.current_color
        
    def set_background_color(self, color):
        """设置背景颜色"""
        self.current_color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS['text']};
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self.hover_color.name()};
            }}
            
            QPushButton:pressed {{
                background-color: {self.active_color.name()};
            }}
        """)
    
    # 定义属性动画
    backgroundColor = pyqtProperty(str, get_background_color, set_background_color)


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib画布组件"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, facecolor=COLORS['background']):
        """
        初始化Matplotlib画布
        """
        # 优化绘图参数，提高性能
        import matplotlib as mpl
        mpl.rcParams['path.simplify'] = True  # 简化曲线以减少点数
        mpl.rcParams['path.simplify_threshold'] = 0.8  # 曲线简化阈值(0~1)
        mpl.rcParams['agg.path.chunksize'] = 10000  # 分块处理大路径
        
        # 创建图形
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=facecolor)
        
        # 创建子图并设置样式
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor(facecolor)
        self.axes.grid(True, color=COLORS['grid'], linestyle='-', alpha=0.3)
        self.axes.tick_params(axis='both', colors=COLORS['text'])
        
        # 减少绘图元素的复杂度
        self.axes.patch.set_alpha(0.8)  # 提高透明度处理效率
        
        # 设置外观
        for spine in self.axes.spines.values():
            spine.set_color(COLORS['border'])
            spine.set_linewidth(1.5)
        
        # 禁用自动缩放以提高性能
        self.axes.autoscale(enable=False)
            
        # 初始化基类
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 使画布可以接收焦点
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(300, 200)


class ModernGroupBox(QGroupBox):
    """现代风格的分组框"""
    
    def __init__(self, title, color, parent=None):
        super().__init__(title, parent)
        self.color = QColor(color)
        
        # 设置样式
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['panel']};
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                color: {COLORS['text']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: {color};
                border-radius: 4px;
            }}
        """)


class WavePanel(QWidget):
    """波形显示面板"""
    
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标题
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
        
        # 创建画布
        self.canvas = MatplotlibCanvas(self)
        
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
        layout.addWidget(self.canvas)
        layout.addWidget(self.formula_label)
        
        self.setLayout(layout)

    def set_formula(self, formula):
        """设置公式文本"""
        self.formula_label.setText(formula)


class LissajousPanel(QWidget):
    """李萨如图形显示面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel("李萨如图形")
        title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 14pt;
            background-color: {COLORS['accent3']};
            border-radius: 4px;
            padding: 5px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建画布
        self.canvas = MatplotlibCanvas(self)
        self.canvas.axes.set_aspect('equal')  # 保持X和Y比例相同
        
        # 设置坐标轴标签
        self.canvas.axes.set_xlabel('X振幅', color=COLORS['text'])
        self.canvas.axes.set_ylabel('Y振幅', color=COLORS['text'])
        
        # 创建频率比显示标签
        self.ratio_label = QLabel()
        self.ratio_label.setStyleSheet(f"""
            color: {COLORS['accent3']};
            font-weight: bold;
            font-size: 12pt;
            background-color: rgba(26, 58, 108, 180);
            border: 1px solid {COLORS['accent3']};
            border-radius: 4px;
            padding: 8px;
        """)
        self.ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.ratio_label)
        
        self.setLayout(layout)

    def set_ratio(self, ratio):
        """设置频率比文本"""
        self.ratio_label.setText(f"频率比: {ratio}")


class PhaseControlPanel(QWidget):
    """相位差合成专用控制面板组件（不含频率比控制）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # X1方向参数组
        x_group = ModernGroupBox("X1方向参数", COLORS['accent1'])
        x_layout = QVBoxLayout(x_group)
        
        self.a1_slider = AnimatedSlider("振幅 (A1)", 0.1, 1.0, INITIAL_PARAMS['A1'], COLORS['accent1'])
        self.w1_slider = AnimatedSlider("角频率 (ω1)", 0.1, 5.0, INITIAL_PARAMS['omega1'], COLORS['accent1'])
        self.p1_slider = AnimatedSlider("相位 (φ1)", 0.0, 6.28, INITIAL_PARAMS['phi1'], COLORS['accent1'])
        
        x_layout.addWidget(self.a1_slider)
        x_layout.addWidget(self.w1_slider)
        x_layout.addWidget(self.p1_slider)
        
        # X2方向参数组
        y_group = ModernGroupBox("X2方向参数", COLORS['accent2'])
        y_layout = QVBoxLayout(y_group)
        
        self.a2_slider = AnimatedSlider("振幅 (A2)", 0.1, 1.0, INITIAL_PARAMS['A2'], COLORS['accent2'])
        self.w2_slider = AnimatedSlider("角频率 (ω2)", 0.1, 5.0, INITIAL_PARAMS['omega2'], COLORS['accent2'])
        self.p2_slider = AnimatedSlider("相位 (φ2)", 0.0, 6.28, INITIAL_PARAMS['phi2'], COLORS['accent2'])
        
        y_layout.addWidget(self.a2_slider)
        y_layout.addWidget(self.w2_slider)
        y_layout.addWidget(self.p2_slider)
        
        # 频率锁定提示
        freq_info = QLabel("频率已锁定: ω1 = ω2 = 1.0")
        freq_info.setStyleSheet(f"""
            color: {COLORS['accent3']};
            font-weight: bold;
            font-size: 11pt;
            background-color: rgba(26, 58, 108, 180);
            border: 1px solid {COLORS['accent3']};
            border-radius: 4px;
            padding: 8px;
            margin-top: 10px;
        """)
        freq_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        y_layout.addWidget(freq_info)
        
        # 播放控制组
        control_group = ModernGroupBox("播放控制", COLORS['accent4'])
        control_layout = QVBoxLayout(control_group)
        
        # 播放控制按钮
        buttons_layout = QHBoxLayout()
        self.play_btn = AnimatedButton("播放", COLORS['accent4'])
        self.pause_btn = AnimatedButton("暂停", COLORS['panel'])
        self.reset_btn = AnimatedButton("重置", COLORS['panel'])
        
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.reset_btn)
        control_layout.addLayout(buttons_layout)
        
        # 速度和轨迹长度控制
        self.speed_slider = AnimatedSlider("速度", 0.1, 3.0, INITIAL_PARAMS['speed'], COLORS['accent4'])
        self.trail_slider = AnimatedSlider("轨迹长度", 10.0, 200.0, INITIAL_PARAMS['trail_length'], COLORS['accent5'])
        
        control_layout.addWidget(self.speed_slider)
        control_layout.addWidget(self.trail_slider)
        
        # 添加所有控制组到主布局，调整新布局的大小分配
        main_layout.addWidget(x_group, 30)    # 占30%的空间
        main_layout.addWidget(y_group, 30)    # 占30%的空间
        main_layout.addWidget(control_group, 30)  # 占30%的空间
        main_layout.addStretch(10)            # 剩余10%作为弹性空间
        
        self.setLayout(main_layout)
        self.setMinimumWidth(300)


class ControlPanel(QWidget):
    """控制面板组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # X方向参数组
        x_group = ModernGroupBox("X方向参数", COLORS['accent1'])
        x_layout = QVBoxLayout(x_group)
        
        self.a1_slider = AnimatedSlider("振幅 (A1)", 0.1, 1.0, INITIAL_PARAMS['A1'], COLORS['accent1'])
        self.w1_slider = AnimatedSlider("角频率 (ω1)", 0.1, 5.0, INITIAL_PARAMS['omega1'], COLORS['accent1'])
        self.p1_slider = AnimatedSlider("相位 (φ1)", 0.0, 6.28, INITIAL_PARAMS['phi1'], COLORS['accent1'])
        
        x_layout.addWidget(self.a1_slider)
        x_layout.addWidget(self.w1_slider)
        x_layout.addWidget(self.p1_slider)
        
        # Y方向参数组
        y_group = ModernGroupBox("Y方向参数", COLORS['accent2'])
        y_layout = QVBoxLayout(y_group)
        
        self.a2_slider = AnimatedSlider("振幅 (A2)", 0.1, 1.0, INITIAL_PARAMS['A2'], COLORS['accent2'])
        self.w2_slider = AnimatedSlider("角频率 (ω2)", 0.1, 5.0, INITIAL_PARAMS['omega2'], COLORS['accent2'])
        self.p2_slider = AnimatedSlider("相位 (φ2)", 0.0, 6.28, INITIAL_PARAMS['phi2'], COLORS['accent2'])
        
        y_layout.addWidget(self.a2_slider)
        y_layout.addWidget(self.w2_slider)
        y_layout.addWidget(self.p2_slider)
        
        # 频率比控制组
        ratio_group = ModernGroupBox("频率比控制", COLORS['accent3'])
        ratio_layout = QVBoxLayout(ratio_group)
        
        # 频率比按钮网格
        ratio_grid = QGridLayout()
        self.ratio_buttons = {}
        
        row, col = 0, 0
        for i, ratio_key in enumerate(RATIO_PRESETS.keys()):
            btn = AnimatedButton(ratio_key, COLORS['accent3'] if ratio_key == INITIAL_PARAMS['ratio_preset'] else COLORS['panel'])
            self.ratio_buttons[ratio_key] = btn
            ratio_grid.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        ratio_layout.addLayout(ratio_grid)
        
        # 频率调整模式
        mode_layout = QHBoxLayout()
        self.w1_fixed_btn = AnimatedButton("固定ω1", COLORS['panel'])
        self.w2_fixed_btn = AnimatedButton("固定ω2", COLORS['accent3'])
        
        mode_layout.addWidget(self.w1_fixed_btn)
        mode_layout.addWidget(self.w2_fixed_btn)
        ratio_layout.addLayout(mode_layout)
        
        # 播放控制组
        control_group = ModernGroupBox("播放控制", COLORS['accent4'])
        control_layout = QVBoxLayout(control_group)
        
        # 播放控制按钮
        buttons_layout = QHBoxLayout()
        self.play_btn = AnimatedButton("播放", COLORS['accent4'])
        self.pause_btn = AnimatedButton("暂停", COLORS['panel'])
        self.reset_btn = AnimatedButton("重置", COLORS['panel'])
        
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.reset_btn)
        control_layout.addLayout(buttons_layout)
        
        # 速度和轨迹长度控制
        self.speed_slider = AnimatedSlider("速度", 0.1, 3.0, INITIAL_PARAMS['speed'], COLORS['accent4'])
        self.trail_slider = AnimatedSlider("轨迹长度", 10.0, 200.0, INITIAL_PARAMS['trail_length'], COLORS['accent5'])
        
        control_layout.addWidget(self.speed_slider)
        control_layout.addWidget(self.trail_slider)
        
        # 添加所有控制组到主布局
        main_layout.addWidget(x_group)
        main_layout.addWidget(y_group)
        main_layout.addWidget(ratio_group)
        main_layout.addWidget(control_group)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setMinimumWidth(300) 