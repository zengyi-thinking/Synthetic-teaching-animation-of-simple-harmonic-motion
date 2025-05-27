# 简谐运动教学仿真系统 / Simple Harmonic Motion Teaching Simulation System

## 简介 / Introduction

本项目是一个基于 PyQt6 和 Matplotlib 的简谐运动教学仿真系统，专为物理教学设计。系统提供三个不同的简谐运动模块，通过交互式动画和实时参数调整，帮助学习者直观理解简谐运动的各种现象。

This project is a Simple Harmonic Motion (SHM) teaching simulation system based on PyQt6 and Matplotlib, designed specifically for physics education. The system provides three different SHM modules with interactive animations and real-time parameter adjustments to help learners intuitively understand various phenomena of simple harmonic motion.

## 功能特点 / Features

### 三个独立模块 / Three Independent Modules:

1. **同向不同频（拍现象）/ Same Direction with Different Frequencies (Beat Phenomenon)**

   - 展示两个频率接近的简谐波叠加产生的拍现象
   - 可视化拍频、拍周期和包络线
   - Demonstrates the beat phenomenon from two waves with close frequencies
   - Visualizes beat frequency, beat period, and envelope curves

2. **同向同频（相位差合成）/ Same Direction with Same Frequency (Phase Composition)**

   - 展示两个相同频率但不同相位的简谐波的合成
   - 通过相量图直观展示合成原理
   - Shows composition of two waves with same frequency but different phases
   - Intuitively demonstrates composition principles using phasor diagrams

3. **垂直简谐运动（李萨如图形）/ Perpendicular Simple Harmonic Motion (Lissajous Figures)**
   - 展示 X 和 Y 方向上不同频率简谐运动合成的李萨如图形
   - 提供多种频率比预设，观察不同比例下的图形变化
   - Displays Lissajous figures from composition of perpendicular SHMs with different frequencies
   - Provides multiple frequency ratio presets to observe pattern changes

### 交互功能 / Interactive Features:

- 实时调整波形参数（振幅、频率、相位）
- 动态观察波形移动和合成效果
- 播放、暂停和重置动画
- 调整动画速度和轨迹长度
- 频率比精确控制
- Real-time adjustment of wave parameters (amplitude, frequency, phase)
- Dynamic observation of wave movement and composition effects
- Play, pause, and reset animations
- Adjust animation speed and trail length
- Precise frequency ratio control

## 系统要求 / System Requirements

- Python 3.9+
- PyQt6
- Matplotlib
- NumPy
- 其他依赖见 requirements.txt / Other dependencies listed in requirements.txt

## 安装与运行 / Installation and Running

1. 克隆仓库 / Clone the repository:

   ```bash
   git clone https://github.com/your-username/shm-teaching-simulation.git
   cd shm-teaching-simulation
   ```

2. 创建虚拟环境 / Create a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. 安装依赖 / Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. 运行程序 / Run the program:
   ```bash
   python shm_visualization/start.py
   ```

## 使用指南 / Usage Guide

1. 启动程序后，选择要运行的模块
2. 使用左侧控制面板调整参数
3. 观察右侧实时动画效果
4. 使用播放控制按钮控制动画

5. After starting the program, select a module to run
6. Use the left control panel to adjust parameters
7. Observe real-time animation effects on the right
8. Use playback control buttons to control the animation

## 技术实现 / Technical Implementation

- 使用 PyQt6 构建用户界面
- 使用 Matplotlib 嵌入动态图形
- 采用 MVC 架构设计，分离 UI、数据和控制逻辑
- 高性能动画渲染，支持实时参数调整

- UI built with PyQt6
- Dynamic graphics embedded using Matplotlib
- MVC architecture design separating UI, data, and control logic
- High-performance animation rendering with real-time parameter adjustment

## 许可证 / License

本项目采用 MIT 许可证 - 详见 LICENSE 文件

This project is licensed under the MIT License - see the LICENSE file for details

## 致谢 / Acknowledgements

- PyQt6 团队提供的优秀 GUI 框架
- Matplotlib 项目提供的强大可视化工具
- The PyQt6 team for the excellent GUI framework
- The Matplotlib project for powerful visualization tools
