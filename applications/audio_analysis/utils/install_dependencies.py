#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析模块依赖库安装脚本
自动检查和安装所需的依赖库
"""

import subprocess
import sys
import importlib
import os

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装包"""
    try:
        print(f"正在安装 {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败: {e}")
        return False

def main():
    """主安装函数"""
    print("🎵 音频分析模块依赖库安装程序")
    print("=" * 50)
    
    # 定义依赖库列表
    dependencies = [
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("librosa", "librosa"),
        ("soundfile", "soundfile"),
        ("sounddevice", "sounddevice"),
        ("PyQt6", "PyQt6"),
    ]
    
    # 检查已安装的包
    print("检查已安装的依赖库...")
    installed = []
    missing = []
    
    for package_name, import_name in dependencies:
        if check_package(package_name, import_name):
            print(f"✅ {package_name} - 已安装")
            installed.append(package_name)
        else:
            print(f"❌ {package_name} - 未安装")
            missing.append(package_name)
    
    # 安装缺失的包
    if missing:
        print(f"\n需要安装 {len(missing)} 个依赖库:")
        for package in missing:
            print(f"  - {package}")
        
        response = input("\n是否现在安装这些依赖库? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是']:
            print("\n开始安装依赖库...")
            success_count = 0
            
            for package in missing:
                if install_package(package):
                    success_count += 1
            
            print(f"\n安装完成: {success_count}/{len(missing)} 个包安装成功")
            
            if success_count == len(missing):
                print("🎉 所有依赖库安装成功！")
            else:
                print("⚠️ 部分依赖库安装失败，请手动安装")
        else:
            print("跳过安装，请手动安装所需依赖库")
    else:
        print("\n🎉 所有依赖库都已安装！")
    
    # 验证安装
    print("\n验证安装结果...")
    all_installed = True
    
    for package_name, import_name in dependencies:
        if check_package(package_name, import_name):
            print(f"✅ {package_name}")
        else:
            print(f"❌ {package_name}")
            all_installed = False
    
    if all_installed:
        print("\n🚀 音频分析模块已准备就绪！")
        print("可以运行以下命令启动:")
        print("  python audio_editor_ui.py")
    else:
        print("\n⚠️ 部分依赖库仍未安装，请检查安装过程")
    
    # 生成示例音频文件
    if all_installed:
        response = input("\n是否生成示例音频文件? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            try:
                print("正在生成示例音频文件...")
                subprocess.run([sys.executable, "generate_sample_audio.py"], check=True)
                print("✅ 示例音频文件生成完成")
            except subprocess.CalledProcessError:
                print("❌ 示例音频文件生成失败")

if __name__ == "__main__":
    main()
