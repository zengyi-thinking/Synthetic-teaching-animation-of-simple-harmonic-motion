#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for SHM Visualization System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]
else:
    requirements = [
        "PyQt6>=6.0.0",
        "matplotlib>=3.5.0", 
        "numpy>=1.20.0",
    ]

setup(
    name="shm-visualization",
    version="1.0.0",
    description="Simple Harmonic Motion Visualization System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SHM Visualization Team",
    author_email="",
    url="https://github.com/your-org/shm-visualization",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "build": [
            "PyInstaller>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shm-visualization=shm_visualization.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
