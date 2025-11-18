#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无障碍功能管理模块
提供语音合成、屏幕阅读器支持等无障碍功能
"""

import threading
import queue
import time
import os
from typing import Optional, Callable
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("警告: pyttsx3 未安装，语音功能将不可用")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("警告: pygame 未安装，音频反馈将不可用")


class AccessibilityManager:
    """无障碍功能管理器"""
    
    def __init__(self):
        """初始化无障碍管理器"""
        self.tts_engine = None
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        self.voice_rate = 150  # 语速
        self.voice_volume = 0.9  # 音量
        
        self._initialize_tts()
        self._start_speech_thread()
        
        # 音效文件路径
        self.sound_files = {
            'beep': os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds', 'beep.wav'),
            'success': os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds', 'success.wav'),
            'error': os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds', 'error.wav'),
            'navigation_start': os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds', 'nav_start.wav'),
            'navigation_end': os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds', 'nav_end.wav')
        }
        
        if PYGAME_AVAILABLE:
            self._initialize_audio()
    
    def _initialize_tts(self):
        """初始化语音合成引擎"""
        if not TTS_AVAILABLE:
            return
            
        try:
            self.tts_engine = pyttsx3.init()
            
            # 设置语音参数
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # 优先选择中文语音
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # 如果没有中文语音，使用第一个可用语音
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
        except Exception as e:
            print(f"语音合成引擎初始化失败: {e}")
            self.tts_engine = None
    
    def _initialize_audio(self):
        """初始化音频系统"""
        if not PYGAME_AVAILABLE:
            return
            
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # 创建音效目录
            sounds_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds')
            os.makedirs(sounds_dir, exist_ok=True)
            
            # 生成简单的音效文件（如果不存在）
            self._generate_simple_sounds(sounds_dir)
            
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
    
    def _generate_simple_sounds(self, sounds_dir: str):
        """生成简单的音效文件"""
        if not PYGAME_AVAILABLE:
            return
            
        # 这里应该生成实际的音频文件，现在先创建占位符
        for sound_name in self.sound_files.keys():
            sound_path = os.path.join(sounds_dir, f"{sound_name}.wav")
            if not os.path.exists(sound_path):
                # 创建一个空的音频文件作为占位符
                with open(sound_path, 'w') as f:
                    f.write("# 音效文件占位符")
    
    def _start_speech_thread(self):
        """启动语音播放线程"""
        if self.speech_thread is None or not self.speech_thread.is_alive():
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
    
    def _speech_worker(self):
        """语音播放工作线程"""
        while True:
            try:
                text, priority = self.audio_queue.get(timeout=0.1)
                if text is None:  # 停止信号
                    break
                
                self.is_speaking = True
                self._speak_text(text)
                self.is_speaking = False
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"语音播放错误: {e}")
                self.is_speaking = False
    
    def _speak_text(self, text: str):
        """实际播放语音"""
        if not self.tts_engine:
            print(f"[语音] {text}")
            return
            
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"语音播放失败: {e}")
    
    def speak(self, text: str, priority: int = 0, interrupt: bool = False):
        """语音播报文本
        
        Args:
            text: 要播报的文本
            priority: 优先级（数字越大优先级越高）
            interrupt: 是否中断当前播放
        """
        if not text:
            return
            
        if interrupt and self.is_speaking:
            # 清空队列并中断当前播放
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            if self.tts_engine:
                self.tts_engine.stop()
        
        # 将语音任务加入队列
        self.audio_queue.put((text, priority))
    
    def speak_immediately(self, text: str):
        """立即播报（高优先级）"""
        self.speak(text, priority=10, interrupt=True)
    
    def stop_speaking(self):
        """停止语音播放"""
        if self.tts_engine:
            self.tts_engine.stop()
        
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.is_speaking = False
    
    def play_sound(self, sound_name: str):
        """播放音效"""
        if not PYGAME_AVAILABLE or sound_name not in self.sound_files:
            return
            
        sound_path = self.sound_files[sound_name]
        if os.path.exists(sound_path):
            try:
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"音效播放失败: {e}")
    
    def set_voice_rate(self, rate: int):
        """设置语音速度"""
        self.voice_rate = max(50, min(400, rate))  # 限制在合理范围内
        if self.tts_engine:
            self.tts_engine.setProperty('rate', self.voice_rate)
    
    def set_voice_volume(self, volume: float):
        """设置语音音量"""
        self.voice_volume = max(0.0, min(1.0, volume))  # 限制在0-1范围内
        if self.tts_engine:
            self.tts_engine.setProperty('volume', self.voice_volume)
    
    def get_available_voices(self) -> list:
        """获取可用的语音列表"""
        if not self.tts_engine:
            return []
        
        voices = []
        for voice in self.tts_engine.getProperty('voices'):
            voices.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': voice.gender
            })
        return voices
    
    def set_voice(self, voice_id: str):
        """设置语音"""
        if self.tts_engine:
            self.tts_engine.setProperty('voice', voice_id)
    
    def announce_screen_change(self, screen_name: str):
        """播报屏幕切换信息"""
        self.speak(f"已切换到{screen_name}界面")
    
    def announce_button_focus(self, button_name: str):
        """播报按钮焦点信息"""
        self.speak(f"{button_name}按钮")
    
    def announce_list_item(self, item_text: str, index: int, total: int):
        """播报列表项信息"""
        self.speak(f"第{index}项，共{total}项：{item_text}")
    
    def announce_navigation_instruction(self, instruction: str, distance: float = None):
        """播报导航指令"""
        if distance:
            self.speak(f"{instruction}，距离{distance:.0f}米")
        else:
            self.speak(instruction)
    
    def announce_arrival(self, destination: str):
        """播报到达信息"""
        self.play_sound('navigation_end')
        self.speak(f"已到达{destination}")
    
    def announce_error(self, error_message: str):
        """播报错误信息"""
        self.play_sound('error')
        self.speak(f"错误：{error_message}")
    
    def announce_success(self, success_message: str):
        """播报成功信息"""
        self.play_sound('success')
        self.speak(success_message)
    
    def cleanup(self):
        """清理资源"""
        self.stop_speaking()
        
        # 发送停止信号给语音线程
        self.audio_queue.put((None, 0))
        
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass