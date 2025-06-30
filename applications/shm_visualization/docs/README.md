# 简谐运动合成可视化教学系统 / Simple Harmonic Motion Visualization Teaching System

本项目是基于 PyQt6 和 Matplotlib 的简谐运动合成可视化教学系统，用于展示不同类型的简谐运动合成现象。

This project is a Simple Harmonic Motion (SHM) visualization teaching system based on PyQt6 and Matplotlib, designed to demonstrate various types of harmonic motion composition.

## 功能特点 / Features

系统包含三种模式的简谐运动合成展示：

The system includes three modes of harmonic motion composition:

1. **不同向不同频 (Orthogonal SHM)** - 垂直简谐运动合成，生成李萨如图形

   - 可调节 X、Y 两个方向的振幅、角频率和相位
   - 支持多种李萨如图形预设（1:1、1:2、2:3、3:4 等）
   - 实时显示李萨如图形轨迹

   **Orthogonal with Different Frequencies** - Generates Lissajous figures

   - Adjustable amplitude, angular frequency, and phase for X and Y directions
   - Multiple Lissajous figure presets (1:1, 1:2, 2:3, 3:4, etc.)
   - Real-time trajectory display

2. **同向不同频 (Beat Phenomenon)** - 展示拍现象

   - 可调节两个频率接近的简谐运动参数
   - 直观观察拍频和拍周期

   **Same Direction with Different Frequencies** - Demonstrates beat phenomenon

   - Adjustable parameters for two SHM with close frequencies
   - Direct observation of beat frequency and period

3. **同向同频 (Phase Composition)** - 相位差合成

   - 展示相同频率、不同相位的简谐运动合成规律
   - 使用相量图直观理解相位差的影响

   **Same Direction with Same Frequency** - Phase difference composition

   - Demonstrates composition of waves with the same frequency but different phases
   - Uses phasor diagrams for intuitive understanding of phase difference effects

## 系统要求 / System Requirements

- Python 3.8+
- 依赖库 / Dependencies:
  - PyQt6
  - Matplotlib
  - NumPy

## 安装方法 / Installation

1. 克隆或下载本仓库 / Clone or download this repository
2. 安装依赖 / Install dependencies:

```bash
pip install -r requirements.txt
```

## 项目结构 / Project Structure

```
shm_visualization/
├── start.py                    # 主启动器 / Main launcher
├── modules/                    # 核心模块 / Core modules
│   ├── orthogonal_main.py     # 垂直简谐运动模块 / Orthogonal SHM module
│   ├── beat_main.py           # 拍现象模块 / Beat phenomenon module
│   └── phase_main.py          # 相位合成模块 / Phase composition module
├── animations/                 # 动画控制器 / Animation controllers
│   ├── orthogonal_animation.py
│   ├── beat_animation.py
│   └── phase_animation.py
├── ui/                        # 用户界面组件 / UI components
│   ├── ui_framework.py        # UI框架和组件 / UI framework and components
│   └── params_controller.py   # 参数控制器 / Parameter controller
├── utils/                     # 工具函数 / Utility functions
├── tests/                     # 测试文件 / Test files
├── docs/                      # 文档 / Documentation
├── build_scripts/             # 构建脚本 / Build scripts
│   ├── build_app.py          # PyInstaller构建脚本 / PyInstaller build script
│   └── build_fixed.bat       # Windows批处理构建脚本 / Windows batch build script
└── dist/                      # 打包输出目录 / Package output directory
```

## 使用方法 / Usage

### 从源代码运行 / Running from Source Code

启动程序 / Start the program:

```bash
python start.py
```

这将打开启动器界面，您可以选择要运行的模块：
This will open the launcher interface where you can choose which module to run:

或者，您可以直接运行特定模块 / Alternatively, you can directly run a specific module:

```bash
# 不同向不同频（李萨如图形）/ Orthogonal with different frequencies (Lissajous figures)
python -m modules.orthogonal_main

# 同向不同频（拍现象）/ Same direction with different frequencies (Beat phenomenon)
python -m modules.beat_main

# 同向同频（相位差合成）/ Same direction with same frequency (Phase composition)
python -m modules.phase_main
```

### 使用打包版本 / Using Packaged Version

如果您有打包好的可执行文件，直接运行：
If you have the packaged executable, run it directly:

```bash
# Windows
dist/简谐振动的合成演示平台.exe
```

## 界面说明 / Interface Guide

### 控制面板 / Control Panel

- **参数调节 / Parameter Adjustment**: 使用滑块调节简谐运动的振幅、频率和相位参数
- **频率比控制 / Frequency Ratio Control**: 李萨如图形模块中的频率比预设按钮
- **播放控制 / Playback Control**: 播放、暂停、重置按钮控制动画
- **其他控制 / Other Controls**: 调节动画速度、轨迹长度等

### 绘图区域 / Plot Area

- **波形图 / Waveform**: 显示简谐运动波形
- **合成图 / Composite**: 显示合成结果（李萨如图形、拍现象或相位合成）
- **参数显示 / Parameter Display**: 实时显示关键参数信息

## 教学用途 / Educational Purpose

本系统特别适合以下教学场景：

This system is particularly suitable for the following educational scenarios:

- 物理课程中简谐运动合成的演示 / Demonstration of harmonic motion composition in physics courses
- 李萨如图形原理的直观说明 / Visual explanation of Lissajous figure principles
- 拍现象和相位差合成的交互式体验 / Interactive experience of beat phenomenon and phase difference composition
- 简谐运动与相量表示法的关联 / Connection between simple harmonic motion and phasor representation

## 开发指南 / Development Guide

### 运行测试 / Running Tests

```bash
# 测试源代码功能 / Test source code functionality
python tests/test_fixed_app.py

# 测试打包后的应用 / Test packaged application
python tests/test_packaged_app.py
```

### 构建可执行文件 / Building Executable

使用 PyInstaller 构建可执行文件：
Build executable using PyInstaller:

```bash
# 使用 Python 脚本构建 / Build using Python script
python build_scripts/build_app.py

# 或使用批处理脚本（Windows）/ Or use batch script (Windows)
build_scripts/build_fixed.bat
```

### 项目维护 / Project Maintenance

- 所有核心功能模块位于 `modules/` 目录
- UI 组件和框架位于 `ui/` 目录
- 动画控制器位于 `animations/` 目录
- 测试文件位于 `tests/` 目录
- 构建脚本位于 `build_scripts/` 目录

All core functionality modules are in the `modules/` directory
UI components and framework are in the `ui/` directory
Animation controllers are in the `animations/` directory
Test files are in the `tests/` directory
Build scripts are in the `build_scripts/` directory

## 技术特点 / Technical Features

- 基于 PyQt6 构建现代化 UI 界面 / Modern UI built with PyQt6
- 集成 Matplotlib 实现高质量绘图 / High-quality plotting with Matplotlib
- 使用 QPropertyAnimation 实现平滑动画效果 / Smooth animations using QPropertyAnimation
- 深色主题设计，符合现代审美 / Dark theme design that meets modern aesthetics
- 响应式布局，适应不同屏幕尺寸 / Responsive layout for different screen sizes
- 模块化架构，便于维护和扩展 / Modular architecture for easy maintenance and extension
