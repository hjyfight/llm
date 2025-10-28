import json
import openai
from typing import List, Dict, Tuple
from config import settings
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain


class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
    def analyze_sentiment(self, text: str) -> Dict:
        """
        多维度情感分析
        
        使用精心设计的Prompt进行多阶段分析：
        1. 基础情感分类
        2. 细粒度情绪识别
        3. 情感强度评估
        4. 原因提取
        """
        
        prompt = f"""你是一位专业的心理学家和情感分析专家。请对以下文本进行深入的情感分析。

文本："{text}"

请按照以下JSON格式输出分析结果：

{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "emotions": [
        {{"name": "情绪名称", "intensity": 0.0-1.0}},
        ...
    ],
    "intensity": 0.0-1.0,
    "analysis": "详细的情感分析，包括情感的细微变化和复杂性",
    "causes": "分析导致这种情感的可能原因",
    "emotional_context": "情感的上下文和背景"
}}

情绪类型参考（不限于）：
- 积极情绪：快乐(joy)、兴奋(excitement)、满足(contentment)、感激(gratitude)、希望(hope)、平静(calmness)、自信(confidence)、爱(love)
- 消极情绪：悲伤(sadness)、焦虑(anxiety)、愤怒(anger)、恐惧(fear)、失望(disappointment)、孤独(loneliness)、压力(stress)、挫败(frustration)
- 中性情绪：平静(neutral_calm)、思考(contemplation)

注意事项：
1. 一段文本可能包含多种情绪，请列出所有明显的情绪
2. intensity表示该情绪在文本中的强度
3. 要考虑文化背景和表达习惯
4. 注意识别隐含的情绪（如讽刺、委婉等）

请直接返回JSON格式，不要包含其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理学家和情感分析专家。你的分析准确、专业、富有洞察力。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 较低的温度保证结果稳定性
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 提取JSON（处理可能的markdown代码块）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"情感分析错误: {e}")
            # 返回默认结果
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [{"name": "neutral_calm", "intensity": 0.5}],
                "intensity": 0.5,
                "analysis": f"分析过程中出现错误: {str(e)}",
                "causes": "无法确定",
                "emotional_context": "分析失败"
            }
    
    def generate_suggestions(self, sentiment_data: Dict, user_history: List[Dict] = None) -> str:
        """
        基于情感分析生成个性化建议
        
        考虑因素：
        1. 当前情感状态
        2. 用户历史情感趋势（如果有）
        3. 心理学专业知识
        """
        
        # 构建用户历史上下文
        history_context = ""
        if user_history and len(user_history) > 0:
            recent_sentiments = [h.get('sentiment', 'neutral') for h in user_history[-5:]]
            history_context = f"\n\n用户最近的情感状态：{', '.join(recent_sentiments)}"
        
        prompt = f"""你是一位经验丰富的心理咨询师。基于以下情感分析结果，请提供专业的、个性化的建议。

当前情感分析：
- 基础情感：{sentiment_data.get('sentiment', 'neutral')}
- 主要情绪：{', '.join([e['name'] for e in sentiment_data.get('emotions', [])])}
- 情感强度：{sentiment_data.get('intensity', 0.5)}
- 详细分析：{sentiment_data.get('analysis', '')}
- 可能原因：{sentiment_data.get('causes', '')}
{history_context}

请提供以下方面的建议：

1. **即时应对策略**：针对当前情感状态，可以立即采取的行动
2. **认知调整**：帮助重新认识和理解当前的情绪
3. **长期改善**：有助于长期心理健康的建议
4. **寻求帮助**：如果需要，何时应该寻求专业帮助

请用温暖、支持性的语言，提供具体、可操作的建议。建议应该积极正面，但不要过于简单化或忽视问题的严重性。

字数控制在300-500字之间。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位温暖、专业的心理咨询师，擅长提供具体、可操作的心理健康建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"建议生成错误: {e}")
            return "感谢你的分享。如果你持续感到困扰，建议寻求专业心理咨询师的帮助。"
    
    def assess_mental_health(self, records: List[Dict]) -> Dict:
        """
        基于历史记录评估心理健康状况
        
        分析维度：
        1. 情感波动程度
        2. 消极情绪占比
        3. 情感强度趋势
        4. 特定高风险情绪（如持续焦虑、抑郁）
        """
        
        if not records or len(records) == 0:
            return {
                "overall_score": 70,
                "risk_level": "low",
                "key_concerns": ["数据不足"],
                "recommendations": ["继续记录情感日记，积累更多数据"],
                "detailed_analysis": "数据不足，无法进行全面评估。"
            }
        
        # 准备历史数据摘要
        sentiments = [r.get('sentiment', 'neutral') for r in records]
        emotions_summary = {}
        for record in records:
            emotions_str = record.get('emotions', '[]')
            try:
                emotions = json.loads(emotions_str) if isinstance(emotions_str, str) else emotions_str
                for emotion in emotions:
                    name = emotion.get('name', 'unknown')
                    emotions_summary[name] = emotions_summary.get(name, 0) + 1
            except:
                pass
        
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        neutral_count = sentiments.count('neutral')
        
        prompt = f"""你是一位临床心理学家。请基于用户的情感记录历史，进行心理健康评估。

数据统计：
- 总记录数：{len(records)}
- 积极情感：{positive_count}次 ({positive_count/len(records)*100:.1f}%)
- 消极情感：{negative_count}次 ({negative_count/len(records)*100:.1f}%)
- 中性情感：{neutral_count}次 ({neutral_count/len(records)*100:.1f}%)
- 常见情绪：{', '.join([f'{k}({v}次)' for k, v in sorted(emotions_summary.items(), key=lambda x: x[1], reverse=True)[:5]])}

最近5条记录的分析：
{json.dumps([{
    'sentiment': r.get('sentiment'),
    'emotions': r.get('emotions'),
    'analysis': r.get('analysis', '')[:100]
} for r in records[-5:]], ensure_ascii=False, indent=2)}

请按照以下JSON格式输出评估结果：

{{
    "overall_score": 0-100的整体心理健康得分,
    "risk_level": "low/medium/high",
    "key_concerns": ["关注点1", "关注点2", ...],
    "recommendations": ["建议1", "建议2", ...],
    "detailed_analysis": "详细的评估分析，包括积极方面和需要改进的方面"
}}

评分标准：
- 80-100：心理状态良好
- 60-79：基本健康，有改善空间
- 40-59：需要关注，建议采取行动
- 0-39：高风险，强烈建议寻求专业帮助

请直接返回JSON格式，不要包含其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的临床心理学家，擅长基于行为数据进行心理健康评估。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"健康评估错误: {e}")
            return {
                "overall_score": 70,
                "risk_level": "low",
                "key_concerns": ["评估过程出错"],
                "recommendations": ["请稍后重试"],
                "detailed_analysis": f"评估失败: {str(e)}"
            }


# 全局实例
llm_service = LLMService()
