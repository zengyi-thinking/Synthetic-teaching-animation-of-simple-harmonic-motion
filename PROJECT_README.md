# Synthetic Teaching Animation of Simple Harmonic Motion
# 简谐运动合成教学动画系统

A comprehensive educational platform for visualizing and understanding simple harmonic motion phenomena through interactive animations, simulations, and audio analysis tools.

一个全面的教育平台，通过交互式动画、仿真和音频分析工具来可视化和理解简谐运动现象。

## 🎯 Project Overview / 项目概述

This project provides a suite of educational applications designed to help students and educators understand the principles of simple harmonic motion through:

- **Interactive Visualizations**: Real-time animations of harmonic motion phenomena
- **Audio Analysis**: Tools for analyzing harmonic content in audio signals
- **Educational Interface**: User-friendly interfaces designed for teaching environments
- **Comprehensive Documentation**: Detailed guides and technical documentation

本项目提供一套教育应用程序，旨在帮助学生和教育工作者通过以下方式理解简谐运动原理：

- **交互式可视化**：简谐运动现象的实时动画
- **音频分析**：分析音频信号中谐波内容的工具
- **教育界面**：为教学环境设计的用户友好界面
- **全面文档**：详细的指南和技术文档

## 📁 Project Structure / 项目结构

```
Synthetic teaching animation of simple harmonic motion/
├── PROJECT_README.md                 # This comprehensive guide / 本综合指南
├── README.md                         # Original project README / 原始项目README
├── LICENSE                          # Project license / 项目许可证
├── requirements.txt                 # Global dependencies / 全局依赖
├── applications/                    # Main applications / 主要应用程序
│   ├── shm_visualization/          # Core SHM visualization / 核心SHM可视化
│   ├── shm_visualization_music/    # Music-enhanced SHM / 音乐增强SHM
│   └── audio_analysis/             # Audio analysis tools / 音频分析工具
├── docs/                           # Documentation / 文档
│   ├── user-manual/               # User guides / 用户指南
│   ├── technical/                 # Technical documentation / 技术文档
│   └── development/               # Development guides / 开发指南
├── tools/                          # Development tools / 开发工具
│   ├── launchers/                 # Application launchers / 应用启动器
│   ├── build-scripts/             # Build automation / 构建自动化
│   └── testing/                   # Testing utilities / 测试工具
├── assets/                         # Project assets / 项目资源
│   ├── images/                    # Images and diagrams / 图像和图表
│   ├── videos/                    # Demo videos / 演示视频
│   └── documentation/             # Documentation assets / 文档资源
└── archive/                        # Archived content / 归档内容
    ├── old-builds/                # Legacy build artifacts / 旧构建产物
    ├── deprecated-scripts/        # Deprecated scripts / 废弃脚本
    └── legacy-docs/               # Legacy documentation / 旧文档
```

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置要求
- Python 3.8 or higher / Python 3.8或更高版本
- PyQt6
- matplotlib
- numpy

### Installation / 安装

1. **Clone the repository / 克隆仓库**:
   ```bash
   git clone <repository-url>
   cd "Synthetic teaching animation of simple harmonic motion"
   ```

2. **Install dependencies / 安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run applications / 运行应用程序**:
   ```bash
   # Core SHM Visualization / 核心SHM可视化
   cd applications/shm_visualization
   python run.py
   
   # Music-Enhanced SHM / 音乐增强SHM
   cd applications/shm_visualization_music
   python run.py
   
   # Audio Analysis / 音频分析
   cd applications/audio_analysis
   python run_audio_analyzer.py
   ```

## 📱 Applications / 应用程序

### 1. SHM Visualization / SHM可视化
**Location**: `applications/shm_visualization/`

Core educational tool for visualizing simple harmonic motion with three main modules:
- **Orthogonal Motion**: Lissajous figures and perpendicular harmonic motions
- **Beat Phenomenon**: Visualization of beats from interfering waves
- **Phase Composition**: Study of phase relationships in harmonic motion

核心教育工具，用于可视化简谐运动，包含三个主要模块：
- **垂直运动**：李萨如图形和垂直简谐运动
- **拍现象**：干涉波的拍现象可视化
- **相位合成**：简谐运动中相位关系的研究

### 2. SHM Visualization Music / SHM音乐可视化
**Location**: `applications/shm_visualization_music/`

Enhanced version with audio synthesis and harmonic analysis capabilities.
具有音频合成和谐波分析功能的增强版本。

### 3. Audio Analysis / 音频分析
**Location**: `applications/audio_analysis/`

Standalone audio analysis tool for examining harmonic content in audio files.
用于检查音频文件中谐波内容的独立音频分析工具。

## 🛠️ Development / 开发

### Building Applications / 构建应用程序

Each application can be built into standalone executables:

```bash
# Build SHM Visualization
cd applications/shm_visualization
python build/scripts/build_reorganized.py

# Build other applications
cd applications/shm_visualization_music
python build_files/build_app.py
```

### Testing / 测试

```bash
# Run tests for specific applications
cd applications/shm_visualization
python -m pytest tests/

# Use testing tools
cd tools/testing
python test_improvements.py
```

## 📚 Documentation / 文档

- **User Manual**: `docs/user-manual/` - End-user guides and tutorials
- **Technical Docs**: `docs/technical/` - Technical specifications and API documentation  
- **Development**: `docs/development/` - Development guides and contribution guidelines

- **用户手册**：`docs/user-manual/` - 最终用户指南和教程
- **技术文档**：`docs/technical/` - 技术规范和API文档
- **开发文档**：`docs/development/` - 开发指南和贡献准则

## 🏗️ Recent Reorganization / 最近的重组

The project has been recently reorganized to improve maintainability and follow best practices:

- **Modular Structure**: Applications separated into distinct directories
- **Clean Documentation**: Organized documentation hierarchy
- **Archived Legacy**: Old files moved to archive for reference
- **Professional Layout**: Industry-standard project organization

项目最近进行了重组，以提高可维护性并遵循最佳实践：

- **模块化结构**：应用程序分离到不同目录
- **清晰文档**：有组织的文档层次结构
- **归档遗留**：旧文件移至归档以供参考
- **专业布局**：行业标准项目组织

## 🤝 Contributing / 贡献

1. Follow the project structure and organization guidelines
2. Add appropriate tests for new functionality
3. Update documentation as needed
4. Ensure all applications build and run correctly

1. 遵循项目结构和组织准则
2. 为新功能添加适当的测试
3. 根据需要更新文档
4. 确保所有应用程序正确构建和运行

## 📄 License / 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 📞 Contact / 联系方式

For questions, suggestions, or contributions, please refer to the documentation in the `docs/` directory.

如有问题、建议或贡献，请参阅`docs/`目录中的文档。
