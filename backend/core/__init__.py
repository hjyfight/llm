"""
面向对象架构设计

智能情感分析与心理健康辅助系统
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


# ================================
# 数据传输对象 (DTOs)
# ================================

@dataclass
class EmotionData:
    """情感数据传输对象"""
    name: str
    intensity: float
    
    def __post_init__(self):
        if not 0 <= self.intensity <= 1:
            raise ValueError("情感强度必须在0-1之间")


@dataclass
class SentimentAnalysisResult:
    """情感分析结果数据传输对象"""
    user_id: str
    text: str
    sentiment: str  # positive, negative, neutral
    confidence: float
    emotions: List[EmotionData]
    intensity: float
    analysis: str
    causes: str
    suggestions: str
    timestamp: datetime


@dataclass
class HealthScore:
    """健康评分数据传输对象"""
    overall_score: float
    risk_level: str
    key_concerns: List[str]
    recommendations: List[str]
    detailed_analysis: str


@dataclass
class User:
    """用户数据传输对象"""
    id: str
    created_at: datetime
    last_active: datetime
    profile: Dict[str, Any] = None


# ================================
# 抽象接口定义
# ================================

class ISentimentAnalyzer(ABC):
    """情感分析器接口"""
    
    @abstractmethod
    def analyze(self, text: str, user_id: str = "default_user") -> SentimentAnalysisResult:
        """分析文本情感"""
        pass
    
    @abstractmethod
    def batch_analyze(self, texts: List[str], user_id: str = "default_user") -> List[SentimentAnalysisResult]:
        """批量分析文本情感"""
        pass


class IDataManager(ABC):
    """数据管理器接口"""
    
    @abstractmethod
    def save_analysis(self, result: SentimentAnalysisResult) -> int:
        """保存分析结果"""
        pass
    
    @abstractmethod
    def get_user_history(self, user_id: str, limit: int = 100) -> List[SentimentAnalysisResult]:
        """获取用户历史记录"""
        pass
    
    @abstractmethod
    def get_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取统计数据"""
        pass


class IHealthAssessor(ABC):
    """健康评估器接口"""
    
    @abstractmethod
    def assess_health(self, user_id: str, days: int = 30) -> HealthScore:
        """评估用户心理健康"""
        pass
    
    @abstractmethod
    def get_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取情感趋势"""
        pass


class IKnowledgeRetriever(ABC):
    """知识检索器接口"""
    
    @abstractmethod
    def search_knowledge(self, query: str, emotion: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索相关知识"""
        pass
    
    @abstractmethod
    def get_suggestions(self, emotion: str, context: str = None) -> List[str]:
        """获取建议"""
        pass


class IUserManager(ABC):
    """用户管理器接口"""
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """创建用户"""
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        pass
    
    @abstractmethod
    def update_user_activity(self, user_id: str) -> None:
        """更新用户活动时间"""
        pass


# ================================
# 核心业务逻辑类
# ================================

class SentimentAnalysisService:
    """情感分析服务 - 门面模式"""
    
    def __init__(self, 
                 analyzer: ISentimentAnalyzer,
                 data_manager: IDataManager,
                 health_assessor: IHealthAssessor,
                 knowledge_retriever: IKnowledgeRetriever,
                 user_manager: IUserManager):
        self.analyzer = analyzer
        self.data_manager = data_manager
        self.health_assessor = health_assessor
        self.knowledge_retriever = knowledge_retriever
        self.user_manager = user_manager
    
    def analyze_text(self, text: str, user_id: str = "default_user") -> SentimentAnalysisResult:
        """分析文本并保存结果"""
        # 更新用户活动
        self.user_manager.update_user_activity(user_id)
        
        # 执行情感分析
        result = self.analyzer.analyze(text, user_id)
        
        # 保存结果
        self.data_manager.save_analysis(result)
        
        return result
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """获取用户仪表板数据"""
        # 获取历史记录
        history = self.data_manager.get_user_history(user_id, limit=50)
        
        # 获取统计数据
        stats = self.data_manager.get_statistics(user_id, days=30)
        
        # 获取健康评估
        health_score = self.health_assessor.assess_health(user_id, days=30)
        
        # 获取趋势数据
        trends = self.health_assessor.get_trends(user_id, days=30)
        
        return {
            "user_id": user_id,
            "history": history,
            "statistics": stats,
            "health_score": health_score,
            "trends": trends
        }
    
    def get_personalized_suggestions(self, user_id: str, emotion: str = None) -> List[str]:
        """获取个性化建议"""
        # 获取最近的情感记录
        recent_records = self.data_manager.get_user_history(user_id, limit=5)
        
        if not recent_records and not emotion:
            return []
        
        # 如果没有指定情感，使用最近的情感
        if not emotion:
            emotion = recent_records[0].sentiment
        
        # 检索相关知识
        context = recent_records[0].text if recent_records else None
        knowledge = self.knowledge_retriever.search_knowledge(
            query=emotion, 
            emotion=emotion, 
            limit=3
        )
        
        # 获取建议
        suggestions = self.knowledge_retriever.get_suggestions(emotion, context)
        
        return suggestions


class NotificationService:
    """通知服务"""
    
    def __init__(self, health_assessor: IHealthAssessor):
        self.health_assessor = health_assessor
    
    def check_and_notify(self, user_id: str) -> Optional[Dict[str, Any]]:
        """检查用户状态并发送通知"""
        health_score = self.health_assessor.assess_health(user_id, days=7)
        
        # 如果风险等级高，发送通知
        if health_score.risk_level == "high":
            return {
                "type": "risk_alert",
                "user_id": user_id,
                "score": health_score.overall_score,
                "concerns": health_score.key_concerns,
                "message": "检测到您的心理状态可能需要关注，建议寻求专业帮助。"
            }
        
        return None


# ================================
# 工厂类
# ================================

class ServiceFactory:
    """服务工厂 - 创建和配置各种服务"""
    
    @staticmethod
    def create_sentiment_analysis_service() -> SentimentAnalysisService:
        """创建情感分析服务"""
        # 这里会在具体实现中注入实际的依赖
        pass
    
    @staticmethod
    def create_notification_service() -> NotificationService:
        """创建通知服务"""
        # 这里会在具体实现中注入实际的依赖
        pass


# ================================
# 异常类
# ================================

class SentimentAnalysisError(Exception):
    """情感分析异常"""
    pass


class DataValidationError(Exception):
    """数据验证异常"""
    pass


class ServiceUnavailableError(Exception):
    """服务不可用异常"""
    pass


# ================================
# 配置类
# ================================

class SystemConfig:
    """系统配置"""
    
    # API配置
    API_BASE_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:3000"
    
    # 模型配置
    DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    
    # 数据库配置
    DATABASE_URL = "sqlite:///./sentiment_analysis.db"
    CHROMA_PERSIST_DIR = "./chroma_db"
    
    # 业务配置
    DEFAULT_USER_ID = "default_user"
    MAX_HISTORY_DAYS = 365
    HEALTH_ASSESSMENT_DAYS = 30
    
    # 缓存配置
    CACHE_TTL = 3600  # 1小时
    MAX_CACHE_SIZE = 1000


# ================================
# 日志记录器
# ================================

import logging

class Logger:
    """统一日志记录器"""
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """获取日志记录器"""
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger