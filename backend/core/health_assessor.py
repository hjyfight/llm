"""
健康评估器实现

基于历史数据评估用户心理健康状态
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from core import (
    IHealthAssessor, HealthScore, IDataManager, SentimentAnalysisResult,
    Logger, SystemConfig
)


class MentalHealthAssessor(IHealthAssessor):
    """心理健康评估器"""
    
    def __init__(self, data_manager: IDataManager):
        self.data_manager = data_manager
        self.logger = Logger.get_logger(__name__)
    
    def assess_health(self, user_id: str, days: int = 30) -> HealthScore:
        """评估用户心理健康"""
        try:
            self.logger.info(f"开始评估用户 {user_id} 的心理健康状态")
            
            # 获取历史数据
            history = self.data_manager.get_user_history(user_id, limit=1000)
            
            # 过滤指定天数内的数据
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                record for record in history 
                if record.timestamp >= cutoff_date
            ]
            
            if not recent_history:
                return self._create_default_assessment()
            
            # 计算各项指标
            overall_score = self._calculate_overall_score(recent_history)
            risk_level = self._determine_risk_level(overall_score)
            key_concerns = self._identify_key_concerns(recent_history)
            recommendations = self._generate_recommendations(recent_history, risk_level)
            detailed_analysis = self._generate_detailed_analysis(recent_history)
            
            assessment = HealthScore(
                overall_score=overall_score,
                risk_level=risk_level,
                key_concerns=key_concerns,
                recommendations=recommendations,
                detailed_analysis=detailed_analysis
            )
            
            self.logger.info(f"健康评估完成: 得分={overall_score:.1f}, 风险等级={risk_level}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"健康评估失败: {str(e)}")
            return self._create_default_assessment()
    
    def get_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取情感趋势"""
        try:
            stats = self.data_manager.get_statistics(user_id, days)
            
            if not stats or stats.get("total_records", 0) == 0:
                return {
                    "trend_direction": "stable",
                    "stability_score": 0.0,
                    "emotional_volatility": 0.0,
                    "improvement_rate": 0.0,
                    "patterns": []
                }
            
            # 分析趋势
            daily_trends = stats.get("daily_trends", [])
            trend_direction = self._calculate_trend_direction(daily_trends)
            stability_score = self._calculate_stability_score(daily_trends)
            emotional_volatility = self._calculate_volatility(daily_trends)
            improvement_rate = self._calculate_improvement_rate(daily_trends)
            patterns = self._identify_patterns(daily_trends)
            
            trends = {
                "trend_direction": trend_direction,
                "stability_score": stability_score,
                "emotional_volatility": emotional_volatility,
                "improvement_rate": improvement_rate,
                "patterns": patterns
            }
            
            self.logger.info(f"趋势分析完成: 方向={trend_direction}, 稳定性={stability_score:.2f}")
            return trends
            
        except Exception as e:
            self.logger.error(f"趋势分析失败: {str(e)}")
            return {}
    
    def _calculate_overall_score(self, records: List[SentimentAnalysisResult]) -> float:
        """计算总体健康得分"""
        if not records:
            return 50.0  # 默认中等得分
        
        # 基础分数计算
        positive_ratio = sum(1 for r in records if r.sentiment == "positive") / len(records)
        negative_ratio = sum(1 for r in records if r.sentiment == "negative") / len(records)
        neutral_ratio = sum(1 for r in records if r.sentiment == "neutral") / len(records)
        
        # 情感强度调整
        avg_intensity = sum(r.intensity for r in records) / len(records)
        
        # 置信度调整
        avg_confidence = sum(r.confidence for r in records) / len(records)
        
        # 综合计算
        base_score = (positive_ratio * 100 + neutral_ratio * 70 + negative_ratio * 30)
        intensity_adjustment = (avg_intensity - 0.5) * 20  # 强度调整
        confidence_adjustment = (avg_confidence - 0.5) * 10  # 置信度调整
        
        final_score = base_score + intensity_adjustment + confidence_adjustment
        return max(0.0, min(100.0, final_score))
    
    def _determine_risk_level(self, score: float) -> str:
        """确定风险等级"""
        if score >= 70:
            return "low"
        elif score >= 40:
            return "medium"
        else:
            return "high"
    
    def _identify_key_concerns(self, records: List[SentimentAnalysisResult]) -> List[str]:
        """识别主要关注点"""
        concerns = []
        
        # 分析负面情绪频率
        negative_count = sum(1 for r in records if r.sentiment == "negative")
        if negative_count / len(records) > 0.5:
            concerns.append("负面情绪频率较高")
        
        # 分析高强度负面情绪
        high_intensity_negative = sum(1 for r in records 
                                    if r.sentiment == "negative" and r.intensity > 0.7)
        if high_intensity_negative > len(records) * 0.3:
            concerns.append("存在高强度负面情绪")
        
        # 分析特定情绪模式
        emotion_counts = {}
        for record in records:
            for emotion in record.emotions:
                if emotion.name in ["焦虑", "愤怒", "恐惧", "悲伤"]:
                    emotion_counts[emotion.name] = emotion_counts.get(emotion.name, 0) + emotion.intensity
        
        for emotion_name, total_intensity in emotion_counts.items():
            if total_intensity > len(records) * 0.5:
                concerns.append(f"{emotion_name}情绪较为突出")
        
        # 分析趋势
        recent_records = records[-5:]  # 最近5条记录
        if len(recent_records) >= 3:
            recent_negative_ratio = sum(1 for r in recent_records if r.sentiment == "negative") / len(recent_records)
            if recent_negative_ratio > 0.6:
                concerns.append("近期情绪状态恶化")
        
        return concerns if concerns else ["无明显关注点"]
    
    def _generate_recommendations(self, records: List[SentimentAnalysisResult], risk_level: str) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于风险等级的基础建议
        if risk_level == "high":
            recommendations.extend([
                "建议寻求专业心理咨询师的帮助",
                "考虑与信任的朋友或家人交流",
                "保持规律的作息和健康的生活方式"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "尝试放松技巧，如深呼吸或冥想",
                "增加社交活动和体育锻炼",
                "记录情绪日记，了解情绪变化规律"
            ])
        else:
            recommendations.extend([
                "继续保持积极的生活态度",
                "帮助他人可以提升自己的幸福感",
                "设定新的目标和挑战"
            ])
        
        # 基于情绪模式的针对性建议
        emotion_patterns = self._analyze_emotion_patterns(records)
        if "焦虑" in emotion_patterns:
            recommendations.append("练习正念冥想来缓解焦虑")
        if "愤怒" in emotion_patterns:
            recommendations.append("学习情绪管理技巧，如暂停-思考-反应")
        if "悲伤" in emotion_patterns:
            recommendations.append("寻求社交支持，避免孤立自己")
        
        return recommendations[:5]  # 最多返回5条建议
    
    def _generate_detailed_analysis(self, records: List[SentimentAnalysisResult]) -> str:
        """生成详细分析"""
        if not records:
            return "暂无足够数据进行分析。"
        
        total_records = len(records)
        positive_ratio = sum(1 for r in records if r.sentiment == "positive") / total_records
        negative_ratio = sum(1 for r in records if r.sentiment == "negative") / total_records
        avg_intensity = sum(r.intensity for r in records) / total_records
        
        analysis = f"在过去{len(records)}条情感记录中，"
        analysis += f"积极情绪占比{positive_ratio:.1%}，"
        analysis += f"消极情绪占比{negative_ratio:.1%}，"
        analysis += f"平均情感强度为{avg_intensity:.2f}。"
        
        if negative_ratio > 0.5:
            analysis += "负面情绪占比较高，建议关注心理健康状况。"
        elif positive_ratio > 0.6:
            analysis += "整体情绪状态良好，继续保持积极的生活态度。"
        else:
            analysis += "情绪状态相对平衡，建议关注情绪变化趋势。"
        
        return analysis
    
    def _calculate_trend_direction(self, daily_trends: List[Dict]) -> str:
        """计算趋势方向"""
        if len(daily_trends) < 7:
            return "insufficient_data"
        
        # 取前半段和后半段的平均情感得分
        mid_point = len(daily_trends) // 2
        first_half_avg = sum(d.get("sentiment_score", 0) for d in daily_trends[:mid_point]) / mid_point
        second_half_avg = sum(d.get("sentiment_score", 0) for d in daily_trends[mid_point:]) / (len(daily_trends) - mid_point)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_stability_score(self, daily_trends: List[Dict]) -> float:
        """计算稳定性得分"""
        if len(daily_trends) < 3:
            return 0.0
        
        scores = [d.get("sentiment_score", 0) for d in daily_trends]
        mean_score = sum(scores) / len(scores)
        
        # 计算方差
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # 转换为稳定性得分（方差越小，稳定性越高）
        stability = max(0.0, 1.0 - variance)
        return round(stability, 3)
    
    def _calculate_volatility(self, daily_trends: List[Dict]) -> float:
        """计算情感波动性"""
        if len(daily_trends) < 3:
            return 0.0
        
        scores = [d.get("sentiment_score", 0) for d in daily_trends]
        
        # 计算相邻天的差异
        differences = []
        for i in range(1, len(scores)):
            differences.append(abs(scores[i] - scores[i-1]))
        
        # 平均波动性
        volatility = sum(differences) / len(differences) if differences else 0.0
        return round(volatility, 3)
    
    def _calculate_improvement_rate(self, daily_trends: List[Dict]) -> float:
        """计算改善率"""
        if len(daily_trends) < 7:
            return 0.0
        
        # 计算线性回归斜率
        n = len(daily_trends)
        x = list(range(n))
        y = [d.get("sentiment_score", 0) for d in daily_trends]
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0.0
        return round(slope, 4)
    
    def _identify_patterns(self, daily_trends: List[Dict]) -> List[str]:
        """识别情绪模式"""
        patterns = []
        
        if len(daily_trends) < 7:
            return patterns
        
        # 周期性模式
        weekly_patterns = []
        for i in range(7, len(daily_trends)):
            if daily_trends[i]["sentiment_score"] > daily_trends[i-7]["sentiment_score"]:
                weekly_patterns.append("weekly_improvement")
        
        if len(weekly_patterns) > len(daily_trends) * 0.3:
            patterns.append("存在周周期性改善模式")
        
        # 连续负面模式
        consecutive_negative = 0
        max_consecutive_negative = 0
        for day in daily_trends:
            if day.get("sentiment_score", 0) < -0.2:
                consecutive_negative += 1
                max_consecutive_negative = max(max_consecutive_negative, consecutive_negative)
            else:
                consecutive_negative = 0
        
        if max_consecutive_negative >= 3:
            patterns.append("存在连续负面情绪模式")
        
        return patterns
    
    def _analyze_emotion_patterns(self, records: List[SentimentAnalysisResult]) -> List[str]:
        """分析情绪模式"""
        emotion_counts = {}
        for record in records:
            for emotion in record.emotions:
                if emotion.intensity > 0.6:  # 只考虑高强度情绪
                    emotion_counts[emotion.name] = emotion_counts.get(emotion.name, 0) + 1
        
        # 返回出现频率较高的情绪
        threshold = len(records) * 0.3
        return [emotion for emotion, count in emotion_counts.items() if count > threshold]
    
    def _create_default_assessment(self) -> HealthScore:
        """创建默认评估"""
        return HealthScore(
            overall_score=50.0,
            risk_level="medium",
            key_concerns=["数据不足，无法准确评估"],
            recommendations=["请提供更多情感数据以便进行准确评估"],
            detailed_analysis="暂无足够的历史数据来进行心理健康评估。建议先进行几次情感分析。"
        )