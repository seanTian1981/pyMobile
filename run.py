#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声景校园应用启动器
处理依赖检查和错误处理
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """检查依赖库"""
    print("正在检查依赖库...")
    
    required_modules = {
        'kivy': 'Kivy UI框架',
        'sqlite3': 'SQLite数据库',
        'plyer': '设备传感器访问',
        'pytesseract': 'OCR文字识别',
        'opencv-python': 'OpenCV图像处理',
        'Pillow': 'PIL图像处理',
        'pyttsx3': '语音合成',
        'numpy': '数值计算',
        'scipy': '科学计算',
    }
    
    optional_modules = {
        'pygame': '音频播放（可选）',
    }
    
    missing_required = []
    missing_optional = []
    
    for module, description in required_modules.items():
        try:
            if module == 'sqlite3':
                import sqlite3
            elif module == 'opencv-python':
                import cv2
            elif module == 'Pillow':
                import PIL
            else:
                __import__(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"✗ {description} - 未安装")
            missing_required.append(module)
    
    for module, description in optional_modules.items():
        try:
            if module == 'pygame':
                import pygame
            else:
                __import__(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"⚠ {description} - 未安装（可选）")
            missing_optional.append(module)
    
    return missing_required, missing_optional


def install_dependencies(missing_modules):
    """提示安装依赖"""
    if not missing_modules:
        return True
    
    print("\n缺少必要的依赖库，请安装：")
    print("pip install -r requirements.txt")
    
    # 生成requirements.txt如果不存在
    requirements_file = project_root / 'requirements.txt'
    if not requirements_file.exists():
        requirements = """
kivy==2.3.0
Pillow==10.1.0
pytesseract==0.3.10
plyer==2.1.0
numpy==1.24.3
scipy==1.11.4
pyttsx3==2.90
opencv-python==4.8.1.78
pygame==2.5.2
        """.strip()
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        print("已生成 requirements.txt 文件")
    
    return False


def setup_tesseract():
    """设置Tesseract OCR"""
    print("\n检查Tesseract OCR...")
    try:
        import pytesseract
        # 尝试运行tesseract
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR 已安装")
        return True
    except Exception as e:
        print("✗ Tesseract OCR 未安装或配置错误")
        print("请安装Tesseract OCR：")
        print("Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi-sim")
        print("Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki")
        print("macOS: brew install tesseract tesseract-lang")
        return False


def check_directories():
    """检查和创建必要的目录"""
    directories = [
        'data',
        'assets/sounds',
        'assets/images',
        'logs'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录 {directory} 已准备")


def run_app():
    """运行应用"""
    print("\n启动声景校园应用...")
    
    try:
        # 设置环境变量
        os.environ['KIVY_WINDOW'] = 'sdl2'
        
        # 导入并运行应用
        from main import SoundscapeCampusApp
        app = SoundscapeCampusApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"\n应用运行出错: {e}")
        print("请检查依赖库是否正确安装")
        return False
    
    return True


def main():
    """主函数"""
    print("声景校园应用启动器")
    print("=" * 40)
    
    # 检查依赖
    missing_required, missing_optional = check_dependencies()
    
    # 安装依赖
    if missing_required:
        if not install_dependencies(missing_required):
            print("\n依赖库安装失败，无法启动应用")
            return False
    
    # 检查Tesseract
    tesseract_ok = setup_tesseract()
    if not tesseract_ok:
        print("警告: OCR功能将不可用")
    
    # 检查目录
    check_directories()
    
    # 运行应用
    success = run_app()
    
    if success:
        print("\n感谢使用声景校园应用！")
    else:
        print("\n应用启动失败，请检查错误信息")
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)