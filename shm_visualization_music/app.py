# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 主应用程序
整合所有组件，提供用户界面
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
)
from PyQt6.QtCore import Qt

from audio_engine import AudioEngine
from audio_analyzer import AudioAnalyzer
from audio_analysis_ui import AudioAnalysisPanel
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel


class HarmonicMusicApp(QMainWindow):
    """简谐振动与音乐可视化主应用程序"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简谐振动与音乐可视化教学系统")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #222222;
            }
            QTabBar::tab {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """)
        
        # 初始化引擎
        self.audio_engine = AudioEngine()
        self.audio_analyzer = AudioAnalyzer()
        
        # 创建中央部件
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 音频分析标签页
        self.audio_analysis_panel = AudioAnalysisPanel()
        self.tab_widget.addTab(self.audio_analysis_panel, "音频分析")
        
        # 简谐波合成器标签页
        self.harmonic_synthesizer_panel = HarmonicSynthesizerPanel()
        self.tab_widget.addTab(self.harmonic_synthesizer_panel, "简谐波合成器")
        
        # 连接信号
        self.audio_analysis_panel.play_requested.connect(self.on_audio_play)
        self.harmonic_synthesizer_panel.play_requested.connect(self.on_audio_play)
    
    def on_audio_play(self, audio_data):
        """处理音频播放请求"""
        # 播放音频
        self.audio_engine.play_audio(audio_data)


def main():
    app = QApplication(sys.argv)
    window = HarmonicMusicApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 