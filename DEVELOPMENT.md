# 声景校园应用开发文档

## 项目概述

声景校园是一款专为盲人大学生设计的无障碍手机应用，提供离线校园导航和文字识别功能。应用完全支持屏幕阅读器，所有操作都有语音反馈。

## 系统架构

### 核心模块

1. **数据管理模块** (`app/data/`)
   - `database.py`: SQLite数据库管理，存储地点、路径、用户设置等数据
   - 支持离线数据存储，无需网络连接

2. **导航模块** (`app/navigation/`)
   - `navigator.py`: 校园导航和路径规划
   - 支持GPS定位和语音引导
   - 离线地图数据和路径计算

3. **OCR模块** (`app/ocr/`)
   - `ocr_reader.py`: 文字识别和语音朗读
   - 集成Tesseract OCR引擎
   - 支持中英文识别

4. **用户界面模块** (`app/ui/`)
   - `main_screen.py`: 主界面和交互逻辑
   - 完全无障碍设计，支持键盘导航
   - 大按钮和高对比度配色

5. **工具模块** (`app/utils/`)
   - `accessibility.py`: 无障碍功能管理
   - 语音合成和屏幕阅读器支持

## 技术规格

### 开发环境
- Python 3.8+
- Kivy 2.3.0 (跨平台UI框架)
- SQLite 3 (本地数据存储)

### 核心依赖
- `kivy`: 跨平台移动UI框架
- `pytesseract`: OCR文字识别
- `opencv-python`: 图像处理和摄像头访问
- `pyttsx3`: 语音合成
- `plyer`: 设备传感器访问
- `Pillow`: 图像处理

### 可选依赖
- `pygame`: 音效播放
- `scipy`: 科学计算
- `numpy`: 数值计算

## 安装和运行

### 1. 环境准备
```bash
# 安装Python 3.8+
sudo apt-get install python3 python3-pip

# 安装Tesseract OCR (必需)
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 克隆项目
git clone <repository-url>
cd soundscape-campus
```

### 2. 安装依赖
```bash
# 使用安装脚本
./install.sh

# 或手动安装
pip3 install -r requirements.txt
```

### 3. 运行应用
```bash
# 使用启动器（推荐）
python3 run.py

# 或直接运行
python3 main.py
```

## 功能特性

### 校园导航系统
- **离线地图**: 预存校园建筑位置信息
- **语音引导**: 实时转向和距离提示
- **GPS定位**: 使用设备传感器精确定位
- **路径规划**: 计算最优无障碍路径
- **历史记录**: 保存常用路线

### 文字识别系统
- **实时OCR**: 摄像头实时文字识别
- **多语言支持**: 中英文识别
- **语音朗读**: 自动朗读识别结果
- **图像预处理**: 提高识别准确率
- **置信度评估**: 智能过滤低质量结果

### 无障碍交互
- **屏幕阅读器**: 完全兼容主流屏幕阅读器
- **键盘导航**: 全键盘操作支持
- **语音反馈**: 所有操作都有语音提示
- **大按钮界面**: 适合视力障碍用户
- **高对比度**: 清晰的视觉设计

## 数据结构

### 数据库表结构

#### locations（地点表）
```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    description TEXT,
    accessible_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### routes（路径表）
```sql
CREATE TABLE routes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    start_location_id INTEGER,
    end_location_id INTEGER,
    waypoints TEXT,
    distance REAL,
    estimated_time INTEGER,
    is_accessible BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_settings（用户设置表）
```sql
CREATE TABLE user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 开发指南

### 添加新地点
```python
from app.data.database import DatabaseManager

db = DatabaseManager()
db.add_location(
    name="新教学楼",
    category="教学楼",
    latitude=39.9042,
    longitude=116.4074,
    description="新建的教学楼",
    accessible_features="电梯,盲道,无障碍卫生间"
)
```

### 添加新路径
```python
waypoints = [
    {"lat": 39.9042, "lng": 116.4074, "instruction": "从起点出发"},
    {"lat": 39.9047, "lng": 116.4079, "instruction": "向北直行100米"},
    {"lat": 39.9052, "lng": 116.4084, "instruction": "到达终点"}
]

db.add_route(
    name="新路径",
    start_location_id=1,
    end_location_id=2,
    waypoints=waypoints,
    distance=150.0,
    estimated_time=120,
    is_accessible=True
)
```

### 自定义语音反馈
```python
from app.utils.accessibility import AccessibilityManager

accessibility = AccessibilityManager()
accessibility.speak("自定义语音提示")
accessibility.announce_navigation_instruction("前方右转", 50)
accessibility.announce_arrival("图书馆")
```

## 测试

### 运行测试
```bash
python3 test_app.py
```

### 测试覆盖
- 数据库操作测试
- 无障碍功能测试
- 导航算法测试
- OCR功能测试

## 移动端部署

### Android部署
1. 安装Buildozer: `pip install buildozer`
2. 初始化: `buildozer init`
3. 配置buildozer.spec
4. 构建: `buildozer android debug`

### iOS部署
1. 使用kivy-ios工具链
2. 配置Xcode项目
3. 编译和部署

## 性能优化

### 数据库优化
- 使用索引加速查询
- 批量操作减少IO
- 定期清理历史数据

### 图像处理优化
- 降低图像分辨率
- 使用ROI（感兴趣区域）
- 异步处理避免阻塞

### 内存优化
- 及时释放大对象
- 使用生成器处理大数据
- 监控内存使用

## 故障排除

### 常见问题

**Q: OCR识别不准确**
A: 检查光照条件，调整摄像头角度，确保文字清晰

**Q: GPS定位不准确**
A: 检查设备GPS设置，确保在开阔区域使用

**Q:语音不播放**
A: 检查系统音量设置，确认TTS引擎正常工作

**Q:应用启动失败**
A: 检查依赖库安装，查看错误日志

### 日志分析
```bash
# 查看应用日志
tail -f logs/app.log

# 查看OCR日志
tail -f logs/ocr.log

# 查看导航日志
tail -f logs/navigation.log
```

## 贡献指南

### 代码规范
- 使用PEP 8编码规范
- 添加类型提示
- 编写单元测试
- 添加文档注释

### 提交流程
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目地址: https://github.com/seanTian1981/pyMobile
- 问题反馈: 通过GitHub Issues
- 邮箱: [项目维护者邮箱]

---

**声景校园** - 让校园生活更无障碍