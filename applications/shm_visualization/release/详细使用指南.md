# SHM Visualization System - Usage Guide
# 简谐运动可视化系统 - 使用指南

## Quick Start / 快速开始

### Running the Application / 运行应用程序

To run the application directly:
要直接运行应用程序：

```bash
python run.py
```

### Installation / 安装

#### Development Mode / 开发模式
```bash
pip install -e .
```

#### Normal Installation / 正常安装
```bash
pip install .
```

#### From Requirements / 从需求文件安装
```bash
pip install -r requirements.txt
```

## About setup.py / 关于 setup.py

The `setup.py` file is a setuptools configuration file for package installation, not meant for direct execution.
`setup.py` 文件是用于包安装的 setuptools 配置文件，不是用于直接执行的。

If you run `python setup.py` without arguments, you'll get a "no commands supplied" error. This is normal behavior.
如果您运行 `python setup.py` 而不带参数，您会得到"no commands supplied"错误。这是正常行为。

## Project Structure / 项目结构

- `run.py` - Main entry point / 主入口点
- `setup.py` - Package installation configuration / 包安装配置
- `pyproject.toml` - Modern Python project configuration / 现代Python项目配置
- `src/shm_visualization/` - Main application code / 主应用程序代码
- `requirements.txt` - Dependencies / 依赖项

## Troubleshooting / 故障排除

### Import Errors / 导入错误
If you get import errors, try installing in development mode:
如果遇到导入错误，请尝试以开发模式安装：

```bash
pip install -e .
```

### GUI Issues / GUI问题
Make sure you have PyQt6 installed:
确保已安装 PyQt6：

```bash
pip install PyQt6
```

### Dependencies / 依赖项
Install all required dependencies:
安装所有必需的依赖项：

```bash
pip install -r requirements.txt
```
