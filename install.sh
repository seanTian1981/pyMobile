#!/bin/bash
# 声景校园应用安装脚本

echo "=== 声景校园应用安装程序 ==="
echo

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "检测到Python版本: $python_version"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: pip3 未安装"
    echo "请先安装pip3"
    exit 1
fi

echo "开始安装依赖库..."

# 安装Python依赖
pip3 install -r requirements.txt

# 检查Tesseract OCR
echo "检查Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR 已安装"
else
    echo "⚠ Tesseract OCR 未安装"
    echo "请手动安装Tesseract OCR:"
    echo "Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
    echo "CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi-sim"
    echo "macOS: brew install tesseract tesseract-lang"
fi

# 创建必要目录
echo "创建应用目录..."
mkdir -p data assets/sounds logs

echo
echo "=== 安装完成 ==="
echo "运行应用: python3 run.py"
echo "或直接运行: python3 main.py"
echo
echo "注意事项:"
echo "1. 确保Tesseract OCR已安装以使用文字识别功能"
echo "2. 在移动设备上运行需要安装Kivy的移动版本"
echo "3. GPS功能需要设备支持"