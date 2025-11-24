"""
服务工厂和主服务类

负责创建和管理所有服务实例
"""

from core import (
    SentimentAnalysisService, NotificationService, ServiceFactory,
    ISentimentAnalyzer, IDataManager, IHealthAssessor, 
    IKnowledgeRetriever, IUserManager, Logger
)
from core.analyzer import LLMAnalyzer, CachedAnalyzer
from core.data_manager import DatabaseManager
from core.health_assessor import MentalHealthAssessor
from core.knowledge_retriever import MentalHealthKnowledgeRetriever, CachedKnowledgeRetriever
from core.user_manager import SimpleUserManager
from rag_service import RAGService


class SentimentAnalysisServiceFactory(ServiceFactory):
    """情感分析服务工厂实现"""
    
    _instances = {}
    
    @classmethod
    def create_sentiment_analysis_service(cls) -> SentimentAnalysisService:
        """创建完整的情感分析服务"""
        if "main_service" not in cls._instances:
            logger = Logger.get_logger(__name__)
            logger.info("创建情感分析服务实例")
            
            # 创建核心组件
            analyzer = cls._create_analyzer()
            data_manager = cls._create_data_manager()
            health_assessor = cls._create_health_assessor(data_manager)
            knowledge_retriever = cls._create_knowledge_retriever()
            user_manager = cls._create_user_manager()
            
            # 创建主服务
            service = SentimentAnalysisService(
                analyzer=analyzer,
                data_manager=data_manager,
                health_assessor=health_assessor,
                knowledge_retriever=knowledge_retriever,
                user_manager=user_manager
            )
            
            cls._instances["main_service"] = service
            logger.info("情感分析服务创建完成")
        
        return cls._instances["main_service"]
    
    @classmethod
    def create_notification_service(cls) -> NotificationService:
        """创建通知服务"""
        if "notification_service" not in cls._instances:
            logger = Logger.get_logger(__name__)
            logger.info("创建通知服务实例")
            
            # 获取健康评估器
            data_manager = cls._create_data_manager()
            health_assessor = cls._create_health_assessor(data_manager)
            
            # 创建通知服务
            service = NotificationService(health_assessor)
            
            cls._instances["notification_service"] = service
            logger.info("通知服务创建完成")
        
        return cls._instances["notification_service"]
    
    @classmethod
    def _create_analyzer(cls) -> ISentimentAnalyzer:
        """创建情感分析器"""
        # 创建基础分析器
        base_analyzer = LLMAnalyzer()
        
        # 添加缓存装饰器
        cached_analyzer = CachedAnalyzer(base_analyzer)
        
        return cached_analyzer
    
    @classmethod
    def _create_data_manager(cls) -> IDataManager:
        """创建数据管理器"""
        return DatabaseManager()
    
    @classmethod
    def _create_health_assessor(cls, data_manager: IDataManager) -> IHealthAssessor:
        """创建健康评估器"""
        return MentalHealthAssessor(data_manager)
    
    @classmethod
    def _create_knowledge_retriever(cls) -> IKnowledgeRetriever:
        """创建知识检索器"""
        # 创建RAG服务
        rag_service = RAGService()
        
        # 创建基础检索器
        base_retriever = MentalHealthKnowledgeRetriever(rag_service)
        
        # 添加缓存装饰器
        cached_retriever = CachedKnowledgeRetriever(base_retriever)
        
        return cached_retriever
    
    @classmethod
    def _create_user_manager(cls) -> IUserManager:
        """创建用户管理器"""
        return SimpleUserManager()
    
    @classmethod
    def reset_instances(cls):
        """重置所有实例（主要用于测试）"""
        cls._instances.clear()


class ServiceManager:
    """服务管理器 - 单例模式管理所有服务"""
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = Logger.get_logger(__name__)
            self.factory = SentimentAnalysisServiceFactory()
            self._initialize_services()
            self._initialized = True
    
    def _initialize_services(self):
        """初始化所有服务"""
        self.logger.info("初始化服务管理器")
        
        # 创建主要服务
        self._services["sentiment_analysis"] = self.factory.create_sentiment_analysis_service()
        self._services["notification"] = self.factory.create_notification_service()
        
        self.logger.info("服务管理器初始化完成")
    
    def get_sentiment_analysis_service(self) -> SentimentAnalysisService:
        """获取情感分析服务"""
        return self._services["sentiment_analysis"]
    
    def get_notification_service(self) -> NotificationService:
        """获取通知服务"""
        return self._services["notification"]
    
    def get_service(self, service_name: str):
        """根据名称获取服务"""
        return self._services.get(service_name)
    
    def health_check(self) -> dict:
        """健康检查 - 检查所有服务状态"""
        health_status = {
            "status": "healthy",
            "services": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for service_name, service in self._services.items():
            try:
                # 简单的服务可用性检查
                if hasattr(service, '__class__'):
                    health_status["services"][service_name] = {
                        "status": "healthy",
                        "class": service.__class__.__name__
                    }
                else:
                    health_status["services"][service_name] = {
                        "status": "unknown",
                        "class": "Unknown"
                    }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status


# 导入datetime
from datetime import datetime


# 便捷的全局访问函数
def get_sentiment_service() -> SentimentAnalysisService:
    """获取情感分析服务的便捷函数"""
    manager = ServiceManager()
    return manager.get_sentiment_analysis_service()


def get_notification_service() -> NotificationService:
    """获取通知服务的便捷函数"""
    manager = ServiceManager()
    return manager.get_notification_service()


def get_service_manager() -> ServiceManager:
    """获取服务管理器的便捷函数"""
    return ServiceManager()