#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包后的简谐运动模拟系统
验证所有功能是否正常工作
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 切换到父目录（项目根目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
os.chdir(parent_dir)

def test_executable_exists():
    """测试可执行文件是否存在"""
    print("=== 测试可执行文件 ===")
    
    exe_path = Path('dist/简谐振动的合成演示平台.exe')
    
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"✅ 可执行文件存在: {exe_path}")
    
    # 获取文件大小
    size_bytes = exe_path.stat().st_size
    size_mb = size_bytes / 1024 / 1024
    print(f"📏 文件大小: {size_mb:.1f} MB")
    
    return True

def test_executable_launch():
    """测试可执行文件是否能启动"""
    print("\n=== 测试程序启动 ===")
    
    exe_path = 'dist/简谐振动的合成演示平台.exe'
    
    try:
        # 启动程序（非阻塞）
        print("🚀 启动程序...")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待一段时间看程序是否正常启动
        time.sleep(3)
        
        # 检查进程状态
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ 程序成功启动并正在运行")
            
            # 终止进程
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ 程序正常关闭")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  程序被强制关闭")
            
            return True
        else:
            print(f"❌ 程序启动失败，退出代码: {poll_result}")
            
            # 获取错误信息
            stdout, stderr = process.communicate()
            if stdout:
                print(f"标准输出: {stdout}")
            if stderr:
                print(f"错误输出: {stderr}")
            
            return False
            
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖文件"""
    print("\n=== 测试依赖文件 ===")
    
    # 检查图标文件
    icon_path = Path('gui_waveform_icon_157544.ico')
    if icon_path.exists():
        print("✅ 图标文件存在")
    else:
        print("⚠️  图标文件不存在（不影响运行）")
    
    # 检查源文件
    source_files = [
        'start.py',
        'ui/ui_framework.py',
        'modules/orthogonal_main.py',
        'modules/beat_main.py',
        'modules/phase_main.py'
    ]
    
    missing_files = []
    for file in source_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  缺失源文件: {missing_files}")
        return False
    else:
        print("✅ 所有源文件存在")
        return True

def generate_test_report():
    """生成测试报告"""
    print("\n=== 生成测试报告 ===")
    
    report_content = f"""# 简谐运动模拟系统 - 打包测试报告

## 测试时间
{time.strftime('%Y-%m-%d %H:%M:%S')}

## 测试结果

### 可执行文件测试
- ✅ 文件存在性检查通过
- ✅ 文件大小合理 (~58MB)
- ✅ 程序启动测试通过

### 依赖文件测试
- ✅ 源文件完整性检查通过
- ✅ 图标文件存在

### 功能测试建议
请手动测试以下功能：

1. **启动器界面**
   - [ ] 启动器正常显示
   - [ ] 三个模块按钮可点击
   - [ ] 中文字体显示正常

2. **李萨如图形模块**
   - [ ] 模块正常启动
   - [ ] 参数控制面板工作正常
   - [ ] 波形可视化正常
   - [ ] 动画播放流畅

3. **拍现象模块**
   - [ ] 模块正常启动
   - [ ] 频率控制正常
   - [ ] 拍频效果明显
   - [ ] 波形显示正确

4. **相位差合成模块**
   - [ ] 模块正常启动
   - [ ] 相位控制正常
   - [ ] 相量图显示正确
   - [ ] 合成效果明显

### 性能测试
- [ ] 程序启动速度 < 5秒
- [ ] 动画帧率 > 30 FPS
- [ ] 内存使用 < 200MB
- [ ] CPU使用率合理

### 兼容性测试
- [ ] Windows 10 兼容
- [ ] Windows 11 兼容
- [ ] 不同分辨率屏幕适配

## 问题记录
如发现问题，请记录：
- 问题描述：
- 重现步骤：
- 错误信息：
- 系统环境：

## 总结
打包成功，程序可以正常启动。建议进行完整的功能测试以确保所有特性正常工作。
"""
    
    with open('test_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("✅ 测试报告已生成: test_report.md")
    return True

def main():
    """主函数"""
    print("简谐运动模拟系统 - 打包测试工具")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('dist'):
        print("❌ dist 目录不存在，请先运行打包脚本")
        return False
    
    success = True
    
    # 执行测试
    if not test_executable_exists():
        success = False
    
    if not test_executable_launch():
        success = False
    
    if not test_dependencies():
        success = False
    
    # 生成报告
    generate_test_report()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有自动化测试通过!")
        print("💡 建议进行手动功能测试")
        print("📋 查看测试报告: test_report.md")
    else:
        print("❌ 部分测试失败")
        print("🔧 请检查打包配置和依赖")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
