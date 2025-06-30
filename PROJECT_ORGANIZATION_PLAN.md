# Synthetic Teaching Animation Project - Organization Plan
# 简谐运动教学动画项目 - 组织规划

## Current Issues / 当前问题

1. **Duplicate build artifacts**: Multiple `build/` and `dist/` directories
2. **Scattered documentation**: Documentation files in root directory
3. **Old test files**: Outdated test scripts in root
4. **Mixed content**: Source code, build artifacts, and documentation mixed together
5. **Inconsistent naming**: Mix of English and Chinese file names

## Proposed Organization / 建议的组织结构

```
Synthetic teaching animation of simple harmonic motion/
├── README.md                           # Main project overview
├── LICENSE                            # Project license
├── .gitignore                         # Git ignore file
├── requirements.txt                   # Global dependencies
├── docs/                              # Project documentation
│   ├── project-overview.md           # Project overview
│   ├── development-guide.md          # Development guidelines
│   ├── user-manual/                  # User manuals
│   └── technical/                    # Technical documentation
├── applications/                      # Main applications
│   ├── shm_visualization/            # Core SHM visualization (reorganized)
│   ├── shm_visualization_music/      # Music-enhanced SHM visualization
│   └── audio_analysis/               # Audio analysis tools
├── tools/                            # Development and utility tools
│   ├── launchers/                    # Application launchers
│   ├── build-scripts/                # Build automation
│   └── testing/                      # Testing utilities
├── archive/                          # Archived/legacy files
│   ├── old-builds/                   # Old build artifacts
│   ├── deprecated-scripts/           # Deprecated scripts
│   └── legacy-docs/                  # Legacy documentation
└── assets/                           # Shared project assets
    ├── images/                       # Project images
    ├── videos/                       # Demo videos
    └── documentation/                # Documentation assets
```

## Implementation Steps / 实施步骤

### Phase 1: Create New Structure
1. Create main directories
2. Move applications to `applications/`
3. Consolidate documentation in `docs/`
4. Move tools and utilities to `tools/`

### Phase 2: Archive Old Content
1. Move old build artifacts to `archive/old-builds/`
2. Move deprecated scripts to `archive/deprecated-scripts/`
3. Archive legacy documentation

### Phase 3: Clean Up
1. Remove duplicate files
2. Update references and paths
3. Create comprehensive documentation

### Phase 4: Verification
1. Test all applications work from new locations
2. Verify build processes
3. Update documentation

## Benefits / 好处

1. **Clear separation**: Applications, tools, docs, and archives clearly separated
2. **Reduced duplication**: Eliminate duplicate build artifacts and scripts
3. **Better navigation**: Logical structure makes finding files easier
4. **Professional appearance**: Industry-standard project organization
5. **Easier maintenance**: Clear boundaries make updates simpler
