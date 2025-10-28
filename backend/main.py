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

# 创建FastAPI应用
app = FastAPI(
    title="智能情感分析与心理健康辅助系统",
    description="基于大语言模型的多维度情感分析平台",
    version="1.0.0"
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
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    情感分析接口
    
    对用户输入的文本进行多维度情感分析，包括：
    - 基础情感分类（积极/消极/中性）
    - 细粒度情绪识别
    - 情感强度评估
    - 原因分析
    - 个性化建议
    """
    
    try:
        # Step 1: 使用LLM进行情感分析
        sentiment_result = llm_service.analyze_sentiment(request.text)
        
        # Step 2: 获取用户历史记录（用于个性化建议）
        user_history = db.query(SentimentRecord).filter(
            SentimentRecord.user_id == request.user_id
        ).order_by(SentimentRecord.created_at.desc()).limit(10).all()
        
        user_history_dicts = [record.to_dict() for record in user_history]
        
        # Step 3: 使用RAG检索相关知识
        main_emotions = [e['name'] for e in sentiment_result.get('emotions', [])]
        knowledge = rag_service.retrieve_relevant_knowledge(
            query=sentiment_result.get('analysis', ''),
            emotion_categories=None,
            top_k=3
        )
        
        # Step 4: 生成个性化建议（结合历史和知识库）
        suggestions = llm_service.generate_suggestions(
            sentiment_result, 
            user_history_dicts
        )
        
        # 如果有相关知识，添加到建议中
        if knowledge:
            knowledge_text = "\n\n📚 相关专业建议：\n" + "\n".join([
                f"• {k['content']}" for k in knowledge
            ])
            suggestions += knowledge_text
        
        # Step 5: 保存到数据库
        emotions_json = json.dumps(sentiment_result.get('emotions', []), ensure_ascii=False)
        
        record = SentimentRecord(
            user_id=request.user_id,
            text=request.text,
            sentiment=sentiment_result.get('sentiment', 'neutral'),
            confidence=sentiment_result.get('confidence', 0.5),
            emotions=emotions_json,
            intensity=sentiment_result.get('intensity', 0.5),
            analysis=sentiment_result.get('analysis', ''),
            causes=sentiment_result.get('causes', ''),
            suggestions=suggestions
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        # Step 6: 构建响应
        emotions_list = [
            EmotionDetail(name=e['name'], intensity=e['intensity'])
            for e in sentiment_result.get('emotions', [])
        ]
        
        return SentimentAnalysisResponse(
            id=record.id,
            user_id=record.user_id,
            text=record.text,
            sentiment=record.sentiment,
            confidence=record.confidence,
            emotions=emotions_list,
            intensity=record.intensity,
            analysis=record.analysis,
            causes=record.causes,
            suggestions=record.suggestions,
            created_at=record.created_at
        )
        
    except Exception as e:
        print(f"分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.get("/api/sentiment/history/{user_id}")
async def get_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取用户的情感分析历史"""
    
    try:
        records = db.query(SentimentRecord).filter(
            SentimentRecord.user_id == user_id
        ).order_by(SentimentRecord.created_at.desc()).limit(limit).all()
        
        return [record.to_dict() for record in records]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@app.get("/api/sentiment/stats/{user_id}", response_model=SentimentStats)
async def get_stats(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取用户的情感统计"""
    
    try:
        # 获取指定时间范围内的记录
        start_date = datetime.utcnow() - timedelta(days=days)
        records = db.query(SentimentRecord).filter(
            SentimentRecord.user_id == user_id,
            SentimentRecord.created_at >= start_date
        ).order_by(SentimentRecord.created_at).all()
        
        if not records:
            return SentimentStats(
                total_records=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                average_intensity=0,
                most_common_emotions=[],
                trends=[]
            )
        
        # 统计基础数据
        positive_count = sum(1 for r in records if r.sentiment == 'positive')
        negative_count = sum(1 for r in records if r.sentiment == 'negative')
        neutral_count = sum(1 for r in records if r.sentiment == 'neutral')
        
        # 计算平均强度
        avg_intensity = sum(r.intensity or 0 for r in records) / len(records)
        
        # 统计最常见的情绪
        emotion_counts = {}
        for record in records:
            try:
                emotions = json.loads(record.emotions) if isinstance(record.emotions, str) else record.emotions
                for emotion in emotions:
                    name = emotion.get('name', 'unknown')
                    intensity = emotion.get('intensity', 0)
                    if name in emotion_counts:
                        emotion_counts[name]['count'] += 1
                        emotion_counts[name]['total_intensity'] += intensity
                    else:
                        emotion_counts[name] = {'count': 1, 'total_intensity': intensity}
            except:
                pass
        
        most_common = sorted(
            emotion_counts.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )[:5]
        
        most_common_emotions = [
            EmotionDetail(
                name=name,
                intensity=data['total_intensity'] / data['count']
            )
            for name, data in most_common
        ]
        
        # 计算趋势（按天分组）
        trends_dict = {}
        for record in records:
            date_key = record.created_at.strftime('%Y-%m-%d')
            if date_key not in trends_dict:
                trends_dict[date_key] = {
                    'sentiments': [],
                    'emotions': {}
                }
            
            # 情感得分：positive=1, neutral=0, negative=-1
            sentiment_score = {
                'positive': 1,
                'neutral': 0,
                'negative': -1
            }.get(record.sentiment, 0)
            
            trends_dict[date_key]['sentiments'].append(sentiment_score)
            
            # 统计情绪
            try:
                emotions = json.loads(record.emotions) if isinstance(record.emotions, str) else record.emotions
                for emotion in emotions:
                    name = emotion.get('name', 'unknown')
                    intensity = emotion.get('intensity', 0)
                    if name in trends_dict[date_key]['emotions']:
                        trends_dict[date_key]['emotions'][name].append(intensity)
                    else:
                        trends_dict[date_key]['emotions'][name] = [intensity]
            except:
                pass
        
        # 构建趋势列表
        trends = []
        for date_key in sorted(trends_dict.keys()):
            data = trends_dict[date_key]
            avg_sentiment = sum(data['sentiments']) / len(data['sentiments'])
            
            emotion_dist = {
                name: sum(intensities) / len(intensities)
                for name, intensities in data['emotions'].items()
            }
            
            trends.append(SentimentTrend(
                date=date_key,
                sentiment_score=avg_sentiment,
                emotion_distribution=emotion_dist
            ))
        
        return SentimentStats(
            total_records=len(records),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            average_intensity=avg_intensity,
            most_common_emotions=most_common_emotions,
            trends=trends
        )
        
    except Exception as e:
        print(f"统计错误: {e}")
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")


@app.get("/api/health/assessment/{user_id}", response_model=HealthAssessment)
async def assess_health(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """心理健康评估"""
    
    try:
        # 获取指定时间范围内的记录
        start_date = datetime.utcnow() - timedelta(days=days)
        records = db.query(SentimentRecord).filter(
            SentimentRecord.user_id == user_id,
            SentimentRecord.created_at >= start_date
        ).order_by(SentimentRecord.created_at.desc()).all()
        
        # 转换为字典列表
        records_dicts = [record.to_dict() for record in records]
        
        # 使用LLM进行评估
        assessment = llm_service.assess_mental_health(records_dicts)
        
        return HealthAssessment(
            overall_score=assessment.get('overall_score', 70),
            risk_level=assessment.get('risk_level', 'low'),
            key_concerns=assessment.get('key_concerns', []),
            recommendations=assessment.get('recommendations', []),
            detailed_analysis=assessment.get('detailed_analysis', '')
        )
        
    except Exception as e:
        print(f"评估错误: {e}")
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")


@app.get("/api/knowledge/search")
async def search_knowledge(emotion: str = None, query: str = None):
    """搜索心理健康知识库"""
    
    try:
        if emotion:
            results = rag_service.search_by_emotion(emotion, top_k=5)
        elif query:
            results = rag_service.retrieve_relevant_knowledge(query, top_k=5)
        else:
            return {"error": "请提供emotion或query参数"}
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "siliconflow_configured": bool(settings.siliconflow_api_key)
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  智能情感分析与心理健康辅助系统                          ║
    ║  Intelligent Sentiment Analysis & Mental Health System   ║
    ╠══════════════════════════════════════════════════════════╣
    ║  服务地址: http://{settings.host}:{settings.port}                    ║
    ║  API文档: http://{settings.host}:{settings.port}/docs                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
