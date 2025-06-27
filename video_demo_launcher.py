#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教学视频演示启动器
为3分钟教学视频提供快速启动和切换功能
"""

import sys
import os
import subprocess
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

class VideoDemoLauncher(QMainWindow):
    """教学视频演示启动器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简谐运动教学视频演示启动器")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
                color: #eee;
            }
            QPushButton {
                background-color: #16213e;
                color: #eee;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f3460;
                border-color: #e94560;
            }
            QPushButton:pressed {
                background-color: #e94560;
            }
            QLabel {
                color: #eee;
                font-size: 16px;
            }
            QTextEdit {
                background-color: #16213e;
                color: #eee;
                border: 1px solid #0f3460;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("简谐运动合成原理教学演示")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：模块启动按钮
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 模块启动区域
        modules_label = QLabel("教学模块快速启动")
        modules_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_layout.addWidget(modules_label)
        
        # 按照视频演示顺序排列按钮
        self.phase_btn = QPushButton("1. 同向同频模块\n(相位差合成)")
        self.phase_btn.clicked.connect(self.launch_phase_module)
        left_layout.addWidget(self.phase_btn)
        
        self.beat_btn = QPushButton("2. 拍频模块\n(频率差合成)")
        self.beat_btn.clicked.connect(self.launch_beat_module)
        left_layout.addWidget(self.beat_btn)
        
        self.lissajous_btn = QPushButton("3. 李萨如图形模块\n(垂直合成)")
        self.lissajous_btn.clicked.connect(self.launch_lissajous_module)
        left_layout.addWidget(self.lissajous_btn)
        
        # 添加分隔线
        left_layout.addWidget(QLabel("─" * 30))
        
        # 工具按钮
        self.test_btn = QPushButton("运行系统测试")
        self.test_btn.clicked.connect(self.run_system_test)
        left_layout.addWidget(self.test_btn)
        
        self.layout_demo_btn = QPushButton("生成布局示意图")
        self.layout_demo_btn.clicked.connect(self.generate_layout_diagram)
        left_layout.addWidget(self.layout_demo_btn)
        
        left_layout.addStretch()
        
        # 右侧：演示脚本和说明
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        script_label = QLabel("3分钟视频演示脚本要点")
        script_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        right_layout.addWidget(script_label)
        
        # 演示脚本文本
        self.script_text = QTextEdit()
        self.script_text.setPlainText("""
第一部分 (0:00-0:35) - 理论引入
• 钢琴音乐引入简谐运动合成概念
• 音频波形时域和频域分解演示
• 频率分量对音效影响的展示

第二部分 (0:35-2:30) - 软件演示
1. 同向同频模块 (0:35-1:10)
   - 调整振幅A1到1.2
   - 调整相位φ2从0到π
   - 展示相量图优化效果
   - 演示相消干涉现象

2. 拍频模块 (1:10-1:50)
   - 设置频率ω1=1.0, ω2=1.1
   - 观察拍频包络线
   - 调整频率差展示变化
   - 展示拍频频率计算

3. 李萨如图形模块 (1:50-2:30)
   - 展示L型布局设计
   - 设置频率比1:2
   - 调整相位观察图形变化
   - 展示坐标轴对齐特点

第三部分 (2:30-3:00) - 应用总结
• 降噪耳机工作原理
• 声学工程应用
• 理论与实践结合的升华

关键操作提示：
✓ 突出软件创新特点（L型布局、相量图优化）
✓ 强调实时参数调节的教学效果
✓ 展示辅助线系统的视觉引导作用
✓ 体现响应式设计和高性能动画
        """)
        right_layout.addWidget(self.script_text)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # 状态栏
        self.status_label = QLabel("准备就绪 - 选择要启动的教学模块")
        self.status_label.setStyleSheet("color: #4CAF50; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def launch_phase_module(self):
        """启动相位差合成模块"""
        self.status_label.setText("正在启动同向同频模块...")
        try:
            os.chdir('./shm_visualization')
            subprocess.Popen([sys.executable, 'phase_main.py'])
            os.chdir('..')
            self.status_label.setText("✅ 同向同频模块已启动")
        except Exception as e:
            self.status_label.setText(f"❌ 启动失败: {e}")
    
    def launch_beat_module(self):
        """启动拍频模块"""
        self.status_label.setText("正在启动拍频模块...")
        try:
            os.chdir('./shm_visualization')
            subprocess.Popen([sys.executable, 'beat_main.py'])
            os.chdir('..')
            self.status_label.setText("✅ 拍频模块已启动")
        except Exception as e:
            self.status_label.setText(f"❌ 启动失败: {e}")
    
    def launch_lissajous_module(self):
        """启动李萨如图形模块"""
        self.status_label.setText("正在启动李萨如图形模块...")
        try:
            os.chdir('./shm_visualization')
            subprocess.Popen([sys.executable, 'orthogonal_main.py'])
            os.chdir('..')
            self.status_label.setText("✅ 李萨如图形模块已启动")
        except Exception as e:
            self.status_label.setText(f"❌ 启动失败: {e}")
    
    def run_system_test(self):
        """运行系统测试"""
        self.status_label.setText("正在运行系统测试...")
        try:
            result = subprocess.run([sys.executable, 'test_improvements.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.status_label.setText("✅ 系统测试通过")
            else:
                self.status_label.setText("❌ 系统测试失败")
        except Exception as e:
            self.status_label.setText(f"❌ 测试失败: {e}")
    
    def generate_layout_diagram(self):
        """生成布局示意图"""
        self.status_label.setText("正在生成布局示意图...")
        try:
            subprocess.run([sys.executable, 'layout_diagram.py'])
            self.status_label.setText("✅ 布局示意图已生成")
        except Exception as e:
            self.status_label.setText(f"❌ 生成失败: {e}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("简谐运动教学演示启动器")
    app.setApplicationVersion("1.0")
    
    # 创建主窗口
    window = VideoDemoLauncher()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
