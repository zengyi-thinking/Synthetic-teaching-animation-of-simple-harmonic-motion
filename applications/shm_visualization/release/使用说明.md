# Simple Harmonic Motion Visualization System
# 简谐运动可视化系统

A PyQt6-based educational physics simulation application for visualizing simple harmonic motion phenomena.

一个基于PyQt6的教育物理仿真应用程序，用于可视化简谐运动现象。

## Features / 功能特性

- **Orthogonal SHM (Lissajous Figures)** - Visualization of perpendicular harmonic motions with different frequencies
- **Beat Phenomenon** - Observation of beats from two waves with close frequencies  
- **Phase Composition** - Study of phase difference effects in same-frequency waves

- **垂直简谐运动（李萨如图形）** - 不同频率垂直简谐运动的可视化
- **拍现象** - 观察两个频率接近的波的拍现象
- **相位合成** - 研究相同频率波的相位差效应

## Project Structure / 项目结构

```
shm_visualization/
├── src/                        # Source code / 源代码
│   └── shm_visualization/      # Main package / 主包
│       ├── __init__.py
│       ├── main.py            # Application entry point / 应用入口
│       ├── animations/        # Animation controllers / 动画控制器
│       ├── modules/           # Simulation modules / 仿真模块
│       ├── ui/               # User interface components / 用户界面组件
│       └── utils/            # Utility functions / 工具函数
├── assets/                    # Static assets / 静态资源
│   ├── icons/                # Application icons / 应用图标
│   └── images/               # Documentation images / 文档图片
├── build/                     # Build configuration / 构建配置
│   ├── scripts/              # Build automation scripts / 构建自动化脚本
│   └── specs/                # PyInstaller spec files / PyInstaller配置文件
├── docs/                      # Documentation / 文档
│   ├── api/                  # API documentation / API文档
│   ├── user/                 # User guides / 用户指南
│   └── dev/                  # Developer documentation / 开发者文档
├── tests/                     # Test suite / 测试套件
│   ├── unit/                 # Unit tests / 单元测试
│   ├── integration/          # Integration tests / 集成测试
│   └── fixtures/             # Test data and fixtures / 测试数据和固件
├── dist/                      # Distribution files (gitignored) / 分发文件
├── run.py                     # Main entry script / 主入口脚本
├── requirements.txt           # Python dependencies / Python依赖
└── README.md                  # This file / 本文件
```

## Installation / 安装

### Prerequisites / 前置要求

- Python 3.8 or higher / Python 3.8或更高版本
- PyQt6
- matplotlib
- numpy

### Setup / 设置

1. Clone the repository / 克隆仓库:
```bash
git clone <repository-url>
cd shm_visualization
```

2. Install dependencies / 安装依赖:
```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Running from Source / 从源代码运行

```bash
python run.py
```

### Building Executable / 构建可执行文件

```bash
python build/scripts/build_reorganized.py
```

The executable will be created in the `dist/` directory.
可执行文件将在`dist/`目录中创建。

### Running Tests / 运行测试

```bash
# Unit tests / 单元测试
python -m pytest tests/unit/

# Integration tests / 集成测试  
python -m pytest tests/integration/

# All tests / 所有测试
python -m pytest tests/
```

## Development / 开发

### Adding New Modules / 添加新模块

1. Create new module file in `src/shm_visualization/modules/`
2. Create corresponding animation controller in `src/shm_visualization/animations/`
3. Update the main launcher to include the new module
4. Add tests in `tests/unit/` and `tests/integration/`

### Code Organization / 代码组织

- **modules/**: Main simulation modules, each implementing a specific physics phenomenon
- **animations/**: Animation controllers that handle the mathematical calculations and timing
- **ui/**: Reusable UI components and frameworks
- **utils/**: Utility functions and helpers

## Architecture / 架构

The application follows a modular architecture with clear separation of concerns:

- **Presentation Layer**: PyQt6 UI components
- **Business Logic**: Physics calculations and simulations
- **Animation Layer**: Real-time animation controllers
- **Data Layer**: Parameter management and state handling

## Contributing / 贡献

1. Follow the existing code structure and naming conventions
2. Add appropriate tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License / 许可证

[Add your license information here]

## Contact / 联系方式

[Add contact information here]
