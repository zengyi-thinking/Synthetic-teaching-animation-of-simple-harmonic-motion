#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FFmpeg安装助手
============

这个脚本帮助用户下载和设置FFmpeg，用于支持动画保存为视频功能。
"""

import os
import sys
import platform
import subprocess
import shutil
import zipfile
import tarfile
from urllib.request import urlretrieve
from pathlib import Path
import tempfile

def get_ffmpeg_url():
    """根据操作系统获取FFmpeg下载URL"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == 'windows':
        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == 'darwin':  # macOS
        if 'arm' in arch or 'aarch64' in arch:  # Apple Silicon
            return "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
        else:  # Intel
            return "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    elif system == 'linux':
        return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    else:
        raise ValueError(f"不支持的操作系统: {system}")

def download_progress(count, block_size, total_size):
    """下载进度回调函数"""
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\r下载进度: {percent}%")
    sys.stdout.flush()

def download_ffmpeg(url, target_dir):
    """下载FFmpeg"""
    print(f"正在从 {url} 下载FFmpeg...")
    temp_file = tempfile.mktemp(suffix='.tmp')
    try:
        urlretrieve(url, temp_file, download_progress)
        print("\n下载完成!")
        return temp_file
    except Exception as e:
        print(f"\n下载失败: {e}")
        return None

def extract_ffmpeg(file_path, target_dir):
    """解压FFmpeg"""
    print(f"正在解压到 {target_dir}...")
    
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif file_path.endswith('.tar.xz') or file_path.endswith('.tar.gz'):
            with tarfile.open(file_path) as tar_ref:
                tar_ref.extractall(target_dir)
        else:
            print(f"不支持的文件格式: {file_path}")
            return False
        
        print("解压完成!")
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def find_ffmpeg_executable(directory):
    """在解压后的目录中查找ffmpeg可执行文件"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'ffmpeg' or file == 'ffmpeg.exe':
                return os.path.join(root, file)
    return None

def setup_ffmpeg():
    """设置FFmpeg"""
    system = platform.system().lower()
    
    # 检查FFmpeg是否已经安装
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("FFmpeg已经安装在系统中，可以直接使用。")
            return True
    except:
        pass  # FFmpeg未安装，继续安装流程
    
    # 创建目标目录
    target_dir = Path("ffmpeg")
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    
    # 下载并解压FFmpeg
    try:
        url = get_ffmpeg_url()
        downloaded_file = download_ffmpeg(url, target_dir)
        if not downloaded_file:
            return False
        
        if not extract_ffmpeg(downloaded_file, target_dir):
            return False
        
        # 删除临时文件
        os.remove(downloaded_file)
        
        # 查找并移动ffmpeg可执行文件
        ffmpeg_exe = find_ffmpeg_executable(target_dir)
        if not ffmpeg_exe:
            print("无法找到解压后的FFmpeg可执行文件")
            return False
        
        # 如果ffmpeg可执行文件不在目标目录的根目录，移动它
        if os.path.dirname(ffmpeg_exe) != str(target_dir):
            shutil.copy(ffmpeg_exe, target_dir)
        
        print(f"FFmpeg已成功安装到 {target_dir} 目录")
        print("您现在可以运行main.py使用视频保存功能了")
        return True
    except Exception as e:
        print(f"安装过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("FFmpeg安装助手")
    print("===============")
    print("这个脚本将下载并设置FFmpeg，用于支持视频保存功能。")
    
    user_input = input("是否继续安装? (y/n): ")
    if user_input.lower() in ('y', 'yes'):
        if setup_ffmpeg():
            print("安装成功完成!")
        else:
            print("安装失败。")
            print("请尝试手动安装FFmpeg: https://ffmpeg.org/download.html")
    else:
        print("安装已取消。") 