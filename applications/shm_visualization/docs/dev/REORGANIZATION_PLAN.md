# SHM Visualization Project Reorganization Plan

## Current Structure Analysis

### Issues Identified:
1. **Duplicate files**: Multiple `.spec` files in root and build_scripts
2. **Misplaced files**: Documentation files in root directory
3. **Inconsistent naming**: Mix of English and Chinese file names
4. **Empty directories**: `utils/` directory is essentially empty
5. **Build artifacts**: `build/` and `dist/` directories mixed with source code
6. **Cache files**: `__pycache__` directories throughout the project

### Current Directory Structure:
```
shm_visualization/
├── animations/          # ✅ Good - Animation controllers
├── build/              # ❌ Should be in .gitignore, not tracked
├── build_scripts/      # ✅ Good - Build configuration
├── dist/               # ❌ Should be in .gitignore, not tracked
├── docs/               # ✅ Good - Documentation
├── image/              # ❌ Poor naming, should be assets/images/
├── modules/            # ✅ Good - Main simulation modules
├── tests/              # ✅ Good - Test files
├── ui/                 # ✅ Good - UI components
├── utils/              # ❌ Empty, should be removed or populated
├── *.spec files       # ❌ Duplicates, should be in build_scripts only
├── *.md files          # ❌ Should be in docs/
└── start.py            # ✅ Good - Main entry point
```

## Proposed New Structure

### Target Directory Structure:
```
shm_visualization/
├── src/                    # Source code root
│   ├── shm_visualization/  # Main package
│   │   ├── __init__.py
│   │   ├── main.py         # Renamed from start.py
│   │   ├── animations/     # Animation controllers
│   │   ├── modules/        # Simulation modules
│   │   ├── ui/            # UI components
│   │   └── utils/         # Utility functions (if needed)
├── assets/                 # Static assets
│   ├── icons/             # Application icons
│   └── images/            # Documentation images
├── build/                  # Build scripts and configurations
│   ├── scripts/           # Build automation scripts
│   └── specs/             # PyInstaller spec files
├── docs/                   # Documentation
│   ├── api/               # API documentation
│   ├── user/              # User guides
│   └── dev/               # Developer documentation
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data and fixtures
├── dist/                   # Distribution files (gitignored)
├── .gitignore             # Git ignore file
├── README.md              # Main project README
├── requirements.txt       # Python dependencies
└── setup.py               # Package setup (optional)
```

## Implementation Steps

### Phase 1: Create New Directory Structure
1. Create `src/shm_visualization/` as main package directory
2. Create `assets/` with subdirectories
3. Reorganize `build_scripts/` into `build/`
4. Create proper `docs/` structure

### Phase 2: Move and Reorganize Files
1. Move source code to `src/shm_visualization/`
2. Move assets to `assets/`
3. Consolidate documentation in `docs/`
4. Clean up duplicate and obsolete files

### Phase 3: Update References
1. Update import statements
2. Update build scripts
3. Update test files
4. Update documentation

### Phase 4: Verification
1. Test source code execution
2. Test build process
3. Run test suite
4. Verify packaged application

## Benefits of New Structure

1. **Clear Separation**: Source code, assets, docs, and build files clearly separated
2. **Standard Layout**: Follows Python packaging best practices
3. **Scalability**: Easy to add new modules and components
4. **Maintainability**: Logical organization makes code easier to find and modify
5. **Professional**: Industry-standard project structure
