#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FFmpeg��װ����
============

����ű������û����غ�����FFmpeg������֧�ֶ�������Ϊ��Ƶ���ܡ�
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
    """���ݲ���ϵͳ��ȡFFmpeg����URL"""
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
        raise ValueError(f"��֧�ֵĲ���ϵͳ: {system}")

def download_progress(count, block_size, total_size):
    """���ؽ��Ȼص�����"""
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\r���ؽ���: {percent}%")
    sys.stdout.flush()

def download_ffmpeg(url, target_dir):
    """����FFmpeg"""
    print(f"���ڴ� {url} ����FFmpeg...")
    temp_file = tempfile.mktemp(suffix='.tmp')
    try:
        urlretrieve(url, temp_file, download_progress)
        print("\n�������!")
        return temp_file
    except Exception as e:
        print(f"\n����ʧ��: {e}")
        return None

def extract_ffmpeg(file_path, target_dir):
    """��ѹFFmpeg"""
    print(f"���ڽ�ѹ�� {target_dir}...")
    
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif file_path.endswith('.tar.xz') or file_path.endswith('.tar.gz'):
            with tarfile.open(file_path) as tar_ref:
                tar_ref.extractall(target_dir)
        else:
            print(f"��֧�ֵ��ļ���ʽ: {file_path}")
            return False
        
        print("��ѹ���!")
        return True
    except Exception as e:
        print(f"��ѹʧ��: {e}")
        return False

def find_ffmpeg_executable(directory):
    """�ڽ�ѹ���Ŀ¼�в���ffmpeg��ִ���ļ�"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'ffmpeg' or file == 'ffmpeg.exe':
                return os.path.join(root, file)
    return None

def setup_ffmpeg():
    """����FFmpeg"""
    system = platform.system().lower()
    
    # ���FFmpeg�Ƿ��Ѿ���װ
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("FFmpeg�Ѿ���װ��ϵͳ�У�����ֱ��ʹ�á�")
            return True
    except:
        pass  # FFmpegδ��װ��������װ����
    
    # ����Ŀ��Ŀ¼
    target_dir = Path("ffmpeg")
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    
    # ���ز���ѹFFmpeg
    try:
        url = get_ffmpeg_url()
        downloaded_file = download_ffmpeg(url, target_dir)
        if not downloaded_file:
            return False
        
        if not extract_ffmpeg(downloaded_file, target_dir):
            return False
        
        # ɾ����ʱ�ļ�
        os.remove(downloaded_file)
        
        # ���Ҳ��ƶ�ffmpeg��ִ���ļ�
        ffmpeg_exe = find_ffmpeg_executable(target_dir)
        if not ffmpeg_exe:
            print("�޷��ҵ���ѹ���FFmpeg��ִ���ļ�")
            return False
        
        # ���ffmpeg��ִ���ļ�����Ŀ��Ŀ¼�ĸ�Ŀ¼���ƶ���
        if os.path.dirname(ffmpeg_exe) != str(target_dir):
            shutil.copy(ffmpeg_exe, target_dir)
        
        print(f"FFmpeg�ѳɹ���װ�� {target_dir} Ŀ¼")
        print("�����ڿ�������main.pyʹ����Ƶ���湦����")
        return True
    except Exception as e:
        print(f"��װ�����з�������: {e}")
        return False

if __name__ == "__main__":
    print("FFmpeg��װ����")
    print("===============")
    print("����ű������ز�����FFmpeg������֧����Ƶ���湦�ܡ�")
    
    user_input = input("�Ƿ������װ? (y/n): ")
    if user_input.lower() in ('y', 'yes'):
        if setup_ffmpeg():
            print("��װ�ɹ����!")
        else:
            print("��װʧ�ܡ�")
            print("�볢���ֶ���װFFmpeg: https://ffmpeg.org/download.html")
    else:
        print("��װ��ȡ����") 