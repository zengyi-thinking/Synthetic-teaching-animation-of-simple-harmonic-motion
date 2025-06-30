#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析器主界面 - 修复版本
独立的桌面应用程序，用于音频信号的简谐波分解与重构
"""

import sys
import os
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSplitter, QGroupBox, QLabel, QPushButton,
                            QSlider, QCheckBox, QFileDialog, QProgressBar, QTextEdit,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from matplotlib import rcParams

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 导入自定义模块
from audio_processor import AudioProcessor
from frequency_analyzer import FrequencyAnalyzer
from audio_player import AudioPlayer

# 颜色主题
COLORS = {
    'background': '#1e1e1e',
    'panel': '#2d2d2d',
    'border': '#404040',
    'text': '#ffffff',
    'accent1': '#00d4ff',
    'accent2': '#ff6b6b',
    'accent3': '#4ecdc4',
    'accent4': '#45b7d1',
    'button': '#0078d4',
    'button_hover': '#106ebe',
    'button_active': '#005a9e',
    'grid': '#404040'
}

class AnimatedButton(QPushButton):
    """带动画效果的按钮"""
    
    def __init__(self, text, color):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['button_active']};
            }}
        """)

class AudioAnalysisThread(QThread):
    """音频分析线程 - 在后台执行频率分析"""
    
    analysis_completed = pyqtSignal(list)  # 分析完成信号
    progress_updated = pyqtSignal(int)     # 进度更新信号
    error_occurred = pyqtSignal(str)       # 错误信号
    
    def __init__(self, audio_data, sample_rate, n_components=5):
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.n_components = n_components
        self.analyzer = FrequencyAnalyzer(sample_rate)
    
    def run(self):
        """执行频率分析"""
        try:
            self.progress_updated.emit(20)
            
            # 执行频率分析
            components = self.analyzer.analyze_audio(
                self.audio_data, 
                n_components=self.n_components
            )
            
            self.progress_updated.emit(100)
            self.analysis_completed.emit(components)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class SpectrumCanvas(FigureCanvas):
    """频谱显示画布 - 垂直布局显示原始波形、频谱、简谐波分量和重构波形"""

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(16, 12), facecolor=COLORS['background'])
        super().__init__(self.figure)
        self.setParent(parent)

        # 设置样式
        self.figure.patch.set_facecolor(COLORS['background'])

        # 存储当前数据
        self.current_audio = None
        self.current_sample_rate = None
        self.current_components = None
        self.component_axes = []  # 存储分量子图

        # 初始化基本布局
        self.setup_initial_layout()

    def setup_initial_layout(self):
        """设置初始布局 - 只包含原始波形、频谱和重构波形"""
        self.figure.clear()

        # 垂直布局：原始波形 -> 频谱 -> 重构波形
        self.ax_waveform = self.figure.add_subplot(3, 1, 1)      # 原始波形
        self.ax_spectrum = self.figure.add_subplot(3, 1, 2)      # 频谱
        self.ax_reconstructed = self.figure.add_subplot(3, 1, 3) # 重构波形

        # 设置子图样式
        for ax in [self.ax_waveform, self.ax_spectrum, self.ax_reconstructed]:
            ax.set_facecolor(COLORS['panel'])
            ax.tick_params(colors=COLORS['text'], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])

        # 清空分量轴列表
        self.component_axes = []

        self.figure.tight_layout(pad=1.5)

    def setup_dynamic_layout(self, n_components):
        """根据分量数量动态设置布局"""
        self.figure.clear()

        # 计算总行数：原始波形 + 频谱 + 分量数 + 重构波形
        total_rows = 3 + n_components

        # 创建子图
        self.ax_waveform = self.figure.add_subplot(total_rows, 1, 1)      # 原始波形
        self.ax_spectrum = self.figure.add_subplot(total_rows, 1, 2)      # 频谱

        # 为每个分量创建独立的子图
        self.component_axes = []
        for i in range(n_components):
            ax_comp = self.figure.add_subplot(total_rows, 1, 3 + i)
            self.component_axes.append(ax_comp)

        # 重构波形在最后
        self.ax_reconstructed = self.figure.add_subplot(total_rows, 1, total_rows)

        # 设置所有子图样式
        all_axes = [self.ax_waveform, self.ax_spectrum, self.ax_reconstructed] + self.component_axes
        for ax in all_axes:
            ax.set_facecolor(COLORS['panel'])
            ax.tick_params(colors=COLORS['text'], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])

        self.figure.tight_layout(pad=1.0)
    
    def plot_waveform(self, audio_data, sample_rate, title="原始音频波形"):
        """绘制音频波形 - 优化显示为清晰的线条而非密集块"""
        if not hasattr(self, 'ax_waveform') or self.ax_waveform is None:
            print("警告: ax_waveform 不存在，重新初始化布局")
            self.setup_initial_layout()

        self.ax_waveform.clear()

        # 存储数据供其他方法使用
        self.current_audio = audio_data
        self.current_sample_rate = sample_rate

        print(f"绘制波形: 数据长度={len(audio_data)}, 采样率={sample_rate}")

        # 只显示前3秒的数据
        max_samples = int(3 * sample_rate)  # 3秒的样本数
        display_audio = audio_data[:max_samples]

        # 智能下采样 - 确保清晰的线条显示
        target_points = 2000  # 目标显示点数，确保线条清晰
        if len(display_audio) > target_points:
            # 使用智能下采样，保持波形特征
            step = len(display_audio) // target_points

            # 方法1: 简单下采样
            if step <= 10:
                display_audio = display_audio[::step]
                time_axis = np.linspace(0, len(display_audio) * step / sample_rate, len(display_audio))
            else:
                # 方法2: 分段最值采样（保持波形包络）
                segments = np.array_split(display_audio, target_points)
                display_audio = []
                time_points = []

                for i, segment in enumerate(segments):
                    if len(segment) > 0:
                        # 取每段的最大值和最小值
                        max_val = np.max(segment)
                        min_val = np.min(segment)

                        # 添加最小值和最大值点
                        display_audio.extend([min_val, max_val])

                        # 对应的时间点
                        segment_start = i * len(audio_data) / target_points / sample_rate
                        segment_end = (i + 1) * len(audio_data) / target_points / sample_rate
                        time_points.extend([segment_start, segment_end])

                display_audio = np.array(display_audio)
                time_axis = np.array(time_points)
        else:
            time_axis = np.linspace(0, len(display_audio) / sample_rate, len(display_audio))

        print(f"优化显示: 原始={len(audio_data)}点 → 显示={len(display_audio)}点, 时间范围={time_axis[0]:.2f}-{time_axis[-1]:.2f}秒")

        # 绘制清晰的波形线条
        self.ax_waveform.plot(time_axis, display_audio,
                             color=COLORS['accent1'],
                             linewidth=0.8,  # 稍细的线条
                             alpha=0.9,
                             antialiased=True,
                             rasterized=False,
                             marker=None,  # 不显示标记点
                             markersize=0)

        self.ax_waveform.set_title(title, color=COLORS['text'], fontsize=12, fontweight='bold', pad=10)
        self.ax_waveform.set_xlabel('时间 (秒)', color=COLORS['text'], fontsize=10)
        self.ax_waveform.set_ylabel('振幅', color=COLORS['text'], fontsize=10)
        self.ax_waveform.grid(True, alpha=0.3, color=COLORS['grid'], linewidth=0.5)
        self.ax_waveform.set_facecolor(COLORS['panel'])

        # 设置合适的y轴范围
        if len(display_audio) > 0:
            y_max = np.max(np.abs(display_audio))
            if y_max > 0:
                self.ax_waveform.set_ylim(-y_max * 1.1, y_max * 1.1)
            else:
                self.ax_waveform.set_ylim(-1, 1)

        # 设置x轴范围
        self.ax_waveform.set_xlim(0, time_axis[-1])

        print("优化波形绘制完成")
        self.draw()
    
    def plot_spectrum(self, frequencies, magnitudes, components=None, title="频谱分析"):
        """绘制频谱"""
        if not hasattr(self, 'ax_spectrum') or self.ax_spectrum is None:
            print("警告: ax_spectrum 不存在，重新初始化布局")
            self.setup_initial_layout()

        self.ax_spectrum.clear()

        # 存储分量数据
        self.current_components = components

        print(f"绘制频谱: 频率范围={frequencies[0]:.1f}-{frequencies[-1]:.1f}Hz, 分量数={len(components) if components else 0}")

        # 绘制频谱 - 优化线条显示
        self.ax_spectrum.plot(frequencies, magnitudes,
                             color=COLORS['accent2'],
                             linewidth=1.2,
                             alpha=0.8,
                             antialiased=True,
                             rasterized=False)

        # 标记主要频率分量
        if components:
            colors = [COLORS['accent3'], COLORS['accent4'], '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA500', '#9370DB', '#32CD32']
            for i, comp in enumerate(components):
                if comp.enabled:
                    color = colors[i % len(colors)]
                    self.ax_spectrum.axvline(comp.frequency, color=color,
                                           linestyle='--', alpha=0.8, linewidth=2)
                    self.ax_spectrum.text(comp.frequency, np.max(magnitudes) * 0.9,
                                        f'{comp.frequency:.0f}Hz',
                                        rotation=90, color=color,
                                        fontsize=9, ha='right', fontweight='bold')

        self.ax_spectrum.set_title(title, color=COLORS['text'], fontsize=12, fontweight='bold', pad=10)
        self.ax_spectrum.set_xlabel('频率 (Hz)', color=COLORS['text'], fontsize=10)
        self.ax_spectrum.set_ylabel('幅度', color=COLORS['text'], fontsize=10)
        self.ax_spectrum.set_xlim(0, 2000)  # 限制显示范围
        self.ax_spectrum.grid(True, alpha=0.3, color=COLORS['grid'], linewidth=0.5)
        self.ax_spectrum.set_facecolor(COLORS['panel'])

        # 如果有分量数据，重新设置布局并绘制分量
        if components and self.current_audio is not None:
            enabled_components = [comp for comp in components if comp.enabled]
            if enabled_components:
                print(f"重新设置布局，启用的分量数: {len(enabled_components)}")
                self.setup_dynamic_layout(len(enabled_components))
                # 重新绘制频谱（因为布局改变了）
                self.ax_spectrum.clear()
                self.ax_spectrum.plot(frequencies, magnitudes, color=COLORS['accent2'], linewidth=1.2, alpha=0.8)

                # 重新标记分量
                for i, comp in enumerate(enabled_components):
                    color = colors[i % len(colors)]
                    self.ax_spectrum.axvline(comp.frequency, color=color,
                                           linestyle='--', alpha=0.8, linewidth=2)
                    self.ax_spectrum.text(comp.frequency, np.max(magnitudes) * 0.9,
                                        f'{comp.frequency:.0f}Hz',
                                        rotation=90, color=color,
                                        fontsize=9, ha='right', fontweight='bold')

                self.ax_spectrum.set_title(title, color=COLORS['text'], fontsize=12, fontweight='bold', pad=10)
                self.ax_spectrum.set_xlabel('频率 (Hz)', color=COLORS['text'], fontsize=10)
                self.ax_spectrum.set_ylabel('幅度', color=COLORS['text'], fontsize=10)
                self.ax_spectrum.set_xlim(0, 2000)
                self.ax_spectrum.grid(True, alpha=0.3, color=COLORS['grid'], linewidth=0.5)
                self.ax_spectrum.set_facecolor(COLORS['panel'])

                # 绘制分量
                self.plot_components_vertical(enabled_components)

        self.draw()

    def plot_components_vertical(self, components):
        """垂直排列绘制各个简谐波分量的独立波形"""
        if not components or self.current_sample_rate is None:
            print("无分量数据或采样率")
            return

        print(f"绘制垂直分量: {len(components)} 个")

        # 生成时间轴（显示前3秒，确保足够的采样点）
        duration = 3.0  # 显示3秒
        # 使用更高的采样率确保波形平滑
        display_sample_rate = max(self.current_sample_rate, 44100)
        n_samples = int(duration * display_sample_rate)
        t = np.linspace(0, duration, n_samples)

        print(f"时间轴: {len(t)} 个采样点, 范围 0-{duration}秒")

        # 颜色列表
        colors = [COLORS['accent3'], COLORS['accent4'], '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA500', '#9370DB', '#32CD32']

        # 为每个分量绘制独立的子图
        for i, comp in enumerate(components):
            if i < len(self.component_axes):
                ax = self.component_axes[i]
                ax.clear()

                print(f"分量 {i+1}: 频率={comp.frequency:.1f}Hz, 振幅={comp.amplitude:.4f}, 相位={comp.phase:.3f}")

                # 生成正弦波 - 确保振幅足够大以便可见
                base_amplitude = max(abs(comp.amplitude), 0.1)  # 最小振幅0.1
                if comp.amplitude != 0:
                    # 保持原始振幅的符号
                    display_amplitude = base_amplitude * (1 if comp.amplitude >= 0 else -1)
                else:
                    display_amplitude = base_amplitude

                wave = display_amplitude * np.sin(2 * np.pi * comp.frequency * t + comp.phase)

                print(f"  波形数据: 最小值={np.min(wave):.4f}, 最大值={np.max(wave):.4f}")

                # 绘制波形 - 优化线条显示
                color = colors[i % len(colors)]
                ax.plot(t, wave,
                       color=color,
                       linewidth=1.5,
                       alpha=0.9,
                       antialiased=True,
                       rasterized=False,
                       solid_capstyle='round',
                       solid_joinstyle='round')

                # 设置标题和标签
                ax.set_title(f'分量 {i+1}: {comp.frequency:.0f}Hz (原始幅度: {comp.amplitude:.4f})',
                           color=color, fontsize=10, fontweight='bold', pad=5)
                ax.set_ylabel('振幅', color=COLORS['text'], fontsize=9)
                ax.grid(True, alpha=0.3, color=COLORS['grid'], linewidth=0.5)
                ax.set_facecolor(COLORS['panel'])
                ax.tick_params(colors=COLORS['text'], labelsize=8)

                # 设置y轴范围 - 确保有足够的显示空间
                y_range = max(abs(display_amplitude) * 1.3, 0.15)
                ax.set_ylim(-y_range, y_range)

                # 设置x轴范围
                ax.set_xlim(0, duration)

                # 只在最后一个分量上显示x轴标签
                if i == len(components) - 1:
                    ax.set_xlabel('时间 (秒)', color=COLORS['text'], fontsize=9)
                else:
                    ax.set_xlabel('')
                    # 隐藏x轴刻度标签但保留刻度线
                    ax.tick_params(axis='x', labelbottom=False)

                # 设置子图样式
                for spine in ax.spines.values():
                    spine.set_color(COLORS['border'])

                # 添加频率信息文本
                period = 1.0 / comp.frequency if comp.frequency > 0 else 0
                cycles_shown = duration / period if period > 0 else 0
                ax.text(0.02, 0.95, f'周期: {period:.3f}s\n显示: {cycles_shown:.1f}个周期',
                       transform=ax.transAxes, fontsize=8, color=COLORS['text'],
                       verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3',
                       facecolor=COLORS['panel'], alpha=0.8, edgecolor=COLORS['border']))

        print("垂直分量绘制完成")
    
    def plot_reconstructed(self, audio_data, sample_rate, title="重构音频波形"):
        """绘制重构音频波形 - 优化显示为清晰的线条"""
        if not hasattr(self, 'ax_reconstructed') or self.ax_reconstructed is None:
            print("警告: ax_reconstructed 不存在，重新初始化布局")
            self.setup_initial_layout()

        self.ax_reconstructed.clear()

        print(f"绘制重构波形: 数据长度={len(audio_data)}, 采样率={sample_rate}")

        # 只显示前3秒的数据
        max_samples = int(3 * sample_rate)
        display_audio = audio_data[:max_samples]

        # 智能下采样 - 与原始波形使用相同的优化策略
        target_points = 2000  # 目标显示点数
        if len(display_audio) > target_points:
            step = len(display_audio) // target_points

            if step <= 10:
                display_audio = display_audio[::step]
                time_axis = np.linspace(0, len(display_audio) * step / sample_rate, len(display_audio))
            else:
                # 分段最值采样
                segments = np.array_split(display_audio, target_points)
                display_audio = []
                time_points = []

                for i, segment in enumerate(segments):
                    if len(segment) > 0:
                        max_val = np.max(segment)
                        min_val = np.min(segment)
                        display_audio.extend([min_val, max_val])

                        segment_start = i * len(audio_data) / target_points / sample_rate
                        segment_end = (i + 1) * len(audio_data) / target_points / sample_rate
                        time_points.extend([segment_start, segment_end])

                display_audio = np.array(display_audio)
                time_axis = np.array(time_points)
        else:
            time_axis = np.linspace(0, len(display_audio) / sample_rate, len(display_audio))

        print(f"重构波形优化: 原始={len(audio_data)}点 → 显示={len(display_audio)}点")

        # 绘制清晰的重构波形线条
        self.ax_reconstructed.plot(time_axis, display_audio,
                                 color=COLORS['accent4'],
                                 linewidth=0.8,
                                 alpha=0.9,
                                 antialiased=True,
                                 rasterized=False,
                                 marker=None,
                                 markersize=0)

        self.ax_reconstructed.set_title(title, color=COLORS['text'], fontsize=12, fontweight='bold', pad=10)
        self.ax_reconstructed.set_xlabel('时间 (秒)', color=COLORS['text'], fontsize=10)
        self.ax_reconstructed.set_ylabel('振幅', color=COLORS['text'], fontsize=10)
        self.ax_reconstructed.grid(True, alpha=0.3, color=COLORS['grid'], linewidth=0.5)
        self.ax_reconstructed.set_facecolor(COLORS['panel'])

        # 设置合适的y轴范围
        if len(display_audio) > 0:
            y_max = np.max(np.abs(display_audio))
            if y_max > 0:
                self.ax_reconstructed.set_ylim(-y_max * 1.1, y_max * 1.1)
            else:
                self.ax_reconstructed.set_ylim(-1, 1)

        # 设置x轴范围
        self.ax_reconstructed.set_xlim(0, time_axis[-1])

        print("重构波形优化绘制完成")
        self.draw()
    
    def plot_components(self, components):
        """绘制各个简谐波分量的独立波形 - 兼容方法，调用垂直布局"""
        if not components or self.current_sample_rate is None:
            print("plot_components: 无分量数据或采样率")
            return

        # 过滤启用的分量
        enabled_components = [comp for comp in components if comp.enabled]
        if not enabled_components:
            print("plot_components: 所有分量已禁用")
            return

        print(f"plot_components: 调用垂直布局显示 {len(enabled_components)} 个分量")

        # 如果当前不是动态布局，重新设置
        if len(self.component_axes) != len(enabled_components):
            self.setup_dynamic_layout(len(enabled_components))

            # 重新绘制原始波形（如果有数据）
            if self.current_audio is not None:
                self.plot_waveform(self.current_audio, self.current_sample_rate, "原始音频波形")

        # 调用垂直分量显示方法
        self.plot_components_vertical(enabled_components)


class AudioEditorMainWindow(QMainWindow):
    """音频编辑器主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化数据
        self.original_audio = None
        self.reconstructed_audio = None
        self.frequency_components = []
        self.frequency_analyzer = None
        self.analysis_thread = None

        # 初始化组件
        self.audio_processor = AudioProcessor()
        self.audio_player = AudioPlayer()

        # 设置UI
        self.setup_ui()
        self.connect_signals()

        print("🎵 音频分析器初始化完成 - 独立应用程序")

    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("音频分析器 - 简谐波分解与重构工具")
        self.setGeometry(100, 100, 1600, 1000)

        # 设置应用程序字体，确保中文显示正常
        font = QFont()
        font.setFamily("Microsoft YaHei")  # 使用微软雅黑字体
        font.setPointSize(9)
        self.setFont(font)
        QApplication.instance().setFont(font)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 设置左右面板
        self.setup_control_panel(splitter)
        self.setup_display_area(splitter)

        # 设置分割器比例
        splitter.setSizes([400, 1200])

        # 设置样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['accent1']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QTextEdit {{
                background-color: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                border-radius: 3px;
            }}
            QTableWidget {{
                background-color: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                gridline-color: {COLORS['border']};
                selection-background-color: {COLORS['accent1']};
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                padding: 5px;
                border: 1px solid {COLORS['border']};
                font-weight: bold;
            }}
            QProgressBar {{
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                text-align: center;
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent1']};
                border-radius: 3px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {COLORS['border']};
                height: 8px;
                background: {COLORS['panel']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['accent1']};
                border: 1px solid {COLORS['border']};
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['accent1']};
                border-radius: 4px;
            }}
        """)

    def setup_control_panel(self, parent):
        """设置左侧控制面板"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # 文件操作组
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout(file_group)

        self.load_btn = AnimatedButton("加载音频文件", COLORS['button'])
        self.save_btn = AnimatedButton("保存重构音频", COLORS['button'])
        self.save_btn.setEnabled(False)

        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        control_layout.addWidget(file_group)

        # 分析控制组
        analysis_group = QGroupBox("频率分析")
        analysis_layout = QVBoxLayout(analysis_group)

        self.analyze_btn = AnimatedButton("开始频率分析", COLORS['accent2'])
        self.analyze_btn.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        analysis_layout.addWidget(self.analyze_btn)
        analysis_layout.addWidget(self.progress_bar)
        control_layout.addWidget(analysis_group)

        # 播放控制组
        playback_group = QGroupBox("播放控制")
        playback_layout = QVBoxLayout(playback_group)

        self.play_original_btn = AnimatedButton("播放原始音频", COLORS['accent3'])
        self.play_reconstructed_btn = AnimatedButton("播放重构音频", COLORS['accent4'])
        self.stop_btn = AnimatedButton("停止播放", COLORS['accent2'])

        self.play_original_btn.setEnabled(False)
        self.play_reconstructed_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        playback_layout.addWidget(self.play_original_btn)
        playback_layout.addWidget(self.play_reconstructed_btn)
        playback_layout.addWidget(self.stop_btn)
        control_layout.addWidget(playback_group)

        # 频率分量控制组
        components_group = QGroupBox("频率分量控制")
        components_layout = QVBoxLayout(components_group)

        self.components_table = QTableWidget()
        self.components_table.setColumnCount(4)
        self.components_table.setHorizontalHeaderLabels(["启用", "频率(Hz)", "振幅", "振幅调节"])

        # 设置表格列宽
        header = self.components_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        components_layout.addWidget(self.components_table)
        control_layout.addWidget(components_group)

        # 音频信息组
        info_group = QGroupBox("音频信息")
        info_layout = QVBoxLayout(info_group)

        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlainText("请加载音频文件...")

        info_layout.addWidget(self.info_text)
        control_layout.addWidget(info_group)
        control_layout.addStretch()

        parent.addWidget(control_widget)

    def setup_display_area(self, parent):
        """设置右侧显示区域"""
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)

        # 频谱显示画布
        self.spectrum_canvas = SpectrumCanvas()
        display_layout.addWidget(self.spectrum_canvas)

        parent.addWidget(display_widget)

    def connect_signals(self):
        """连接信号和槽"""
        # 文件操作
        self.load_btn.clicked.connect(self.load_audio_file)
        self.save_btn.clicked.connect(self.save_reconstructed_audio)

        # 分析控制
        self.analyze_btn.clicked.connect(self.start_frequency_analysis)

        # 播放控制
        self.play_original_btn.clicked.connect(self.play_original_audio)
        self.play_reconstructed_btn.clicked.connect(self.play_reconstructed_audio)
        self.stop_btn.clicked.connect(self.stop_playback)

        # 音频播放器信号
        self.audio_player.playback_started.connect(lambda: self.stop_btn.setEnabled(True))
        self.audio_player.playback_stopped.connect(lambda: self.stop_btn.setEnabled(False))

    def load_audio_file(self):
        """加载音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            "音频文件 (*.wav *.mp3 *.flac *.ogg);;所有文件 (*)"
        )

        if file_path:
            try:
                # 加载音频
                audio_data, sample_rate = self.audio_processor.load_audio(file_path)
                self.original_audio = audio_data

                # 更新信息显示
                info = self.audio_processor.get_audio_info()
                self.update_audio_info(info)

                # 绘制原始波形
                self.spectrum_canvas.plot_waveform(audio_data, sample_rate, "原始音频波形")

                # 启用分析按钮
                self.analyze_btn.setEnabled(True)
                self.play_original_btn.setEnabled(True)

                QMessageBox.information(self, "成功", f"音频文件加载成功！\n文件: {os.path.basename(file_path)}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"音频文件加载失败：\n{str(e)}")

    def save_reconstructed_audio(self):
        """保存重构音频"""
        if self.reconstructed_audio is None:
            QMessageBox.warning(self, "警告", "没有可保存的重构音频！")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存重构音频",
            "reconstructed_audio.wav",
            "WAV文件 (*.wav);;所有文件 (*)"
        )

        if file_path:
            try:
                success = self.audio_processor.save_audio(
                    self.reconstructed_audio,
                    file_path,
                    self.audio_processor.target_sr
                )

                if success:
                    QMessageBox.information(self, "成功", f"重构音频保存成功！\n文件: {os.path.basename(file_path)}")
                else:
                    QMessageBox.critical(self, "错误", "音频保存失败！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"音频保存失败：\n{str(e)}")

    def start_frequency_analysis(self):
        """开始频率分析"""
        if self.original_audio is None:
            QMessageBox.warning(self, "警告", "请先加载音频文件！")
            return

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)

        # 创建分析线程
        self.analysis_thread = AudioAnalysisThread(
            self.original_audio,
            self.audio_processor.target_sr,
            n_components=8  # 提取8个主要分量
        )

        # 连接信号
        self.analysis_thread.analysis_completed.connect(self.on_analysis_completed)
        self.analysis_thread.progress_updated.connect(self.progress_bar.setValue)
        self.analysis_thread.error_occurred.connect(self.on_analysis_error)

        # 启动分析
        self.analysis_thread.start()

    def on_analysis_completed(self, components):
        """频率分析完成处理"""
        print(f"分析完成，获得 {len(components)} 个频率分量")

        self.frequency_components = components
        self.frequency_analyzer = self.analysis_thread.analyzer

        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)

        # 为每个分量设置original_amplitude属性
        for comp in components:
            if not hasattr(comp, 'original_amplitude'):
                comp.original_amplitude = comp.amplitude

        # 更新频率分量表格
        self.update_components_table()

        # 绘制频谱和分量
        try:
            frequencies, magnitudes = self.frequency_analyzer.get_frequency_spectrum()
            print(f"频谱数据: {len(frequencies)} 个频率点")
            self.spectrum_canvas.plot_spectrum(frequencies, magnitudes, components, "频谱分析结果")
        except Exception as e:
            print(f"绘制频谱时出错: {e}")
            import traceback
            traceback.print_exc()

        # 生成初始重构音频
        try:
            self.update_reconstructed_audio()
        except Exception as e:
            print(f"重构音频时出错: {e}")
            import traceback
            traceback.print_exc()

        QMessageBox.information(self, "完成", f"频率分析完成！\n提取了 {len(components)} 个主要频率分量。")

    def on_analysis_error(self, error_message):
        """分析错误处理"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "分析错误", f"频率分析失败：\n{error_message}")

    def update_components_table(self):
        """更新频率分量控制表格"""
        self.components_table.setRowCount(len(self.frequency_components))

        for i, component in enumerate(self.frequency_components):
            # 启用复选框
            enable_checkbox = QCheckBox()
            enable_checkbox.setChecked(component.enabled)
            enable_checkbox.stateChanged.connect(lambda state, idx=i: self.toggle_component(idx, state))
            self.components_table.setCellWidget(i, 0, enable_checkbox)

            # 频率显示
            freq_item = QTableWidgetItem(f"{component.frequency:.1f}")
            freq_item.setFlags(freq_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.components_table.setItem(i, 1, freq_item)

            # 振幅显示
            amp_item = QTableWidgetItem(f"{component.amplitude:.4f}")
            amp_item.setFlags(amp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.components_table.setItem(i, 2, amp_item)

            # 振幅调节滑块
            amp_slider = QSlider(Qt.Orientation.Horizontal)
            amp_slider.setRange(0, 200)  # 0-200%
            amp_slider.setValue(100)  # 默认100%
            amp_slider.valueChanged.connect(lambda value, idx=i: self.adjust_component_amplitude(idx, value))
            self.components_table.setCellWidget(i, 3, amp_slider)

    def toggle_component(self, index, state):
        """切换频率分量的启用状态"""
        if index < len(self.frequency_components):
            self.frequency_components[index].enabled = (state == Qt.CheckState.Checked.value)
            self.update_reconstructed_audio()
            # 更新分量波形显示
            self.spectrum_canvas.plot_components(self.frequency_components)

    def adjust_component_amplitude(self, index, value):
        """调整频率分量的振幅"""
        if index < len(self.frequency_components):
            # 将滑块值(0-200)转换为振幅倍数(0-2.0)
            multiplier = value / 100.0
            original_amplitude = self.frequency_components[index].original_amplitude
            self.frequency_components[index].amplitude = original_amplitude * multiplier

            # 更新表格显示
            amp_item = self.components_table.item(index, 2)
            if amp_item:
                amp_item.setText(f"{self.frequency_components[index].amplitude:.4f}")

            self.update_reconstructed_audio()
            # 更新分量波形显示
            self.spectrum_canvas.plot_components(self.frequency_components)

    def update_reconstructed_audio(self):
        """更新重构音频"""
        if self.frequency_components and self.frequency_analyzer:
            try:
                # 重构音频 - 不传递参数，使用默认时长
                self.reconstructed_audio = self.frequency_analyzer.reconstruct_audio()

                print(f"重构音频成功: {len(self.reconstructed_audio)} 样本")

                # 更新显示
                self.spectrum_canvas.plot_reconstructed(
                    self.reconstructed_audio,
                    self.audio_processor.target_sr,
                    "重构音频波形"
                )

                # 启用播放和保存按钮
                self.play_reconstructed_btn.setEnabled(True)
                self.save_btn.setEnabled(True)

            except Exception as e:
                print(f"重构音频失败: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "警告", f"重构音频失败：\n{str(e)}")

    def update_audio_info(self, info):
        """更新音频信息显示"""
        if info:
            info_text = f"""
📁 文件信息:
   路径: {os.path.basename(info.get('file_path', 'N/A'))}
   时长: {info.get('duration', 0):.2f} 秒
   采样率: {info.get('sample_rate', 0)} Hz
   声道数: {info.get('channels', 0)}

📊 音频特性:
   样本数: {info.get('samples', 0):,}
   最大振幅: {info.get('max_amplitude', 0):.4f}
   RMS: {info.get('rms', 0):.4f}
   动态范围: {info.get('dynamic_range', 0):.1f} dB

🎵 分析状态:
   频率分量: {len(self.frequency_components)} 个
   重构状态: {'已完成' if self.reconstructed_audio is not None else '未完成'}
            """
            self.info_text.setPlainText(info_text.strip())
        else:
            self.info_text.setPlainText("请加载音频文件...")

    def play_original_audio(self):
        """播放原始音频"""
        if self.original_audio is not None:
            try:
                print(f"播放原始音频: {len(self.original_audio)} 样本")
                self.audio_player.load_audio(self.original_audio)
                self.audio_player.play()
                print("✅ 原始音频播放开始")
            except Exception as e:
                print(f"❌ 原始音频播放失败: {e}")
                QMessageBox.warning(self, "播放错误", f"原始音频播放失败：\n{str(e)}")

    def play_reconstructed_audio(self):
        """播放重构音频"""
        if self.reconstructed_audio is not None:
            try:
                print(f"播放重构音频: {len(self.reconstructed_audio)} 样本")
                print(f"波形数据: 最小值={np.min(self.reconstructed_audio):.4f}, 最大值={np.max(self.reconstructed_audio):.4f}")
                self.audio_player.load_audio(self.reconstructed_audio)
                self.audio_player.play()
                print("✅ 重构音频播放开始")
            except Exception as e:
                print(f"❌ 重构音频播放失败: {e}")
                QMessageBox.warning(self, "播放错误", f"重构音频播放失败：\n{str(e)}")

    def stop_playback(self):
        """停止播放"""
        self.audio_player.stop()


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("音频分析器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("音频分析工具")

    # 创建主窗口
    window = AudioEditorMainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
