from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()


class SentimentRecord(Base):
    """情感分析记录模型"""
    __tablename__ = "sentiment_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="default_user")
    text = Column(Text, nullable=False)
    
    # 基础情感分类
    sentiment = Column(String)  # positive, negative, neutral
    confidence = Column(Float)
    
    # 细粒度情绪
    emotions = Column(Text)  # JSON格式存储多个情绪及其强度
    
    # 情感强度
    intensity = Column(Float)  # 0-1
    
    # 分析结果
    analysis = Column(Text)  # 详细的情感分析
    causes = Column(Text)  # 情感原因
    suggestions = Column(Text)  # 建议
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "emotions": self.emotions,
            "intensity": self.intensity,
            "analysis": self.analysis,
            "causes": self.causes,
            "suggestions": self.suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 创建表
Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
