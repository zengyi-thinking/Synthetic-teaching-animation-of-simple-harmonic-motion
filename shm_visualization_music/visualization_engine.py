# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 可视化引擎
负责绘制波形、频谱和振动图形
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.animation as animation
from typing import List, Tuple, Dict, Optional, Union, Callable
from PyQt6.QtCore import QObject, pyqtSignal

from harmonic_core import HarmonicMotion, SuperpositionMotion, HarmonicParams, HarmonicType


# 设置matplotlib支持中文
def setup_chinese_font():
    """设置matplotlib支持中文显示"""
    # 使用全局变量来跟踪是否已经打印过信息
    if not hasattr(setup_chinese_font, '_printed_info'):
        setup_chinese_font._printed_info = False
    
    try:
        # 查找系统中的中文字体，优先使用微软雅黑/思源/文泉驿等更完整的字体
        # 按优先级排序的字体关键词列表
        font_priorities = [
            'microsoft yahei', 'msyh',  # 微软雅黑
            'simsun', 'simsun-extb',    # 宋体
            'simhei',                   # 黑体
            'source han sans', 'source han serif',  # 思源黑体/宋体
            'wqy',                      # 文泉驿
            'noto sans cjk', 'noto serif cjk',  # Noto CJK
            'droid sans fallback',      # Android默认中文
            'kaiti', 'simkai',          # 楷体
            'fangsong',                 # 仿宋
            'nsimsun'                   # 新宋体
        ]
        
        # 收集所有系统字体
        all_fonts = fm.findSystemFonts()
        
        # 按优先级查找中文字体
        chinese_fonts = []
        selected_font = None
        
        for priority_font in font_priorities:
            matching_fonts = [f for f in all_fonts if priority_font in f.lower()]
            if matching_fonts:
                chinese_fonts.extend(matching_fonts)
                if selected_font is None:
                    selected_font = matching_fonts[0]
        
        # 如果找到了中文字体
        if selected_font:
            if not setup_chinese_font._printed_info:
                print(f"可视化引擎使用中文字体: {os.path.basename(selected_font)}")
                setup_chinese_font._printed_info = True
                
            # 获取字体属性
            font_prop = fm.FontProperties(fname=selected_font)
            font_name = font_prop.get_name()
            
            # 设置matplotlib字体参数
            plt.rcParams['font.sans-serif'] = [font_name, 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            plt.rcParams['font.family'] = 'sans-serif'
            
            # 直接设置默认字体属性，这对于中文标签很重要
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['mathtext.fontset'] = 'cm'  # 使用计算机现代字体集
            
            # 额外设置，尝试解决特殊字符问题
            plt.rcParams['axes.formatter.use_mathtext'] = True
            
            return True
        else:
            # 回退到内置字体
            if not setup_chinese_font._printed_info:
                print("可视化引擎未找到中文字体，尝试使用内置字体")
                setup_chinese_font._printed_info = True
                
            # 尝试使用matplotlib内置支持的字体
            plt.rcParams['font.sans-serif'] = [
                'DejaVu Sans',       # Linux内置
                'Bitstream Vera Sans',
                'Arial Unicode MS',  # Windows内置
                'Hiragino Sans GB',  # macOS内置
                'SimHei', 'SimSun',  # 希望matplotlib已预先注册
                'sans-serif'         # 最终回退
            ]
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 强制使用字体支持中文的基本回退设置
            from matplotlib import rcsetup
            fallback_fonts = [f for f in rcsetup.get_validation_for_rcparam('font.sans-serif')[1] if 'WenQuanYi' in f or 'Noto' in f]
            if fallback_fonts:
                plt.rcParams['font.sans-serif'] = fallback_fonts + plt.rcParams['font.sans-serif']
                
            return True
    except Exception as e:
        if not setup_chinese_font._printed_info:
            print(f"设置中文字体失败: {e}")
            setup_chinese_font._printed_info = True
        return False

# 在模块导入时立即应用字体设置
setup_chinese_font()


class MatplotlibCanvas(FigureCanvasQTAgg):
    """Matplotlib画布，用于在Qt界面中绘图"""
    
    def __init__(self, fig=None, parent=None, dpi=100):
        # 重新应用中文字体设置，确保每个画布都应用了字体设置
        setup_chinese_font()
        
        if fig is None:
            fig = Figure(figsize=(5, 4), dpi=dpi)
        self.fig = fig
        super(MatplotlibCanvas, self).__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # 设置图表样式
        plt.style.use('dark_background')
        self.fig.patch.set_facecolor('#2a2a2a')  # 深灰背景
        self.axes.set_facecolor('#1e1e1e')      # 更深的灰色
        self.axes.spines['bottom'].set_color('#cccccc')
        self.axes.spines['top'].set_color('#cccccc')
        self.axes.spines['left'].set_color('#cccccc')
        self.axes.spines['right'].set_color('#cccccc')
        self.axes.tick_params(colors='#cccccc')
        self.axes.xaxis.label.set_color('#cccccc')
        self.axes.yaxis.label.set_color('#cccccc')
        self.axes.title.set_color('#ffffff')


class WaveformVisualizer(QObject):
    """波形可视化器，用于绘制时域波形"""
    
    update_complete = pyqtSignal()
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.time_data = np.linspace(0, 1, 1000)
        self.wave_data = np.zeros_like(self.time_data)
        self.line = None
        self.point_marker = None
        self.current_time = 0
        self.is_playing = False
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(0, 1)
        self.canvas.axes.set_ylim(-1.1, 1.1)
        self.canvas.axes.set_xlabel('时间 (秒)')
        self.canvas.axes.set_ylabel('振幅')
        self.canvas.axes.set_title('波形图')
        
        # 初始化绘图元素
        self._init_plot()
    
    def _init_plot(self):
        """初始化绘图元素"""
        # 确保应用了中文字体设置
        setup_chinese_font()
        
        # 波形线
        self.line, = self.canvas.axes.plot(
            self.time_data, 
            self.wave_data, 
            color='#4CAF50', 
            linewidth=2
        )
        
        # 当前位置标记
        self.point_marker, = self.canvas.axes.plot(
            [0], [0], 
            'o', 
            markersize=8, 
            color='#FF9800', 
            alpha=0.8
        )
        
        # 垂直线标记当前位置
        self.time_line = self.canvas.axes.axvline(
            x=0, 
            color='#03A9F4', 
            linestyle='--', 
            alpha=0.6
        )
        
        # 再次设置中文标题和标签，确保中文显示
        self.canvas.axes.set_xlabel('时间 (秒)')
        self.canvas.axes.set_ylabel('振幅')
        self.canvas.axes.set_title('波形图')
        
        self.canvas.draw()
    
    def update_waveform(self, time_data, wave_data, current_time=None):
        """更新波形数据
        
        Args:
            time_data: 时间数组
            wave_data: 波形数据
            current_time: 当前时间点
        """
        # 确保应用了中文字体设置
        setup_chinese_font()
        
        self.time_data = time_data
        self.wave_data = wave_data
        
        if current_time is not None:
            self.current_time = current_time
        
        # 更新坐标轴范围
        x_min, x_max = min(time_data), max(time_data)
        y_min, y_max = min(wave_data), max(wave_data)
        padding = (y_max - y_min) * 0.1
        
        self.canvas.axes.set_xlim(x_min, x_max)
        self.canvas.axes.set_ylim(y_min - padding, y_max + padding)
        
        # 更新波形
        self.line.set_data(time_data, wave_data)
        
        # 找到最接近当前时间的索引
        if current_time is not None:
            idx = np.argmin(np.abs(time_data - current_time))
            self.point_marker.set_data([time_data[idx]], [wave_data[idx]])
            self.time_line.set_xdata([time_data[idx]])
        
        # 再次设置中文标题和标签，确保中文显示
        self.canvas.axes.set_xlabel('时间 (秒)')
        self.canvas.axes.set_ylabel('振幅')
        self.canvas.axes.set_title('原始波形')
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def update_current_time(self, current_time):
        """更新当前时间位置
        
        Args:
            current_time: 当前时间点
        """
        self.current_time = current_time
        
        # 找到最接近当前时间的索引
        idx = np.argmin(np.abs(self.time_data - current_time))
        
        # 更新标记位置
        self.point_marker.set_data([self.time_data[idx]], [self.wave_data[idx]])
        self.time_line.set_xdata([self.time_data[idx]])
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def clear(self):
        """清除波形图"""
        self.line.set_data([], [])
        self.point_marker.set_data([], [])
        self.time_line.set_xdata([0])
        self.canvas.draw()


class SpectrumVisualizer(QObject):
    """频谱可视化器，用于绘制频域分析"""
    
    update_complete = pyqtSignal()
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.freq_data = np.linspace(0, 1000, 1000)
        self.magnitude_data = np.zeros_like(self.freq_data)
        self.bars = None
        self.peak_markers = []  # 存储峰值标记点
        self.peak_labels = []   # 存储峰值标签
        
        # 确保应用中文字体
        setup_chinese_font()
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(0, 1000)
        self.canvas.axes.set_ylim(0, 1.1)
        self.canvas.axes.set_xlabel('频率 (Hz)')
        self.canvas.axes.set_ylabel('归一化振幅')
        self.canvas.axes.set_title('频谱图')
        
        # 初始化绘图元素
        self._init_plot()
    
    def _init_plot(self):
        """初始化绘图元素"""
        # 确保应用中文字体
        setup_chinese_font()
        
        # 使用线条代替条形图，性能更好
        self.line, = self.canvas.axes.plot(
            self.freq_data, 
            self.magnitude_data, 
            color='#E91E63', 
            linewidth=1.5
        )
        
        # 添加标记音符频率的垂直线
        self.note_lines = {}
        self.note_texts = {}
        
        # 常用音符频率
        note_freqs = {
            'C4': 261.63,
            'E4': 329.63,
            'G4': 392.00,
            'A4': 440.00,
            'C5': 523.25
        }
        
        for note, freq in note_freqs.items():
            # 添加垂直线
            line = self.canvas.axes.axvline(
                x=freq, 
                color='#FFEB3B', 
                linestyle='--', 
                alpha=0.4
            )
            
            # 添加文本标签
            text = self.canvas.axes.text(
                freq, 1.05, 
                note, 
                horizontalalignment='center',
                color='#FFEB3B'
            )
            
            self.note_lines[note] = line
            self.note_texts[note] = text
        
        # 再次设置中文标题和标签
        self.canvas.axes.set_xlabel('频率 (Hz)')
        self.canvas.axes.set_ylabel('归一化振幅')
        self.canvas.axes.set_title('频谱图')
        
        self.canvas.draw()
    
    def _find_peaks(self, freqs, mags, threshold=0.3, min_distance=5):
        """找出频谱中的主要峰值
        
        Args:
            freqs: 频率数组
            mags: 幅值数组
            threshold: 峰值阈值，相对于最大值的比例
            min_distance: 峰值之间的最小间隔（索引数）
            
        Returns:
            peak_freqs, peak_mags: 峰值频率和对应幅值
        """
        from scipy.signal import find_peaks
        
        # 如果频谱为空，返回空列表
        if len(freqs) == 0 or len(mags) == 0:
            return [], []
            
        # 找出峰值
        height = np.max(mags) * threshold if np.max(mags) > 0 else 0
        peaks, _ = find_peaks(mags, height=height, distance=min_distance)
        
        # 提取峰值频率和幅值
        peak_freqs = freqs[peaks]
        peak_mags = mags[peaks]
        
        # 按幅值降序排序
        sort_indices = np.argsort(peak_mags)[::-1]
        peak_freqs = peak_freqs[sort_indices]
        peak_mags = peak_mags[sort_indices]
        
        return peak_freqs, peak_mags
    
    def update_spectrum(self, freq_data, magnitude_data, max_freq=None):
        """更新频谱数据
        
        Args:
            freq_data: 频率数组
            magnitude_data: 幅值数组
            max_freq: 最大频率，用于限制显示范围
        """
        # 确保应用中文字体
        setup_chinese_font()
        
        self.freq_data = freq_data
        self.magnitude_data = magnitude_data
        
        # 归一化幅度值
        if np.max(magnitude_data) > 0:
            self.magnitude_data = magnitude_data / np.max(magnitude_data)
        
        # 智能调整最大频率显示范围
        # 找出幅值大于5%最大值的最大频率，作为显示上限
        if max_freq is None:
            if len(freq_data) > 0 and len(magnitude_data) > 0:
                significant_freqs = freq_data[magnitude_data > 0.05 * np.max(magnitude_data)]
                if len(significant_freqs) > 0:
                    max_display_freq = min(1000, np.ceil(max(significant_freqs) * 1.5))  # 显示到最大有效频率的1.5倍，但不超过1000Hz
                    max_freq = max_display_freq
                else:
                    max_freq = 1000  # 如果没有明显的频率成分，默认显示1000Hz
            else:
                max_freq = 1000
        
        # 更新坐标轴范围
        self.canvas.axes.set_xlim(0, max_freq)
        self.canvas.axes.set_ylim(0, 1.1)
        
        # 更新频谱线
        self.line.set_data(freq_data, self.magnitude_data)
        
        # 清除旧的峰值标记
        for marker in self.peak_markers:
            if marker in self.canvas.axes.lines:
                marker.remove()
        self.peak_markers = []
        
        for label in self.peak_labels:
            if label in self.canvas.axes.texts:
                label.remove()
        self.peak_labels = []
        
        # 找出主要峰值并标记
        peak_freqs, peak_mags = self._find_peaks(freq_data, self.magnitude_data, threshold=0.1)
        
        # 只显示最强的几个峰值
        max_peaks_to_show = 10 if len(peak_freqs) <= 10 else 10
        
        # 检测是否是拍现象（两个频率接近的峰值）
        is_beat = False
        if len(peak_freqs) >= 2:
            # 计算接近的频率对
            close_freq_pairs = []
            for i in range(len(peak_freqs)):
                for j in range(i+1, len(peak_freqs)):
                    freq_diff = abs(peak_freqs[i] - peak_freqs[j])
                    # 如果频率差小于10Hz，可能是拍现象
                    if freq_diff < 10:
                        close_freq_pairs.append((i, j, freq_diff))
                        is_beat = True
            
            # 如果检测到拍现象，优先标记这些频率对
            if is_beat:
                # 按频率差排序
                close_freq_pairs.sort(key=lambda x: x[2])
                
                # 标记最接近的频率对
                for i, j, diff in close_freq_pairs[:3]:  # 最多标记前3对
                    # 添加第一个峰值
                    marker1, = self.canvas.axes.plot(
                        peak_freqs[i], peak_mags[i],
                        'o', markersize=8, 
                        color='#FF9800',  # 使用醒目的颜色
                        alpha=0.9
                    )
                    self.peak_markers.append(marker1)
                    
                    # 标记文本（频率和频率差）
                    text1 = self.canvas.axes.text(
                        peak_freqs[i], peak_mags[i] + 0.07,
                        f"{peak_freqs[i]:.1f} Hz",
                        horizontalalignment='center',
                        fontsize=9,
                        color='white',
                        bbox=dict(facecolor='#333333', alpha=0.7, boxstyle='round,pad=0.2')
                    )
                    self.peak_labels.append(text1)
                    
                    # 添加第二个峰值
                    marker2, = self.canvas.axes.plot(
                        peak_freqs[j], peak_mags[j],
                        'o', markersize=8, 
                        color='#FF9800',  # 使用相同颜色表示它们是一对
                        alpha=0.9
                    )
                    self.peak_markers.append(marker2)
                    
                    # 标记文本（频率）
                    text2 = self.canvas.axes.text(
                        peak_freqs[j], peak_mags[j] + 0.07,
                        f"{peak_freqs[j]:.1f} Hz",
                        horizontalalignment='center',
                        fontsize=9,
                        color='white',
                        bbox=dict(facecolor='#333333', alpha=0.7, boxstyle='round,pad=0.2')
                    )
                    self.peak_labels.append(text2)
                    
                    # 添加频率差注释
                    x_mid = (peak_freqs[i] + peak_freqs[j]) / 2
                    y_mid = max(peak_mags[i], peak_mags[j]) + 0.15
                    beat_text = self.canvas.axes.text(
                        x_mid, y_mid,
                        f"拍频: {diff:.1f} Hz",
                        horizontalalignment='center',
                        fontsize=9,
                        color='#FF9800',
                        weight='bold',
                        bbox=dict(facecolor='#333333', alpha=0.8, boxstyle='round,pad=0.2')
                    )
                    self.peak_labels.append(beat_text)
                    
                    # 添加连接两个峰值的虚线
                    connector, = self.canvas.axes.plot(
                        [peak_freqs[i], peak_freqs[j]],
                        [peak_mags[i] - 0.05, peak_mags[j] - 0.05],
                        '--', color='#FF9800', alpha=0.6, linewidth=1.5
                    )
                    self.peak_markers.append(connector)
        
        # 如果不是拍现象，或者除了拍现象峰值外，还要标记其他峰值
        if not is_beat or max_peaks_to_show:
            num_peaks = min(max_peaks_to_show or 5, len(peak_freqs))
            
            # 使用不同的颜色
            colors = ['#4CAF50', '#2196F3', '#9C27B0', '#E91E63', '#00BCD4', 
                     '#8BC34A', '#FFC107', '#795548', '#607D8B', '#F44336']
            
            already_marked = set()  # 跟踪已标记的频率索引
            
            # 如果有拍现象，则需要跳过已经标记过的峰值
            if is_beat:
                for i, j, _ in close_freq_pairs[:3]:
                    already_marked.add(i)
                    already_marked.add(j)
            
            marked_count = 0
            for i in range(len(peak_freqs)):
                if i in already_marked:
                    continue
                    
                if marked_count >= num_peaks:
                    break
                    
                color = colors[marked_count % len(colors)]
                
                # 添加峰值标记点
                marker, = self.canvas.axes.plot(
                    peak_freqs[i], peak_mags[i],
                    'o', markersize=6, 
                    color=color, 
                    alpha=0.8
                )
                self.peak_markers.append(marker)
                
                # 添加频率标签
                text = self.canvas.axes.text(
                    peak_freqs[i], peak_mags[i] + 0.05,
                    f"{peak_freqs[i]:.1f} Hz",
                    horizontalalignment='center',
                    fontsize=8,
                    color='white',
                    bbox=dict(facecolor='#333333', alpha=0.7, boxstyle='round,pad=0.2')
                )
                self.peak_labels.append(text)
                
                marked_count += 1
        
        # 再次设置中文标题和标签
        self.canvas.axes.set_xlabel('频率 (Hz)')
        self.canvas.axes.set_ylabel('归一化振幅')
        self.canvas.axes.set_title('频谱分析')
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def highlight_frequency(self, freq, alpha=1.0, color='#FF5722'):
        """高亮显示特定频率
        
        Args:
            freq: 要高亮的频率
            alpha: 透明度
            color: 颜色
        """
        # 添加高亮线
        highlight_line = self.canvas.axes.axvline(
            x=freq, 
            color=color, 
            linestyle='-', 
            alpha=alpha,
            linewidth=2
        )
        
        self.canvas.draw()
        return highlight_line
    
    def clear(self):
        """清除频谱图"""
        self.line.set_data([], [])
        self.canvas.draw()


class HarmonicMotionVisualizer(QObject):
    """简谐振动可视化器，用于绘制运动轨迹"""
    
    update_complete = pyqtSignal()
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.time_data = np.linspace(0, 2*np.pi, 100)
        self.motion_data = np.zeros_like(self.time_data)
        self.is_playing = False
        
        # 绘图元素
        self.line = None
        self.point_marker = None
        self.pendulum_line = None
        self.spring_line = None
        
        # 当前状态
        self.current_time = 0
        self.current_position = 0
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(-1.2, 1.2)
        self.canvas.axes.set_ylim(-1.2, 1.2)
        self.canvas.axes.set_aspect('equal')
        self.canvas.axes.set_title('简谐振动图')
        
        # 隐藏刻度标签
        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])
        
        # 显示参考坐标轴
        self.canvas.axes.axhline(y=0, color='#555555', linestyle='-', alpha=0.5)
        self.canvas.axes.axvline(x=0, color='#555555', linestyle='-', alpha=0.5)
        
        # 初始化绘图元素
        self._init_plot()
    
    def _init_plot(self):
        """初始化绘图元素"""
        # 轨迹线
        self.line, = self.canvas.axes.plot(
            [], [], 
            color='#42A5F5', 
            linewidth=2, 
            alpha=0.6
        )
        
        # 质点标记
        self.point_marker, = self.canvas.axes.plot(
            [0], [0], 
            'o', 
            markersize=12, 
            color='#FF5722', 
            alpha=0.9
        )
        
        self.canvas.draw()
    
    def set_pendulum_mode(self):
        """设置为单摆可视化模式"""
        # 清除之前的图形
        if self.spring_line is not None:
            self.spring_line.remove()
            self.spring_line = None
        
        # 添加摆线
        if self.pendulum_line is None:
            self.pendulum_line, = self.canvas.axes.plot(
                [0, 0], [0, 0], 
                color='#AAAAAA', 
                linewidth=2, 
                alpha=0.7
            )
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(-1.2, 1.2)
        self.canvas.axes.set_ylim(-1.2, 0.2)
        
        # 绘制固定点
        self.canvas.axes.plot([0], [0], 'o', markersize=6, color='#AAAAAA')
        
        self.canvas.draw()
    
    def set_spring_mode(self):
        """设置为弹簧振子可视化模式"""
        # 清除之前的图形
        if self.pendulum_line is not None:
            self.pendulum_line.remove()
            self.pendulum_line = None
        
        # 添加弹簧线
        if self.spring_line is None:
            self.spring_line, = self.canvas.axes.plot(
                [0, 0], [0, 0], 
                color='#AAAAAA', 
                linewidth=2, 
                alpha=0.7
            )
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(-1.2, 1.2)
        self.canvas.axes.set_ylim(-0.2, 0.2)
        
        # 绘制固定点
        self.canvas.axes.plot([-1], [0], 's', markersize=10, color='#AAAAAA')
        
        self.canvas.draw()
    
    def update_motion(self, time_data, motion_data, current_time=None):
        """更新运动数据
        
        Args:
            time_data: 时间数组
            motion_data: 位置数据
            current_time: 当前时间点
        """
        self.time_data = time_data
        self.motion_data = motion_data
        
        if current_time is not None:
            self.current_time = current_time
            
            # 找到最接近当前时间的索引
            idx = np.argmin(np.abs(time_data - current_time))
            self.current_position = motion_data[idx]
        
        # 更新轨迹线
        self.line.set_data(self.time_data, self.motion_data)
        
        # 更新质点位置
        self.point_marker.set_data([self.current_position], [0])
        
        # 如果是单摆模式
        if self.pendulum_line is not None:
            # 计算摆线的坐标，从(0,0)到当前位置
            pendulum_length = 1.0
            angle = np.arcsin(self.current_position / pendulum_length)
            pendulum_x = pendulum_length * np.sin(angle)
            pendulum_y = -pendulum_length * np.cos(angle)
            self.pendulum_line.set_data([0, pendulum_x], [0, pendulum_y])
            self.point_marker.set_data([pendulum_x], [pendulum_y])
        
        # 如果是弹簧模式
        if self.spring_line is not None:
            # 从固定点(-1,0)到当前位置
            self.spring_line.set_data([-1, self.current_position], [0, 0])
            self.point_marker.set_data([self.current_position], [0])
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def update_current_time(self, current_time):
        """更新当前时间位置
        
        Args:
            current_time: 当前时间点
        """
        self.current_time = current_time
        
        # 找到最接近当前时间的索引
        idx = np.argmin(np.abs(self.time_data - current_time))
        self.current_position = self.motion_data[idx]
        
        # 更新质点位置
        self.point_marker.set_data([self.current_position], [0])
        
        # 如果是单摆模式
        if self.pendulum_line is not None:
            # 计算摆线的坐标，从(0,0)到当前位置
            pendulum_length = 1.0
            angle = np.arcsin(self.current_position / pendulum_length)
            pendulum_x = pendulum_length * np.sin(angle)
            pendulum_y = -pendulum_length * np.cos(angle)
            self.pendulum_line.set_data([0, pendulum_x], [0, pendulum_y])
            self.point_marker.set_data([pendulum_x], [pendulum_y])
        
        # 如果是弹簧模式
        if self.spring_line is not None:
            # 从固定点(-1,0)到当前位置
            self.spring_line.set_data([-1, self.current_position], [0, 0])
            self.point_marker.set_data([self.current_position], [0])
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def clear(self):
        """清除运动图"""
        self.line.set_data([], [])
        self.point_marker.set_data([0], [0])
        if self.pendulum_line is not None:
            self.pendulum_line.set_data([0, 0], [0, 0])
        if self.spring_line is not None:
            self.spring_line.set_data([-1, 0], [0, 0])
        self.canvas.draw()


class LissajousVisualizer(QObject):
    """李萨如图形可视化器"""
    
    update_complete = pyqtSignal()
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.x_data = np.zeros(100)
        self.y_data = np.zeros(100)
        self.current_x = 0
        self.current_y = 0
        self.is_playing = False
        
        # 绘图元素
        self.line = None
        self.point_marker = None
        self.trail_line = None
        self.trail_x = []
        self.trail_y = []
        self.max_trail_length = 100
        
        # 设置坐标轴
        self.canvas.axes.set_xlim(-1.2, 1.2)
        self.canvas.axes.set_ylim(-1.2, 1.2)
        self.canvas.axes.set_aspect('equal')
        self.canvas.axes.set_title('李萨如图形')
        
        # 显示参考坐标轴
        self.canvas.axes.axhline(y=0, color='#555555', linestyle='-', alpha=0.5)
        self.canvas.axes.axvline(x=0, color='#555555', linestyle='-', alpha=0.5)
        
        # 初始化绘图元素
        self._init_plot()
    
    def _init_plot(self):
        """初始化绘图元素"""
        # 轨迹线
        self.line, = self.canvas.axes.plot(
            self.x_data, 
            self.y_data, 
            color='#9C27B0', 
            linewidth=1.5, 
            alpha=0.5
        )
        
        # 当前点标记
        self.point_marker, = self.canvas.axes.plot(
            [0], [0], 
            'o', 
            markersize=10, 
            color='#FF9800', 
            alpha=0.9
        )
        
        # 轨迹线
        self.trail_line, = self.canvas.axes.plot(
            [], [], 
            color='#4CAF50', 
            linewidth=2, 
            alpha=0.8
        )
        
        self.canvas.draw()
    
    def update_lissajous(self, x_data, y_data, current_x=None, current_y=None):
        """更新李萨如图形数据
        
        Args:
            x_data: X坐标数组
            y_data: Y坐标数组
            current_x: 当前X坐标
            current_y: 当前Y坐标
        """
        self.x_data = x_data
        self.y_data = y_data
        
        if current_x is not None and current_y is not None:
            self.current_x = current_x
            self.current_y = current_y
            
            # 添加当前点到轨迹
            self.trail_x.append(current_x)
            self.trail_y.append(current_y)
            
            # 限制轨迹长度
            if len(self.trail_x) > self.max_trail_length:
                self.trail_x = self.trail_x[-self.max_trail_length:]
                self.trail_y = self.trail_y[-self.max_trail_length:]
        
        # 更新李萨如图形
        self.line.set_data(x_data, y_data)
        
        # 更新当前点
        self.point_marker.set_data([self.current_x], [self.current_y])
        
        # 更新轨迹
        self.trail_line.set_data(self.trail_x, self.trail_y)
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def update_current_position(self, current_x, current_y):
        """更新当前位置
        
        Args:
            current_x: 当前X坐标
            current_y: 当前Y坐标
        """
        self.current_x = current_x
        self.current_y = current_y
        
        # 添加当前点到轨迹
        self.trail_x.append(current_x)
        self.trail_y.append(current_y)
        
        # 限制轨迹长度
        if len(self.trail_x) > self.max_trail_length:
            self.trail_x = self.trail_x[-self.max_trail_length:]
            self.trail_y = self.trail_y[-self.max_trail_length:]
        
        # 更新当前点
        self.point_marker.set_data([current_x], [current_y])
        
        # 更新轨迹
        self.trail_line.set_data(self.trail_x, self.trail_y)
        
        self.canvas.draw()
        self.update_complete.emit()
    
    def set_trail_length(self, length):
        """设置轨迹长度
        
        Args:
            length: 轨迹点数量
        """
        self.max_trail_length = length
        
        # 裁剪现有轨迹
        if len(self.trail_x) > length:
            self.trail_x = self.trail_x[-length:]
            self.trail_y = self.trail_y[-length:]
            self.trail_line.set_data(self.trail_x, self.trail_y)
            self.canvas.draw()
    
    def clear_trail(self):
        """清除轨迹"""
        self.trail_x = []
        self.trail_y = []
        self.trail_line.set_data([], [])
        self.canvas.draw()
    
    def clear(self):
        """清除所有图形"""
        self.line.set_data([], [])
        self.point_marker.set_data([0], [0])
        self.clear_trail()
        self.canvas.draw()


# 测试代码
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("可视化测试")
    window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # 创建画布
    canvas = MatplotlibCanvas()
    layout.addWidget(canvas)
    
    # 创建波形可视化器
    visualizer = WaveformVisualizer(canvas)
    
    # 生成测试数据
    time_data = np.linspace(0, 1, 1000)
    wave_data = np.sin(2 * np.pi * 5 * time_data)  # 5Hz正弦波
    
    # 更新波形
    visualizer.update_waveform(time_data, wave_data, 0.5)
    
    window.show()
    sys.exit(app.exec()) 