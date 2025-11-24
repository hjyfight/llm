"""
知识检索器实现

基于RAG的知识检索和建议生成
"""

from typing import List, Dict, Any, Optional
from core import (
    IKnowledgeRetriever, Logger, SystemConfig
)
from rag_service import RAGService


class MentalHealthKnowledgeRetriever(IKnowledgeRetriever):
    """心理健康知识检索器"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.logger = Logger.get_logger(__name__)
    
    def search_knowledge(self, query: str, emotion: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索相关知识"""
        try:
            self.logger.info(f"搜索知识: query={query}, emotion={emotion}")
            
            # 构建搜索查询
            search_query = self._build_search_query(query, emotion)
            
            # 使用RAG服务搜索
            results = self.rag_service.search_knowledge(search_query, limit)
            
            # 处理结果
            processed_results = []
            for result in results:
                processed_result = {
                    "id": result.get("id", ""),
                    "content": result.get("content", ""),
                    "category": result.get("category", ""),
                    "technique": result.get("technique", ""),
                    "relevance_score": result.get("relevance_score", 0.0),
                    "source": "mental_health_knowledge_base"
                }
                processed_results.append(processed_result)
            
            self.logger.info(f"返回 {len(processed_results)} 条知识结果")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"知识搜索失败: {str(e)}")
            return []
    
    def get_suggestions(self, emotion: str, context: str = None) -> List[str]:
        """获取个性化建议"""
        try:
            self.logger.info(f"获取建议: emotion={emotion}")
            
            # 基于情绪的基础建议
            base_suggestions = self._get_base_suggestions(emotion)
            
            # 基于上下文的增强建议
            context_suggestions = []
            if context:
                context_suggestions = self._get_context_suggestions(emotion, context)
            
            # 搜索相关知识并生成建议
            knowledge_suggestions = []
            knowledge_results = self.search_knowledge(emotion, emotion, limit=3)
            for result in knowledge_results:
                if result.get("content"):
                    knowledge_suggestions.append(result["content"][:100] + "...")
            
            # 合并并去重
            all_suggestions = base_suggestions + context_suggestions + knowledge_suggestions
            unique_suggestions = list(dict.fromkeys(all_suggestions))  # 保持顺序去重
            
            return unique_suggestions[:5]  # 最多返回5条建议
            
        except Exception as e:
            self.logger.error(f"获取建议失败: {str(e)}")
            return ["建议寻求专业帮助"]
    
    def _build_search_query(self, query: str, emotion: str = None) -> str:
        """构建搜索查询"""
        if emotion:
            return f"{emotion} {query}"
        return query
    
    def _get_base_suggestions(self, emotion: str) -> List[str]:
        """基于情绪的基础建议"""
        suggestion_map = {
            "positive": [
                "继续保持积极的心态！",
                "分享你的快乐，让正能量传递给他人。",
                "记录下美好的时刻，培养感恩的心态。"
            ],
            "negative": [
                "允许自己感受负面情绪，这是正常的。",
                "尝试深呼吸练习，有助于缓解压力。",
                "与信任的朋友或家人交流你的感受。"
            ],
            "neutral": [
                "保持平和的心态，这是很好的状态。",
                "可以尝试一些新的活动来丰富生活。",
                "关注当下，练习正念冥想。"
            ]
        }
        
        return suggestion_map.get(emotion, ["关注自己的情绪变化，适时调整。"])
    
    def _get_context_suggestions(self, emotion: str, context: str) -> List[str]:
        """基于上下文的建议"""
        suggestions = []
        context_lower = context.lower()
        
        # 基于关键词的上下文分析
        if "工作" in context_lower or "job" in context_lower:
            if emotion == "negative":
                suggestions.extend([
                    "工作压力很大时，记得适当休息和放松。",
                    "尝试时间管理技巧，合理安排工作任务。"
                ])
            elif emotion == "positive":
                suggestions.extend([
                    "工作成就感很棒，继续保持这种状态！",
                    "可以考虑分享你的工作经验，帮助同事。"
                ])
        
        if "学习" in context_lower or "study" in context_lower:
            suggestions.extend([
                "学习过程中的情绪波动是正常的。",
                "制定合理的学习计划，避免过度压力。"
            ])
        
        if "家庭" in context_lower or "family" in context_lower:
            suggestions.extend([
                "家庭关系很重要，多花时间与家人沟通。",
                "学会设定健康的家庭边界。"
            ])
        
        if "健康" in context_lower or "health" in context_lower:
            if emotion == "negative":
                suggestions.extend([
                    "关注健康问题时，保持积极的心态很重要。",
                    "定期体检，遵循医生的建议。"
                ])
        
        return suggestions


class CachedKnowledgeRetriever(IKnowledgeRetriever):
    """带缓存的知识检索器"""
    
    def __init__(self, retriever: IKnowledgeRetriever):
        self.retriever = retriever
        self.cache = {}
        self.cache_ttl = SystemConfig.CACHE_TTL
        self.logger = Logger.get_logger(__name__)
    
    def search_knowledge(self, query: str, emotion: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """带缓存的知识搜索"""
        cache_key = f"search_{query}_{emotion}_{limit}"
        
        # 检查缓存
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                self.logger.info(f"使用缓存的知识搜索结果: {query}")
                return cached_result
        
        # 执行搜索
        result = self.retriever.search_knowledge(query, emotion, limit)
        
        # 缓存结果
        self.cache[cache_key] = (result, datetime.now())
        
        return result
    
    def get_suggestions(self, emotion: str, context: str = None) -> List[str]:
        """带缓存的建议获取"""
        cache_key = f"suggestions_{emotion}_{hash(context) if context else 'none'}"
        
        # 检查缓存
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                self.logger.info(f"使用缓存的建议结果: {emotion}")
                return cached_result
        
        # 获取建议
        result = self.retriever.get_suggestions(emotion, context)
        
        # 缓存结果
        self.cache[cache_key] = (result, datetime.now())
        
        return result


# 导入datetime
from datetime import datetime