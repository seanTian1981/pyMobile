#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
处理所有本地数据存储操作
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化数据库管理器"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'campus.db')
        
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()
    
    def _ensure_database_exists(self):
        """确保数据库目录存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """创建数据库表"""
        with self._get_connection() as conn:
            # 校园地点表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    description TEXT,
                    accessible_features TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 路径表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_location_id INTEGER,
                    end_location_id INTEGER,
                    waypoints TEXT,
                    distance REAL,
                    estimated_time INTEGER,
                    is_accessible BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (start_location_id) REFERENCES locations (id),
                    FOREIGN KEY (end_location_id) REFERENCES locations (id)
                )
            ''')
            
            # 用户设置表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 历史记录表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS navigation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_location TEXT,
                    end_location TEXT,
                    route_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completion_status TEXT DEFAULT 'completed'
                )
            ''')
            
            conn.commit()
    
    def add_location(self, name: str, category: str, latitude: float, 
                    longitude: float, description: str = None, 
                    accessible_features: str = None) -> int:
        """添加校园地点"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO locations (name, category, latitude, longitude, description, accessible_features)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, category, latitude, longitude, description, accessible_features))
            conn.commit()
            return cursor.lastrowid
    
    def get_locations_by_category(self, category: str = None) -> List[Dict]:
        """根据类别获取地点列表"""
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute('''
                    SELECT * FROM locations WHERE category = ? ORDER BY name
                ''', (category,))
            else:
                cursor = conn.execute('SELECT * FROM locations ORDER BY category, name')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_location_by_id(self, location_id: int) -> Optional[Dict]:
        """根据ID获取地点信息"""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM locations WHERE id = ?', (location_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_route(self, name: str, start_location_id: int, end_location_id: int,
                  waypoints: List[Dict], distance: float, estimated_time: int,
                  is_accessible: bool = True) -> int:
        """添加路径"""
        waypoints_json = json.dumps(waypoints)
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO routes (name, start_location_id, end_location_id, waypoints, 
                                  distance, estimated_time, is_accessible)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, start_location_id, end_location_id, waypoints_json, 
                  distance, estimated_time, is_accessible))
            conn.commit()
            return cursor.lastrowid
    
    def get_route(self, start_location_id: int, end_location_id: int) -> Optional[Dict]:
        """获取两点之间的路径"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM routes 
                WHERE start_location_id = ? AND end_location_id = ?
                ORDER BY is_accessible DESC, distance ASC
                LIMIT 1
            ''', (start_location_id, end_location_id))
            row = cursor.fetchone()
            if row:
                route = dict(row)
                route['waypoints'] = json.loads(route['waypoints'])
                return route
            return None
    
    def save_user_setting(self, key: str, value: str):
        """保存用户设置"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()
    
    def get_user_setting(self, key: str, default_value: str = None) -> Optional[str]:
        """获取用户设置"""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT value FROM user_settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row['value'] if row else default_value
    
    def add_navigation_history(self, start_location: str, end_location: str, 
                              route_name: str, completion_status: str = 'completed'):
        """添加导航历史记录"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO navigation_history (start_location, end_location, route_name, completion_status)
                VALUES (?, ?, ?, ?)
            ''', (start_location, end_location, route_name, completion_status))
            conn.commit()
    
    def get_navigation_history(self, limit: int = 10) -> List[Dict]:
        """获取导航历史记录"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM navigation_history 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def initialize_sample_data(self):
        """初始化示例数据"""
        # 检查是否已有数据
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM locations')
            count = cursor.fetchone()['count']
            
            if count == 0:
                # 添加示例地点
                locations = [
                    ("主教学楼", "教学楼", 39.9042, 116.4074, "主要教学场所", "电梯,盲道,无障碍卫生间"),
                    ("图书馆", "学习设施", 39.9052, 116.4084, "图书借阅和学习", "电梯,盲道,无障碍卫生间,语音导览"),
                    ("第一食堂", "餐饮设施", 39.9032, 116.4064, "学生用餐场所", "盲道,无障碍餐桌,语音菜单"),
                    ("学生宿舍A栋", "宿舍", 39.9062, 116.4094, "学生住宿", "电梯,盲道,无障碍设施"),
                    ("体育馆", "体育设施", 39.9022, 116.4054, "体育活动和锻炼", "盲道,无障碍更衣室"),
                ]
                
                for loc in locations:
                    self.add_location(*loc)
                
                # 添加示例路径
                self.add_route(
                    "主教学楼到图书馆", 1, 2,
                    [{"lat": 39.9042, "lng": 116.4074, "instruction": "从主教学楼出发"},
                     {"lat": 39.9047, "lng": 116.4079, "instruction": "向北直行100米"},
                     {"lat": 39.9052, "lng": 116.4084, "instruction": "到达图书馆"}],
                    150.0, 120, True
                )