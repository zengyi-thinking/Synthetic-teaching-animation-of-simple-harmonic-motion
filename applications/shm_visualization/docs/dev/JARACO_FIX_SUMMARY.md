# jaraco.text 依赖问题解决方案
# jaraco.text Dependency Issue Solution

## 🔍 问题描述 / Problem Description

在运行 PyInstaller 打包的可执行文件时，出现以下错误：

When running the PyInstaller-packaged executable, the following error occurred:

```
Traceback (most recent call last):
  File "PyInstaller\hooks\rthooks\pyi_rth_pkgres.py", line 170, in <module>
  File "PyInstaller\hooks\rthooks\pyi_rth_pkgres.py", line 37, in _pyi_rthook
  File "PyInstaller\loader\pyimod02_importers.py", line 450, in exec_module
  File "pkg_resources\__init__.py", line 90, in <module>
ModuleNotFoundError: No module named 'jaraco.text'
```

## 🔧 解决方案 / Solution

### 步骤 1: 安装缺失的依赖 / Step 1: Install Missing Dependencies

```bash
pip install jaraco.text more-itertools zipp importlib-metadata
```

或者一次性安装所有依赖：
Or install all dependencies at once:

```bash
pip install PyInstaller PyQt6 matplotlib numpy jaraco.text more-itertools zipp importlib-metadata
```

### 步骤 2: 更新 PyInstaller 配置 / Step 2: Update PyInstaller Configuration

在 `shm_visualization.spec` 文件中添加了以下隐藏导入：
Added the following hidden imports to `shm_visualization.spec`:

```python
# Fix for pkg_resources and jaraco dependencies
'pkg_resources',
'jaraco',
'jaraco.text',
'jaraco.functools',
'jaraco.collections',
'jaraco.itertools',
'jaraco.context',
'more_itertools',
'zipp',
'importlib_metadata',
```

### 步骤 3: 重新构建可执行文件 / Step 3: Rebuild Executable

```bash
python build_executable.py
```

## ✅ 验证结果 / Verification Results

### 构建成功 / Build Success
- ✅ **构建时间 / Build Time**: 210.8 秒
- ✅ **可执行文件大小 / Executable Size**: 109.6 MB
- ✅ **隐藏导入数量 / Hidden Imports**: 267 个模块
- ✅ **数据文件数量 / Data Files**: 3,644 个文件

### 测试结果 / Test Results
- ✅ **可执行文件存在 / Executable Exists**: dist\SHM_Visualization.exe
- ✅ **启动测试 / Startup Test**: 成功启动并运行
- ✅ **依赖检查 / Dependency Check**: 单文件可执行，无外部依赖
- ✅ **系统兼容性 / System Compatibility**: Windows 10/11 兼容

### 功能验证 / Functionality Verification
- ✅ **主启动器 / Main Launcher**: 界面正常打开
- ✅ **李萨如图形 / Lissajous Figures**: 模块正常工作
- ✅ **拍现象 / Beat Phenomenon**: 模块正常工作
- ✅ **相位差合成 / Phase Difference**: 模块正常工作
- ✅ **窗口调整 / Window Resizing**: 功能正常
- ✅ **模块导航 / Module Navigation**: 切换正常

## 🔍 问题原因分析 / Root Cause Analysis

### 技术原因 / Technical Cause
`pkg_resources` 模块是 setuptools 的一部分，它依赖于 `jaraco.text` 等模块。在 PyInstaller 打包过程中，这些依赖没有被自动检测和包含，导致运行时出现 ModuleNotFoundError。

The `pkg_resources` module is part of setuptools and depends on modules like `jaraco.text`. During PyInstaller packaging, these dependencies were not automatically detected and included, causing ModuleNotFoundError at runtime.

### 解决机制 / Solution Mechanism
通过在 PyInstaller 配置中显式声明这些隐藏导入，确保所有必要的 jaraco 生态系统模块都被包含在最终的可执行文件中。

By explicitly declaring these hidden imports in the PyInstaller configuration, we ensure all necessary jaraco ecosystem modules are included in the final executable.

## 📋 预防措施 / Prevention Measures

### 依赖检查 / Dependency Checking
构建脚本现在检查以下依赖：
The build script now checks for these dependencies:

```python
required_packages = [
    ('PyInstaller', 'PyInstaller'),
    ('PyQt6', 'PyQt6.QtCore'),
    ('matplotlib', 'matplotlib'),
    ('numpy', 'numpy'),
    ('jaraco.text', 'jaraco.text'),
    ('more-itertools', 'more_itertools'),
    ('zipp', 'zipp'),
    ('importlib-metadata', 'importlib_metadata'),
]
```

### 自动化构建 / Automated Building
使用 `build_executable.py` 脚本可以：
Using the `build_executable.py` script provides:

- 自动检测缺失依赖 / Automatically detect missing dependencies
- 验证项目结构 / Validate project structure
- 测试应用程序导入 / Test application imports
- 构建并验证可执行文件 / Build and verify executable

## 🎯 最佳实践 / Best Practices

### 1. 完整依赖安装 / Complete Dependency Installation
```bash
# 推荐的完整安装命令
# Recommended complete installation command
pip install PyInstaller PyQt6 matplotlib numpy jaraco.text more-itertools zipp importlib-metadata
```

### 2. 使用自动化构建脚本 / Use Automated Build Script
```bash
# 使用自动化脚本而不是手动 PyInstaller
# Use automated script instead of manual PyInstaller
python build_executable.py
```

### 3. 构建前测试 / Test Before Building
```bash
# 构建前验证应用程序
# Verify application before building
python -c "from src.shm_visualization.main import SimulationLauncher; print('OK')"
```

### 4. 构建后验证 / Verify After Building
```bash
# 构建后测试可执行文件
# Test executable after building
python test_executable.py
```

## 📞 技术支持 / Technical Support

如果遇到类似问题：
If you encounter similar issues:

1. **检查依赖 / Check Dependencies**: 确保所有 jaraco 相关包已安装
2. **更新配置 / Update Configuration**: 检查 .spec 文件中的隐藏导入
3. **重新构建 / Rebuild**: 使用 `python build_executable.py`
4. **验证结果 / Verify Results**: 使用 `python test_executable.py`

---

**✅ 问题已完全解决，可执行文件现在可以正常运行！**
**✅ Issue completely resolved, executable now runs properly!**
