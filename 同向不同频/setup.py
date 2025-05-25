import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本是否满足要求"""
    print("检查Python版本...")
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    print(f"Python版本: {sys.version.split()[0]} ?")

def install_dependencies():
    """安装所需的Python依赖"""
    print("安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成 ?")
    except subprocess.CalledProcessError:
        print("错误: 依赖安装失败")
        sys.exit(1)

def check_ffmpeg():
    """检查FFmpeg是否已安装"""
    print("检查FFmpeg...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("FFmpeg已安装 ?")
            return True
    except FileNotFoundError:
        pass
    
    return False

def install_ffmpeg():
    """指导用户如何安装FFmpeg"""
    system = platform.system()
    print("未检测到FFmpeg。请按照以下说明安装FFmpeg:")
    
    if system == "Windows":
        print("""
1. 访问 https://ffmpeg.org/download.html 下载Windows版本
2. 解压缩下载的文件
3. 将解压后的bin文件夹路径添加到系统环境变量PATH中
4. 重启命令提示符或PowerShell
""")
    elif system == "Darwin":  # macOS
        print("""
使用Homebrew安装FFmpeg:
$ brew install ffmpeg
""")
    elif system == "Linux":
        print("""
在大多数Linux发行版上，您可以使用包管理器安装FFmpeg:

对于Ubuntu/Debian:
$ sudo apt update
$ sudo apt install ffmpeg

对于Fedora:
$ sudo dnf install ffmpeg

对于Arch Linux:
$ sudo pacman -S ffmpeg
""")
    else:
        print("请访问 https://ffmpeg.org/download.html 获取适合您系统的安装说明")
    
    input("安装完FFmpeg后按Enter键继续...")

def create_venv():
    """创建并激活虚拟环境"""
    if not os.path.exists(".venv"):
        print("创建虚拟环境...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
            print("虚拟环境创建完成 ?")
        except subprocess.CalledProcessError:
            print("错误: 虚拟环境创建失败")
            sys.exit(1)
    else:
        print("已存在虚拟环境 ?")

def main():
    """主函数"""
    print("=== 简谐振动合成动画环境设置 ===")
    
    check_python_version()
    create_venv()
    
    # 提示用户激活虚拟环境
    system = platform.system()
    if system == "Windows":
        print("\n请先激活虚拟环境:")
        print(".venv\\Scripts\\activate")
    else:
        print("\n请先激活虚拟环境:")
        print("source .venv/bin/activate")
    
    response = input("虚拟环境是否已激活? (y/n): ")
    if response.lower() != 'y':
        print("请先激活虚拟环境再运行此脚本")
        sys.exit(0)
    
    install_dependencies()
    
    if not check_ffmpeg():
        install_ffmpeg()
        if not check_ffmpeg():
            print("警告: FFmpeg安装未完成或未添加到PATH。视频保存功能可能无法正常工作。")
    
    print("\n设置完成! 现在您可以运行:")
    print("python main.py")

if __name__ == "__main__":
    main() 