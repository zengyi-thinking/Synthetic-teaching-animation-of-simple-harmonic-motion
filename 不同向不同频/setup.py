#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="lissajous_demo",
    version="1.0.0",
    description="李萨如图形 - 不同向不同频简谐振动合成演示",
    author="Physics Demo",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
    ],
    python_requires=">=3.6",
) 