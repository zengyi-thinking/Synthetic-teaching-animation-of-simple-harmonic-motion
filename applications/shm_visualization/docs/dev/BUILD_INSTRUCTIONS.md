# SHM Visualization PyInstaller Build Instructions

# 简谐运动可视化系统 PyInstaller 构建说明

This document provides comprehensive instructions for building a standalone executable (.exe) file for the SHM Visualization application using PyInstaller.

## 📋 Prerequisites / 前置要求

### System Requirements / 系统要求

- **Operating System**: Windows 10/11 (64-bit recommended)
- **Python**: 3.8 or higher (tested with Python 3.13.1)
- **RAM**: At least 4GB (8GB recommended for building)
- **Disk Space**: At least 2GB free space for build process

### Required Dependencies / 必需依赖

```bash
pip install PyInstaller>=6.0
pip install PyQt6>=6.4.0
pip install matplotlib>=3.5.0
pip install numpy>=1.22.0
pip install jaraco.text
pip install more-itertools
pip install zipp
pip install importlib-metadata
```

### Quick Install All Dependencies / 快速安装所有依赖

```bash
pip install PyInstaller PyQt6 matplotlib numpy jaraco.text more-itertools zipp importlib-metadata
```

## 🚀 Quick Build / 快速构建

### Option 1: Automated Build Script (Recommended)

```bash
cd applications/shm_visualization
python build_executable.py
```

### Option 2: Manual PyInstaller Command

```bash
cd applications/shm_visualization
pyinstaller --clean shm_visualization.spec
```

## 📁 Project Structure / 项目结构

```
applications/shm_visualization/
├── run.py                          # Main entry point
├── shm_visualization.spec          # PyInstaller specification file
├── build_executable.py             # Automated build script
├── src/
│   └── shm_visualization/
│       ├── __init__.py
│       ├── main.py                 # Application launcher
│       ├── ui/
│       │   ├── ui_framework.py     # UI components
│       │   └── params_controller.py
│       ├── modules/
│       │   ├── beat_main.py        # Beat phenomenon module
│       │   ├── orthogonal_main.py  # Lissajous figures module
│       │   └── phase_main.py       # Phase difference module
│       └── animations/
│           ├── beat_animation.py
│           ├── orthogonal_animation.py
│           └── phase_animation.py
├── assets/
│   └── icons/
│       └── gui_waveform_icon_157544.ico
└── dist/                           # Generated executable location
    └── SHM_Visualization.exe
```

## 🔧 Build Process Details / 构建过程详情

### Step 1: Dependency Installation / 步骤 1：安装依赖

```bash
# Install all required packages
pip install -r requirements.txt
pip install PyInstaller

# Verify installations
python -c "import PyInstaller; print(f'PyInstaller: {PyInstaller.__version__}')"
python -c "import PyQt6; print('PyQt6: OK')"
python -c "import matplotlib; print(f'matplotlib: {matplotlib.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
```

### Step 2: Run Build Script / 步骤 2：运行构建脚本

```bash
python build_executable.py
```

The build script will:

1. ✅ Check Python version compatibility
2. ✅ Verify all dependencies are installed
3. ✅ Validate project structure
4. ✅ Test application imports
5. ✅ Clean previous build directories
6. ✅ Run PyInstaller with optimized settings
7. ✅ Test the generated executable

### Step 3: Locate Executable / 步骤 3：定位可执行文件

After successful build:

- **Executable location**: `dist/SHM_Visualization.exe`
- **File size**: ~110 MB
- **Dependencies**: All bundled (no external requirements)

## 🧪 Testing the Executable / 测试可执行文件

### Basic Test / 基本测试

```bash
# Test executable startup
.\dist\SHM_Visualization.exe
```

### Comprehensive Test / 综合测试

1. **Launch Application**: Double-click `SHM_Visualization.exe`
2. **Test Main Interface**: Verify the launcher window opens
3. **Test Navigation**: Click each module button:
   - 李萨如图形 (Lissajous Figures)
   - 拍现象 (Beat Phenomenon)
   - 相位差合成 (Phase Difference)
4. **Test Window Resizing**: Drag window corners to resize
5. **Test Module Functionality**: Verify simulations run correctly

## 📦 Distribution / 分发

### Single File Distribution / 单文件分发

The generated `SHM_Visualization.exe` is a standalone executable that:

- ✅ Contains all Python dependencies
- ✅ Includes all PyQt6 libraries
- ✅ Bundles matplotlib and numpy
- ✅ Contains all application modules
- ✅ Includes assets and icons
- ✅ Requires no Python installation on target systems

### System Requirements for End Users / 最终用户系统要求

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 200MB free space
- **No additional software required**

## 🔍 Troubleshooting / 故障排除

### Common Issues / 常见问题

#### Issue 1: "PyInstaller not found"

```bash
# Solution:
pip install PyInstaller
```

#### Issue 2: "PyQt6 import error"

```bash
# Solution:
pip install PyQt6 PyQt6-Qt6 PyQt6-sip
```

#### Issue 3: "Module not found during build"

```bash
# Solution: Check that all modules are in src/shm_visualization/
# Verify project structure matches the expected layout
```

#### Issue 4: "Executable won't start"

```bash
# Solution: Run from command line to see error messages
cd dist
SHM_Visualization.exe
```

#### Issue 5: "Missing DLL errors"

```bash
# Solution: Ensure all dependencies are installed in the build environment
pip install --upgrade PyQt6 matplotlib numpy
```

#### Issue 6: "ModuleNotFoundError: No module named 'jaraco.text'"

```bash
# This error occurs during PyInstaller packaging
# Solution: Install missing jaraco dependencies
pip install jaraco.text more-itertools zipp importlib-metadata

# Then rebuild the executable
python build_executable.py
```

### Build Optimization / 构建优化

#### Reduce Executable Size / 减小可执行文件大小

```bash
# Edit shm_visualization.spec and add more excludes:
excludes=[
    'tkinter', 'unittest', 'test', 'distutils',
    'setuptools', 'pip', 'email', 'html', 'http',
    'urllib', 'xml', 'pydoc'
]
```

#### Debug Build Issues / 调试构建问题

```bash
# Run PyInstaller with debug output
pyinstaller --clean --debug=all shm_visualization.spec
```

## 📝 Build Script Features / 构建脚本功能

The `build_executable.py` script provides:

- ✅ **Automated dependency checking**
- ✅ **Project structure validation**
- ✅ **Application testing before build**
- ✅ **Clean build environment**
- ✅ **Comprehensive error reporting**
- ✅ **Build time measurement**
- ✅ **Executable validation**

## 🎯 Advanced Configuration / 高级配置

### Custom Icon / 自定义图标

The build uses the icon from `assets/icons/gui_waveform_icon_157544.ico`. To change:

1. Replace the icon file
2. Update the path in `shm_visualization.spec`

### Console Mode / 控制台模式

To enable console output for debugging:

```python
# In shm_visualization.spec, change:
console=False  # to
console=True
```

### Additional Data Files / 额外数据文件

To include additional files:

```python
# In shm_visualization.spec, add to datas:
datas=[
    ('path/to/your/file', 'destination/in/exe'),
    # ... existing entries
]
```

## ✅ Success Indicators / 成功指标

A successful build should show:

- ✅ All dependency checks pass
- ✅ Project structure validation passes
- ✅ Application test passes
- ✅ PyInstaller completes without errors
- ✅ Executable file is created (~110 MB)
- ✅ Executable starts without errors
- ✅ All three simulation modules work

## 📞 Support / 支持

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all dependencies are correctly installed
3. Ensure project structure is intact
4. Run the build script for detailed error reporting

---

**Build Time**: ~5-6 minutes on modern hardware
**Final Executable**: `dist/SHM_Visualization.exe` (~110 MB)
**Compatibility**: Windows 10/11 (64-bit)
