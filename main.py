#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声景校园 - 主应用入口
专为盲人大学生设计的无障碍校园导航应用
"""

import sys
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

# 设置窗口配置
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('kivy', 'log_level', 'info')

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_screen import MainScreen
from app.data.database import DatabaseManager
from app.utils.accessibility import AccessibilityManager


class SoundscapeCampusApp(App):
    """声景校园主应用类"""
    
    def __init__(self):
        super().__init__()
        self.title = "声景校园"
        self.db_manager = None
        self.accessibility_manager = None
        
    def build(self):
        """构建应用界面"""
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()
        
        # 初始化无障碍管理器
        self.accessibility_manager = AccessibilityManager()
        
        # 设置窗口属性
        Window.bind(on_keyboards=self._on_keyboard)
        
        # 创建主界面
        main_screen = MainScreen(
            db_manager=self.db_manager,
            accessibility_manager=self.accessibility_manager
        )
        
        # 欢迎语音提示
        self.accessibility_manager.speak("欢迎使用声景校园应用")
        
        return main_screen
    
    def _on_keyboard(self, instance, keyboard, keycode, text, modifiers):
        """键盘事件处理"""
        if keycode == 27:  # ESC键
            self.stop()
        return False
    
    def on_pause(self):
        """应用暂停处理"""
        return True
    
    def on_resume(self):
        """应用恢复处理"""
        self.accessibility_manager.speak("声景校园应用已恢复")


if __name__ == '__main__':
    SoundscapeCampusApp().run()