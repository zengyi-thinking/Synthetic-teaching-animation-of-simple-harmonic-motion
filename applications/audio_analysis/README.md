# Audio Analyzer - Harmonic Motion Teaching Tool

A professional audio analysis application designed for teaching harmonic motion and Fourier analysis concepts.

## 🎯 Overview

This audio analyzer provides an intuitive way to understand complex audio signals by decomposing them into harmonic components. Perfect for physics, mathematics, and music education.

### Key Features

- **Audio Loading & Analysis** - Support for common audio formats
- **Frequency Decomposition** - Break down complex signals into harmonic components
- **Interactive Visualization** - Real-time waveform, spectrum, and component displays
- **Parameter Control** - Adjust component amplitudes and observe effects
- **Audio Reconstruction** - Synthesize audio from modified components
- **Playback Comparison** - Compare original and reconstructed audio

## 📁 Project Structure

```
audio_analysis/
├── 📄 Core Application Files
│   ├── run_audio_analyzer.py      # Main application entry point
│   ├── audio_editor_ui.py         # User interface components
│   ├── audio_player.py            # Audio playback functionality
│   ├── audio_processor.py         # Audio processing utilities
│   ├── frequency_analyzer.py      # Frequency analysis engine
│   ├── requirements.txt           # Python dependencies
│   └── 启动音频分析器.bat         # Windows launcher
│
├── 📁 tests/                      # Test files and verification scripts
│   ├── test_audio_analysis.py     # Core functionality tests
│   ├── test_final_fixes.py        # Fix verification tests
│   ├── test_sine_wave_display.py  # Waveform display tests
│   ├── test_ui_fixes.py           # UI functionality tests
│   ├── test_ui_improvements.py    # UI enhancement tests
│   ├── demo_audio_analysis.py     # Demo and example usage
│   └── demo_report.txt            # Demo results
│
├── 📁 docs/                       # Documentation
│   ├── FINAL_FIXES_COMPLETE.md    # Complete fix documentation
│   └── PROJECT_SUMMARY.md         # Project overview
│
├── 📁 utils/                      # Utility scripts
│   ├── generate_sample_audio.py   # Sample audio generator
│   └── install_dependencies.py    # Dependency installer
│
└── 📁 sample_audio/               # Sample audio files
    ├── A4_440Hz.wav               # Pure A4 tone
    ├── C_major_chord.wav          # C major chord
    ├── complex_harmonics.wav      # Complex harmonic signal
    ├── beat_frequency_demo.wav    # Beat frequency demonstration
    └── ... (more sample files)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (recommended)

### Installation

1. **Clone or download the project**

   ```bash
   cd audio_analysis
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or use the automated installer:

   ```bash
   python utils/install_dependencies.py
   ```

3. **Launch the application**
   ```bash
   python run_audio_analyzer.py
   ```
   Or double-click `启动音频分析器.bat` on Windows

### Basic Usage

1. **Load Audio** → Click "加载音频文件" to load an audio file
2. **Analyze** → Click "开始频率分析" to decompose the signal
3. **Explore** → Use checkboxes and sliders to modify components
4. **Listen** → Play original and reconstructed audio to compare
5. **Save** → Export the reconstructed audio if desired

## 🎓 Educational Applications

### Physics Education

- **Harmonic Motion** - Visualize how complex motions decompose into simple harmonics
- **Wave Superposition** - Demonstrate how waves add constructively and destructively
- **Fourier Analysis** - Show practical applications of Fourier transforms

### Mathematics Education

- **Signal Processing** - Introduce concepts of frequency domain analysis
- **Trigonometry** - Connect sine waves to mathematical functions
- **Data Analysis** - Demonstrate real-world data processing techniques

### Music Education

- **Harmony Analysis** - Understand chord structures and overtones
- **Timbre Studies** - Explore what makes instruments sound different
- **Audio Engineering** - Learn about digital audio processing

## 🔧 Technical Details

### Core Components

| File                    | Purpose                                               |
| ----------------------- | ----------------------------------------------------- |
| `audio_editor_ui.py`    | Main GUI with waveform displays and controls          |
| `frequency_analyzer.py` | FFT-based frequency analysis and component extraction |
| `audio_player.py`       | Cross-platform audio playback with threading          |
| `audio_processor.py`    | Audio I/O, format conversion, and preprocessing       |

### Key Technologies

- **PyQt6** - Modern cross-platform GUI framework
- **NumPy/SciPy** - High-performance numerical computing
- **Matplotlib** - Professional scientific plotting
- **librosa** - Advanced audio analysis library
- **sounddevice** - Real-time audio I/O

### Features

- ✅ **Clean Waveform Display** - Optimized rendering for clear visualization
- ✅ **Intelligent Downsampling** - Maintains visual clarity for large files
- ✅ **Real-time Parameter Control** - Immediate feedback on component changes
- ✅ **Professional Audio Quality** - High-fidelity processing throughout
- ✅ **Robust Error Handling** - Graceful handling of edge cases

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python tests/test_audio_analysis.py      # Core functionality
python tests/test_final_fixes.py         # Recent fixes
python tests/test_ui_improvements.py     # UI enhancements
```

## 📚 Documentation

- **[Complete Fix Documentation](docs/FINAL_FIXES_COMPLETE.md)** - Detailed technical fixes
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Comprehensive project overview

## 🛠️ Development

### Adding New Features

1. Core functionality goes in the main directory
2. Tests go in `tests/` with descriptive names
3. Utilities go in `utils/`
4. Document changes in `docs/`

### Code Style

- Follow PEP 8 conventions
- Use descriptive variable names
- Add docstrings for public methods
- Include error handling for user-facing functions

## 🐛 Troubleshooting

### Common Issues

**Audio playback not working:**

- Check system audio settings
- Verify audio device connections
- Try different sample rates

**Slow analysis performance:**

- Use shorter audio files for testing
- Close other CPU-intensive applications
- Consider reducing analysis resolution

**Display issues:**

- Update graphics drivers
- Check Python/library versions
- Try different display scaling settings

### Getting Help

1. Check the documentation in `docs/`
2. Run the test suite to identify issues
3. Review error messages in the console output

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.
