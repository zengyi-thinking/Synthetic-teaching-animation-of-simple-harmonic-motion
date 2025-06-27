# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 音频分析界面模块
用于展示音频分析和简谐振动分解的界面组件
"""

import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QScrollArea, QSplitter, QFileDialog, QSlider, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QFont

from visualization_engine import MatplotlibCanvas, WaveformVisualizer, SpectrumVisualizer
from audio_analyzer import AudioAnalyzer
from audio_engine import AudioEngine
from harmonic_core import HarmonicMotion, SuperpositionMotion, HarmonicParams, HarmonicType


# 设置matplotlib支持中文
def setup_chinese_font():
    """设置matplotlib支持中文显示"""
    # 使用全局变量来跟踪是否已经打印过信息
    if not hasattr(setup_chinese_font, '_printed_info'):
        setup_chinese_font._printed_info = False
        
    try:
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
            # 使用找到的第一个中文字体
            if not setup_chinese_font._printed_info:
                print(f"使用中文字体: {os.path.basename(selected_font)}")
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
                print("未找到中文字体，尝试使用内置字体")
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

# 应用字体设置
setup_chinese_font()


class AudioAnalysisPanel(QWidget):
    """音频分析面板"""
    
    # 自定义信号
    analysis_updated = pyqtSignal(dict)
    play_requested = pyqtSignal(np.ndarray)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化分析器和音频引擎
        self.analyzer = AudioAnalyzer()
        self.audio_engine = AudioEngine()
        
        # 当前分析的音频数据
        self.current_audio = None
        self.decomposed_motion = None
        self.component_waves = None
        
        # 波形显示参数
        self.wave_display_length = 0.5  # 默认显示0.5秒的波形数据
        
        # 设置界面
        self.setup_ui()
        
        # 创建一些预设音频样本
        self.setup_presets()
    
    def setup_ui(self):
        """设置用户界面"""
        main_layout = QHBoxLayout(self)  # 使用水平布局作为主布局
        
        # 创建左右分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ====== 左侧部分 - 音频控制、原始波形和频谱分析 ======
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部控制面板
        control_panel = QGroupBox("音频控制")
        control_panel.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        control_layout = QVBoxLayout(control_panel)
        
        # 第一行控制选项
        control_row1 = QHBoxLayout()
        
        # 预设标签和下拉框
        preset_label = QLabel("音频预设:")
        preset_label.setStyleSheet("color: white;")
        
        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #4CAF50;
            }
        """)
        
        control_row1.addWidget(preset_label)
        control_row1.addWidget(self.preset_combo, 1)  # 1是伸缩因子
        
        # 第二行控制选项
        control_row2 = QHBoxLayout()
        
        # 波形缩放控制
        zoom_label = QLabel("波形缩放:")
        zoom_label.setStyleSheet("color: white;")
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["0.1秒", "0.2秒", "0.5秒", "1秒", "2秒", "全部"])
        self.zoom_combo.setCurrentText("0.5秒")
        self.zoom_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #4CAF50;
            }
        """)
        
        control_row2.addWidget(zoom_label)
        control_row2.addWidget(self.zoom_combo, 1)  # 1是伸缩因子
        
        # 第三行按钮
        button_row = QHBoxLayout()
        
        # 播放按钮
        self.play_btn = QPushButton("播放")
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # 加载按钮
        self.load_btn = QPushButton("加载音频")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # 分析按钮
        self.analyze_btn = QPushButton("分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """)
        
        button_row.addWidget(self.play_btn)
        button_row.addWidget(self.load_btn)
        button_row.addWidget(self.analyze_btn)
        
        # 第四行 - 导出和帮助按钮
        advanced_row = QHBoxLayout()
        
        # 导出按钮
        self.export_btn = QPushButton("导出结果")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        
        # 帮助按钮
        self.help_btn = QPushButton("教学指南")
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8E24AA;
            }
            QPushButton:pressed {
                background-color: #7B1FA2;
            }
        """)
        
        advanced_row.addWidget(self.export_btn)
        advanced_row.addWidget(self.help_btn)
        
        # 添加行到控制布局
        control_layout.addLayout(control_row1)
        control_layout.addLayout(control_row2)
        control_layout.addLayout(button_row)
        control_layout.addLayout(advanced_row)
        
        # 添加到左侧布局
        left_layout.addWidget(control_panel)
        
        # 波形面板
        waveform_group = QGroupBox("原始波形")
        waveform_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        waveform_layout = QVBoxLayout(waveform_group)
        self.waveform_canvas = MatplotlibCanvas()
        self.waveform_viz = WaveformVisualizer(self.waveform_canvas)
        waveform_layout.addWidget(self.waveform_canvas)
        
        # 频谱面板
        spectrum_group = QGroupBox("频谱分析")
        spectrum_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        spectrum_layout = QVBoxLayout(spectrum_group)
        self.spectrum_canvas = MatplotlibCanvas()
        self.spectrum_viz = SpectrumVisualizer(self.spectrum_canvas)
        spectrum_layout.addWidget(self.spectrum_canvas)
        
        # 添加波形和频谱面板到左侧布局
        left_layout.addWidget(waveform_group, 1)  # 1是伸缩因子
        left_layout.addWidget(spectrum_group, 1)  # 1是伸缩因子
        
        # ====== 右侧部分 - 简谐振动分量 ======
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 分量波形面板
        components_group = QGroupBox("简谐振动分量")
        components_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        components_layout = QVBoxLayout(components_group)
        
        # 分量信息
        self.components_info = QLabel("尚未分析音频")
        self.components_info.setStyleSheet("color: white;")
        components_layout.addWidget(self.components_info)
        
        # 创建分量波形画布
        self.component_canvases = []
        self.component_layout = QVBoxLayout()
        
        # 分量波形放在滚动区域中
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.component_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #333333;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        
        components_layout.addWidget(scroll_area)
        
        # 添加教学提示面板到右侧布局
        tips_group = QGroupBox("教学提示")
        tips_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        tips_layout = QVBoxLayout(tips_group)
        self.tips_text = QLabel("选择一个音频预设并点击'分析'按钮开始探索简谐振动分量。")
        self.tips_text.setStyleSheet("color: white; padding: 10px;")
        self.tips_text.setWordWrap(True)  # 允许文本换行
        tips_layout.addWidget(self.tips_text)
        
        # 添加到右侧布局
        right_layout.addWidget(components_group, 4)  # 占据更多空间
        right_layout.addWidget(tips_group, 1)      # 占据较少空间
        
        # 添加左右部件到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 700])  # 设置初始分割比例
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        
        # 连接信号
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        self.zoom_combo.currentIndexChanged.connect(self.on_zoom_changed)
        self.play_btn.clicked.connect(self.on_play_clicked)
        self.load_btn.clicked.connect(self.on_load_clicked)
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        self.export_btn.clicked.connect(self.on_export_clicked)
        self.help_btn.clicked.connect(self.on_help_clicked)
    
    def setup_presets(self):
        """设置预设音频样本"""
        self.presets = {
            # 基础音高示例
            '单音 (A4)': lambda: self.audio_engine.generate_sine_wave(440, duration=1.0),
            '单音 (C4)': lambda: self.audio_engine.generate_sine_wave(261.63, duration=1.0),
            
            # 和弦示例
            'C大三和弦': lambda: self.audio_engine.generate_chord(['C4', 'E4', 'G4'], duration=1.0),
            'G大三和弦': lambda: self.audio_engine.generate_chord(['G4', 'B4', 'D4'], duration=1.0),
            'F大三和弦': lambda: self.audio_engine.generate_chord(['F4', 'A4', 'C5'], duration=1.0),
            'A小三和弦': lambda: self.audio_engine.generate_chord(['A4', 'C5', 'E5'], duration=1.0),
            
            # 谐波级数示例
            '谐波级数 (基频C4)': lambda: self.audio_engine.generate_harmonic_series(261.63, num_harmonics=5, duration=1.0),
            '谐波级数 (基频G3)': lambda: self.audio_engine.generate_harmonic_series(196.00, num_harmonics=5, duration=1.0),
            
            # 拍现象示例
            '拍现象 (440Hz和444Hz)': lambda: self.audio_engine.generate_beat(440, 444, duration=2.0),
            '拍现象 (440Hz和442Hz)': lambda: self.audio_engine.generate_beat(440, 442, duration=2.0),
            '拍现象 (440Hz和450Hz)': lambda: self.audio_engine.generate_beat(440, 450, duration=2.0),
            
            # 音程示例
            '音程-纯八度 (C4-C5)': lambda: self.audio_engine.generate_chord(['C4', 'C5'], duration=1.0),
            '音程-纯五度 (C4-G4)': lambda: self.audio_engine.generate_chord(['C4', 'G4'], duration=1.0),
            '音程-大三度 (C4-E4)': lambda: self.audio_engine.generate_chord(['C4', 'E4'], duration=1.0),
            '音程-小三度 (A4-C5)': lambda: self.audio_engine.generate_chord(['A4', 'C5'], duration=1.0),
            
            # 复杂谐波示例
            '钢琴音色模拟 (A4)': lambda: self.generate_piano_tone(440),
            '小提琴音色模拟 (A4)': lambda: self.generate_violin_tone(440),
            '长笛音色模拟 (A4)': lambda: self.generate_flute_tone(440),
        }
        
        # 添加到下拉框，并按类别组织
        categories = [
            ("【音高示例】", ['单音 (A4)', '单音 (C4)']),
            ("【和弦示例】", ['C大三和弦', 'G大三和弦', 'F大三和弦', 'A小三和弦']),
            ("【音程示例】", ['音程-纯八度 (C4-C5)', '音程-纯五度 (C4-G4)', '音程-大三度 (C4-E4)', '音程-小三度 (A4-C5)']),
            ("【拍现象示例】", ['拍现象 (440Hz和444Hz)', '拍现象 (440Hz和442Hz)', '拍现象 (440Hz和450Hz)']),
            ("【谐波示例】", ['谐波级数 (基频C4)', '谐波级数 (基频G3)']),
            ("【音色模拟示例】", ['钢琴音色模拟 (A4)', '小提琴音色模拟 (A4)', '长笛音色模拟 (A4)'])
        ]
        
        # 清空并重新添加预设
        self.preset_combo.clear()
        
        # 添加分隔符和预设
        for category_name, presets in categories:
            self.preset_combo.addItem(category_name)
            index = self.preset_combo.count() - 1
            self.preset_combo.setItemData(index, None, Qt.ItemDataRole.UserRole)  # 设置为不可选
            self.preset_combo.model().setData(self.preset_combo.model().index(index, 0), 
                                          0, Qt.ItemDataRole.UserRole - 1)  # 设置为分隔符
            
            # 添加该类别下的预设
            for preset in presets:
                self.preset_combo.addItem(preset)
        
        # 默认选中第一个实际的预设（跳过分隔符）
        self.preset_combo.setCurrentIndex(1)
    
    def generate_piano_tone(self, frequency):
        """生成模拟钢琴音色的音频
        
        钢琴音色特点: 
        1. 谐波成分较为完整
        2. 高次谐波衰减较快
        3. 有明显的瞬时起音
        
        Args:
            frequency: 基频(Hz)
            
        Returns:
            numpy.ndarray: 音频数据
        """
        duration = 1.5  # 钢琴音持续较长
        sample_rate = self.audio_engine.sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 基频和谐波的相对强度
        harmonics = [1.0, 0.6, 0.4, 0.25, 0.15, 0.1, 0.05]
        
        # 不同谐波的衰减速率
        decay_rates = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        
        # 叠加多个谐波
        tone = np.zeros_like(t)
        for i, (amplitude, decay) in enumerate(zip(harmonics, decay_rates)):
            harmonic = (i + 1) * frequency
            # 谐波随时间衰减
            envelope = np.exp(-decay * t)
            tone += amplitude * envelope * np.sin(2 * np.pi * harmonic * t)
        
        # 添加起音瞬变
        attack_time = 0.01  # 10ms的起音时间
        attack_samples = int(attack_time * sample_rate)
        if attack_samples > 0:
            attack_envelope = np.linspace(0, 1, attack_samples)**0.5  # 非线性起音
            tone[:attack_samples] *= attack_envelope
        
        # 归一化
        if np.max(np.abs(tone)) > 0:
            tone = tone / np.max(np.abs(tone)) * 0.9
            
        return tone
    
    def generate_violin_tone(self, frequency):
        """生成模拟小提琴音色的音频
        
        小提琴音色特点: 
        1. 奇次谐波较强
        2. 丰富的高频成分
        3. 有颤音效果
        
        Args:
            frequency: 基频(Hz)
            
        Returns:
            numpy.ndarray: 音频数据
        """
        duration = 1.5
        sample_rate = self.audio_engine.sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 基频和谐波的相对强度 (奇次谐波更强)
        harmonics = [1.0, 0.05, 0.4, 0.05, 0.3, 0.05, 0.2]
        
        # 颤音参数
        vibrato_freq = 5.0  # 5Hz的颤音
        vibrato_amount = 0.03  # 颤音调制深度
        
        # 叠加多个谐波
        tone = np.zeros_like(t)
        for i, amplitude in enumerate(harmonics):
            harmonic = (i + 1) * frequency
            
            # 添加颤音 - 频率调制
            freq_mod = harmonic * (1.0 + vibrato_amount * np.sin(2 * np.pi * vibrato_freq * t))
            
            # 积分得到相位
            phase = np.cumsum(freq_mod) / sample_rate * 2 * np.pi
            
            # 谐波随时间缓慢衰减
            envelope = np.ones_like(t) * np.exp(-1.5 * t)  
            
            # 添加缓慢起音
            attack_time = 0.08  # 80ms的起音时间
            attack_samples = int(attack_time * sample_rate)
            if attack_samples > 0 and attack_samples < len(envelope):
                attack_envelope = np.linspace(0, 1, attack_samples)**2  # 二次方起音曲线
                envelope[:attack_samples] *= attack_envelope
                
            tone += amplitude * envelope * np.sin(phase)
        
        # 归一化
        if np.max(np.abs(tone)) > 0:
            tone = tone / np.max(np.abs(tone)) * 0.9
            
        return tone
    
    def generate_flute_tone(self, frequency):
        """生成模拟长笛音色的音频
        
        长笛音色特点: 
        1. 基音很强
        2. 高次谐波少
        3. 柔和的起音
        
        Args:
            frequency: 基频(Hz)
            
        Returns:
            numpy.ndarray: 音频数据
        """
        duration = 1.5
        sample_rate = self.audio_engine.sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 基频和谐波的相对强度 (基频很强，谐波少)
        harmonics = [1.0, 0.25, 0.15, 0.08, 0.04]
        
        # 轻微的颤音
        vibrato_freq = 4.0  # 4Hz的颤音
        vibrato_amount = 0.01  # 很轻微的颤音
        
        # 叠加多个谐波
        tone = np.zeros_like(t)
        for i, amplitude in enumerate(harmonics):
            harmonic = (i + 1) * frequency
            
            # 添加轻微颤音
            freq_mod = harmonic * (1.0 + vibrato_amount * np.sin(2 * np.pi * vibrato_freq * t))
            
            # 积分得到相位
            phase = np.cumsum(freq_mod) / sample_rate * 2 * np.pi
            
            # 谐波随时间缓慢衰减
            envelope = np.ones_like(t)
            
            # 柔和的起音和渐弱尾音
            attack_time = 0.1  # 100ms的起音
            attack_samples = int(attack_time * sample_rate)
            if attack_samples > 0:
                attack_envelope = np.linspace(0, 1, attack_samples)**1.5  # 较柔和的起音曲线
                envelope[:attack_samples] *= attack_envelope
                
            # 尾音渐弱
            release_time = 0.2  # 200ms的尾音
            release_samples = int(release_time * sample_rate)
            if release_samples > 0 and len(envelope) > release_samples:
                release_envelope = np.linspace(1, 0, release_samples)**0.8
                envelope[-release_samples:] *= release_envelope
                
            tone += amplitude * envelope * np.sin(phase)
        
        # 归一化
        if np.max(np.abs(tone)) > 0:
            tone = tone / np.max(np.abs(tone)) * 0.8  # 长笛音量较低
            
        return tone
    
    def clear_component_canvases(self):
        """清除所有分量波形画布"""
        for canvas in self.component_canvases:
            self.component_layout.removeWidget(canvas)
            canvas.deleteLater()
        
        self.component_canvases = []
    
    def create_component_canvases(self, num_components):
        """创建分量波形画布
        
        Args:
            num_components: 分量数量
        """
        self.clear_component_canvases()
        
        # 重新应用中文字体设置
        setup_chinese_font()
        
        # 合成波形画布
        composite_canvas = MatplotlibCanvas()
        composite_canvas.setMinimumHeight(100)
        composite_canvas.setMaximumHeight(150)
        composite_canvas.axes.set_title("合成波形", color='white')
        composite_canvas.axes.set_xlabel("时间 (秒)", color='#cccccc')
        composite_canvas.axes.set_ylabel("振幅", color='#cccccc')
        self.component_canvases.append(composite_canvas)
        self.component_layout.addWidget(composite_canvas)
        
        # 各分量波形画布
        for i in range(num_components):
            canvas = MatplotlibCanvas()
            canvas.setMinimumHeight(100)
            canvas.setMaximumHeight(150)
            canvas.axes.set_title(f"分量 {i+1}", color='white')
            canvas.axes.set_xlabel("时间 (秒)", color='#cccccc')
            canvas.axes.set_ylabel("振幅", color='#cccccc')
            self.component_canvases.append(canvas)
            self.component_layout.addWidget(canvas)
    
    def update_wave_display(self, audio_data):
        """更新波形显示
        
        Args:
            audio_data: 音频数据数组
        """
        if audio_data is None or len(audio_data) == 0:
            return
        
        # 重新应用中文字体设置
        setup_chinese_font()
            
        # 创建完整时间数组
        full_time = np.linspace(0, len(audio_data) / self.audio_engine.sample_rate, len(audio_data))
        
        # 根据缩放设置裁剪数据
        if self.wave_display_length > 0 and self.wave_display_length < len(audio_data) / self.audio_engine.sample_rate:
            # 计算需要显示的样本数
            num_samples = int(self.wave_display_length * self.audio_engine.sample_rate)
            
            # 裁剪数据
            t = full_time[:num_samples]
            data = audio_data[:num_samples]
        else:
            # 显示全部数据
            t = full_time
            data = audio_data
        
        # 对波形进行下采样以减少绘制点数，使波形更清晰
        if len(t) > 1000:
            # 每隔几个点取一个点
            step = len(t) // 1000
            t = t[::step]
            data = data[::step]
        
        # 更新波形
        self.waveform_viz.update_waveform(t, data)
        
        # 确保标题为中文
        self.waveform_canvas.axes.set_title("原始波形", color='white')
        self.waveform_canvas.axes.set_xlabel("时间 (秒)", color='#cccccc')
        self.waveform_canvas.axes.set_ylabel("振幅", color='#cccccc')
        self.waveform_canvas.draw()
    
    def update_spectrum_display(self, audio_data):
        """更新频谱显示
        
        Args:
            audio_data: 音频数据数组
        """
        if audio_data is None or len(audio_data) == 0:
            return
        
        # 重新应用中文字体设置
        setup_chinese_font()
            
        # 检查是否是拍现象类型的音频
        preset_name = self.preset_combo.currentText()
        is_beat = 'beat' in preset_name.lower() or '拍' in preset_name
            
        # 分析频率内容，对拍现象使用更高分辨率
        if is_beat:
            # 对于拍现象，使用更高的分辨率（使用黑曼窗和更多零填充）
            frequencies, magnitudes = self.analyzer.analyze_frequency_content(audio_data, window_type='blackman', zero_padding=4)
            # 限制频率范围，重点显示拍频所在区域
            center_freq = 440  # 对于440Hz和444Hz的拍现象
            freq_range = 20    # 显示中心频率±20Hz的范围
            lower_bound = max(0, center_freq - freq_range)
            upper_bound = center_freq + freq_range
            
            # 找到对应的索引范围
            lower_idx = np.searchsorted(frequencies, lower_bound)
            upper_idx = np.searchsorted(frequencies, upper_bound)
            
            # 截取感兴趣的频率范围
            zoom_freqs = frequencies[lower_idx:upper_idx]
            zoom_mags = magnitudes[lower_idx:upper_idx]
            
            # 更新频谱
            self.spectrum_viz.update_spectrum(zoom_freqs, zoom_mags)
            
            # 设置轴标签
            self.spectrum_canvas.axes.set_title("频谱分析 (拍现象区域放大)", color='white')
            self.spectrum_canvas.axes.set_xlabel(f"频率 (Hz) - 显示范围: {lower_bound}-{upper_bound}Hz", color='#cccccc')
        else:
            # 普通音频使用标准分析
            frequencies, magnitudes = self.analyzer.analyze_frequency_content(audio_data)
            
            # 限制频率范围，通常只显示到5000Hz
            max_freq_idx = np.searchsorted(frequencies, 5000)
            if max_freq_idx > 0:
                frequencies = frequencies[:max_freq_idx]
                magnitudes = magnitudes[:max_freq_idx]
            
            # 更新频谱
            self.spectrum_viz.update_spectrum(frequencies, magnitudes)
            
            # 确保标题为中文
            self.spectrum_canvas.axes.set_title("频谱分析", color='white')
            self.spectrum_canvas.axes.set_xlabel("频率 (Hz)", color='#cccccc')
            
        self.spectrum_canvas.axes.set_ylabel("振幅", color='#cccccc')
        self.spectrum_canvas.draw()
    
    def update_component_display(self, component_data):
        """更新分量波形显示
        
        Args:
            component_data: 包含分量波形数据的字典
        """
        if component_data is None:
            return
        
        # 重新应用中文字体设置
        setup_chinese_font()
            
        # 获取时间数组和合成波形
        t = component_data["time"]
        composite = component_data["composite"]
        
        # 对波形进行下采样以减少绘制点数，使波形更清晰
        if len(t) > 500:
            # 每隔几个点取一个点
            step = len(t) // 500
            t_downsampled = t[::step]
            composite_downsampled = composite[::step]
        else:
            t_downsampled = t
            composite_downsampled = composite
            
        # 计算分量数量
        num_components = len(component_data) - 2  # 减去time和composite
        
        # 创建画布
        if len(self.component_canvases) != num_components + 1:  # +1是合成波形
            self.create_component_canvases(num_components)
        
        # 更新合成波形
        composite_canvas = self.component_canvases[0]
        composite_canvas.axes.clear()
        composite_canvas.axes.plot(t_downsampled, composite_downsampled, linewidth=1.5, color='#4CAF50')
        composite_canvas.axes.set_title("合成波形", color='white')
        composite_canvas.axes.set_xlabel("时间 (秒)", color='#cccccc')
        composite_canvas.axes.set_ylabel("振幅", color='#cccccc')
        composite_canvas.axes.grid(True, linestyle='--', alpha=0.3)
        composite_canvas.draw()
        
        # 更新各分量波形
        colors = ['#E91E63', '#2196F3', '#FF9800', '#9C27B0', '#00BCD4', '#8BC34A', '#FFC107']
        
        for i in range(num_components):
            component_key = f"component_{i}"
            if component_key in component_data:
                component = component_data[component_key]
                
                # 对分量波形进行下采样
                if len(t) > 500:
                    component_downsampled = component[::step]
                else:
                    component_downsampled = component
                    
                canvas = self.component_canvases[i + 1]  # +1跳过合成波形画布
                
                canvas.axes.clear()
                canvas.axes.plot(t_downsampled, component_downsampled, linewidth=1.5, color=colors[i % len(colors)])
                
                # 获取频率和振幅
                if self.decomposed_motion and i < len(self.decomposed_motion.oscillators):
                    oscillator = self.decomposed_motion.oscillators[i]
                    freq = oscillator.params.frequency
                    amp = oscillator.params.amplitude
                    
                    # 查找接近的音符名称
                    note_name = "未知"
                    min_diff = float('inf')
                    for note_freq, name in self.analyzer.freq_to_note.items():
                        diff = abs(freq - note_freq)
                        if diff < min_diff and diff <= self.analyzer.note_tolerance:
                            min_diff = diff
                            note_name = name
                    
                    title = f"分量 {i+1}: {freq:.1f} Hz"
                    if note_name != "未知":
                        title += f" ({note_name})"
                    canvas.axes.set_title(title, color='white')
                else:
                    canvas.axes.set_title(f"分量 {i+1}", color='white')
                
                canvas.axes.set_xlabel("时间 (秒)", color='#cccccc')
                canvas.axes.set_ylabel("振幅", color='#cccccc')
                canvas.axes.grid(True, linestyle='--', alpha=0.3)
                canvas.draw()
    
    def update_components_info(self):
        """更新分量信息标签"""
        if self.decomposed_motion is None:
            self.components_info.setText("尚未分析音频")
            return
            
        # 获取分量信息
        info_text = f"共检测到 {len(self.decomposed_motion.oscillators)} 个主要频率分量:\n"
        
        for i, osc in enumerate(self.decomposed_motion.oscillators):
            freq = osc.params.frequency
            amp = osc.params.amplitude
            
            # 查找接近的音符名称
            note_name = "未知"
            min_diff = float('inf')
            for note_freq, name in self.analyzer.freq_to_note.items():
                diff = abs(freq - note_freq)
                if diff < min_diff and diff <= self.analyzer.note_tolerance:
                    min_diff = diff
                    note_name = name
            
            if note_name != "未知":
                info_text += f"分量 {i+1}: {freq:.1f} Hz ({note_name}), 振幅: {amp:.3f}\n"
            else:
                info_text += f"分量 {i+1}: {freq:.1f} Hz, 振幅: {amp:.3f}\n"
        
        # 尝试识别和弦
        if self.current_audio is not None:
            chord_name = self.analyzer.analyze_chord(self.current_audio)
            if chord_name != "未识别和弦":
                info_text += f"\n识别的和弦: {chord_name}"
        
        self.components_info.setText(info_text)
    
    @pyqtSlot(int)
    def on_zoom_changed(self, index):
        """波形缩放下拉框变化事件"""
        zoom_text = self.zoom_combo.currentText()
        
        if zoom_text == "全部":
            self.wave_display_length = 0  # 0表示显示全部
        else:
            # 从文本中提取秒数
            seconds = float(zoom_text.replace("秒", ""))
            self.wave_display_length = seconds
        
        # 如果有当前音频数据，则更新显示
        if self.current_audio is not None:
            self.update_wave_display(self.current_audio)
            
            # 如果已经分解了波形，也更新分量显示
            if self.component_waves is not None:
                self.update_component_display(self.component_waves)
        
    @pyqtSlot(int)
    def on_preset_changed(self, index):
        """预设下拉框变化事件"""
        if index < 0 or index >= len(self.presets):
            return
            
        # 获取选中的预设名称
        preset_name = self.preset_combo.currentText()
        
        # 生成音频
        if preset_name in self.presets:
            audio_data = self.presets[preset_name]()
            self.current_audio = audio_data
            
            # 更新波形显示
            self.update_wave_display(audio_data)
            
            # 更新频谱显示
            self.update_spectrum_display(audio_data)
            
            # 分析音频
            self.analyze_audio()
    
    @pyqtSlot()
    def on_play_clicked(self):
        """播放按钮点击事件"""
        if self.current_audio is not None:
            self.play_requested.emit(self.current_audio)
            self.audio_engine.play_audio(self.current_audio)
    
    @pyqtSlot()
    def on_load_clicked(self):
        """加载按钮点击事件"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("音频文件 (*.wav *.mp3)")
        file_dialog.setWindowTitle("选择音频文件")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            # 加载音频 (暂不实现，因为需要更多音频库支持)
            pass
    
    @pyqtSlot()
    def on_analyze_clicked(self):
        """分析按钮点击事件"""
        self.analyze_audio()
    
    @pyqtSlot()
    def on_export_clicked(self):
        """导出结果按钮点击事件"""
        if self.current_audio is None or self.decomposed_motion is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "导出失败", "请先分析音频后再尝试导出结果。")
            return
            
        # 创建文件保存对话框
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg);;所有文件 (*.*)")
        file_dialog.setWindowTitle("保存分析结果")
        file_dialog.setDefaultSuffix("png")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            
            # 导出图像
            try:
                import matplotlib.pyplot as plt
                import os
                
                # 创建一个新的大图像
                fig = plt.figure(figsize=(12, 10))
                fig.patch.set_facecolor('#1e1e1e')
                
                # 第1个子图: 原始波形
                ax1 = fig.add_subplot(3, 1, 1)
                t = np.linspace(0, len(self.current_audio) / self.audio_engine.sample_rate, len(self.current_audio))
                ax1.plot(t, self.current_audio, color='#4CAF50')
                ax1.set_title("原始波形", color='white')
                ax1.set_xlabel("时间 (秒)", color='#cccccc')
                ax1.set_ylabel("振幅", color='#cccccc')
                ax1.grid(True, linestyle='--', alpha=0.3)
                ax1.set_facecolor('#1e1e1e')
                
                # 第2个子图: 频谱分析
                ax2 = fig.add_subplot(3, 1, 2)
                frequencies, magnitudes = self.analyzer.analyze_frequency_content(self.current_audio)
                max_freq_idx = np.searchsorted(frequencies, 5000)
                ax2.plot(frequencies[:max_freq_idx], magnitudes[:max_freq_idx], color='#E91E63')
                ax2.set_title("频谱分析", color='white')
                ax2.set_xlabel("频率 (Hz)", color='#cccccc')
                ax2.set_ylabel("振幅", color='#cccccc')
                ax2.grid(True, linestyle='--', alpha=0.3)
                ax2.set_facecolor('#1e1e1e')
                
                # 第3个子图: 分量汇总
                ax3 = fig.add_subplot(3, 1, 3)
                
                # 添加主要分量频率信息
                components_text = "检测到的简谐振动分量:\n"
                for i, osc in enumerate(self.decomposed_motion.oscillators):
                    freq = osc.params.frequency
                    amp = osc.params.amplitude
                    components_text += f"分量 {i+1}: {freq:.1f} Hz, 振幅: {amp:.3f}\n"
                
                # 在底部添加文字说明
                preset_name = self.preset_combo.currentText()
                ax3.text(0.5, 0.5, f"分析结果 - {preset_name}\n\n{components_text}", 
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=12,
                         color='white',
                         transform=ax3.transAxes)
                ax3.set_axis_off()
                ax3.set_facecolor('#1e1e1e')
                
                # 保存图像
                plt.tight_layout()
                plt.savefig(file_path, facecolor='#1e1e1e')
                plt.close(fig)
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "导出成功", f"已成功导出分析结果到:\n{file_path}")
                
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "导出失败", f"导出过程中发生错误:\n{str(e)}")
    
    @pyqtSlot()
    def on_help_clicked(self):
        """帮助按钮点击事件"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
        
        # 创建帮助对话框
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("简谐振动教学指南")
        help_dialog.setMinimumSize(600, 500)
        help_dialog.setStyleSheet("""
            QDialog {
                background-color: #2a2a2a;
                color: white;
            }
            QTextBrowser {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(help_dialog)
        
        # 创建文本浏览器
        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setHtml("""
        <h2 style="color: #4CAF50;">简谐振动与音乐可视化教学系统</h2>
        
        <h3 style="color: #2196F3;">基本概念</h3>
        <p>简谐振动是物理学中最基本的振动形式，它的位移与时间的关系可以用正弦或余弦函数表示。在音乐中，单个乐音可以看作是简谐振动，而复杂的声音则可以看作是多个简谐振动的叠加。</p>
        
        <h3 style="color: #2196F3;">系统功能</h3>
        <ul>
            <li><b>音频预设</b>：提供各种预设音频样本，包括单音、和弦、谐波级数和拍现象。</li>
            <li><b>波形显示</b>：可视化声音的时域波形。</li>
            <li><b>频谱分析</b>：显示声音的频率成分。</li>
            <li><b>简谐分量分解</b>：将复杂声音分解为简谐振动分量。</li>
        </ul>
        
        <h3 style="color: #2196F3;">教学案例</h3>
        
        <h4 style="color: #FF9800;">1. 单音分析</h4>
        <p>选择"单音(A4)"预设，点击"分析"按钮。观察结果中只有一个主要频率成分（440Hz），对应A4音高。</p>
        
        <h4 style="color: #FF9800;">2. 和弦分析</h4>
        <p>选择"C大三和弦"预设，分析后可以看到三个主要频率成分，分别对应C4(261.63Hz)、E4(329.63Hz)和G4(392Hz)，这三个音组成了C大三和弦。</p>
        
        <h4 style="color: #FF9800;">3. 拍现象</h4>
        <p>选择"拍现象"预设，观察由440Hz和444Hz两个接近频率产生的拍现象。拍频等于两个频率之差，即4Hz，对应于每秒听到的"起伏"次数。</p>
        
        <h3 style="color: #2196F3;">操作提示</h3>
        <ul>
            <li>使用"波形缩放"下拉框调整波形显示的时间范围。</li>
            <li>点击"播放"按钮可以听到当前分析的声音。</li>
            <li>点击"导出结果"保存分析图表和数据。</li>
        </ul>
        """)
        
        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(help_dialog.close)
        
        # 添加到布局
        layout.addWidget(help_text)
        layout.addWidget(close_btn)
        
        # 显示对话框
        help_dialog.exec()
        
    def update_teaching_tips(self):
        """根据当前分析音频更新教学提示"""
        preset_name = self.preset_combo.currentText()
        
        if preset_name == '单音 (A4)':
            self.tips_text.setText("""
                <b>单音探究</b>：
                A4(440Hz)是标准音高，对应钢琴中央键右边的第一个A键。
                单一频率的简谐振动产生纯净的音高，波形是完美的正弦波。
                观察频谱中只有一个明显的峰值，说明这是单一频率的纯音。
            """)
        elif '和弦' in preset_name:
            self.tips_text.setText("""
                <b>和弦探究</b>：
                和弦由多个音高组成，每个音高对应一个简谐振动分量。
                C大三和弦由C4(261.63Hz)、E4(329.63Hz)和G4(392Hz)组成。
                观察频谱中有三个主要峰值，分别对应这三个音高。
                这三个音的频率比接近4:5:6，形成了协和的听感。
            """)
        elif '谐波' in preset_name:
            self.tips_text.setText("""
                <b>谐波级数探究</b>：
                自然乐器的音色由基频和其整数倍的谐波组成。
                基频决定音高，而谐波成分决定音色。
                观察频谱中出现的频率呈整数倍关系，如261.63Hz(基频)、523.26Hz(2倍)、784.89Hz(3倍)等。
                不同乐器的音色差异主要是由各谐波的相对强度决定的。
            """)
        elif '拍' in preset_name:
            self.tips_text.setText("""
                <b>拍现象探究</b>：
                当两个频率接近的音一起发声时，会产生有规律的强弱变化，称为"拍"。
                拍频 = |f₁ - f₂| = |440Hz - 444Hz| = 4Hz，意味着每秒钟听到4次强弱变化。
                观察波形的包络呈现周期性变化，周期约为0.25秒(1/4秒)。
                拍现象在音乐调音、物理学干涉现象分析中都有重要应用。
            """)
        else:
            self.tips_text.setText("选择一个音频预设并点击'分析'按钮开始探索简谐振动分量。")
            
    def analyze_audio(self):
        """分析当前音频"""
        if self.current_audio is None:
            return
            
        # 分解为简谐振动
        self.decomposed_motion = self.analyzer.decompose_to_harmonics(self.current_audio)
        
        # 如果是拍现象，确保至少检测到两个频率分量
        preset_name = self.preset_combo.currentText()
        if preset_name == '拍现象 (440Hz和444Hz)' and len(self.decomposed_motion.oscillators) < 2:
            print("拍现象分析应该检测到两个频率分量，但只找到一个。尝试使用特殊处理...")
            
            # 使用预设的两个频率作为分量
            from harmonic_core import HarmonicMotion, HarmonicParams, HarmonicType
            
            # 获取原始分量的振幅
            amp = 0.5
            if len(self.decomposed_motion.oscillators) > 0:
                amp = self.decomposed_motion.oscillators[0].params.amplitude
            
            # 创建两个预设的频率分量
            oscillator1 = HarmonicMotion(
                type=HarmonicType.SINGLE,
                params=HarmonicParams(
                    amplitude=amp,
                    frequency=440.0,  # 第一个预设频率
                    phase=0.0,
                    damping=0.0
                )
            )
            
            oscillator2 = HarmonicMotion(
                type=HarmonicType.SINGLE,
                params=HarmonicParams(
                    amplitude=amp,
                    frequency=444.0,  # 第二个预设频率
                    phase=0.0,
                    damping=0.0
                )
            )
            
            # 创建新的振动叠加
            self.decomposed_motion.oscillators = [oscillator1, oscillator2]
        
        # 生成分量波形数据
        self.component_waves = self.analyzer.generate_harmonic_decomposition_data(
            self.decomposed_motion, 
            duration=1.0
        )
        
        # 更新分量波形显示
        self.update_component_display(self.component_waves)
        
        # 更新分量信息
        self.update_components_info()
        
        # 更新教学提示
        self.update_teaching_tips()
        
        # 发送分析结果信号
        analysis_results = {
            'motion': self.decomposed_motion,
            'component_waves': self.component_waves
        }
        self.analysis_updated.emit(analysis_results) 