from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class SentimentAnalysisRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., description="要分析的文本")
    user_id: str = Field(default="default_user", description="用户ID")


class EmotionDetail(BaseModel):
    """情绪详情"""
    name: str = Field(..., description="情绪名称")
    intensity: float = Field(..., ge=0, le=1, description="情绪强度")


class SentimentAnalysisResponse(BaseModel):
    """情感分析响应"""
    id: int
    user_id: str
    text: str
    sentiment: str = Field(..., description="基础情感分类: positive/negative/neutral")
    confidence: float = Field(..., ge=0, le=1, description="分类置信度")
    emotions: List[EmotionDetail] = Field(..., description="细粒度情绪列表")
    intensity: float = Field(..., ge=0, le=1, description="总体情感强度")
    analysis: str = Field(..., description="详细分析")
    causes: str = Field(..., description="情感原因")
    suggestions: str = Field(..., description="改善建议")
    created_at: datetime


class SentimentTrend(BaseModel):
    """情感趋势"""
    date: str
    sentiment_score: float  # -1 to 1
    emotion_distribution: Dict[str, float]


class SentimentStats(BaseModel):
    """情感统计"""
    total_records: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_intensity: float
    most_common_emotions: List[EmotionDetail]
    trends: List[SentimentTrend]


class HealthAssessment(BaseModel):
    """心理健康评估"""
    overall_score: float = Field(..., ge=0, le=100, description="总体心理健康得分")
    risk_level: str = Field(..., description="风险等级: low/medium/high")
    key_concerns: List[str] = Field(..., description="主要关注点")
    recommendations: List[str] = Field(..., description="建议")
    detailed_analysis: str = Field(..., description="详细分析")
