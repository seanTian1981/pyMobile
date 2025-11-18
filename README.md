# 声景校园 - 无障碍校园导航应用
专为盲人大学生设计的离线校园导航和文字识别应用

## 功能特性
- 🧭 离线校园导航与语音引导
- 📷 实时文字识别与语音朗读
- ♿ 完全无障碍交互界面
- 📱 本地数据存储，无需网络

## 技术栈
- Python 3.8+
- Kivy (跨平台移动UI)
- Tesseract OCR (离线文字识别)
- SQLite (本地数据存储)
- Plyer (设备传感器访问)

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行应用
```bash
python main.py
```

## 项目结构
```
├── app/
│   ├── __init__.py
│   ├── main.py              # 主应用入口
│   ├── navigation/          # 导航模块
│   ├── ocr/                # 文字识别模块
│   ├── ui/                 # 用户界面
│   ├── data/               # 数据管理
│   └── utils/              # 工具函数
├── data/                   # 本地数据文件
├── assets/                 # 资源文件
└── requirements.txt
```

## 开发阶段
- Phase 1: 基础导航和OCR功能
- Phase 2: 无障碍交互优化
- Phase 3: 个性化和高级功能