#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声景校园应用演示脚本
展示应用的主要功能和结构
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_app_structure():
    """显示应用结构"""
    print("=== 声景校园应用结构 ===")
    print("""
声景校园/
├── main.py                 # 主应用入口
├── run.py                  # 启动器脚本
├── test_app.py            # 测试脚本
├── install.sh             # 安装脚本
├── requirements.txt       # 依赖列表
├── README.md              # 项目说明
├── DEVELOPMENT.md         # 开发文档
├── USER_MANUAL.md         # 用户手册
├── .gitignore             # Git忽略文件
├── app/                   # 应用主目录
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   ├── data/              # 数据管理模块
│   │   ├── __init__.py
│   │   └── database.py    # 数据库管理
│   ├── navigation/        # 导航模块
│   │   ├── __init__.py
│   │   └── navigator.py   # 校园导航器
│   ├── ocr/              # OCR模块
│   │   ├── __init__.py
│   │   └── ocr_reader.py # 文字识别器
│   ├── ui/               # 用户界面模块
│   │   ├── __init__.py
│   │   └── main_screen.py # 主界面
│   └── utils/            # 工具模块
│       ├── __init__.py
│       └── accessibility.py # 无障碍管理
├── data/                 # 数据目录
│   └── campus.db         # 校园数据库
└── assets/               # 资源目录
    ├── sounds/           # 音效文件
    └── images/           # 图片资源
    """)

def show_features():
    """显示主要功能"""
    print("\n=== 主要功能特性 ===")
    features = [
        "🧭 离线校园导航",
        "   • 预存校园地图数据",
        "   • GPS定位和路径规划", 
        "   • 语音引导和方向提示",
        "",
        "📷 OCR文字识别",
        "   • 实时摄像头文字识别",
        "   • 中英文识别支持",
        "   • 自动语音朗读",
        "",
        "♿ 无障碍交互",
        "   • 完整屏幕阅读器支持",
        "   • 键盘快捷键操作",
        "   • 语音反馈所有操作",
        "   • 大按钮高对比度界面",
        "",
        "💾 本地数据存储",
        "   • SQLite数据库",
        "   • 无需网络连接",
        "   • 用户设置和历史记录"
    ]
    
    for feature in features:
        print(feature)

def show_tech_stack():
    """显示技术栈"""
    print("\n=== 技术栈 ===")
    tech_stack = [
        "开发语言: Python 3.8+",
        "UI框架: Kivy 2.3.0 (跨平台)",
        "数据库: SQLite 3",
        "OCR引擎: Tesseract",
        "图像处理: OpenCV + Pillow",
        "语音合成: pyttsx3",
        "传感器访问: Plyer",
        "数值计算: NumPy + SciPy"
    ]
    
    for tech in tech_stack:
        print(f"• {tech}")

def show_installation():
    """显示安装说明"""
    print("\n=== 安装说明 ===")
    print("1. 环境要求:")
    print("   • Python 3.8+")
    print("   • Tesseract OCR")
    print("   • pip3")
    print()
    print("2. 安装步骤:")
    print("   • git clone <repository>")
    print("   • cd soundscape-campus")
    print("   • ./install.sh")
    print("   • python3 run.py")
    print()
    print("3. 依赖安装:")
    print("   • pip3 install -r requirements.txt")
    print("   • sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")

def show_usage():
    """显示使用方法"""
    print("\n=== 使用方法 ===")
    print("启动应用:")
    print("  python3 run.py")
    print()
    print("快捷键:")
    print("  N - 校园导航")
    print("  O - 文字识别")
    print("  P - 常用地点")
    print("  S - 设置")
    print("  H - 帮助")
    print("  Q - 退出")
    print()
    print("测试功能:")
    print("  python3 test_app.py")

def main():
    """主函数"""
    print("声景校园应用演示")
    print("=" * 50)
    
    show_app_structure()
    show_features()
    show_tech_stack()
    show_installation()
    show_usage()
    
    print("\n" + "=" * 50)
    print("更多信息请查看:")
    print("• README.md - 项目概述")
    print("• DEVELOPMENT.md - 开发文档")
    print("• USER_MANUAL.md - 用户手册")
    print()
    print("声景校园 - 让校园生活更无障碍")

if __name__ == '__main__':
    main()