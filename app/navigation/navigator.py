#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园导航模块
提供离线校园导航和语音引导功能
"""

import math
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from plyer import gps
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("警告: plyer 未安装，GPS功能将不可用")

from app.data.database import DatabaseManager
from app.utils.accessibility import AccessibilityManager


@dataclass
class Location:
    """地点数据类"""
    id: int
    name: str
    category: str
    latitude: float
    longitude: float
    description: str = ""
    accessible_features: str = ""


@dataclass
class NavigationInstruction:
    """导航指令数据类"""
    instruction: str
    distance: float
    direction: str
    waypoint_lat: float
    waypoint_lng: float


class CampusNavigator:
    """校园导航器"""
    
    def __init__(self, db_manager: DatabaseManager, accessibility_manager: AccessibilityManager):
        """初始化导航器"""
        self.db_manager = db_manager
        self.accessibility_manager = accessibility_manager
        self.is_navigating = False
        self.current_route = None
        self.current_instruction_index = 0
        self.current_location = None
        self.destination = None
        
        # GPS配置
        self.gps_provider = 'gps'
        self.gps_accuracy_threshold = 50  # 米
        self.last_gps_update = 0
        self.gps_update_interval = 5  # 秒
        
        # 导航参数
        self.arrival_threshold = 10  # 到达判定距离（米）
        self.instruction_distance_threshold = 20  # 播报指令的距离阈值（米）
        
        if GPS_AVAILABLE:
            self._initialize_gps()
    
    def _initialize_gps(self):
        """初始化GPS"""
        try:
            gps.configure(on_location=self._on_location_update)
            print("GPS初始化成功")
        except Exception as e:
            print(f"GPS初始化失败: {e}")
    
    def _on_location_update(self, **kwargs):
        """GPS位置更新回调"""
        if 'lat' in kwargs and 'lon' in kwargs:
            self.current_location = {
                'latitude': kwargs['lat'],
                'longitude': kwargs['lon'],
                'accuracy': kwargs.get('accuracy', 0),
                'timestamp': time.time()
            }
            self.last_gps_update = time.time()
            
            # 如果正在导航，检查是否需要更新指令
            if self.is_navigating:
                self._check_navigation_progress()
    
    def start_navigation(self):
        """启动导航功能"""
        self.accessibility_manager.speak("校园导航功能已启动")
        self.accessibility_manager.speak("请选择目的地")
        
        # 获取可用地点列表
        locations = self.db_manager.get_locations_by_category()
        if not locations:
            self.accessibility_manager.announce_error("没有可用的地点数据")
            return
        
        # 按类别分组并语音播报
        categories = {}
        for loc_data in locations:
            category = loc_data['category']
            if category not in categories:
                categories[category] = []
            location = Location(
                id=loc_data['id'],
                name=loc_data['name'],
                category=loc_data['category'],
                latitude=loc_data['latitude'],
                longitude=loc_data['longitude'],
                description=loc_data.get('description', ''),
                accessible_features=loc_data.get('accessible_features', '')
            )
            categories[category].append(location)
        
        self.accessibility_manager.speak(f"可用地点类别：{', '.join(categories.keys())}")
        
        # 模拟用户选择（实际应用中应该通过UI交互）
        self._simulate_destination_selection(categories)
    
    def _simulate_destination_selection(self, categories: Dict[str, List[Location]]):
        """模拟目的地选择（实际应用中应该通过UI实现）"""
        # 默认选择第一个地点作为演示
        if categories:
            first_category = list(categories.keys())[0]
            if categories[first_category]:
                destination = categories[first_category][0]
                self.accessibility_manager.speak(f"已选择目的地：{destination.name}")
                self._start_navigation_to_destination(destination)
    
    def _start_navigation_to_destination(self, destination: Location):
        """开始导航到指定目的地"""
        self.destination = destination
        
        # 获取当前位置（如果没有GPS，使用模拟位置）
        if not self.current_location:
            self.current_location = self._get_simulated_current_location()
        
        # 查找路径
        start_loc = self._find_nearest_location(
            self.current_location['latitude'],
            self.current_location['longitude']
        )
        
        if not start_loc:
            self.accessibility_manager.announce_error("无法确定起始位置")
            return
        
        route = self.db_manager.get_route(start_loc.id, destination.id)
        if not route:
            self.accessibility_manager.announce_error(f"没有找到到{destination.name}的路径")
            return
        
        # 开始导航
        self.current_route = route
        self.current_instruction_index = 0
        self.is_navigating = True
        
        self.accessibility_manager.speak(f"开始导航到{destination.name}")
        self.accessibility_manager.play_sound('navigation_start')
        
        # 开始GPS跟踪
        if GPS_AVAILABLE:
            try:
                gps.start(self.gps_provider, self.gps_update_interval * 1000)
            except Exception as e:
                print(f"GPS启动失败: {e}")
                self._simulate_navigation()
        else:
            self._simulate_navigation()
    
    def _find_nearest_location(self, lat: float, lng: float) -> Optional[Location]:
        """查找最近的地点"""
        locations = self.db_manager.get_locations_by_category()
        if not locations:
            return None
        
        min_distance = float('inf')
        nearest_location = None
        
        for loc_data in locations:
            distance = self._calculate_distance(lat, lng, loc_data['latitude'], loc_data['longitude'])
            if distance < min_distance:
                min_distance = distance
                nearest_location = Location(
                    id=loc_data['id'],
                    name=loc_data['name'],
                    category=loc_data['category'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    description=loc_data.get('description', ''),
                    accessible_features=loc_data.get('accessible_features', '')
                )
        
        return nearest_location
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点间距离（米）"""
        # 使用Haversine公式
        R = 6371000  # 地球半径（米）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_simulated_current_location(self) -> Dict:
        """获取模拟当前位置（用于测试）"""
        # 模拟在校园内的某个位置
        return {
            'latitude': 39.9040,
            'longitude': 116.4070,
            'accuracy': 5,
            'timestamp': time.time()
        }
    
    def _simulate_navigation(self):
        """模拟导航过程（用于测试）"""
        if not self.current_route or not self.is_navigating:
            return
        
        waypoints = self.current_route['waypoints']
        total_instructions = len(waypoints)
        
        def update_instruction(index):
            if index >= total_instructions or not self.is_navigating:
                return
            
            waypoint = waypoints[index]
            instruction = waypoint.get('instruction', '继续前进')
            distance = self._calculate_distance(
                self.current_location['latitude'],
                self.current_location['longitude'],
                waypoint['lat'],
                waypoint['lng']
            )
            
            self.accessibility_manager.announce_navigation_instruction(instruction, distance)
            
            # 模拟移动到下一个点
            self.current_location['latitude'] = waypoint['lat']
            self.current_location['longitude'] = waypoint['lng']
            
            # 继续下一个指令
            if index < total_instructions - 1:
                # 延迟3秒后播放下一个指令
                import threading
                threading.Timer(3.0, lambda: update_instruction(index + 1)).start()
            else:
                # 到达目的地
                self._on_arrival()
        
        # 开始第一个指令
        update_instruction(0)
    
    def _check_navigation_progress(self):
        """检查导航进度"""
        if not self.is_navigating or not self.current_route:
            return
        
        waypoints = self.current_route['waypoints']
        if self.current_instruction_index >= len(waypoints):
            return
        
        current_waypoint = waypoints[self.current_instruction_index]
        distance = self._calculate_distance(
            self.current_location['latitude'],
            self.current_location['longitude'],
            current_waypoint['lat'],
            current_waypoint['lng']
        )
        
        # 检查是否需要播报指令
        if distance <= self.instruction_distance_threshold:
            instruction = current_waypoint.get('instruction', '继续前进')
            self.accessibility_manager.announce_navigation_instruction(instruction, distance)
            
            # 检查是否到达当前航点
            if distance <= 5:  # 5米内认为到达航点
                self.current_instruction_index += 1
                
                # 检查是否到达目的地
                if self.current_instruction_index >= len(waypoints):
                    self._on_arrival()
    
    def _on_arrival(self):
        """到达目的地"""
        self.is_navigating = False
        self.accessibility_manager.announce_arrival(self.destination.name)
        
        # 记录导航历史
        if self.db_manager:
            self.db_manager.add_navigation_history(
                start_location="当前位置",
                end_location=self.destination.name,
                route_name=self.current_route['name'] if self.current_route else "未知路径"
            )
        
        # 停止GPS
        if GPS_AVAILABLE:
            try:
                gps.stop()
            except:
                pass
    
    def stop_navigation(self):
        """停止导航"""
        if self.is_navigating:
            self.is_navigating = False
            self.accessibility_manager.speak("导航已停止")
            
            # 停止GPS
            if GPS_AVAILABLE:
                try:
                    gps.stop()
                except:
                    pass
    
    def get_nearby_locations(self, radius: float = 100) -> List[Location]:
        """获取附近地点"""
        if not self.current_location:
            return []
        
        locations = self.db_manager.get_locations_by_category()
        nearby_locations = []
        
        for loc_data in locations:
            distance = self._calculate_distance(
                self.current_location['latitude'],
                self.current_location['longitude'],
                loc_data['latitude'],
                loc_data['longitude']
            )
            
            if distance <= radius:
                location = Location(
                    id=loc_data['id'],
                    name=loc_data['name'],
                    category=loc_data['category'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    description=loc_data.get('description', ''),
                    accessible_features=loc_data.get('accessible_features', '')
                )
                nearby_locations.append((location, distance))
        
        # 按距离排序
        nearby_locations.sort(key=lambda x: x[1])
        return [loc for loc, _ in nearby_locations]
    
    def announce_nearby_places(self):
        """播报附近地点"""
        nearby = self.get_nearby_locations()
        if not nearby:
            self.accessibility_manager.speak("附近没有找到地点")
            return
        
        self.accessibility_manager.speak(f"附近有{len(nearby)}个地点：")
        for location in nearby[:5]:  # 最多播报5个
            distance = self._calculate_distance(
                self.current_location['latitude'],
                self.current_location['longitude'],
                location.latitude,
                location.longitude
            )
            self.accessibility_manager.speak(f"{location.name}，距离{distance:.0f}米")
    
    def get_navigation_status(self) -> Dict:
        """获取导航状态"""
        return {
            'is_navigating': self.is_navigating,
            'destination': self.destination.name if self.destination else None,
            'current_instruction_index': self.current_instruction_index,
            'total_instructions': len(self.current_route['waypoints']) if self.current_route else 0,
            'current_location': self.current_location
        }