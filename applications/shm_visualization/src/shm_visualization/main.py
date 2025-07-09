# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 启动器
方便用户选择不同的模拟模块
"""

import sys
import os
import importlib
import traceback
from functools import partial
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from .ui.ui_framework import COLORS, get_app_instance

# 添加模块路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class SimulationLauncher(QMainWindow):
    """简谐运动模拟启动器"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("简谐运动模拟系统")
        self.setMinimumSize(800, 500)  # 设置最小尺寸
        self.resize(900, 550)  # 设置初始尺寸，但允许调整
        self.current_module_window = None  # 存储当前打开的模块窗口引用
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建标题区域 - 简化设计
        title_container = QWidget()
        title_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(5)
        title_layout.setContentsMargins(10, 10, 10, 10)

        # 创建标题标签 - 减小字体，去掉过度装饰
        title_label = QLabel("简谐运动模拟系统")
        title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 24pt;
            font-weight: bold;
            background: transparent;
            margin: 0px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建副标题标签 - 调整大小和颜色
        subtitle_label = QLabel("Simple Harmonic Motion Visualization System")
        subtitle_label.setStyleSheet(f"""
            color: {COLORS['accent1']};
            font-size: 12pt;
            background: transparent;
            margin: 0px;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # 创建描述标签 - 简化样式
        description_label = QLabel("请选择要运行的模拟模块")
        description_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 16pt;
            margin: 15px 0px;
            font-weight: normal;
        """)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建模块选择区域
        modules_container = QWidget()
        modules_layout = QGridLayout(modules_container)
        modules_layout.setSpacing(20)
        modules_layout.setContentsMargins(10, 10, 10, 10)
        # 设置列的拉伸因子，使卡片能够适应窗口大小
        modules_layout.setColumnStretch(0, 1)
        modules_layout.setColumnStretch(1, 1)
        modules_layout.setColumnStretch(2, 1)

        # 创建三个模块按钮 - 简化数据结构
        modules = [
            {
                "name": "李萨如图形",
                "subtitle": "不同向不同频",
                "description": "垂直简谐运动合成，观察李萨如图形",
                "module": ".modules.orthogonal_main",
                "icon": "📊"
            },
            {
                "name": "拍现象",
                "subtitle": "同向不同频",
                "description": "观察两个频率接近的简谐波合成产生的拍现象",
                "module": ".modules.beat_main",
                "icon": "🌊"
            },
            {
                "name": "相位差合成",
                "subtitle": "同向同频",
                "description": "观察两个相同频率不同相位的简谐波合成效果",
                "module": ".modules.phase_main",
                "icon": "⚡"
            }
        ]

        for i, module in enumerate(modules):
            # 创建模块卡片 - 简洁设计
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['panel']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 10px;
                    margin: 2px;
                }}
                QFrame:hover {{
                    border: 2px solid {COLORS['accent1']};
                    background-color: rgba(21, 34, 56, 0.95);
                }}
            """)
            card.setMinimumSize(250, 280)  # 设置最小尺寸，允许调整
            card.setMaximumSize(350, 400)  # 设置最大尺寸

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(10)

            # 图标区域
            icon_label = QLabel(module['icon'])
            icon_label.setStyleSheet(f"""
                color: {COLORS['accent1']};
                font-size: 36pt;
                background: transparent;
                margin: 0px;
            """)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 主标题
            title_label = QLabel(module['name'])
            title_label.setStyleSheet(f"""
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 16pt;
                background: transparent;
                margin: 0px;
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 副标题
            subtitle_label = QLabel(module['subtitle'])
            subtitle_label.setStyleSheet(f"""
                color: {COLORS['accent1']};
                font-size: 11pt;
                background: transparent;
                margin: 0px;
            """)
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 描述文本
            desc_label = QLabel(module['description'])
            desc_label.setStyleSheet(f"""
                color: rgba(255, 255, 255, 0.8);
                font-size: 10pt;
                background: transparent;
                margin: 5px 0px;
            """)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)

            # 启动按钮 - 简化设计
            btn = QPushButton("启动")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent1']};
                    color: {COLORS['text']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12pt;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['button_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['button_active']};
                }}
            """)
            btn.setFixedHeight(36)
            btn.clicked.connect(partial(self.run_module, module['module']))

            # 添加组件到卡片
            card_layout.addWidget(icon_label)
            card_layout.addWidget(title_label)
            card_layout.addWidget(subtitle_label)
            card_layout.addWidget(desc_label)
            card_layout.addStretch(1)
            card_layout.addWidget(btn)

            # 添加卡片到网格
            modules_layout.addWidget(card, 0, i)

        # 组装主布局
        main_layout.addWidget(title_container)
        main_layout.addWidget(description_label)
        main_layout.addWidget(modules_container, 1)  # 给模块区域更多空间

        # 添加版权信息 - 简化样式
        copyright_label = QLabel("© 简谐运动教学演示系统")
        copyright_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.5);
            font-size: 10pt;
            background: transparent;
            margin: 10px 0px;
        """)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(copyright_label)

    def run_module(self, module_name):
        """运行选择的模块"""
        print(f"正在启动模块: {module_name}")

        # 隐藏而不是关闭启动器
        self.hide()

        # 确保添加了当前目录到系统路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # 检查模块文件是否存在
        try:
            module_path_parts = module_name.split('.')
            module_file = os.path.join(current_dir, *module_path_parts[:-1], f"{module_path_parts[-1]}.py")
            if not os.path.exists(module_file):
                print(f"模块文件未找到: {module_file}")
                self.show()
                return
        except Exception as e:
            print(f"模块路径解析错误: {e}")
            self.show()
            return

        # 导入并运行选定的模块
        try:
            # 如果模块已经导入过，重新导入以获取最新代码
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                if module_name.startswith('.'):
                    # For relative imports, provide the package parameter
                    module = importlib.import_module(module_name, package='shm_visualization')
                else:
                    module = importlib.import_module(module_name)

            # 确保模块有main函数
            if not hasattr(module, 'main'):
                print(f"模块没有main函数: {module_name}")
                self.show()
                return

            # 创建模块窗口并存储引用
            self.current_module_window = module.main()

            # 确保window实例有效
            if not self.current_module_window:
                print(f"模块未返回有效窗口: {module_name}")
                self.show()
                return

            # 当模块窗口关闭时，重新显示启动器
            if hasattr(self.current_module_window, 'closeEvent'):
                original_close_event = self.current_module_window.closeEvent

                def new_close_event(event):
                    print(f"模块窗口关闭: {module_name}")
                    # 调用原始的closeEvent
                    if original_close_event:
                        original_close_event(event)
                    # 重新显示启动器
                    self.show()

                self.current_module_window.closeEvent = new_close_event
            else:
                print(f"警告：窗口没有closeEvent: {module_name}")

        except ImportError as e:
            print(f"无法导入模块：{module_name}")
            print(f"错误详情: {e}")
            traceback_info = traceback.format_exc()
            print(f"Traceback: {traceback_info}")
            self.show()  # 导入失败也要重新显示启动器
        except Exception as e:
            print(f"运行模块时出错：{module_name}")
            print(f"错误详情: {e}")
            traceback_info = traceback.format_exc()
            print(f"Traceback: {traceback_info}")
            self.show()  # 发生错误也要重新显示启动器


def main():
    """程序入口"""
    # 使用全局应用实例
    app = get_app_instance()

    # 创建并显示启动器
    launcher = SimulationLauncher()
    launcher.show()

    # 启动Qt事件循环
    print("正在启动Qt事件循环...")

    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\n用户中断应用程序")
        return 0
    except Exception as e:
        print(f"应用程序错误: {e}")
        return 1

# 在文件最后添加主程序执行入口点
if __name__ == "__main__":
    main()
