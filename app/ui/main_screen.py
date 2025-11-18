#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主界面模块
提供应用的主要用户界面，支持无障碍交互
"""

import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from app.navigation.navigator import CampusNavigator
from app.cr.ocr_reader import OCRReader
from app.utils.accessibility import AccessibilityManager


class AccessibleButton(Button):
    """无障碍按钮类"""
    
    def __init__(self, text: str, accessibility_manager: AccessibilityManager, 
                 on_press_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.accessibility_manager = accessibility_manager
        self.on_press_callback = on_press_callback
        
        # 设置无障碍友好的样式
        self.font_size = '20sp'
        self.size_hint_y = None
        self.height = 80
        self.background_color = (0.2, 0.6, 0.9, 1)
        self.color = (1, 1, 1, 1)
        
        # 绑定焦点事件
        self.bind(on_press=self._on_press)
        self.bind(on_enter=self._on_enter)
        self.bind(on_leave=self._on_leave)
    
    def _on_press(self, instance):
        """按钮按下事件"""
        self.accessibility_manager.announce_button_focus(self.text)
        if self.on_press_callback:
            self.on_press_callback()
    
    def _on_enter(self, instance):
        """鼠标进入事件"""
        self.accessibility_manager.announce_button_focus(self.text)
        self.background_color = (0.3, 0.7, 1.0, 1)
    
    def _on_leave(self, instance):
        """鼠标离开事件"""
        self.background_color = (0.2, 0.6, 0.9, 1)


class MainScreen(Screen):
    """主屏幕类"""
    
    def __init__(self, db_manager=None, accessibility_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.db_manager = db_manager
        self.accessibility_manager = accessibility_manager
        
        # 初始化功能模块
        self.navigator = CampusNavigator(db_manager, accessibility_manager)
        self.ocr_reader = OCRReader(accessibility_manager)
        
        # 设置屏幕背景
        self._setup_background()
        
        # 创建主布局
        self._create_main_layout()
        
        # 绑定键盘事件
        self._bind_keyboard_events()
    
    def _setup_background(self):
        """设置背景"""
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # 浅灰色背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        """更新背景矩形"""
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def _create_main_layout(self):
        """创建主布局"""
        # 主容器
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title_label = Label(
            text='声景校园',
            font_size='32sp',
            size_hint_y=None,
            height=60,
            color=(0.1, 0.1, 0.1, 1),
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # 功能按钮网格
        button_grid = GridLayout(cols=2, spacing=15, size_hint_y=None)
        button_grid.bind(minimum_height=button_grid.setter('height'))
        
        # 导航按钮
        nav_button = AccessibleButton(
            text='校园导航\n(按N键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._open_navigation
        )
        button_grid.add_widget(nav_button)
        
        # OCR文字识别按钮
        ocr_button = AccessibleButton(
            text='文字识别\n(按O键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._open_ocr
        )
        button_grid.add_widget(ocr_button)
        
        # 常用地点按钮
        places_button = AccessibleButton(
            text='常用地点\n(按P键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._open_places
        )
        button_grid.add_widget(places_button)
        
        # 设置按钮
        settings_button = AccessibleButton(
            text='设置\n(按S键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._open_settings
        )
        button_grid.add_widget(settings_button)
        
        # 帮助按钮
        help_button = AccessibleButton(
            text='帮助\n(按H键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._open_help
        )
        button_grid.add_widget(help_button)
        
        # 退出按钮
        exit_button = AccessibleButton(
            text='退出\n(按Q键)',
            accessibility_manager=self.accessibility_manager,
            on_press_callback=self._exit_app
        )
        button_grid.add_widget(exit_button)
        
        # 将按钮网格放入滚动视图
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(button_grid)
        main_layout.add_widget(scroll_view)
        
        # 状态栏
        self.status_label = Label(
            text='准备就绪。请选择功能或按快捷键。',
            font_size='16sp',
            size_hint_y=None,
            height=40,
            color=(0.3, 0.3, 0.3, 1),
            text_size=(Window.width - 40, None)
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
        
        # 初始化示例数据
        if self.db_manager:
            self.db_manager.initialize_sample_data()
    
    def _bind_keyboard_events(self):
        """绑定键盘事件"""
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
    
    def _on_keyboard_closed(self):
        """键盘关闭事件"""
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """键盘按下事件"""
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        
        # 快捷键映射
        shortcuts = {
            'n': self._open_navigation,
            'o': self._open_ocr,
            'p': self._open_places,
            's': self._open_settings,
            'h': self._open_help,
            'q': self._exit_app,
            'escape': self._exit_app
        }
        
        if key.lower() in shortcuts:
            shortcuts[key.lower()]()
            return True
        
        return False
    
    def _open_navigation(self):
        """打开导航功能"""
        self.accessibility_manager.speak("正在打开校园导航功能")
        self.navigator.start_navigation()
        self._update_status("导航功能已启动")
    
    def _open_ocr(self):
        """打开OCR文字识别"""
        self.accessibility_manager.speak("正在打开文字识别功能")
        self.ocr_reader.start_ocr()
        self._update_status("文字识别功能已启动")
    
    def _open_places(self):
        """打开常用地点"""
        self.accessibility_manager.speak("正在打开常用地点列表")
        self._show_places_list()
    
    def _open_settings(self):
        """打开设置"""
        self.accessibility_manager.speak("正在打开设置界面")
        self._show_settings()
    
    def _open_help(self):
        """打开帮助"""
        self.accessibility_manager.speak("正在打开帮助信息")
        self._show_help()
    
    def _exit_app(self):
        """退出应用"""
        self.accessibility_manager.speak("正在退出应用")
        App.get_running_app().stop()
    
    def _show_places_list(self):
        """显示常用地点列表"""
        if not self.db_manager:
            self.accessibility_manager.announce_error("数据库未初始化")
            return
        
        locations = self.db_manager.get_locations_by_category()
        if not locations:
            self.accessibility_manager.speak("暂无可用地点")
            return
        
        # 按类别分组显示地点
        categories = {}
        for location in locations:
            category = location['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(location)
        
        # 语音播报可用地点
        self.accessibility_manager.speak(f"找到{len(locations)}个地点")
        for i, (category, places) in enumerate(categories.items()):
            self.accessibility_manager.speak(f"{category}：{len(places)}个地点")
            for place in places:
                self.accessibility_manager.speak(f"- {place['name']}")
        
        self._update_status(f"已加载{len(locations)}个地点")
    
    def _show_settings(self):
        """显示设置界面"""
        settings_info = """
        设置选项：
        1. 语音速度调节
        2. 音量控制
        3. 导航偏好设置
        4. 无障碍模式配置
        """
        self.accessibility_manager.speak(settings_info)
        self._update_status("设置界面已打开")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
        声景校园使用帮助：
        
        快捷键：
        N - 打开校园导航
        O - 打开文字识别
        P - 查看常用地点
        S - 打开设置
        H - 播放帮助信息
        Q - 退出应用
        
        导航功能：
        选择目的地后，应用将提供语音引导
        
        文字识别：
        将摄像头对准文字，应用会自动识别并朗读
        
        无障碍支持：
        应用完全支持屏幕阅读器，所有操作都有语音反馈
        """
        self.accessibility_manager.speak(help_text)
        self._update_status("帮助信息已显示")
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.text = message
        self.accessibility_manager.speak(message)
    
    def on_enter(self):
        """进入屏幕时调用"""
        self.accessibility_manager.announce_screen_change("主界面")
    
    def on_leave(self):
        """离开屏幕时调用"""
        pass