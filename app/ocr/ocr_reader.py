#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR文字识别模块
提供离线文字识别和语音朗读功能
"""

import os
import threading
import time
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("警告: OpenCV 未安装，摄像头功能将不可用")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("警告: Tesseract 未安装，OCR功能将不可用")

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: Pillow 未安装，图像处理功能将不可用")

from app.utils.accessibility import AccessibilityManager


@dataclass
class OCRResult:
    """OCR识别结果数据类"""
    text: str
    confidence: float
    language: str = "zh"
    timestamp: float = 0
    bbox: Optional[List] = None


class OCRReader:
    """OCR文字识别器"""
    
    def __init__(self, accessibility_manager: AccessibilityManager):
        """初始化OCR识别器"""
        self.accessibility_manager = accessibility_manager
        self.is_running = False
        self.camera = None
        self.current_frame = None
        self.last_ocr_result = None
        self.ocr_thread = None
        
        # OCR配置
        self.ocr_languages = ['chi_sim', 'eng']  # 中文简体和英文
        self.confidence_threshold = 60  # 置信度阈值
        self.auto_capture_interval = 3  # 自动捕获间隔（秒）
        self.last_capture_time = 0
        
        # 图像预处理配置
        self.preprocess_config = {
            'resize_factor': 2.0,  # 放大因子
            'blur_kernel': (3, 3),  # 模糊核
            'noise_filter': True,  # 噪声过滤
            'contrast_enhance': 1.5,  # 对比度增强
            'brightness_adjust': 1.2  # 亮度调整
        }
        
        # 初始化组件
        self._initialize_ocr()
        self._initialize_camera()
    
    def _initialize_ocr(self):
        """初始化OCR引擎"""
        if not TESSERACT_AVAILABLE:
            self.accessibility_manager.announce_error("OCR引擎未安装，文字识别功能不可用")
            return
        
        try:
            # 设置Tesseract路径（如果需要）
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # 测试OCR功能
            test_text = pytesseract.image_to_string(
                Image.new('RGB', (100, 50), color='white'),
                lang='eng'
            )
            print("OCR引擎初始化成功")
            
        except Exception as e:
            print(f"OCR引擎初始化失败: {e}")
            self.accessibility_manager.announce_error("OCR引擎初始化失败")
    
    def _initialize_camera(self):
        """初始化摄像头"""
        if not OPENCV_AVAILABLE:
            self.accessibility_manager.announce_error("摄像头模块未安装，文字识别功能不可用")
            return
        
        try:
            # 尝试打开默认摄像头
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                print("摄像头初始化成功")
                # 设置摄像头参数
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
            else:
                print("无法打开摄像头")
                self.accessibility_manager.announce_error("无法打开摄像头")
                self.camera = None
                
        except Exception as e:
            print(f"摄像头初始化失败: {e}")
            self.accessibility_manager.announce_error("摄像头初始化失败")
            self.camera = None
    
    def start_ocr(self):
        """启动OCR功能"""
        if not TESSERACT_AVAILABLE or not OPENCV_AVAILABLE:
            self.accessibility_manager.announce_error("OCR功能不可用，请检查依赖库安装")
            return
        
        if self.is_running:
            self.accessibility_manager.speak("文字识别功能已在运行")
            return
        
        if not self.camera:
            self.accessibility_manager.announce_error("摄像头未初始化")
            return
        
        self.is_running = True
        self.accessibility_manager.speak("文字识别功能已启动，请将摄像头对准文字")
        
        # 启动OCR线程
        self.ocr_thread = threading.Thread(target=self._ocr_worker, daemon=True)
        self.ocr_thread.start()
    
    def stop_ocr(self):
        """停止OCR功能"""
        self.is_running = False
        self.accessibility_manager.speak("文字识别功能已停止")
        
        # 等待线程结束
        if self.ocr_thread and self.ocr_thread.is_alive():
            self.ocr_thread.join(timeout=2.0)
    
    def _ocr_worker(self):
        """OCR工作线程"""
        while self.is_running:
            try:
                # 捕获图像
                ret, frame = self.camera.read()
                if not ret:
                    print("无法捕获图像")
                    time.sleep(0.1)
                    continue
                
                self.current_frame = frame
                
                # 检查是否需要自动OCR
                current_time = time.time()
                if current_time - self.last_capture_time >= self.auto_capture_interval:
                    self._perform_ocr(frame)
                    self.last_capture_time = current_time
                
                time.sleep(0.1)  # 控制帧率
                
            except Exception as e:
                print(f"OCR处理错误: {e}")
                time.sleep(0.5)
    
    def _perform_ocr(self, frame):
        """执行OCR识别"""
        try:
            # 预处理图像
            processed_image = self._preprocess_image(frame)
            
            # 执行OCR
            custom_config = r'--oem 3 --psm 6 -l ' + '+'.join(self.ocr_languages)
            text = pytesseract.image_to_string(
                processed_image,
                config=custom_config
            )
            
            # 获取置信度信息
            data = pytesseract.image_to_data(
                processed_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            if cleaned_text and avg_confidence >= self.confidence_threshold:
                # 创建OCR结果
                ocr_result = OCRResult(
                    text=cleaned_text,
                    confidence=avg_confidence,
                    language='zh',
                    timestamp=time.time()
                )
                
                self.last_ocr_result = ocr_result
                
                # 语音播报识别结果
                self._announce_ocr_result(ocr_result)
                
        except Exception as e:
            print(f"OCR识别失败: {e}")
    
    def _preprocess_image(self, frame):
        """预处理图像以提高OCR准确率"""
        if not PIL_AVAILABLE:
            # 如果PIL不可用，直接返回OpenCV图像
            return frame
        
        try:
            # 转换为PIL图像
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # 放大图像
            if self.preprocess_config['resize_factor'] != 1.0:
                new_size = (
                    int(image.width * self.preprocess_config['resize_factor']),
                    int(image.height * self.preprocess_config['resize_factor'])
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 增强对比度
            if self.preprocess_config['contrast_enhance'] != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(self.preprocess_config['contrast_enhance'])
            
            # 调整亮度
            if self.preprocess_config['brightness_adjust'] != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(self.preprocess_config['brightness_adjust'])
            
            # 转换为灰度图
            image = image.convert('L')
            
            # 去噪
            if self.preprocess_config['noise_filter']:
                image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return frame
    
    def _clean_text(self, text: str) -> str:
        """清理识别的文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        cleaned = ' '.join(text.split())
        
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        import re
        cleaned = re.sub(r'[^\u4e00-\u9fff\w\s.,!?;:()[\]{}"\'-]', '', cleaned)
        
        return cleaned.strip()
    
    def _announce_ocr_result(self, result: OCRResult):
        """语音播报OCR结果"""
        if not result or not result.text:
            return
        
        # 播报识别到的文字
        self.accessibility_manager.speak(f"识别到文字：{result.text}")
        
        # 如果置信度较低，给出提示
        if result.confidence < 80:
            self.accessibility_manager.speak(f"识别置信度{result.confidence:.0f}%，建议重新拍摄")
    
    def capture_and_recognize(self) -> Optional[OCRResult]:
        """手动捕获并识别文字"""
        if not self.camera:
            self.accessibility_manager.announce_error("摄像头未初始化")
            return None
        
        try:
            # 捕获单帧图像
            ret, frame = self.camera.read()
            if not ret:
                self.accessibility_manager.announce_error("无法捕获图像")
                return None
            
            # 执行OCR
            self._perform_ocr(frame)
            
            return self.last_ocr_result
            
        except Exception as e:
            print(f"手动识别失败: {e}")
            self.accessibility_manager.announce_error("文字识别失败")
            return None
    
    def repeat_last_result(self):
        """重复播报最后一次识别结果"""
        if self.last_ocr_result:
            self.accessibility_manager.speak(f"最后一次识别结果：{self.last_ocr_result.text}")
            self.accessibility_manager.speak(f"置信度：{self.last_ocr_result.confidence:.0f}%")
        else:
            self.accessibility_manager.speak("暂无识别结果")
    
    def get_current_frame(self):
        """获取当前摄像头画面"""
        return self.current_frame
    
    def is_ocr_available(self) -> bool:
        """检查OCR功能是否可用"""
        return TESSERACT_AVAILABLE and OPENCV_AVAILABLE and self.camera is not None
    
    def set_ocr_languages(self, languages: List[str]):
        """设置OCR识别语言"""
        self.ocr_languages = languages
        self.accessibility_manager.speak(f"OCR语言已设置为：{', '.join(languages)}")
    
    def set_confidence_threshold(self, threshold: int):
        """设置置信度阈值"""
        self.confidence_threshold = max(0, min(100, threshold))
        self.accessibility_manager.speak(f"置信度阈值已设置为：{self.confidence_threshold}%")
    
    def set_auto_capture_interval(self, interval: int):
        """设置自动捕获间隔"""
        self.auto_capture_interval = max(1, interval)
        self.accessibility_manager.speak(f"自动捕获间隔已设置为：{self.auto_capture_interval}秒")
    
    def cleanup(self):
        """清理资源"""
        self.stop_ocr()
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        print("OCR资源已清理")


# OCR功能演示和测试函数
def demo_ocr_functionality(accessibility_manager):
    """演示OCR功能（用于测试）"""
    ocr_reader = OCRReader(accessibility_manager)
    
    if not ocr_reader.is_ocr_available():
        accessibility_manager.announce_error("OCR功能不可用")
        return
    
    try:
        # 启动OCR
        ocr_reader.start_ocr()
        
        # 等待用户操作
        accessibility_manager.speak("OCR演示已启动，按任意键停止")
        
        # 这里应该等待用户输入，实际应用中通过UI控制
        
    finally:
        # 清理资源
        ocr_reader.cleanup()