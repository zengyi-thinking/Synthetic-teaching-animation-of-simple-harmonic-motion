# Import Resolution Guide for SHM Visualization
# SHM可视化导入解析指南

## Problem Description / 问题描述

After the project reorganization, Pylance (VS Code's Python language server) was unable to resolve imports for the `shm_visualization` package, even though the application ran correctly at runtime.

项目重组后，Pylance（VS Code的Python语言服务器）无法解析`shm_visualization`包的导入，尽管应用程序在运行时正确执行。

**Error**: `无法解析导入"shm_visualization.main"Pylance(reportMissingImports)`

## Root Cause / 根本原因

The issue occurred because:

1. **Dynamic Path Addition**: The `run.py` script dynamically added the `src/` directory to `sys.path` at runtime
2. **Static Analysis Limitation**: Pylance performs static analysis and couldn't see the dynamic path changes
3. **Package Structure**: The reorganized `src/` layout wasn't recognized by the IDE

问题发生的原因：

1. **动态路径添加**：`run.py`脚本在运行时动态添加`src/`目录到`sys.path`
2. **静态分析限制**：Pylance执行静态分析，无法看到动态路径更改
3. **包结构**：重组的`src/`布局未被IDE识别

## Solution Implemented / 实施的解决方案

### 1. Package Installation in Development Mode / 开发模式包安装

**Created**: `pyproject.toml` and `setup.py` for proper package configuration
**Command**: `pip install -e .`

This makes the package available system-wide while keeping it editable for development.

**创建**：`pyproject.toml`和`setup.py`用于正确的包配置
**命令**：`pip install -e .`

这使得包在系统范围内可用，同时保持开发时的可编辑性。

### 2. VS Code Configuration / VS Code配置

**Created**: `.vscode/settings.json` with:
```json
{
    "python.analysis.extraPaths": ["./src"],
    "python.analysis.autoSearchPaths": true,
    "python.analysis.include": ["./src/**"]
}
```

This tells Pylance where to find the package sources.

**创建**：`.vscode/settings.json`，告诉Pylance在哪里找到包源代码。

### 3. Modern Python Package Structure / 现代Python包结构

**Files Created**:
- `pyproject.toml` - Modern Python package configuration
- `setup.py` - Backward compatibility setup script
- Proper `__init__.py` files in all package directories

**创建的文件**：
- `pyproject.toml` - 现代Python包配置
- `setup.py` - 向后兼容的设置脚本
- 所有包目录中的正确`__init__.py`文件

### 4. Updated Entry Point / 更新的入口点

**Modified**: `run.py` to:
1. Try importing the installed package first
2. Fall back to development mode if needed
3. Provide clear error messages

**修改**：`run.py`以：
1. 首先尝试导入已安装的包
2. 如果需要，回退到开发模式
3. 提供清晰的错误消息

## Verification Steps / 验证步骤

### 1. Check Package Installation / 检查包安装
```bash
pip list | grep shm-visualization
# Should show: shm-visualization 1.0.0
```

### 2. Test Direct Import / 测试直接导入
```python
from shm_visualization.main import main
print("✅ Import successful!")
```

### 3. Test Application Launch / 测试应用程序启动
```bash
python run.py
# Should start without import errors
```

### 4. Check Pylance Resolution / 检查Pylance解析
- Open `run.py` in VS Code
- The import `from shm_visualization.main import main as app_main` should not show errors
- Intellisense should work for the imported modules

## Benefits of This Solution / 此解决方案的好处

### 1. IDE Integration / IDE集成
- ✅ Pylance can resolve all imports
- ✅ Intellisense works correctly
- ✅ Go-to-definition works
- ✅ Auto-completion works

### 2. Development Workflow / 开发工作流程
- ✅ Package is editable (changes reflect immediately)
- ✅ No need to modify PYTHONPATH manually
- ✅ Works in any Python environment
- ✅ Compatible with virtual environments

### 3. Distribution / 分发
- ✅ Package can be built with standard tools
- ✅ Can be uploaded to PyPI if needed
- ✅ Proper dependency management
- ✅ Entry points defined for command-line usage

### 4. Maintenance / 维护
- ✅ Follows Python packaging best practices
- ✅ Compatible with modern Python tools
- ✅ Clear project structure
- ✅ Proper metadata and configuration

## Troubleshooting / 故障排除

### If Imports Still Don't Work / 如果导入仍然不工作

1. **Reinstall in development mode**:
   ```bash
   pip uninstall shm-visualization
   pip install -e .
   ```

2. **Check VS Code Python interpreter**:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the correct Python environment

3. **Reload VS Code window**:
   - Press `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

4. **Clear Pylance cache**:
   - Press `Ctrl+Shift+P`
   - Type "Python: Clear Cache and Reload Window"

### If Package Installation Fails / 如果包安装失败

1. **Check Python version**: Ensure Python 3.8+ is being used
2. **Update pip**: `python -m pip install --upgrade pip`
3. **Check dependencies**: Ensure PyQt6, matplotlib, numpy are available

## Future Maintenance / 未来维护

### Adding New Modules / 添加新模块
1. Create the module in the appropriate `src/shm_visualization/` subdirectory
2. Add `__init__.py` if creating a new package
3. The module will be automatically available after saving

### Updating Dependencies / 更新依赖
1. Update `requirements.txt`
2. Update `pyproject.toml` dependencies section
3. Reinstall: `pip install -e .`

### Building for Distribution / 构建分发
```bash
# Build wheel
python -m build

# Install from wheel
pip install dist/shm_visualization-1.0.0-py3-none-any.whl
```

## Conclusion / 结论

This solution provides a robust, maintainable approach to package management that:
- Resolves IDE import issues
- Follows Python best practices
- Maintains development flexibility
- Enables proper distribution

此解决方案提供了一种强大、可维护的包管理方法，它：
- 解决IDE导入问题
- 遵循Python最佳实践
- 保持开发灵活性
- 支持正确的分发
