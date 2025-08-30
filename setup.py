"""
PostureFix - Setup Script
Uygulamayı dağıtım için paketleme
"""

from setuptools import setup, find_packages
import os
import sys

# Sürüm bilgisi
VERSION = "1.0.0"
DESCRIPTION = "Akıllı Postür Düzeltme Uygulaması"
LONG_DESCRIPTION = """
PostureFix, bilgisayar başında çalışan kişiler için geliştirilmiş 
akıllı postür izleme ve düzeltme uygulamasıdır. MediaPipe ve OpenCV 
teknolojilerini kullanarak gerçek zamanlı postür analizi yapar.
"""

# README dosyasını oku
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return LONG_DESCRIPTION

# Requirements dosyasını oku
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except:
        return []

# Veri dosyalarını bul
def find_data_files():
    data_files = []
    
    # Assets klasörü
    if os.path.exists("assets"):
        for root, dirs, files in os.walk("assets"):
            if files:
                data_files.append((root, [os.path.join(root, f) for f in files]))
    
    return data_files

setup(
    name="posturefix",
    version=VERSION,
    author="PostureFix Team",
    author_email="support@posturefix.com",
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/posturefix/PostureFix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="posture, health, computer vision, mediapipe, opencv, wellness, ergonomics",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-qt>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "gpu": [
            "tensorflow-gpu>=2.13.0",
            "torch>=2.0.1+cu118",
        ],
        "audio": [
            "pygame>=2.5.0",
            "pydub>=0.25.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "posturefix=main:main",
        ],
        "gui_scripts": [
            "posturefix-gui=main:main",
        ]
    },
    data_files=find_data_files(),
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yml", "*.yaml"],
        "assets": ["*"],
        "gui/styles": ["*.qss", "*.css"],
    },
    zip_safe=False,
    platforms=["Windows", "Linux", "macOS"],
    project_urls={
        "Bug Reports": "https://github.com/posturefix/PostureFix/issues",
        "Source": "https://github.com/posturefix/PostureFix",
        "Documentation": "https://docs.posturefix.com",
        "Funding": "https://github.com/sponsors/posturefix",
    },
)
