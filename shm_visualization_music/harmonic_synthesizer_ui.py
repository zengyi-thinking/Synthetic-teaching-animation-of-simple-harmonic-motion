# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 简谐波合成器UI模块
允许用户添加、调整多个简谐波分量并合成音频
"""

import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QScrollArea, QSplitter, QFileDialog, QSlider, QCheckBox,
    QFormLayout, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QFont

from visualization_engine import MatplotlibCanvas, WaveformVisualizer, SpectrumVisualizer
from audio_engine import AudioEngine


class HarmonicComponent:
    """简谐波分量"""
    def __init__(self, frequency=440.0, amplitude=0.5, phase=0.0):
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.enabled = True
        # 默认包络参数
        self.attack = 0.02   # 起音时间(秒)
        self.decay = 0.1     # 衰减时间(秒)
        self.sustain = 0.7   # 延音水平(相对于峰值的比例)
        self.release = 0.3   # 释放时间(秒)


class HarmonicSynthesizerPanel(QWidget):
    """简谐波合成器面板"""
    
    synthesis_updated = pyqtSignal(dict)  # 合成结果更新信号
    play_requested = pyqtSignal(np.ndarray)  # 播放请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化音频引擎
        self.audio_engine = AudioEngine()
        
        # 初始化简谐分量列表
        self.harmonic_components = []  # 存储所有简谐分量
        self.component_widgets = []    # 存储所有分量控件
        self.current_audio = None
        
        # 音色增强选项
        self.use_envelope = True      # 是否使用ADSR包络
        self.add_reverb = True        # 是否添加混响
        self.reverb_amount = 0.3      # 混响强度(0-1)
        self.note_duration = 1.0      # 音符持续时间(秒)
        
        # 波形叠加效果参数
        self.freq_offset = 0.0        # 频率偏移量(Hz)
        self.phase_randomization = 0.0 # 相位随机化强度(0-1)
        self.subharmonic_amount = 0.0  # 次谐波强度(0-1)
        
        # 自定义预设
        self.custom_presets = {}      # 存储用户自定义预设
        
        # 播放控制
        self.is_playing = False       # 是否正在播放
        self.loop_playback = False    # 是否循环播放
        
        # 设置UI
        self.setup_ui()
        
        # 设置预设
        self.setup_presets()
        
        # 添加默认的一个分量
        self.add_harmonic_component(440.0, 0.8, 0.0)
    
    def setup_ui(self):
        """设置用户界面"""
        main_layout = QHBoxLayout(self)  # 主布局为水平布局
        
        # 创建左右分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ====== 左侧区域: 简谐分量控制 ======
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("简谐波合成器")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 10px;")
        left_layout.addWidget(title_label)
        
        # 预设选择组
        preset_group = QGroupBox("音色预设")
        preset_group.setStyleSheet("""
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
        preset_layout = QVBoxLayout(preset_group)
        
        # 预设选择下拉框
        preset_form = QFormLayout()
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
        preset_form.addRow("选择预设:", self.preset_combo)
        preset_layout.addLayout(preset_form)
        
        # 应用预设按钮
        preset_buttons_layout = QHBoxLayout()
        
        apply_preset_btn = QPushButton("应用预设")
        apply_preset_btn.setStyleSheet("""
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
        apply_preset_btn.clicked.connect(self.on_apply_preset)
        
        # 添加保存预设按钮
        save_preset_btn = QPushButton("保存预设")
        save_preset_btn.setStyleSheet("""
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
        save_preset_btn.clicked.connect(self.on_save_preset)
        
        preset_buttons_layout.addWidget(apply_preset_btn)
        preset_buttons_layout.addWidget(save_preset_btn)
        preset_layout.addLayout(preset_buttons_layout)
        
        left_layout.addWidget(preset_group)

        # ====== 音色增强控制组 ======
        enhancement_group = QGroupBox("音色增强")
        enhancement_group.setStyleSheet("""
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
        enhancement_layout = QVBoxLayout(enhancement_group)

        # === 波形叠加效果控制 ===
        waveform_layering_group = QGroupBox("波形叠加")
        waveform_layering_group.setStyleSheet("border: none; color: white; font-weight: bold;")
        waveform_layering_layout = QVBoxLayout(waveform_layering_group)
        
        # 频率偏移控制 - 创建合唱/相位效果
        freq_offset_layout = QHBoxLayout()
        freq_offset_label = QLabel("频率偏移:")
        freq_offset_label.setStyleSheet("color: white;")
        self.freq_offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_offset_slider.setRange(0, 100)  # 0 到 10Hz，精度0.1Hz
        self.freq_offset_slider.setValue(0)
        self.freq_offset_slider.valueChanged.connect(self.on_freq_offset_changed)
        self.freq_offset_value = QLabel("0.0 Hz")
        self.freq_offset_value.setStyleSheet("color: white;")
        freq_offset_layout.addWidget(freq_offset_label)
        freq_offset_layout.addWidget(self.freq_offset_slider)
        freq_offset_layout.addWidget(self.freq_offset_value)
        waveform_layering_layout.addLayout(freq_offset_layout)
        
        # 相位随机化控制 - 创造更丰富的音色
        phase_rand_layout = QHBoxLayout()
        phase_rand_label = QLabel("相位随机:")
        phase_rand_label.setStyleSheet("color: white;")
        self.phase_rand_slider = QSlider(Qt.Orientation.Horizontal)
        self.phase_rand_slider.setRange(0, 100)  # 0 到 100%
        self.phase_rand_slider.setValue(0)
        self.phase_rand_slider.valueChanged.connect(self.on_phase_rand_changed)
        self.phase_rand_value = QLabel("0%")
        self.phase_rand_value.setStyleSheet("color: white;")
        phase_rand_layout.addWidget(phase_rand_label)
        phase_rand_layout.addWidget(self.phase_rand_slider)
        phase_rand_layout.addWidget(self.phase_rand_value)
        waveform_layering_layout.addLayout(phase_rand_layout)
        
        # 添加次谐波控制 - 增加低音厚重感
        subharmonic_layout = QHBoxLayout()
        subharmonic_label = QLabel("次谐波:")
        subharmonic_label.setStyleSheet("color: white;")
        self.subharmonic_slider = QSlider(Qt.Orientation.Horizontal)
        self.subharmonic_slider.setRange(0, 100)  # 0 到 100%
        self.subharmonic_slider.setValue(0)
        self.subharmonic_slider.valueChanged.connect(self.on_subharmonic_changed)
        self.subharmonic_value = QLabel("0%")
        self.subharmonic_value.setStyleSheet("color: white;")
        subharmonic_layout.addWidget(subharmonic_label)
        subharmonic_layout.addWidget(self.subharmonic_slider)
        subharmonic_layout.addWidget(self.subharmonic_value)
        waveform_layering_layout.addLayout(subharmonic_layout)
        
        enhancement_layout.addWidget(waveform_layering_group)

        # ADSR包络控制
        adsr_layout = QVBoxLayout()
        adsr_label = QLabel("包络控制 (ADSR)")
        adsr_label.setStyleSheet("color: white; font-weight: bold;")
        adsr_layout.addWidget(adsr_label)
        
        # 启用包络复选框
        self.envelope_cb = QCheckBox("启用包络")
        self.envelope_cb.setChecked(self.use_envelope)
        self.envelope_cb.setStyleSheet("color: white;")
        self.envelope_cb.toggled.connect(self.on_toggle_envelope)
        adsr_layout.addWidget(self.envelope_cb)
        
        # 包络参数滑块
        adsr_sliders = QFormLayout()
        
        # 起音时间滑块
        self.attack_slider = QSlider(Qt.Orientation.Horizontal)
        self.attack_slider.setRange(1, 300)  # 0.001秒到0.3秒
        self.attack_slider.setValue(int(0.02 * 1000))  # 默认20ms
        self.attack_slider.valueChanged.connect(self.on_adsr_changed)
        adsr_sliders.addRow("起音时间:", self.attack_slider)
        
        # 衰减时间滑块
        self.decay_slider = QSlider(Qt.Orientation.Horizontal)
        self.decay_slider.setRange(10, 500)  # 0.01秒到0.5秒
        self.decay_slider.setValue(int(0.1 * 1000))  # 默认100ms
        self.decay_slider.valueChanged.connect(self.on_adsr_changed)
        adsr_sliders.addRow("衰减时间:", self.decay_slider)
        
        # 延音水平滑块
        self.sustain_slider = QSlider(Qt.Orientation.Horizontal)
        self.sustain_slider.setRange(1, 100)  # 0.01到1.0
        self.sustain_slider.setValue(int(0.7 * 100))  # 默认0.7
        self.sustain_slider.valueChanged.connect(self.on_adsr_changed)
        adsr_sliders.addRow("延音水平:", self.sustain_slider)
        
        # 释放时间滑块
        self.release_slider = QSlider(Qt.Orientation.Horizontal)
        self.release_slider.setRange(10, 1000)  # 0.01秒到1秒
        self.release_slider.setValue(int(0.3 * 1000))  # 默认300ms
        self.release_slider.valueChanged.connect(self.on_adsr_changed)
        adsr_sliders.addRow("释放时间:", self.release_slider)
        
        adsr_layout.addLayout(adsr_sliders)
        enhancement_layout.addLayout(adsr_layout)
        
        # 混响控制
        reverb_layout = QVBoxLayout()
        reverb_label = QLabel("混响控制")
        reverb_label.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")
        reverb_layout.addWidget(reverb_label)
        
        # 启用混响复选框
        self.reverb_cb = QCheckBox("启用混响")
        self.reverb_cb.setChecked(self.add_reverb)
        self.reverb_cb.setStyleSheet("color: white;")
        self.reverb_cb.toggled.connect(self.on_toggle_reverb)
        reverb_layout.addWidget(self.reverb_cb)
        
        # 混响强度滑块
        reverb_slider_layout = QFormLayout()
        self.reverb_slider = QSlider(Qt.Orientation.Horizontal)
        self.reverb_slider.setRange(0, 100)
        self.reverb_slider.setValue(int(self.reverb_amount * 100))
        self.reverb_slider.valueChanged.connect(self.on_reverb_amount_changed)
        reverb_slider_layout.addRow("混响强度:", self.reverb_slider)
        reverb_layout.addLayout(reverb_slider_layout)
        
        enhancement_layout.addLayout(reverb_layout)
        
        # 音符持续时间控制
        duration_layout = QFormLayout()
        duration_layout.setContentsMargins(0, 10, 0, 0)
        
        # 持续时间滑块
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(5, 30)  # 0.5秒到3秒
        self.duration_slider.setValue(int(self.note_duration * 10))  # 默认1秒
        self.duration_slider.valueChanged.connect(self.on_duration_changed)
        
        # 持续时间标签
        self.duration_label = QLabel(f"音符持续时间: {self.note_duration}秒")
        self.duration_label.setStyleSheet("color: white;")
        
        duration_layout.addRow(self.duration_label, self.duration_slider)
        enhancement_layout.addLayout(duration_layout)
        
        left_layout.addWidget(enhancement_group)
        
        # 分量控制组
        components_group = QGroupBox("波形分量")
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
        
        # 分量控制布局
        components_layout = QVBoxLayout(components_group)
        
        # 分量列表放在滚动区域内
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.components_layout = QVBoxLayout(scroll_content)
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
        
        # 添加新分量按钮
        self.add_component_btn = QPushButton("添加分量")
        self.add_component_btn.setStyleSheet("""
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
        self.add_component_btn.clicked.connect(self.on_add_component)
        components_layout.addWidget(self.add_component_btn)
        
        # 添加按钮行 - 包含清除和锁定谐波比例
        button_row = QHBoxLayout()
        
        # 清除所有分量按钮
        self.clear_btn = QPushButton("清除全部")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear_components)
        
        # 锁定谐波比例
        self.lock_harmonics_cb = QCheckBox("锁定谐波比例")
        self.lock_harmonics_cb.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #999999;
                background-color: #333333;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #4CAF50;
                background-color: #4CAF50;
            }
        """)
        
        button_row.addWidget(self.clear_btn)
        button_row.addWidget(self.lock_harmonics_cb)
        components_layout.addLayout(button_row)
        
        left_layout.addWidget(components_group, 1)  # 1是伸缩因子，允许这个区域扩展
        
        # ====== 右侧区域: 合成结果 ======
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 合成波形面板
        waveform_group = QGroupBox("合成波形")
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
        
        # 播放控制布局
        control_layout = self.setup_playback_controls()
        
        # 添加到右侧布局
        right_layout.addWidget(waveform_group, 1)
        right_layout.addWidget(spectrum_group, 1)
        right_layout.addLayout(control_layout)
        
        # 添加帮助文本
        help_text = QLabel(
            "简谐波合成器: 通过添加不同频率、振幅和相位的简谐波，"
            "观察各种波形的合成效果。尝试使用预设或自定义创建各种音色。"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #AAAAAA; padding: 5px;")
        right_layout.addWidget(help_text)
        
        # 添加左右部件到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])  # 设置初始分割比例
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
    
    def setup_presets(self):
        """设置音色预设"""
        self.presets = {
            "纯正弦波": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0}
            ],
            "方波近似": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*3, "amplitude": 1/3, "phase": 0},
                {"frequency": 440*5, "amplitude": 1/5, "phase": 0},
                {"frequency": 440*7, "amplitude": 1/7, "phase": 0},
                {"frequency": 440*9, "amplitude": 1/9, "phase": 0}
            ],
            "三角波近似": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*3, "amplitude": 1/9, "phase": np.pi},
                {"frequency": 440*5, "amplitude": 1/25, "phase": 0},
                {"frequency": 440*7, "amplitude": 1/49, "phase": np.pi},
                {"frequency": 440*9, "amplitude": 1/81, "phase": 0}
            ],
            "锯齿波近似": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 1/2, "phase": 0},
                {"frequency": 440*3, "amplitude": 1/3, "phase": 0},
                {"frequency": 440*4, "amplitude": 1/4, "phase": 0},
                {"frequency": 440*5, "amplitude": 1/5, "phase": 0}
            ],
            "钢琴音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.7, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.3, "phase": np.pi/4},
                {"frequency": 440*4, "amplitude": 0.25, "phase": 0},
                {"frequency": 440*5, "amplitude": 0.1, "phase": np.pi/3},
                {"frequency": 440*6, "amplitude": 0.05, "phase": 0}
            ],
            "明亮钢琴音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.9, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.6, "phase": 0},
                {"frequency": 440*4, "amplitude": 0.4, "phase": np.pi/6},
                {"frequency": 440*5, "amplitude": 0.3, "phase": np.pi/4},
                {"frequency": 440*6, "amplitude": 0.2, "phase": np.pi/3},
                {"frequency": 440*7, "amplitude": 0.1, "phase": np.pi/2}
            ],
            "小提琴音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.4, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.7, "phase": np.pi/6},
                {"frequency": 440*4, "amplitude": 0.3, "phase": np.pi/4},
                {"frequency": 440*5, "amplitude": 0.5, "phase": np.pi/3},
                {"frequency": 440*6, "amplitude": 0.2, "phase": np.pi/2}
            ],
            "长笛音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.6, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.1, "phase": 0},
                {"frequency": 440*4, "amplitude": 0.05, "phase": 0}
            ],
            "单簧管音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.05, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.8, "phase": 0},
                {"frequency": 440*4, "amplitude": 0.05, "phase": 0},
                {"frequency": 440*5, "amplitude": 0.6, "phase": 0},
                {"frequency": 440*7, "amplitude": 0.3, "phase": 0},
                {"frequency": 440*9, "amplitude": 0.1, "phase": 0}
            ],
            "管风琴音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.8, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.6, "phase": 0},
                {"frequency": 440*4, "amplitude": 0.5, "phase": 0},
                {"frequency": 440*5, "amplitude": 0.45, "phase": 0},
                {"frequency": 440*6, "amplitude": 0.4, "phase": 0},
                {"frequency": 440*7, "amplitude": 0.35, "phase": 0},
                {"frequency": 440*8, "amplitude": 0.3, "phase": 0}
            ],
            "吉他音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.5, "phase": np.pi/8},
                {"frequency": 440*3, "amplitude": 0.33, "phase": np.pi/6},
                {"frequency": 440*4, "amplitude": 0.2, "phase": np.pi/4},
                {"frequency": 440*5, "amplitude": 0.15, "phase": np.pi/3},
                {"frequency": 440*6, "amplitude": 0.1, "phase": np.pi/2}
            ],
            "铜管音色": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.4, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.2, "phase": 0},
                {"frequency": 440*4, "amplitude": 0.1, "phase": 0},
                {"frequency": 440*5, "amplitude": 0.3, "phase": np.pi/4},
                {"frequency": 440*6, "amplitude": 0.05, "phase": np.pi/3}
            ],
            "合成弦乐": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.5, "phase": np.pi/8},
                {"frequency": 440*3, "amplitude": 0.3, "phase": np.pi/4},
                {"frequency": 440*4, "amplitude": 0.2, "phase": np.pi/3},
                {"frequency": 440*5, "amplitude": 0.1, "phase": np.pi/2},
                {"frequency": 440*1.01, "amplitude": 0.3, "phase": 0},  # 微偏离基频，产生合唱效果
                {"frequency": 440*2.01, "amplitude": 0.15, "phase": 0}
            ],
            "音箱效果": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2, "amplitude": 0.2, "phase": 0},
                {"frequency": 440*3, "amplitude": 0.1, "phase": np.pi/2},
                {"frequency": 440*0.5, "amplitude": 0.3, "phase": 0},   # 次谐波
                {"frequency": 440*1.003, "amplitude": 0.7, "phase": 0}, # 微偏离产生搏动
                {"frequency": 440*2*1.003, "amplitude": 0.1, "phase": 0}
            ],
            "钟声效果": [
                {"frequency": 440, "amplitude": 1.0, "phase": 0},
                {"frequency": 440*2.01, "amplitude": 0.6, "phase": np.pi/4}, # 微偏离的倍频
                {"frequency": 440*3.003, "amplitude": 0.4, "phase": np.pi/3},
                {"frequency": 440*4.004, "amplitude": 0.3, "phase": np.pi/2},
                {"frequency": 440*5.007, "amplitude": 0.2, "phase": np.pi/1.5}
            ]
        }
        
        # 添加到下拉框
        self.preset_combo.clear()
        for preset_name in self.presets.keys():
            self.preset_combo.addItem(preset_name)
    
    def add_harmonic_component(self, frequency=None, amplitude=0.5, phase=0.0):
        """添加新的简谐波分量
        
        Args:
            frequency: 频率(Hz)，如果为None则自动根据基频计算
            amplitude: 振幅
            phase: 相位(弧度)
        """
        if frequency is None:
            # 如果已有分量，新分量频率为基频的整数倍
            if self.harmonic_components:
                base_freq = self.harmonic_components[0].frequency
                harmonic_num = len(self.harmonic_components) + 1
                frequency = base_freq * harmonic_num
            else:
                frequency = 440.0  # 默认A4音
        
        # 创建新分量
        component = HarmonicComponent(frequency, amplitude, phase)
        self.harmonic_components.append(component)
        
        # 创建控制UI
        component_widget = self._create_component_controls(
            len(self.harmonic_components)-1, 
            component
        )
        self.components_layout.addWidget(component_widget)
        self.component_widgets.append(component_widget)
        
        # 更新合成波形
        self.update_synthesis()
    
    def _create_component_controls(self, index, component):
        """为简谐分量创建控制界面
        
        Args:
            index: 分量索引
            component: 简谐分量对象
            
        Returns:
            QWidget: 包含所有控制器的部件
        """
        widget = QGroupBox(f"分量 {index+1}")
        widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 5px;
                padding: 5px;
                color: white;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(5)
        
        # 分量信息标签
        info_label = QLabel(f"频率: {component.frequency:.1f} Hz | 振幅: {component.amplitude:.2f} | 相位: {component.phase/np.pi:.2f}π")
        info_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(info_label)
        
        # 控制器布局
        controls_layout = QFormLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # 频率控制
        freq_slider = QSlider(Qt.Orientation.Horizontal)
        freq_slider.setRange(20, 5000)  # 20Hz到5000Hz
        freq_slider.setValue(int(component.frequency))
        freq_slider.valueChanged.connect(
            lambda v: self._update_component(index, "frequency", float(v), info_label)
        )
        controls_layout.addRow("频率:", freq_slider)
        
        # 振幅控制
        amp_slider = QSlider(Qt.Orientation.Horizontal)
        amp_slider.setRange(0, 100)
        amp_slider.setValue(int(component.amplitude * 100))
        amp_slider.valueChanged.connect(
            lambda v: self._update_component(index, "amplitude", v/100, info_label)
        )
        controls_layout.addRow("振幅:", amp_slider)
        
        # 相位控制
        phase_slider = QSlider(Qt.Orientation.Horizontal)
        phase_slider.setRange(0, 200)  # 0到2π
        phase_slider.setValue(int(component.phase * 100 / np.pi))
        phase_slider.valueChanged.connect(
            lambda v: self._update_component(index, "phase", v*np.pi/100, info_label)
        )
        controls_layout.addRow("相位:", phase_slider)
        
        layout.addLayout(controls_layout)
        
        # 底部操作区
        bottom_layout = QHBoxLayout()
        
        # 启用/禁用复选框
        enable_checkbox = QCheckBox("启用")
        enable_checkbox.setChecked(True)
        enable_checkbox.setStyleSheet("color: white;")
        enable_checkbox.toggled.connect(
            lambda state: self._toggle_component(index, state)
        )
        
        # 删除按钮
        remove_btn = QPushButton("删除")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        remove_btn.clicked.connect(lambda: self._remove_component(index))
        
        bottom_layout.addWidget(enable_checkbox)
        bottom_layout.addStretch()
        bottom_layout.addWidget(remove_btn)
        
        layout.addLayout(bottom_layout)
        
        return widget
    
    def _update_component(self, index, attribute, value, label):
        """更新简谐分量参数
        
        Args:
            index: 分量索引
            attribute: 属性名('frequency', 'amplitude', 'phase')
            value: 新值
            label: 要更新的信息标签
        """
        if index < 0 or index >= len(self.harmonic_components):
            return
            
        # 更新组件属性
        component = self.harmonic_components[index]
        setattr(component, attribute, value)
        
        # 如果锁定了谐波比例且修改的是频率，则更新所有分量的频率
        if attribute == "frequency" and self.lock_harmonics_cb.isChecked() and index == 0:
            base_freq = value
            for i, comp in enumerate(self.harmonic_components[1:], 1):
                harmonic_freq = base_freq * (i + 1)
                comp.frequency = harmonic_freq
                
                # 更新其他分量的UI
                if i < len(self.component_widgets):
                    other_label = self.component_widgets[i].findChild(QLabel)
                    if other_label:
                        other_label.setText(
                            f"频率: {comp.frequency:.1f} Hz | 振幅: {comp.amplitude:.2f} | 相位: {comp.phase/np.pi:.2f}π"
                        )
        
        # 更新信息标签
        label.setText(
            f"频率: {component.frequency:.1f} Hz | 振幅: {component.amplitude:.2f} | 相位: {component.phase/np.pi:.2f}π"
        )
        
        # 更新合成波形
        self.update_synthesis()
    
    def _toggle_component(self, index, enabled):
        """启用/禁用简谐分量
        
        Args:
            index: 分量索引
            enabled: 是否启用
        """
        if index < 0 or index >= len(self.harmonic_components):
            return
            
        self.harmonic_components[index].enabled = enabled
        self.update_synthesis()
    
    def _remove_component(self, index):
        """删除指定的简谐分量
        
        Args:
            index: 分量索引
        """
        if index < 0 or index >= len(self.harmonic_components):
            return
            
        # 移除分量数据
        self.harmonic_components.pop(index)
        
        # 移除UI组件
        if index < len(self.component_widgets):
            widget = self.component_widgets.pop(index)
            self.components_layout.removeWidget(widget)
            widget.deleteLater()
        
        # 更新剩余分量的标题
        for i, widget in enumerate(self.component_widgets):
            widget.setTitle(f"分量 {i+1}")
        
        # 更新合成波形
        self.update_synthesis()
    
    def on_toggle_envelope(self, enabled):
        """启用/禁用包络控制"""
        self.use_envelope = enabled
        self.update_synthesis()
        
    def on_toggle_reverb(self, enabled):
        """启用/禁用混响效果"""
        self.add_reverb = enabled
        self.update_synthesis()
        
    def on_reverb_amount_changed(self, value):
        """调整混响效果强度"""
        self.reverb_amount = value / 100.0
        self.update_synthesis()
    
    def on_duration_changed(self, value):
        """调整音符持续时间"""
        self.note_duration = value / 10.0
        self.duration_label.setText(f"音符持续时间: {self.note_duration:.1f}秒")
        self.update_synthesis()
        
    def on_adsr_changed(self):
        """包络参数变更处理函数"""
        # 更新所有分量的ADSR参数
        for component in self.harmonic_components:
            component.attack = self.attack_slider.value() / 1000.0
            component.decay = self.decay_slider.value() / 1000.0
            component.sustain = self.sustain_slider.value() / 100.0
            component.release = self.release_slider.value() / 1000.0
        
        self.update_synthesis()
    
    def apply_adsr_envelope(self, wave, attack, decay, sustain, release, duration):
        """应用ADSR包络到波形
        
        Args:
            wave: 音频波形数组
            attack: 起音时间(秒)
            decay: 衰减时间(秒)
            sustain: 延音水平
            release: 释放时间(秒)
            duration: 音符总持续时间(秒)
            
        Returns:
            numpy.ndarray: 应用包络后的波形
        """
        if not self.use_envelope:
            return wave
            
        sample_rate = self.audio_engine.sample_rate
        total_samples = len(wave)
        
        # 计算各阶段样本点数
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        
        # 计算延音阶段结束点
        sustain_end = int(total_samples - (release * sample_rate))
        
        # 生成包络数组
        envelope = np.ones_like(wave)
        
        # 起音阶段 - 线性上升
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
            
        # 衰减阶段 - 从峰值衰减到延音水平
        if decay_samples > 0:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)
            
        # 延音阶段 - 保持在延音水平
        envelope[attack_samples+decay_samples:sustain_end] = sustain
        
        # 释放阶段 - 从延音水平衰减到零
        release_samples = total_samples - sustain_end
        if release_samples > 0:
            envelope[sustain_end:] = np.linspace(sustain, 0, release_samples)
            
        # 应用包络
        return wave * envelope
    
    def apply_reverb(self, wave):
        """应用简单的混响效果
        
        Args:
            wave: 音频波形数组
            
        Returns:
            numpy.ndarray: 添加混响后的波形
        """
        if not self.add_reverb or self.reverb_amount <= 0:
            return wave
        
        # 创建混响延迟
        sample_rate = self.audio_engine.sample_rate
        
        # 多个延迟反射，延迟时间和衰减系数
        delays = [
            (int(0.03 * sample_rate), 0.7),  # 30ms, 70% 强度
            (int(0.05 * sample_rate), 0.5),  # 50ms, 50% 强度
            (int(0.07 * sample_rate), 0.3),  # 70ms, 30% 强度
            (int(0.1 * sample_rate), 0.2),   # 100ms, 20% 强度
            (int(0.15 * sample_rate), 0.1)   # 150ms, 10% 强度
        ]
        
        # 创建混响波形
        reverb_wave = np.zeros(len(wave) + int(0.3 * sample_rate))  # 添加额外尾部空间
        reverb_wave[:len(wave)] = wave  # 复制原始信号
        
        # 添加延迟反射
        for delay, gain in delays:
            delayed = np.zeros_like(reverb_wave)
            delayed[delay:delay+len(wave)] += wave * gain * self.reverb_amount
            reverb_wave += delayed
            
        # 为了保持原始长度，修剪回原来的长度
        reverb_wave = reverb_wave[:len(wave)]
        
        # 归一化，防止削波
        if np.max(np.abs(reverb_wave)) > 0:
            reverb_wave = reverb_wave / np.max(np.abs(reverb_wave))
            
        return reverb_wave
    
    def update_synthesis(self):
        """更新合成波形和音频"""
        if not self.harmonic_components:
            # 如果没有分量，清除画布
            self.waveform_viz.canvas.figure.clear()
            self.spectrum_viz.canvas.figure.clear()
            self.waveform_viz.canvas.draw()
            self.spectrum_viz.canvas.draw()
            return
            
        sample_rate = self.audio_engine.sample_rate
        duration = self.note_duration  # 使用用户设置的持续时间
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 初始化为零
        composite_wave = np.zeros_like(t)
        
        # 添加每个分量
        components_data = {"time": t, "composite": None}
        
        for i, component in enumerate(self.harmonic_components):
            if component.enabled:
                # 应用频率偏移效果
                if self.freq_offset > 0 and i > 0:  # 对第二个分量开始应用频率偏移
                    # 奇数分量略微提高频率，偶数分量略微降低频率
                    offset = self.freq_offset * (1 if i % 2 == 1 else -1)
                    freq = component.frequency + offset
                else:
                    freq = component.frequency
                
                # 应用相位随机化，每个分量有不同相位
                if self.phase_randomization > 0:
                    # 使用固定随机种子，确保每次渲染相同组件时相位一致
                    np.random.seed(i + 1)  
                    # 基础相位 + 随机偏移
                    phase = component.phase + np.random.uniform(
                        -np.pi * self.phase_randomization, 
                        np.pi * self.phase_randomization
                    )
                else:
                    phase = component.phase
                
                # 生成基本分量波形
                wave = component.amplitude * np.sin(
                    2 * np.pi * freq * t + phase
                )
                
                # 添加次谐波 (仅对前几个分量添加)
                if self.subharmonic_amount > 0 and i < 3:  # 只对前3个分量添加次谐波
                    # 次谐波是基频的一半
                    subharmonic = component.amplitude * self.subharmonic_amount * np.sin(
                        2 * np.pi * (freq / 2) * t + phase
                    )
                    wave += subharmonic
                
                # 应用ADSR包络
                if self.use_envelope:
                    wave = self.apply_adsr_envelope(
                        wave, 
                        component.attack,
                        component.decay,
                        component.sustain,
                        component.release,
                        duration
                    )
                
                # 添加到合成波
                composite_wave += wave
                
                # 存储分量数据（无论启用状态如何，都存储所有分量）
                components_data[f"component_{i}"] = wave
        
        # 归一化合成波
        if np.max(np.abs(composite_wave)) > 0:
            composite_wave = composite_wave / np.max(np.abs(composite_wave)) * 0.9
        
        # 应用混响效果
        if self.add_reverb:
            composite_wave = self.apply_reverb(composite_wave)
            
        # 存储合成波
        components_data["composite"] = composite_wave
        self.current_audio = composite_wave
        
        # 更新可视化
        self._update_visualization(components_data)
        
        # 发送合成结果信号
        self.synthesis_updated.emit(components_data)
    
    def _update_visualization(self, components_data):
        """更新波形和频谱可视化
        
        Args:
            components_data: 包含时间、合成波和各分量的字典
        """
        if not components_data:
            return
            
        try:
            # 获取时间和合成波形数据
            t = components_data["time"]
            composite = components_data["composite"]
            
            # 清除当前的波形图和频谱图
            self.waveform_viz.canvas.figure.clear()
            self.spectrum_viz.canvas.figure.clear()
            
            # 配置绘图样式
            plt.style.use('dark_background')
            
            # 设置波形颜色
            wave_colors = ['#00FFFF', '#FFD700', '#FF69B4', '#7CFC00', '#FF4500', '#1E90FF']  # 青色，金色，粉色，草绿色，橙红色，淡蓝色
            
            # ========== 绘制波形图 ==========
            # 创建多个子图：上方显示合成波形，下方显示各个分量
            fig_wave = self.waveform_viz.canvas.figure
            
            # 获取启用的分量
            enabled_components = []
            enabled_indices = []
            for i, comp in enumerate(self.harmonic_components):
                if comp.enabled:
                    enabled_components.append(comp)
                    enabled_indices.append(i)
            
            # 限制显示的分量数，避免过于拥挤
            max_components_to_show = 4  # 最多显示4个分量 + 合成波
            show_warning = False
            if len(enabled_components) > max_components_to_show:
                enabled_components = enabled_components[:max_components_to_show]
                enabled_indices = enabled_indices[:max_components_to_show]
                show_warning = True
            
            # 计算需要多少子图
            num_subplots = 1 + len(enabled_components)  # 合成波 + 启用的分量
            
            # 创建子图，使用GridSpec以便更灵活地控制布局
            gs = fig_wave.add_gridspec(num_subplots, 1, 
                                       height_ratios=[2] + [1] * (num_subplots - 1),  # 合成波给2倍空间
                                       hspace=0.5)  # 增加子图间距
            
            # 创建子图
            axes = []
            
            # 合成波子图
            ax_composite = fig_wave.add_subplot(gs[0])
            ax_composite.set_title("合成波形", fontsize=12, color='white', pad=8)
            ax_composite.set_facecolor('#0A0A0A')  # 深黑背景，增加对比度
            axes.append(ax_composite)
            
            # 分量子图
            for i in range(1, num_subplots):
                comp_idx = i - 1
                ax = fig_wave.add_subplot(gs[i])
                if comp_idx < len(enabled_components):
                    comp = enabled_components[comp_idx]
                    freq = comp.frequency
                    amp = comp.amplitude
                    title = f"分量 {enabled_indices[comp_idx]+1}: {freq:.1f}Hz (振幅: {amp:.2f})"
                    ax.set_title(title, fontsize=9, color='white', pad=5)
                    ax.set_facecolor('#0A0A0A')  # 深黑背景，增加对比度
                axes.append(ax)
            
            # 对波形进行下采样以减少绘制点数，更强的下采样率
            if len(t) > 500:
                step = max(len(t) // 500, 1)  # 确保至少下采样2倍
                t_downsampled = t[::step]
                composite_downsampled = composite[::step]
            else:
                t_downsampled = t
                composite_downsampled = composite
            
            # 绘制合成波形
            axes[0].plot(t_downsampled, composite_downsampled, color=wave_colors[0], linewidth=1.5)
            axes[0].set_ylabel("振幅", fontsize=10)
            axes[0].grid(True, alpha=0.3, color='#333333')
            
            # 设置Y轴范围，保持一致且有适当间距
            y_max = 1.05  # 稍微大于1，给标签留出空间
            for ax in axes:
                ax.set_ylim(-y_max, y_max)
            
            # 绘制各个分量波形，更宽松的布局
            for i in range(1, num_subplots):
                comp_idx = i - 1
                if comp_idx < len(enabled_indices):
                    original_idx = enabled_indices[comp_idx]
                    component_key = f"component_{original_idx}"
                    if component_key in components_data:
                        component_wave = components_data[component_key]
                        if len(component_wave) > 500:
                            component_wave = component_wave[::step]
                        
                        # 为每个分量使用不同的颜色
                        color_idx = (comp_idx % (len(wave_colors) - 1)) + 1  # 跳过第一个颜色(留给合成波)
                        axes[i].plot(t_downsampled, component_wave, color=wave_colors[color_idx], linewidth=1.5)
                        axes[i].set_ylabel("振幅", fontsize=8)
                        axes[i].grid(True, alpha=0.3, color='#333333')
                        
                        # 使用填充区域增强波形可见性
                        axes[i].fill_between(t_downsampled, 0, component_wave, 
                                           color=wave_colors[color_idx], alpha=0.1)
                        
                        # 周期标记，简化为只在第一个周期添加标记
                        if comp_idx == 0 and len(t_downsampled) > 100:  # 确保有足够的点
                            freq = enabled_components[comp_idx].frequency
                            if freq > 0:
                                period = 1.0 / freq
                                if t_downsampled[-1] > period:
                                    mark_time = period
                                    # 只在第一个分量波形上添加标记
                                    axes[i].axvline(x=mark_time, color='#555555', alpha=0.5, 
                                                  linestyle='--', linewidth=0.8)
                                    axes[i].text(mark_time + 0.02, 0.8, f'周期: {period:.4f}秒', 
                                               color='white', fontsize=8, alpha=0.8)
            
            # 只在最后一个子图上显示x轴标签
            for i in range(num_subplots-1):
                axes[i].set_xticklabels([])
            
            axes[-1].set_xlabel("时间 (秒)", fontsize=10)
            
            # 不使用tight_layout，改用手动调整，避免警告
            fig_wave.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1, hspace=0.5)
            
            # 如果有太多分量被省略，添加警告文本
            if show_warning:
                fig_wave.text(0.5, 0.01, f"注意: 仅显示前{max_components_to_show}个分量 (共{len(self.harmonic_components)}个)",
                            ha='center', color='yellow', fontsize=8, alpha=0.7)
            
            # ========== 绘制频谱图 ==========
            if composite is not None:
                frequencies, magnitudes = self.audio_engine.analyze_frequency_content(composite)
                
                # 限制频率范围，通常只显示到8000Hz或更低
                max_freq_idx = np.searchsorted(frequencies, 8000)
                if max_freq_idx > 0:
                    frequencies = frequencies[:max_freq_idx]
                    magnitudes = magnitudes[:max_freq_idx]
                
                # 检测峰值，以便在频谱图上标记
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(magnitudes, height=0.1, distance=20)  # 增加distance减少标记密度
                
                # 绘制频谱图
                fig_spectrum = self.spectrum_viz.canvas.figure
                ax_spectrum = fig_spectrum.add_subplot(111)
                ax_spectrum.set_title("频率分析", fontsize=12, color='white')
                ax_spectrum.set_facecolor('#0A0A0A')  # 深黑背景，增加对比度
                
                # 绘制频谱，使用渐变色
                # 添加频谱填充，增强视觉效果
                ax_spectrum.fill_between(frequencies, magnitudes, color=wave_colors[0], alpha=0.2)
                ax_spectrum.plot(frequencies, magnitudes, color=wave_colors[0], linewidth=1.2)
                
                # 标记分量频率，使用更清晰的布局
                already_marked_freqs = []
                for comp_idx, comp in enumerate(enabled_components):
                    freq = comp.frequency
                    # 避免标记太接近的频率
                    if any(abs(freq - f) < 20 for f in already_marked_freqs):
                        continue
                        
                    already_marked_freqs.append(freq)
                    # 找到最接近的频率点
                    closest_idx = np.argmin(np.abs(frequencies - freq))
                    if closest_idx < len(frequencies):
                        mag = magnitudes[closest_idx]
                        # 使用与波形相同的颜色
                        color_idx = (comp_idx % (len(wave_colors) - 1)) + 1
                        ax_spectrum.axvline(x=freq, color=wave_colors[color_idx], alpha=0.5, linestyle='--')
                        ax_spectrum.plot(freq, mag, 'o', color=wave_colors[color_idx], markersize=6)
                        
                        # 智能放置标签，避免重叠
                        y_pos = mag + 0.05
                        if comp_idx > 0:
                            y_pos += 0.03 * comp_idx  # 稍微上移每个后续标签
                        
                        ax_spectrum.text(freq, y_pos, f"{freq:.1f}Hz", 
                                        fontsize=9, color=wave_colors[color_idx],
                                        ha='center', va='bottom', fontweight='bold')
                
                # 标记其他主要峰值，限制数量避免拥挤
                max_other_peaks = 3
                peak_count = 0
                for peak_idx in peaks:
                    if peak_count >= max_other_peaks:
                        break
                        
                    if peak_idx < len(frequencies) and peak_idx < len(magnitudes):
                        freq = frequencies[peak_idx]
                        # 跳过已经标记过的分量频率或接近的频率
                        if any(abs(comp.frequency - freq) < 20 for comp in enabled_components):
                            continue
                            
                        # 对于次要峰值，只标记显著的峰值
                        mag = magnitudes[peak_idx]
                        if mag < 0.1:  # 忽略幅度太小的峰值
                            continue
                            
                        ax_spectrum.plot(freq, mag, 'ro', markersize=4, alpha=0.7)
                        peak_count += 1
                
                ax_spectrum.set_xlabel("频率 (Hz)", fontsize=10)
                ax_spectrum.set_ylabel("幅度", fontsize=10)
                ax_spectrum.grid(True, alpha=0.3, color='#333333')
                ax_spectrum.set_xlim(0, frequencies[-1])
                
                # 稍微提高y轴上限，给标记留空间
                ax_spectrum.set_ylim(0, min(1.2, max(magnitudes) * 1.3))
                
                # 添加标题，显示音符信息
                if len(enabled_components) > 0:
                    base_freq = enabled_components[0].frequency
                    note_name = self._get_note_name(base_freq)
                    if note_name:
                        fig_spectrum.text(0.5, 0.95, f"基频: {base_freq:.1f}Hz ({note_name})", 
                                        fontsize=10, color='white', ha='center')
                
                # 使用手动调整而不是tight_layout
                fig_spectrum.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
            
            # 刷新画布
            self.waveform_viz.canvas.draw()
            self.spectrum_viz.canvas.draw()
            
        except Exception as e:
            print(f"可视化更新出错: {e}")
            
    def _get_note_name(self, frequency):
        """根据频率获取音符名称
        
        Args:
            frequency: 频率(Hz)
            
        Returns:
            str: 音符名称，如找不到则返回None
        """
        # A4 = 440Hz
        notes = ['A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab']
        # 计算离A4的半音数
        try:
            h = round(12 * np.log2(frequency / 440.0))
            octave = 4 + (h // 12)
            n = h % 12
            note_name = f"{notes[n]}{octave}"
            return note_name
        except:
            return None
    
    def on_add_component(self):
        """添加分量按钮处理函数"""
        self.add_harmonic_component()
    
    def on_clear_components(self):
        """清除所有分量按钮处理函数"""
        # 清除分量数据
        self.harmonic_components = []
        
        # 清除UI组件
        for widget in self.component_widgets:
            self.components_layout.removeWidget(widget)
            widget.deleteLater()
        self.component_widgets = []
        
        # 添加一个默认分量
        self.add_harmonic_component(440.0, 0.8, 0.0)
    
    def on_apply_preset(self):
        """应用预设按钮处理函数"""
        preset_name = self.preset_combo.currentText()
        
        # 处理自定义预设标记
        if preset_name.startswith("★ "):
            preset_name = preset_name[2:]  # 移除★标记
            
            if preset_name in self.custom_presets:
                self._apply_custom_preset(preset_name)
                return
        
        # 处理内置预设
        if preset_name in self.presets:
            # 清除当前分量
            self.on_clear_components()
            
            # 延迟一小段时间，确保UI更新
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._apply_preset_components(preset_name))
    
    def _apply_custom_preset(self, preset_name):
        """应用自定义预设
        
        Args:
            preset_name: 预设名称
        """
        if preset_name not in self.custom_presets:
            return
            
        preset_data = self.custom_presets[preset_name]
        
        # 清除现有组件
        for widget in self.component_widgets:
            self.components_layout.removeWidget(widget)
            widget.deleteLater()
        self.component_widgets = []
        self.harmonic_components = []
        
        # 添加分量
        for comp_data in preset_data["components"]:
            self.add_harmonic_component(
                comp_data["frequency"], 
                comp_data["amplitude"], 
                comp_data["phase"]
            )
        
        # 应用包络设置
        if "envelope" in preset_data:
            env = preset_data["envelope"]
            self.use_envelope = env.get("enabled", True)
            self.envelope_cb.setChecked(self.use_envelope)
            
            # 更新滑块值
            self.attack_slider.setValue(int(env.get("attack", 0.02) * 1000))
            self.decay_slider.setValue(int(env.get("decay", 0.1) * 1000))
            self.sustain_slider.setValue(int(env.get("sustain", 0.7) * 100))
            self.release_slider.setValue(int(env.get("release", 0.3) * 1000))
        
        # 应用混响设置
        if "reverb" in preset_data:
            rev = preset_data["reverb"]
            self.add_reverb = rev.get("enabled", True)
            self.reverb_cb.setChecked(self.add_reverb)
            self.reverb_amount = rev.get("amount", 0.3)
            self.reverb_slider.setValue(int(self.reverb_amount * 100))
        
        # 应用效果设置
        if "effects" in preset_data:
            fx = preset_data["effects"]
            
            # 频率偏移
            self.freq_offset = fx.get("freq_offset", 0.0)
            self.freq_offset_slider.setValue(int(self.freq_offset * 10))
            self.freq_offset_value.setText(f"{self.freq_offset:.1f} Hz")
            
            # 相位随机化
            self.phase_randomization = fx.get("phase_rand", 0.0)
            self.phase_rand_slider.setValue(int(self.phase_randomization * 100))
            self.phase_rand_value.setText(f"{int(self.phase_randomization * 100)}%")
            
            # 次谐波
            self.subharmonic_amount = fx.get("subharmonic", 0.0)
            self.subharmonic_slider.setValue(int(self.subharmonic_amount * 100))
            self.subharmonic_value.setText(f"{int(self.subharmonic_amount * 100)}%")
        
        # 应用持续时间
        if "duration" in preset_data:
            self.note_duration = preset_data.get("duration", 1.0)
            self.duration_slider.setValue(int(self.note_duration * 10))
            self.duration_label.setText(f"音符持续时间: {self.note_duration:.1f}秒")
        
        # 更新合成
        self.update_synthesis()
    
    def setup_playback_controls(self):
        """设置播放控制布局"""
        # 创建水平布局
        control_layout = QHBoxLayout()
        
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
        self.play_btn.clicked.connect(self.on_play)
        
        # 停止按钮
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)  # 初始状态禁用
        
        # 循环播放复选框
        self.loop_cb = QCheckBox("循环播放")
        self.loop_cb.setStyleSheet("color: white;")
        self.loop_cb.toggled.connect(self.on_toggle_loop)
        
        # 导出按钮
        self.export_btn = QPushButton("导出波形")
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
        self.export_btn.clicked.connect(self.on_export)
        
        # 添加所有控件到布局
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.loop_cb)
        control_layout.addWidget(self.export_btn)
        
        return control_layout
        
    def on_play(self):
        """播放按钮处理函数"""
        if self.current_audio is not None:
            # 发送播放信号
            self.play_requested.emit(self.current_audio)
            
            # 开始播放音频
            self.audio_engine.play_audio(self.current_audio, loop=self.loop_playback)
            
            # 更新UI状态
            self.is_playing = True
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.play_btn.setText("播放中...")
    
    def on_stop(self):
        """停止播放"""
        # 停止音频引擎播放
        self.audio_engine.stop_audio()
        
        # 重置UI状态
        self.is_playing = False
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.play_btn.setText("播放")
    
    def on_toggle_loop(self, checked):
        """切换循环播放状态"""
        self.loop_playback = checked
        # 如果正在播放，更新音频引擎的循环播放状态
        if self.is_playing:
            self.audio_engine.set_loop(checked)
    
    def on_export(self):
        """导出按钮处理函数"""
        if self.current_audio is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "导出失败", "请先生成合成波形")
            return
            
        # 创建文件保存对话框
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("音频文件 (*.wav);;所有文件 (*.*)")
        file_dialog.setWindowTitle("导出合成波形")
        file_dialog.setDefaultSuffix("wav")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                self.audio_engine.save_audio(self.current_audio, file_path)
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "导出成功", f"已成功将合成波形导出至:\n{file_path}")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "导出失败", f"导出过程中发生错误:\n{str(e)}")
    
    # ========== 预设相关方法 ==========
    def _apply_preset_components(self, preset_name):
        """应用内置预设中的分量
        
        Args:
            preset_name: 预设名称
        """
        if preset_name not in self.presets:
            return
            
        # 清除现有组件
        for widget in self.component_widgets:
            self.components_layout.removeWidget(widget)
            widget.deleteLater()
        self.component_widgets = []
        self.harmonic_components = []
        
        # 添加预设中的分量
        components = self.presets[preset_name]
        for comp_data in components:
            self.add_harmonic_component(
                comp_data["frequency"], 
                comp_data["amplitude"], 
                comp_data["phase"]
            )
            
        # 根据乐器类型自动设置合适的ADSR包络
        # 钢琴类音色
        if "钢琴" in preset_name:
            self.attack_slider.setValue(int(0.01 * 1000))  # 10ms快速起音
            self.decay_slider.setValue(int(0.3 * 1000))    # 300ms中等衰减
            self.sustain_slider.setValue(int(0.5 * 100))   # 0.5延音水平
            self.release_slider.setValue(int(0.8 * 1000))  # 800ms中等释放
            self.on_adsr_changed()
            
        # 弦乐类音色
        elif any(s in preset_name for s in ["提琴", "弦乐"]):
            self.attack_slider.setValue(int(0.08 * 1000))  # 80ms缓慢起音
            self.decay_slider.setValue(int(0.1 * 1000))    # 100ms短衰减
            self.sustain_slider.setValue(int(0.7 * 100))   # 0.7高延音水平
            self.release_slider.setValue(int(0.3 * 1000))  # 300ms释放
            self.on_adsr_changed()
            
        # 管类音色
        elif any(s in preset_name for s in ["笛", "管风琴", "单簧管"]):
            self.attack_slider.setValue(int(0.03 * 1000))  # 30ms中等起音
            self.decay_slider.setValue(int(0.05 * 1000))   # 50ms短衰减
            self.sustain_slider.setValue(int(0.9 * 100))   # 0.9高延音水平
            self.release_slider.setValue(int(0.15 * 1000)) # 150ms短释放
            self.on_adsr_changed()
            
        # 铜管类音色
        elif "铜管" in preset_name:
            self.attack_slider.setValue(int(0.04 * 1000))  # 40ms起音
            self.decay_slider.setValue(int(0.1 * 1000))    # 100ms衰减
            self.sustain_slider.setValue(int(0.8 * 100))   # 0.8延音水平
            self.release_slider.setValue(int(0.2 * 1000))  # 200ms释放
            self.on_adsr_changed()
            
        # 吉他音色
        elif "吉他" in preset_name:
            self.attack_slider.setValue(int(0.01 * 1000))  # 10ms快速起音
            self.decay_slider.setValue(int(0.2 * 1000))    # 200ms衰减
            self.sustain_slider.setValue(int(0.3 * 100))   # 0.3低延音水平
            self.release_slider.setValue(int(0.4 * 1000))  # 400ms释放
            self.on_adsr_changed()
            
        # 钟声效果
        elif "钟声" in preset_name:
            self.attack_slider.setValue(int(0.005 * 1000)) # 5ms非常快的起音
            self.decay_slider.setValue(int(0.5 * 1000))    # 500ms较长衰减
            self.sustain_slider.setValue(int(0.1 * 100))   # 0.1很低的延音水平
            self.release_slider.setValue(int(1.0 * 1000))  # 1000ms长释放
            self.on_adsr_changed()

    def on_save_preset(self):
        """保存当前设置为自定义预设"""
        # 检查是否有分量可保存
        if not self.harmonic_components:
            QMessageBox.warning(self, "保存失败", "没有可保存的分量")
            return
            
        # 请求预设名称
        preset_name, ok = QInputDialog.getText(
            self, "保存预设", "预设名称:", 
            text="我的预设" + str(len(self.custom_presets) + 1)
        )
        
        if ok and preset_name:
            # 检查是否重复
            if preset_name in self.presets or preset_name in self.custom_presets:
                overwrite = QMessageBox.question(
                    self, "确认覆盖", 
                    f"预设'{preset_name}'已存在，是否覆盖?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if overwrite != QMessageBox.StandardButton.Yes:
                    return
            
            # 保存当前分量配置
            components_data = []
            for comp in self.harmonic_components:
                if comp.enabled:  # 只保存启用的分量
                    components_data.append({
                        "frequency": comp.frequency,
                        "amplitude": comp.amplitude, 
                        "phase": comp.phase
                    })
            
            # 保存额外参数
            preset_info = {
                "components": components_data,
                "envelope": {
                    "enabled": self.use_envelope,
                    "attack": self.attack_slider.value() / 1000.0,
                    "decay": self.decay_slider.value() / 1000.0,
                    "sustain": self.sustain_slider.value() / 100.0,
                    "release": self.release_slider.value() / 1000.0
                },
                "reverb": {
                    "enabled": self.add_reverb,
                    "amount": self.reverb_amount
                },
                "effects": {
                    "freq_offset": self.freq_offset,
                    "phase_rand": self.phase_randomization,
                    "subharmonic": self.subharmonic_amount
                },
                "duration": self.note_duration
            }
            
            # 添加到自定义预设
            self.custom_presets[preset_name] = preset_info
            
            # 更新预设下拉框
            self._update_preset_combo()
            
            # 选择新保存的预设
            idx = self.preset_combo.findText("★ " + preset_name)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
                
            QMessageBox.information(self, "保存成功", f"预设'{preset_name}'已保存")
    
    def _update_preset_combo(self):
        """更新预设下拉框"""
        current_text = self.preset_combo.currentText()
        
        # 清除现有预设
        self.preset_combo.clear()
        
        # 添加内置预设
        for name in self.presets.keys():
            self.preset_combo.addItem(name)
        
        # 添加自定义预设，带有标识
        if self.custom_presets:
            self.preset_combo.insertSeparator(self.preset_combo.count())
            for name in self.custom_presets.keys():
                self.preset_combo.addItem("★ " + name)
        
        # 尝试恢复之前选择的预设
        idx = self.preset_combo.findText(current_text)
        if idx >= 0:
            self.preset_combo.setCurrentIndex(idx)

    # ========== 波形叠加效果控制相关方法 ==========
    def on_freq_offset_changed(self, value):
        """频率偏移滑块变更处理"""
        self.freq_offset = value / 10.0  # 0-10Hz，精度0.1Hz
        self.freq_offset_value.setText(f"{self.freq_offset:.1f} Hz")
        self.update_synthesis()
        
    def on_phase_rand_changed(self, value):
        """相位随机化滑块变更处理"""
        self.phase_randomization = value / 100.0  # 0-100%
        self.phase_rand_value.setText(f"{value}%")
        self.update_synthesis()
        
    def on_subharmonic_changed(self, value):
        """次谐波滑块变更处理"""
        self.subharmonic_amount = value / 100.0  # 0-100%
        self.subharmonic_value.setText(f"{value}%")
        self.update_synthesis()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    window = HarmonicSynthesizerPanel()
    window.show()
    
    sys.exit(app.exec()) 