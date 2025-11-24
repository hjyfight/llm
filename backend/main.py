from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime, timedelta

from config import settings
from models import SentimentRecord, get_db
from schemas import (
    SentimentAnalysisRequest, 
    SentimentAnalysisResponse,
    EmotionDetail,
    SentimentStats,
    SentimentTrend,
    HealthAssessment
)
from llm_service import llm_service
from rag_service import rag_service

# 导入新的面向对象服务
from core.service_factory import get_sentiment_service, get_service_manager

# 创建FastAPI应用
app = FastAPI(
    title="智能情感分析与心理健康辅助系统",
    description="基于大语言模型的多维度情感分析平台 - 面向对象设计架构",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能情感分析与心理健康辅助系统 API",
        "version": "2.0.0",
        "architecture": "面向对象设计架构",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查 - 使用新的面向对象架构"""
    try:
        service_manager = get_service_manager()
        health_status = service_manager.health_check()
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    情感分析接口 - 使用新的面向对象架构
    
    对用户输入的文本进行多维度情感分析，包括：
    - 基础情感分类（积极/消极/中性）
    - 细粒度情绪识别
    - 情感强度评估
    - 原因分析
    - 个性化建议
    """
    
    try:
        # 使用新的面向对象服务
        sentiment_service = get_sentiment_service()
        result = sentiment_service.analyze_text(request.text, request.user_id)
        
        # 转换为响应格式
        response = SentimentAnalysisResponse(
            id=result.id,
            user_id=result.userId,
            text=result.text,
            sentiment=result.sentiment,
            confidence=result.confidence,
            emotions=[
                EmotionDetail(name=e.name, intensity=e.intensity) 
                for e in result.emotions
            ],
            intensity=result.intensity,
            analysis=result.analysis,
            causes=result.causes,
            suggestions=result.suggestions,
            created_at=result.timestamp
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")


@app.get("/api/sentiment/history/{user_id}")
async def get_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取用户的情感分析历史 - 使用新的面向对象架构"""
    
    try:
        # 使用新的面向对象服务
        sentiment_service = get_sentiment_service()
        history = sentiment_service.data_manager.get_user_history(user_id, limit)
        
        # 转换为字典格式
        return [
            {
                "id": result.id,
                "user_id": result.userId,
                "text": result.text,
                "sentiment": result.sentiment,
                "confidence": result.confidence,
                "emotions": [{"name": e.name, "intensity": e.intensity} for e in result.emotions],
                "intensity": result.intensity,
                "analysis": result.analysis,
                "causes": result.causes,
                "suggestions": result.suggestions,
                "created_at": result.timestamp
            }
            for result in history
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@app.get("/api/sentiment/stats/{user_id}", response_model=SentimentStats)
async def get_stats(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取用户的情感统计 - 使用新的面向对象架构"""
    
    try:
        # 使用新的面向对象服务
        sentiment_service = get_sentiment_service()
        stats = sentiment_service.data_manager.get_statistics(user_id, days)
        
        # 转换为响应格式
        return SentimentStats(
            total_records=stats.get("total_records", 0),
            positive_count=stats.get("positive_count", 0),
            negative_count=stats.get("negative_count", 0),
            neutral_count=stats.get("neutral_count", 0),
            average_intensity=stats.get("average_intensity", 0.0),
            most_common_emotions=[
                EmotionDetail(name=e["name"], intensity=e.get("average_intensity", 0.0))
                for e in stats.get("most_common_emotions", [])
            ],
            trends=[
                SentimentTrend(
                    date=trend["date"],
                    sentiment_score=trend.get("sentiment_score", 0.0),
                    emotion_distribution={}
                )
                for trend in stats.get("daily_trends", [])
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@app.get("/api/health/assessment/{user_id}", response_model=HealthAssessment)
async def assess_health(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取用户心理健康评估 - 使用新的面向对象架构"""
    
    try:
        # 使用新的面向对象服务
        sentiment_service = get_sentiment_service()
        health_score = sentiment_service.health_assessor.assess_health(user_id, days)
        
        # 转换为响应格式
        return HealthAssessment(
            overall_score=health_score.overallScore,
            risk_level=health_score.riskLevel,
            key_concerns=health_score.keyConcerns,
            recommendations=health_score.recommendations,
            detailed_analysis=health_score.detailedAnalysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康评估失败: {str(e)}")


@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str = None,
    emotion: str = None,
    limit: int = 5
):
    """搜索心理健康知识库 - 使用新的面向对象架构"""
    
    try:
        # 使用新的面向对象服务
        sentiment_service = get_sentiment_service()
        knowledge = sentiment_service.knowledge_retriever.search_knowledge(
            query or "", emotion, limit
        )
        
        return {"results": knowledge}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识搜索失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔════════════════════════════════════════════════════════╗
    ║  智能情感分析与心理健康辅助系统                          ║
    ║  Intelligent Sentiment Analysis & Mental Health System   ║
    ║                                                       ║
    ║  面向对象架构版本 v2.0.0                              ║
    ║  Object-Oriented Architecture                         ║
    ╚════════════════════════════════════════════════════════╝
    
    🚀 启动服务器...
    📍 API地址: http://localhost:8000
    📖 文档地址: http://localhost:8000/docs
    🔧 架构: 面向对象设计
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)