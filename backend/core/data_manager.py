"""
数据管理器实现

负责数据持久化和统计计算
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from core import (
    IDataManager, SentimentAnalysisResult, EmotionData,
    DataValidationError, Logger, SystemConfig
)
from models import SentimentRecord, get_db


class DatabaseManager(IDataManager):
    """数据库管理器实现"""
    
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
    
    def save_analysis(self, result: SentimentAnalysisResult) -> int:
        """保存分析结果到数据库"""
        try:
            with Session(get_db().bind) as db:
                # 创建数据库记录
                db_record = SentimentRecord(
                    user_id=result.user_id,
                    text=result.text,
                    sentiment=result.sentiment,
                    confidence=result.confidence,
                    emotions=json.dumps([{"name": e.name, "intensity": e.intensity} for e in result.emotions]),
                    intensity=result.intensity,
                    analysis=result.analysis,
                    causes=result.causes,
                    suggestions=result.suggestions,
                    created_at=result.timestamp
                )
                
                db.add(db_record)
                db.commit()
                db.refresh(db_record)
                
                self.logger.info(f"保存分析结果: ID={db_record.id}, 用户={result.user_id}")
                return db_record.id
                
        except Exception as e:
            self.logger.error(f"保存分析结果失败: {str(e)}")
            raise DataValidationError(f"保存失败: {str(e)}")
    
    def get_user_history(self, user_id: str, limit: int = 100) -> List[SentimentAnalysisResult]:
        """获取用户历史记录"""
        try:
            with Session(get_db().bind) as db:
                records = db.query(SentimentRecord).filter(
                    SentimentRecord.user_id == user_id
                ).order_by(desc(SentimentRecord.created_at)).limit(limit).all()
                
                results = []
                for record in records:
                    emotions = json.loads(record.emotions) if record.emotions else []
                    emotion_data = [EmotionData(name=e["name"], intensity=e["intensity"]) for e in emotions]
                    
                    result = SentimentAnalysisResult(
                        user_id=record.user_id,
                        text=record.text,
                        sentiment=record.sentiment,
                        confidence=record.confidence,
                        emotions=emotion_data,
                        intensity=record.intensity,
                        analysis=record.analysis,
                        causes=record.causes,
                        suggestions=record.suggestions,
                        timestamp=record.created_at
                    )
                    results.append(result)
                
                self.logger.info(f"获取用户 {user_id} 的 {len(results)} 条历史记录")
                return results
                
        except Exception as e:
            self.logger.error(f"获取历史记录失败: {str(e)}")
            return []
    
    def get_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取统计数据"""
        try:
            with Session(get_db().bind) as db:
                # 计算起始日期
                start_date = datetime.now() - timedelta(days=days)
                
                # 基础统计查询
                base_query = db.query(SentimentRecord).filter(
                    SentimentRecord.user_id == user_id,
                    SentimentRecord.created_at >= start_date
                )
                
                # 总记录数
                total_records = base_query.count()
                
                if total_records == 0:
                    return {
                        "total_records": 0,
                        "positive_count": 0,
                        "negative_count": 0,
                        "neutral_count": 0,
                        "average_intensity": 0.0,
                        "most_common_emotions": [],
                        "daily_trends": []
                    }
                
                # 情感分类统计
                sentiment_stats = base_query.with_entities(
                    SentimentRecord.sentiment,
                    func.count(SentimentRecord.id).label('count')
                ).group_by(SentimentRecord.sentiment).all()
                
                positive_count = next((s.count for s in sentiment_stats if s.sentiment == 'positive'), 0)
                negative_count = next((s.count for s in sentiment_stats if s.sentiment == 'negative'), 0)
                neutral_count = next((s.count for s in sentiment_stats if s.sentiment == 'neutral'), 0)
                
                # 平均强度
                avg_intensity = base_query.with_entities(
                    func.avg(SentimentRecord.intensity)
                ).scalar() or 0.0
                
                # 最常见情绪
                emotion_stats = self._calculate_emotion_statistics(base_query.all())
                
                # 每日趋势
                daily_trends = self._calculate_daily_trends(base_query.all(), days)
                
                stats = {
                    "total_records": total_records,
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "neutral_count": neutral_count,
                    "average_intensity": round(avg_intensity, 3),
                    "most_common_emotions": emotion_stats,
                    "daily_trends": daily_trends
                }
                
                self.logger.info(f"生成用户 {user_id} 的统计数据")
                return stats
                
        except Exception as e:
            self.logger.error(f"计算统计数据失败: {str(e)}")
            return {}
    
    def _calculate_emotion_statistics(self, records: List[SentimentRecord]) -> List[Dict[str, Any]]:
        """计算情绪统计"""
        emotion_counts = {}
        emotion_intensities = {}
        
        for record in records:
            if record.emotions:
                try:
                    emotions = json.loads(record.emotions)
                    for emotion in emotions:
                        name = emotion["name"]
                        intensity = emotion["intensity"]
                        
                        if name not in emotion_counts:
                            emotion_counts[name] = 0
                            emotion_intensities[name] = []
                        
                        emotion_counts[name] += 1
                        emotion_intensities[name].append(intensity)
                except json.JSONDecodeError:
                    continue
        
        # 排序并返回前10个最常见情绪
        sorted_emotions = sorted(
            emotion_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        result = []
        for name, count in sorted_emotions:
            avg_intensity = sum(emotion_intensities[name]) / len(emotion_intensities[name])
            result.append({
                "name": name,
                "count": count,
                "average_intensity": round(avg_intensity, 3)
            })
        
        return result
    
    def _calculate_daily_trends(self, records: List[SentimentRecord], days: int) -> List[Dict[str, Any]]:
        """计算每日趋势"""
        # 按日期分组
        daily_data = {}
        
        for record in records:
            date_key = record.created_at.strftime("%Y-%m-%d")
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "intensity_sum": 0.0,
                    "count": 0
                }
            
            daily_data[date_key][record.sentiment] += 1
            daily_data[date_key]["intensity_sum"] += record.intensity
            daily_data[date_key]["count"] += 1
        
        # 生成完整的日期范围
        trends = []
        current_date = datetime.now() - timedelta(days=days-1)
        
        for i in range(days):
            date_key = current_date.strftime("%Y-%m-%d")
            data = daily_data.get(date_key, {
                "date": date_key,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "intensity_sum": 0.0,
                "count": 0
            })
            
            # 计算情感得分（积极=+1，中性=0，消极=-1）
            sentiment_score = (data["positive"] - data["negative"]) / max(data["count"], 1)
            avg_intensity = data["intensity_sum"] / max(data["count"], 1)
            
            trends.append({
                "date": date_key,
                "sentiment_score": round(sentiment_score, 3),
                "average_intensity": round(avg_intensity, 3),
                "positive": data["positive"],
                "negative": data["negative"],
                "neutral": data["neutral"],
                "total": data["count"]
            })
            
            current_date += timedelta(days=1)
        
        return trends


class InMemoryManager(IDataManager):
    """内存数据管理器（用于测试和开发）"""
    
    def __init__(self):
        self.records = []
        self.logger = Logger.get_logger(__name__)
    
    def save_analysis(self, result: SentimentAnalysisResult) -> int:
        """保存到内存"""
        record_id = len(self.records) + 1
        result.id = record_id
        self.records.append(result)
        self.logger.info(f"保存分析结果到内存: ID={record_id}")
        return record_id
    
    def get_user_history(self, user_id: str, limit: int = 100) -> List[SentimentAnalysisResult]:
        """从内存获取历史"""
        user_records = [
            r for r in self.records 
            if r.user_id == user_id
        ][:limit]
        self.logger.info(f"从内存获取用户 {user_id} 的 {len(user_records)} 条记录")
        return user_records
    
    def get_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """从内存计算统计"""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_records = [
            r for r in self.records 
            if r.user_id == user_id and r.timestamp >= cutoff_date
        ]
        
        if not user_records:
            return {
                "total_records": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "average_intensity": 0.0,
                "most_common_emotions": [],
                "daily_trends": []
            }
        
        # 简化统计计算
        positive_count = sum(1 for r in user_records if r.sentiment == "positive")
        negative_count = sum(1 for r in user_records if r.sentiment == "negative")
        neutral_count = sum(1 for r in user_records if r.sentiment == "neutral")
        avg_intensity = sum(r.intensity for r in user_records) / len(user_records)
        
        return {
            "total_records": len(user_records),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "average_intensity": round(avg_intensity, 3),
            "most_common_emotions": [],
            "daily_trends": []
        }