"""
情感分析器实现

基于大语言模型的情感分析器具体实现
"""

import json
import openai
from typing import List, Dict
from core import (
    ISentimentAnalyzer, SentimentAnalysisResult, EmotionData,
    SentimentAnalysisError, Logger, SystemConfig
)
from config import settings


class LLMAnalyzer(ISentimentAnalyzer):
    """基于LLM的情感分析器"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url
        )
        self.model = settings.siliconflow_model
        self.logger = Logger.get_logger(__name__)
    
    def analyze(self, text: str, user_id: str = "default_user") -> SentimentAnalysisResult:
        """分析单个文本的情感"""
        try:
            self.logger.info(f"开始分析文本: {text[:50]}...")
            
            # 构建分析提示
            prompt = self._build_analysis_prompt(text)
            
            # 调用LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理学家和情感分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=SystemConfig.TEMPERATURE,
                max_tokens=SystemConfig.MAX_TOKENS
            )
            
            # 解析响应
            result_json = json.loads(response.choices[0].message.content)
            
            # 转换为数据传输对象
            emotions = [
                EmotionData(name=emotion["name"], intensity=emotion["intensity"])
                for emotion in result_json.get("emotions", [])
            ]
            
            result = SentimentAnalysisResult(
                user_id=user_id,
                text=text,
                sentiment=result_json["sentiment"],
                confidence=result_json["confidence"],
                emotions=emotions,
                intensity=result_json["intensity"],
                analysis=result_json["analysis"],
                causes=result_json["causes"],
                suggestions=self._generate_suggestions(result_json["sentiment"], emotions),
                timestamp=datetime.now()
            )
            
            self.logger.info(f"分析完成: {result.sentiment} (置信度: {result.confidence:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {str(e)}")
            raise SentimentAnalysisError(f"分析失败: {str(e)}")
    
    def batch_analyze(self, texts: List[str], user_id: str = "default_user") -> List[SentimentAnalysisResult]:
        """批量分析文本情感"""
        results = []
        for text in texts:
            try:
                result = self.analyze(text, user_id)
                results.append(result)
            except SentimentAnalysisError as e:
                self.logger.warning(f"批量分析中跳过失败项: {str(e)}")
                continue
        
        return results
    
    def _build_analysis_prompt(self, text: str) -> str:
        """构建分析提示"""
        return f"""请对以下文本进行深入的情感分析，并按照JSON格式输出：

文本："{text}"

请输出以下格式的JSON：
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "emotions": [
        {{"name": "情绪名称", "intensity": 0.0-1.0}}
    ],
    "intensity": 0.0-1.0,
    "analysis": "详细的情感分析",
    "causes": "情感原因分析"
}}

情绪类型参考：快乐、悲伤、愤怒、焦虑、恐惧、惊讶、厌恶、平静、兴奋、沮丧等。"""
    
    def _generate_suggestions(self, sentiment: str, emotions: List[EmotionData]) -> str:
        """生成基础建议"""
        suggestions_map = {
            "positive": "保持积极的心态！继续做让你感到快乐的事情。",
            "negative": "感到低落是正常的。尝试深呼吸、散步或与朋友聊天。",
            "neutral": "保持平静的状态。可以尝试一些新的活动来丰富生活。"
        }
        
        base_suggestion = suggestions_map.get(sentiment, "关注自己的情感变化，适时调整。")
        
        # 根据具体情绪添加建议
        emotion_suggestions = []
        for emotion in emotions:
            if emotion.intensity > 0.7:
                if emotion.name == "焦虑":
                    emotion_suggestions.append("尝试冥想或渐进性肌肉放松来缓解焦虑。")
                elif emotion.name == "愤怒":
                    emotion_suggestions.append("深呼吸并数到10，避免冲动决策。")
                elif emotion.name == "悲伤":
                    emotion_suggestions.append("允许自己感受悲伤，同时寻求支持。")
        
        if emotion_suggestions:
            return base_suggestion + " " + " ".join(emotion_suggestions)
        
        return base_suggestion


class CachedAnalyzer(ISentimentAnalyzer):
    """带缓存的分析器装饰器"""
    
    def __init__(self, analyzer: ISentimentAnalyzer):
        self.analyzer = analyzer
        self.cache = {}
        self.cache_ttl = SystemConfig.CACHE_TTL
        self.logger = Logger.get_logger(__name__)
    
    def analyze(self, text: str, user_id: str = "default_user") -> SentimentAnalysisResult:
        """带缓存的分析"""
        cache_key = f"{user_id}_{hash(text)}"
        
        # 检查缓存
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                self.logger.info(f"使用缓存结果: {text[:30]}...")
                return cached_result
        
        # 执行分析
        result = self.analyzer.analyze(text, user_id)
        
        # 缓存结果
        self.cache[cache_key] = (result, datetime.now())
        
        # 清理过期缓存
        self._cleanup_cache()
        
        return result
    
    def batch_analyze(self, texts: List[str], user_id: str = "default_user") -> List[SentimentAnalysisResult]:
        """批量分析（带缓存）"""
        return self.analyzer.batch_analyze(texts, user_id)
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (_, timestamp) in self.cache.items():
            if (current_time - timestamp).seconds > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")


# 导入datetime
from datetime import datetime