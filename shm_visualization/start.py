# -*- coding: utf-8 -*-
"""
简谐运动模拟 - 启动器
方便用户选择不同的模拟模块
"""

import sys
import os
import importlib
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from ui_framework import COLORS, get_app_instance

# 添加模块路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class SimulationLauncher(QMainWindow):
    """简谐运动模拟启动器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Harmonic Motion Simulator 简谐运动模拟启动器")
        self.setFixedSize(1000, 600)  # 加大窗口尺寸
        self.current_module_window = None  # 存储当前打开的模块窗口引用
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口样式
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        
        # 创建标题标签
        title_label = QLabel("Simple Harmonic Motion Simulation System\n简谐运动模拟系统")
        title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 24pt;  # 增大字体
            background-color: {COLORS['accent3']};
            border-radius: 10px;
            padding: 20px;  # 增加内边距
            margin-bottom: 30px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建描述标签
        description_label = QLabel("Please select a simulation module / 请选择要运行的模拟模块：")
        description_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 14pt;  # 增大字体
            margin: 15px;
        """)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建按钮网格布局
        button_layout = QGridLayout()
        button_layout.setSpacing(20)  # 增加按钮间距
        
        # 创建三个模块按钮
        modules = [
            {
                "name": "Orthogonal SHM (Lissajous Figures)",
                "name_cn": "不同向不同频（李萨如图形）",
                "description": "Visualization of orthogonal SHM with different frequencies",
                "description_cn": "垂直简谐运动合成，观察李萨如图形",
                "module": "orthogonal_main",
                "color": COLORS['accent1']
            },
            {
                "name": "Beat Phenomenon",
                "name_cn": "同向不同频（拍现象）",
                "description": "Observation of beats from two waves with close frequencies",
                "description_cn": "观察两个频率接近的简谐波合成产生的拍现象",
                "module": "beat_main",
                "color": COLORS['accent2']
            },
            {
                "name": "Phase Composition",
                "name_cn": "同向同频（相位差合成）",
                "description": "Study the effects of phase difference in same-frequency waves",
                "description_cn": "观察两个相同频率不同相位的简谐波合成效果",
                "module": "phase_main",
                "color": COLORS['accent3']
            }
        ]
        
        for i, module in enumerate(modules):
            # 创建模块卡片
            card = QFrame()
            card.setStyleSheet(f"""
                background-color: {COLORS['panel']};
                border: 3px solid {module['color']};
                border-radius: 10px;
            """)
            card.setMinimumHeight(300)  # 设置最小高度
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)  # 增加卡片内边距
            
            # 卡片标题
            card_title = QLabel(f"{module['name']}\n{module['name_cn']}")
            card_title.setStyleSheet(f"""
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 16pt;  # 增大字体
                background-color: {module['color']};
                border-radius: 5px;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            """)
            card_title.setMinimumHeight(80)  # 确保足够高度显示双行标题
            card_title.setWordWrap(True)  # 允许文本换行
            
            # 卡片描述
            card_desc = QLabel(f"{module['description']}\n{module['description_cn']}")
            card_desc.setStyleSheet(f"""
                color: {COLORS['text']};
                font-size: 12pt;  # 增大字体
                margin: 15px;
                qproperty-alignment: AlignCenter;
            """)
            card_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_desc.setWordWrap(True)  # 允许文本换行
            card_desc.setMinimumHeight(80)  # 确保足够高度显示说明文本
            
            # 卡片按钮
            btn = QPushButton("Run / 运行")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {module['color']};
                    color: {COLORS['text']};
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 14pt;  # 增大字体
                    min-height: 50px;  # 确保按钮足够高
                }}
                
                QPushButton:hover {{
                    background-color: {COLORS['button_hover']};
                }}
                
                QPushButton:pressed {{
                    background-color: {COLORS['button_active']};
                }}
            """)
            btn.clicked.connect(lambda checked, m=module['module']: self.run_module(m))
            
            card_layout.addWidget(card_title)
            card_layout.addWidget(card_desc)
            card_layout.addStretch(1)  # 添加弹性空间
            card_layout.addWidget(btn)
            
            # 添加卡片到网格
            button_layout.addWidget(card, 0, i)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        main_layout.addLayout(button_layout, 1)  # 设置拉伸因子使卡片占据更多空间
        
        # 添加版权信息
        copyright_label = QLabel("© Simple Harmonic Motion Teaching Demo - Based on PyQt6 and Matplotlib")
        copyright_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 10pt;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setContentsMargins(0, 15, 0, 0)  # 增加上边距
        
        main_layout.addWidget(copyright_label)
    
    def run_module(self, module_name):
        """运行选择的模块"""
        print(f"Starting module / 正在启动模块: {module_name}")
        
        # 隐藏而不是关闭启动器
        self.hide()
        
        # 确保添加了当前目录到系统路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 检查模块文件是否存在
        module_file = os.path.join(current_dir, f"{module_name}.py")
        if not os.path.exists(module_file):
            print(f"Module file not found / 模块文件未找到: {module_file}")
            self.show()
            return
        
        # 导入并运行选定的模块
        try:
            # 如果模块已经导入过，重新导入以获取最新代码
            if module_name in sys.modules:
                print(f"Reloading module / 重新加载模块: {module_name}")
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            # 确保模块有main函数
            if not hasattr(module, 'main'):
                print(f"Module does not have main function / 模块没有main函数: {module_name}")
                self.show()
                return
            
            # 创建模块窗口并存储引用
            self.current_module_window = module.main()
            
            # 确保window实例有效
            if not self.current_module_window:
                print(f"Module did not return a valid window / 模块未返回有效窗口: {module_name}")
                self.show()
                return
            
            # 当模块窗口关闭时，重新显示启动器
            if hasattr(self.current_module_window, 'closeEvent'):
                original_close_event = self.current_module_window.closeEvent
                
                def new_close_event(event):
                    print(f"Module window closed / 模块窗口关闭: {module_name}")
                    # 调用原始的closeEvent
                    if original_close_event:
                        original_close_event(event)
                    # 重新显示启动器
                    self.show()
                
                self.current_module_window.closeEvent = new_close_event
            else:
                print(f"Warning: Window has no closeEvent / 警告：窗口没有closeEvent: {module_name}")
            
        except ImportError as e:
            print(f"Cannot import module / 无法导入模块：{module_name}")
            print(f"Error details / 错误详情: {e}")
            traceback_info = traceback.format_exc()
            print(f"Traceback: {traceback_info}")
            self.show()  # 导入失败也要重新显示启动器
        except Exception as e:
            print(f"Error running module / 运行模块时出错：{module_name}")
            print(f"Error details / 错误详情: {e}")
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
    
    # 只有在直接运行此模块时才执行事件循环
    if __name__ == "__main__":
        sys.exit(app.exec())
    
    # 返回启动器对象
    return launcher

# 在文件最后添加主程序执行入口点
if __name__ == "__main__":
    main() 