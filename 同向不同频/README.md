# 简谐振动合成模拟

这个项目使用 Python 和 Matplotlib 创建了一个交互式简谐振动合成模拟器。你可以通过调整两个简谐振动的参数（振幅、角频率和初相位）来观察它们的合成效果。

## 功能

- 分别显示两个简谐振动
- 实时显示振动的合成波形
- 允许通过滑块调整振动参数
- 包括播放、暂停和重置功能
- 支持保存视频（需要 FFmpeg）

## 系统要求

- Python 3.6+
- 依赖包：numpy, matplotlib
- 可选：FFmpeg（用于保存视频）

## 快速开始

1. 安装 Python 依赖：

   ```
   pip install -r requirements.txt
   ```

2. 安装 FFmpeg（可选，用于保存视频）：

   ```
   python install_ffmpeg.py
   ```

   如果自动安装失败，请手动安装 FFmpeg：

   - 访问 https://ffmpeg.org/download.html 下载
   - 将其添加到系统 PATH 中

3. 运行模拟程序：
   ```
   python main.py
   ```

## 使用说明

- 上部图表显示第一个简谐振动
- 中部图表显示第二个简谐振动
- 下部图表显示合成振动（绿色）
- 使用左侧的滑块调整各振动的参数：
  - A: 振幅
  - w: 角频率
  - p: 初相位
- 使用按钮控制播放：
  - Play: 开始播放
  - Pause: 暂停播放
  - Reset: 重置所有参数

## 文件说明

- main.py: 主程序文件
- install_ffmpeg.py: FFmpeg 安装助手
- requirements.txt: Python 依赖列表
