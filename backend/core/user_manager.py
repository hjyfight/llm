"""
用户管理器实现

负责用户信息管理和活动追踪
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from core import (
    IUserManager, User, Logger, SystemConfig
)


class SimpleUserManager(IUserManager):
    """简单用户管理器实现"""
    
    def __init__(self):
        self.users = {}  # 简单内存存储，实际应用应使用数据库
        self.logger = Logger.get_logger(__name__)
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """创建新用户"""
        try:
            user_id = user_data.get("id", f"user_{datetime.now().timestamp()}")
            
            # 检查用户是否已存在
            if user_id in self.users:
                self.logger.warning(f"用户 {user_id} 已存在")
                return self.users[user_id]
            
            # 创建用户对象
            user = User(
                id=user_id,
                created_at=datetime.now(),
                last_active=datetime.now(),
                profile=user_data.get("profile", {})
            )
            
            # 存储用户
            self.users[user_id] = user
            
            self.logger.info(f"创建用户: {user_id}")
            return user
            
        except Exception as e:
            self.logger.error(f"创建用户失败: {str(e)}")
            raise
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        user = self.users.get(user_id)
        if user:
            self.logger.info(f"获取用户信息: {user_id}")
        else:
            self.logger.warning(f"用户不存在: {user_id}")
        return user
    
    def update_user_activity(self, user_id: str) -> None:
        """更新用户活动时间"""
        if user_id in self.users:
            self.users[user_id].last_active = datetime.now()
            self.logger.debug(f"更新用户活动时间: {user_id}")
        else:
            # 如果用户不存在，创建默认用户
            self.create_user({"id": user_id})
    
    def get_all_users(self) -> List[User]:
        """获取所有用户（管理功能）"""
        return list(self.users.values())
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id in self.users:
            del self.users[user_id]
            self.logger.info(f"删除用户: {user_id}")
            return True
        return False


class UserProfileManager:
    """用户配置文件管理器"""
    
    def __init__(self, user_manager: IUserManager):
        self.user_manager = user_manager
        self.logger = Logger.get_logger(__name__)
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """更新用户配置文件"""
        try:
            user = self.user_manager.get_user(user_id)
            if not user:
                return False
            
            # 更新配置文件
            if user.profile is None:
                user.profile = {}
            
            user.profile.update(profile_data)
            
            self.logger.info(f"更新用户配置文件: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新配置文件失败: {str(e)}")
            return False
    
    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """获取用户偏好设置"""
        user = self.user_manager.get_user(user_id)
        if not user or not user.profile:
            return default
        
        return user.profile.get(key, default)
    
    def set_preference(self, user_id: str, key: str, value: Any) -> bool:
        """设置用户偏好"""
        return self.update_profile(user_id, {key: value})


class UserAnalytics:
    """用户分析器"""
    
    def __init__(self, user_manager: IUserManager, data_manager):
        self.user_manager = user_manager
        self.data_manager = data_manager
        self.logger = Logger.get_logger(__name__)
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            user = self.user_manager.get_user(user_id)
            if not user:
                return {}
            
            # 获取情感分析统计
            sentiment_stats = self.data_manager.get_statistics(user_id, days=30)
            
            # 计算用户活跃度
            days_active = self._calculate_active_days(user_id)
            
            # 计算使用频率
            usage_frequency = self._calculate_usage_frequency(user_id)
            
            user_stats = {
                "user_id": user_id,
                "created_at": user.created_at.isoformat(),
                "last_active": user.last_active.isoformat(),
                "days_active": days_active,
                "usage_frequency": usage_frequency,
                "sentiment_statistics": sentiment_stats,
                "engagement_score": self._calculate_engagement_score(user_id)
            }
            
            return user_stats
            
        except Exception as e:
            self.logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    def _calculate_active_days(self, user_id: str) -> int:
        """计算活跃天数"""
        history = self.data_manager.get_user_history(user_id, limit=1000)
        
        if not history:
            return 0
        
        # 计算不同的日期
        unique_dates = set()
        for record in history:
            unique_dates.add(record.timestamp.date())
        
        return len(unique_dates)
    
    def _calculate_usage_frequency(self, user_id: str) -> str:
        """计算使用频率"""
        history = self.data_manager.get_user_history(user_id, limit=100)
        
        if not history:
            return "none"
        
        # 计算最近30天的使用次数
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_records = [r for r in history if r.timestamp >= cutoff_date]
        
        if len(recent_records) >= 20:
            return "daily"
        elif len(recent_records) >= 10:
            return "weekly"
        elif len(recent_records) >= 3:
            return "monthly"
        else:
            return "occasional"
    
    def _calculate_engagement_score(self, user_id: str) -> float:
        """计算用户参与度得分"""
        history = self.data_manager.get_user_history(user_id, limit=100)
        
        if not history:
            return 0.0
        
        # 基于多个因素计算参与度
        factors = {
            "record_count": min(len(history) / 50, 1.0),  # 记录数量
            "consistency": self._calculate_consistency(history),  # 使用一致性
            "diversity": self._calculate_emotion_diversity(history),  # 情感多样性
            "recency": self._calculate_recency(history)  # 最近活跃度
        }
        
        # 加权平均
        weights = {
            "record_count": 0.3,
            "consistency": 0.3,
            "diversity": 0.2,
            "recency": 0.2
        }
        
        engagement_score = sum(factors[key] * weights[key] for key in factors)
        return round(engagement_score, 3)
    
    def _calculate_consistency(self, history: List) -> float:
        """计算使用一致性"""
        if len(history) < 7:
            return 0.0
        
        # 计算记录的时间间隔方差
        intervals = []
        for i in range(1, len(history)):
            interval = (history[i-1].timestamp - history[i].timestamp).days
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        
        # 方差越小，一致性越高
        consistency = max(0.0, 1.0 - variance / 30)  # 标准化到30天
        return consistency
    
    def _calculate_emotion_diversity(self, history: List) -> float:
        """计算情感多样性"""
        emotions = set()
        for record in history:
            emotions.add(record.sentiment)
            for emotion in record.emotions:
                emotions.add(emotion.name)
        
        diversity = min(len(emotions) / 10, 1.0)  # 假设最多10种不同的情感
        return diversity
    
    def _calculate_recency(self, history: List) -> float:
        """计算最近活跃度"""
        if not history:
            return 0.0
        
        most_recent = history[0].timestamp  # 假设历史记录按时间倒序排列
        days_since_last = (datetime.now() - most_recent).days
        
        # 越近的记录得分越高
        recency = max(0.0, 1.0 - days_since_last / 30)
        return recency


# 导入必要的模块
from typing import List
from datetime import timedelta