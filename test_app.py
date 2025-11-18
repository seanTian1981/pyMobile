#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声景校园应用测试脚本
用于验证各模块功能是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.data.database import DatabaseManager
from app.utils.accessibility import AccessibilityManager
from app.navigation.navigator import CampusNavigator
from app.ocr.ocr_reader import OCRReader


def test_database():
    """测试数据库功能"""
    print("=== 测试数据库功能 ===")
    
    try:
        db_manager = DatabaseManager()
        
        # 初始化示例数据
        db_manager.initialize_sample_data()
        
        # 测试获取地点
        locations = db_manager.get_locations_by_category()
        print(f"获取到 {len(locations)} 个地点")
        
        for location in locations[:3]:  # 显示前3个地点
            print(f"- {location['name']} ({location['category']})")
        
        # 测试用户设置
        db_manager.save_user_setting("test_key", "test_value")
        value = db_manager.get_user_setting("test_key")
        print(f"用户设置测试: {value}")
        
        print("数据库功能测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"数据库功能测试失败: {e}")
        return False


def test_accessibility():
    """测试无障碍功能"""
    print("\n=== 测试无障碍功能 ===")
    
    try:
        accessibility_manager = AccessibilityManager()
        
        # 测试语音功能（静音模式）
        print("语音功能初始化成功")
        
        # 测试音量设置
        accessibility_manager.set_voice_volume(0.8)
        accessibility_manager.set_voice_rate(180)
        
        # 测试可用语音
        voices = accessibility_manager.get_available_voices()
        print(f"可用语音数量: {len(voices)}")
        
        print("无障碍功能测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"无障碍功能测试失败: {e}")
        return False


def test_navigation():
    """测试导航功能"""
    print("\n=== 测试导航功能 ===")
    
    try:
        db_manager = DatabaseManager()
        accessibility_manager = AccessibilityManager()
        
        # 初始化示例数据
        db_manager.initialize_sample_data()
        
        navigator = CampusNavigator(db_manager, accessibility_manager)
        
        # 测试距离计算
        distance = navigator._calculate_distance(39.9042, 116.4074, 39.9052, 116.4084)
        print(f"距离计算测试: {distance:.2f} 米")
        
        # 测试查找最近地点
        nearest = navigator._find_nearest_location(39.9040, 116.4070)
        if nearest:
            print(f"最近地点: {nearest.name}")
        
        # 测试导航状态
        status = navigator.get_navigation_status()
        print(f"导航状态: {status}")
        
        print("导航功能测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"导航功能测试失败: {e}")
        return False


def test_ocr():
    """测试OCR功能"""
    print("\n=== 测试OCR功能 ===")
    
    try:
        accessibility_manager = AccessibilityManager()
        ocr_reader = OCRReader(accessibility_manager)
        
        # 测试OCR可用性
        available = ocr_reader.is_ocr_available()
        print(f"OCR功能可用: {available}")
        
        # 测试参数设置
        ocr_reader.set_confidence_threshold(70)
        ocr_reader.set_auto_capture_interval(2)
        ocr_reader.set_ocr_languages(['chi_sim'])
        
        print("OCR功能测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"OCR功能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("声景校园应用功能测试")
    print("=" * 50)
    
    # 运行各项测试
    tests = [
        ("数据库功能", test_database),
        ("无障碍功能", test_accessibility),
        ("导航功能", test_navigation),
        ("OCR功能", test_ocr),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("✓ 所有功能测试通过，应用可以正常运行")
        return True
    else:
        print("✗ 部分功能测试失败，请检查依赖库安装")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)