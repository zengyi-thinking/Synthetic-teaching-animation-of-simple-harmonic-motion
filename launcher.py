# -*- coding: utf-8 -*-
"""
简谐运动教学仿真系统 - 启动包装器
用于处理已打包应用程序的启动流程
强化版本，提高稳定性，防止闪退
"""

import os
import sys
import traceback
import importlib.util
import time
import datetime

# 全局变量，用于保持窗口对象的引用
main_window = None

def create_error_window(title, message):
    """创建简单的错误窗口显示错误信息"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication([])
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    except Exception as e:
        print(f"无法创建错误窗口: {e}")
        print(f"错误信息: {message}")
        # 如果在PyInstaller环境中，暂停以便用户看到错误信息
        if getattr(sys, 'frozen', False):
            print("按任意键退出...")
            time.sleep(5)

def log_error(message, exception=None):
    """记录错误信息到日志文件"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"error_log_{timestamp}.txt")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")
            if exception:
                f.write(f"异常信息: {str(exception)}\n")
                f.write(traceback.format_exc())
                f.write("\n\n")
    except:
        pass

def check_environment():
    """检查运行环境并返回状态信息"""
    env_info = {}
    
    print("=" * 50)
    print("简谐运动教学仿真系统 - 启动检查")
    print("=" * 50)
    
    print("正在检查运行环境...")
    
    # 检查操作系统
    env_info["os"] = sys.platform
    if hasattr(sys, 'getwindowsversion'):
        env_info["windows_build"] = sys.getwindowsversion().build
    print(f"操作系统: {env_info['os']} {env_info.get('windows_build', '')}")
    
    # 检查Python版本
    env_info["python_version"] = sys.version
    print(f"Python版本: {env_info['python_version']}")
    
    # 检测是否在PyInstaller环境中运行
    env_info["is_pyinstaller"] = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    print(f"PyInstaller环境: {'是' if env_info['is_pyinstaller'] else '否'}")
    
    # 获取应用程序路径
    if env_info["is_pyinstaller"]:
        env_info["app_path"] = sys._MEIPASS  # PyInstaller环境
    else:
        env_info["app_path"] = os.path.abspath(os.path.dirname(__file__))  # 普通Python环境
    
    print(f"应用程序路径: {env_info['app_path']}")
    
    # 添加模块路径
    env_info["shm_dir"] = os.path.join(env_info["app_path"], 'shm_visualization')
    print(f"添加到导入路径: {env_info['shm_dir']}")
    if env_info["shm_dir"] not in sys.path:
        sys.path.insert(0, env_info["shm_dir"])
    
    print(f"添加到导入路径: {env_info['app_path']}")
    if env_info["app_path"] not in sys.path:
        sys.path.insert(0, env_info["app_path"])
    
    # 检查目录是否存在
    env_info["shm_dir_exists"] = os.path.exists(env_info["shm_dir"])
    if not env_info["shm_dir_exists"]:
        print(f"警告: 找不到必要的目录: {env_info['shm_dir']}")
    
    # 列出Python文件
    if env_info["shm_dir_exists"]:
        try:
            py_files = [f for f in os.listdir(env_info["shm_dir"]) if f.endswith('.py')]
            env_info["py_files"] = py_files
            print(f"找到Python文件: {', '.join(py_files)}")
        except Exception as e:
            print(f"无法列出Python文件: {str(e)}")
    
    # 检查关键模块是否存在
    ui_framework_path = os.path.join(env_info["shm_dir"], 'ui_framework.py')
    env_info["ui_framework_exists"] = os.path.exists(ui_framework_path)
    if not env_info["ui_framework_exists"]:
        print(f"警告: UI框架文件不存在: {ui_framework_path}")
    
    # 检查依赖项
    try:
        import PyQt6
        print("PyQt6导入成功")
    except ImportError as e:
        log_error("PyQt6导入失败", e)
        print(f"警告: PyQt6导入失败: {str(e)}")

    try:
        import matplotlib
        print("matplotlib导入成功")
    except ImportError as e:
        log_error("matplotlib导入失败", e)
        print(f"警告: matplotlib导入失败: {str(e)}")

    try:
        import numpy
        print("numpy导入成功")
    except ImportError as e:
        log_error("numpy导入失败", e)
        print(f"警告: numpy导入失败: {str(e)}")
    
    return env_info

def main():
    """主函数入口"""
    global main_window
    
    # 创建日志目录
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"创建日志目录失败: {e}")

    try:
        # 设置异常钩子，捕获所有未处理的异常
        def exception_hook(exc_type, exc_value, exc_traceback):
            error_msg = f"未捕获异常: {exc_type.__name__}: {exc_value}"
            log_error(error_msg)
            print(error_msg)
            print(traceback.format_exc())
            
            # 在终端显示可读的错误信息
            if getattr(sys, 'frozen', False):
                create_error_window("程序错误", f"{error_msg}\n\n请查看日志获取详细信息")
            else:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        # 设置全局异常处理器
        sys.excepthook = exception_hook

        # 检查环境
        env_info = check_environment()
        
        print("\n环境检查通过，准备启动主程序...")
        
        # 初始化基础库
        try:
            # 初始化PyQt
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance() or QApplication([])
            print("QApplication已初始化")
            
            # 初始化matplotlib
            import matplotlib
            print("matplotlib已初始化")
            
            # 强制修复频率参数
            try:
                from shm_visualization.ui_framework import INITIAL_PARAMS
                print(f"原始omega2值: {INITIAL_PARAMS['omega2']}")
                print(f"原始ratio_preset值: {INITIAL_PARAMS['ratio_preset']}")
                INITIAL_PARAMS['omega2'] = 1.0
                INITIAL_PARAMS['ratio_preset'] = '1:1'
                print("已修复频率参数")
                print(f"修复后omega2值: {INITIAL_PARAMS['omega2']}")
                print(f"修复后ratio_preset值: {INITIAL_PARAMS['ratio_preset']}")
            except Exception as e:
                print(f"修复频率参数失败: {e}")
        except Exception as e:
            log_error("初始化基础库失败", e)
            create_error_window("初始化失败", f"初始化基础库失败: {e}")
            return 1
        
        # 导入启动模块
        start_module = None
        error_messages = []
        
        # 方法1: 直接从shm_visualization目录导入
        if env_info.get("shm_dir_exists", False) and 'start.py' in env_info.get("py_files", []):
            try:
                print("尝试方法1: 从shm_visualization目录导入...")
                import shm_visualization.start as start_module
                print("方法1导入成功!")
            except Exception as e:
                error_msg = f"方法1导入失败: {str(e)}"
                print(error_msg)
                log_error(error_msg, e)
                error_messages.append(error_msg)
                
        # 方法2: 尝试直接导入
        if start_module is None:
            try:
                print("尝试方法2: 直接导入start模块...")
                import start as start_module
                print("方法2导入成功!")
            except ImportError as e:
                error_msg = f"方法2导入失败: {str(e)}"
                print(error_msg)
                log_error(error_msg, e)
                error_messages.append(error_msg)
        
        # 方法3: 使用importlib从文件加载
        if start_module is None:
            try:
                print("尝试方法3: 使用importlib从文件加载...")
                start_path = None
                
                # 检查几个可能的位置
                possible_paths = [
                    os.path.join(env_info["app_path"], 'start.py'),
                    os.path.join(env_info["app_path"], 'shm_visualization', 'start.py'),
                    os.path.join(env_info["shm_dir"], 'start.py')
                ]
                
                for p in possible_paths:
                    if os.path.exists(p):
                        start_path = p
                        print(f"找到start.py文件: {p}")
                        break
                
                if start_path:
                    spec = importlib.util.spec_from_file_location("start", start_path)
                    if spec:
                        start_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(start_module)
                        print("方法3导入成功!")
                    else:
                        error_msg = "无法从文件创建模块规范"
                        print(error_msg)
                        log_error(error_msg)
                        error_messages.append(error_msg)
                else:
                    error_msg = "找不到start.py文件"
                    print(error_msg)
                    log_error(error_msg)
                    error_messages.append(error_msg)
            except Exception as e:
                error_msg = f"方法3导入失败: {str(e)}"
                print(error_msg)
                log_error(error_msg, e)
                error_messages.append(error_msg)
        
        # 检查是否成功导入模块
        if start_module is None:
            error_msg = "无法导入start模块。请确保文件存在且可访问。"
            print("\n错误: " + error_msg)
            print("\n尝试的导入方法都失败了:")
            for i, msg in enumerate(error_messages, 1):
                print(f"  {i}. {msg}")
            log_error(error_msg)
            create_error_window("导入失败", error_msg)
            return 1
        
        # 确保模块有main函数
        if not hasattr(start_module, 'main'):
            error_msg = f"在start模块中找不到main函数"
            print(f"错误: {error_msg}")
            print(f"模块属性: {dir(start_module)}")
            log_error(error_msg)
            create_error_window("启动失败", error_msg)
            return 1
        
        # 调用启动函数
        print("调用start.main()函数...")
        try:
            # 保存窗口引用到全局变量
            main_window = start_module.main()
            
            # 确保window实例有效
            if not main_window:
                error_msg = "模块未返回有效窗口"
                print(f"错误: {error_msg}")
                log_error(error_msg)
                create_error_window("启动失败", error_msg)
                return 1
            
            print("程序启动成功!")
            
            # 确保窗口显示
            main_window.show()
            
            # 开始事件循环
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app and hasattr(app, 'exec'):
                print("正在启动QApplication事件循环...")
                return app.exec()
            else:
                print("警告: 无法找到有效的QApplication实例")
                input("按Enter键退出...")
                return 0
            
        except Exception as e:
            error_msg = f"启动start.main()时发生错误: {str(e)}"
            print(error_msg)
            traceback_info = traceback.format_exc()
            print(traceback_info)
            log_error(error_msg, e)
            create_error_window("启动失败", f"启动主程序时发生错误: {str(e)}")
            return 1
        
    except Exception as e:
        error_msg = f"启动过程中发生严重错误: {str(e)}"
        print(error_msg)
        traceback_info = traceback.format_exc()
        print(traceback_info)
        log_error(error_msg, e)
        
        create_error_window("严重错误", f"启动过程中发生严重错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 