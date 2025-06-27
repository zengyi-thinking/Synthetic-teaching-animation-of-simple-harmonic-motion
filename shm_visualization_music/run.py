# -*- coding: utf-8 -*-
"""
简谐振动与音乐可视化 - 启动脚本
"""

import sys
import os
import time
import platform
import matplotlib.font_manager as fm

# 确保当前目录在路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def check_chinese_fonts():
    """检查系统中是否有可用的中文字体"""
    chinese_fonts = [f for f in fm.findSystemFonts() if ('simhei' in f.lower() or 
                                                         'microsoft yahei' in f.lower() or 
                                                         'simsun' in f.lower() or
                                                         'kaiti' in f.lower() or
                                                         'msyh' in f.lower() or
                                                         'simkai' in f.lower() or
                                                         'fangsong' in f.lower() or
                                                         'nsimsun' in f.lower())]
    if chinese_fonts:
        print(f"找到中文字体: {os.path.basename(chinese_fonts[0])}")
        return True
    else:
        print("警告：未找到中文字体，可能导致界面中文显示不正确")
        return False

def main():
    try:
        # 输出系统信息
        print(f"系统: {platform.system()} {platform.version()}")
        print(f"Python版本: {platform.python_version()}")
        
        # 检查中文字体
        check_chinese_fonts()
        
        # 导入应用程序
        print("正在启动简谐振动与音乐可视化教学系统...")
        print("加载音频引擎...")
        time.sleep(0.5)  # 增加短暂延迟，使启动过程更平滑
        print("加载可视化引擎...")
        time.sleep(0.5)
        print("初始化用户界面...")
        time.sleep(0.5)
        
        # 导入应用程序
        try:
            from app import main as app_main
            print("启动完成！")
            app_main()
        except ImportError as e:
            print(f"导入应用程序失败: {str(e)}")
            print("请确保所有依赖包已安装，可运行：pip install -r requirements.txt")
            input("按回车键退出...")
            sys.exit(1)
            
    except Exception as e:
        print(f"启动失败: {str(e)}")
        input("按回车键退出...")
        sys.exit(1)

# 运行主程序
if __name__ == "__main__":
    main() 