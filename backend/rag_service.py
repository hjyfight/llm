import chromadb
from chromadb.config import Settings
from typing import List, Dict
from config import settings as app_settings


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) 服务
    
    用于存储和检索心理健康知识库，增强建议的专业性和准确性
    """
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=app_settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # 获取或创建知识库集合
        self.collection = self.client.get_or_create_collection(
            name="mental_health_knowledge",
            metadata={"description": "心理健康知识库"}
        )
        
        # 初始化知识库
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化心理健康知识库"""
        
        # 检查是否已经初始化
        if self.collection.count() > 0:
            return
        
        # 心理健康知识条目
        knowledge_items = [
            {
                "id": "anxiety_management_1",
                "content": "焦虑管理：深呼吸练习是缓解焦虑的有效方法。尝试4-7-8呼吸法：吸气4秒，憋气7秒，呼气8秒。重复3-5次可以激活副交感神经系统，降低焦虑水平。",
                "category": "anxiety",
                "technique": "breathing"
            },
            {
                "id": "anxiety_management_2",
                "content": "焦虑应对：认知重构技术。当焦虑时，识别自动化负面思维，问自己：这个想法有证据吗？最坏的结果是什么？我能应对吗？这有助于打破焦虑循环。",
                "category": "anxiety",
                "technique": "cognitive"
            },
            {
                "id": "depression_support_1",
                "content": "应对悲伤：行为激活是治疗抑郁的有效方法。即使不想动，也要强迫自己做一些小事，如散步10分钟、洗澡、整理房间。行动会带来动力，而不是等待动力才行动。",
                "category": "sadness",
                "technique": "behavioral"
            },
            {
                "id": "depression_support_2",
                "content": "抑郁症状识别：如果你在两周内持续感到悲伤、失去兴趣、睡眠或食欲改变、疲劳、无价值感，这可能是抑郁症的信号。请尽快咨询专业心理健康服务。",
                "category": "sadness",
                "technique": "awareness"
            },
            {
                "id": "stress_management_1",
                "content": "压力管理：时间管理和优先级排序。使用艾森豪威尔矩阵将任务分为重要紧急、重要不紧急、不重要紧急、不重要不紧急。专注于重要的事情，学会说不。",
                "category": "stress",
                "technique": "time_management"
            },
            {
                "id": "stress_management_2",
                "content": "压力释放：规律运动是自然的抗压药。每周至少150分钟中等强度运动（如快走）可以降低皮质醇水平，增加内啡肽，改善睡眠和情绪。",
                "category": "stress",
                "technique": "exercise"
            },
            {
                "id": "anger_management_1",
                "content": "愤怒管理：暂停技巧。当感到愤怒时，给自己一个暂停。离开现场，做深呼吸，等待情绪平复后再回应。冲动时做的决定往往是最糟糕的。",
                "category": "anger",
                "technique": "pause"
            },
            {
                "id": "anger_management_2",
                "content": "表达愤怒：使用'我'语句而非'你'语句。说'我感到受伤，因为...'而不是'你总是...'。这样可以表达感受而不攻击他人，促进有效沟通。",
                "category": "anger",
                "technique": "communication"
            },
            {
                "id": "loneliness_support_1",
                "content": "孤独应对：主动连接。发起小的社交互动，如给朋友发消息、参加兴趣小组、志愿服务。质量比数量重要，一两个深度连接胜过许多浅层关系。",
                "category": "loneliness",
                "technique": "connection"
            },
            {
                "id": "sleep_hygiene_1",
                "content": "睡眠卫生：保持规律作息，即使周末也尽量同一时间睡觉和起床。睡前1小时避免屏幕，创造凉爽、黑暗、安静的睡眠环境。良好睡眠是心理健康的基础。",
                "category": "general",
                "technique": "sleep"
            },
            {
                "id": "mindfulness_1",
                "content": "正念练习：每天5-10分钟的正念冥想可以降低压力、改善注意力、增强情绪调节能力。专注于当下的呼吸和身体感觉，不评判地观察思维的来去。",
                "category": "general",
                "technique": "mindfulness"
            },
            {
                "id": "self_compassion_1",
                "content": "自我同情：像对待好朋友一样对待自己。当犯错或失败时，不要自我批评，而是用理解和善意的态度。自我同情比自我批评更能促进成长和改变。",
                "category": "general",
                "technique": "self_compassion"
            },
            {
                "id": "professional_help_1",
                "content": "何时寻求专业帮助：如果情绪困扰影响日常生活、工作或人际关系超过两周；有自伤或自杀想法；物质滥用；创伤后应激；无法通过自助方法缓解。专业帮助是力量的表现，不是弱点。",
                "category": "crisis",
                "technique": "professional"
            },
            {
                "id": "gratitude_practice_1",
                "content": "感恩练习：每天写下3件感恩的事情，可以是小事（如美味的咖啡）或大事（如家人的支持）。感恩练习可以重新训练大脑关注积极面，提升整体幸福感。",
                "category": "positive",
                "technique": "gratitude"
            },
            {
                "id": "social_support_1",
                "content": "建立支持系统：识别你的支持网络——家人、朋友、同事、治疗师。不同的人可以提供不同类型的支持。不要害怕寻求帮助，大多数人都愿意提供支持。",
                "category": "general",
                "technique": "support"
            }
        ]
        
        # 添加到向量数据库
        ids = [item["id"] for item in knowledge_items]
        documents = [item["content"] for item in knowledge_items]
        metadatas = [{k: v for k, v in item.items() if k not in ["id", "content"]} 
                     for item in knowledge_items]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"知识库初始化完成，添加了 {len(knowledge_items)} 条知识")
    
    def retrieve_relevant_knowledge(self, query: str, emotion_categories: List[str] = None, top_k: int = 3) -> List[Dict]:
        """
        检索相关的心理健康知识
        
        Args:
            query: 查询文本（通常是情感分析结果）
            emotion_categories: 情绪类别列表（用于过滤）
            top_k: 返回top k个结果
            
        Returns:
            相关知识列表
        """
        
        try:
            # 构建查询
            where_filter = None
            if emotion_categories:
                # 如果指定了情绪类别，添加过滤条件
                where_filter = {"category": {"$in": emotion_categories}}
            
            # 执行查询
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter
            )
            
            # 格式化结果
            knowledge_list = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    knowledge_list.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return knowledge_list
            
        except Exception as e:
            print(f"知识检索错误: {e}")
            return []
    
    def add_knowledge(self, content: str, category: str, technique: str, id: str = None):
        """添加新的知识条目"""
        
        import uuid
        if not id:
            id = f"custom_{uuid.uuid4().hex[:8]}"
        
        self.collection.add(
            ids=[id],
            documents=[content],
            metadatas=[{"category": category, "technique": technique}]
        )
    
    def search_by_emotion(self, emotion: str, top_k: int = 3) -> List[Dict]:
        """根据情绪类别搜索知识"""
        
        # 映射情绪到类别
        emotion_category_map = {
            "joy": "positive",
            "happiness": "positive",
            "excitement": "positive",
            "contentment": "positive",
            "gratitude": "positive",
            "anxiety": "anxiety",
            "worry": "anxiety",
            "fear": "anxiety",
            "sadness": "sadness",
            "depression": "sadness",
            "loneliness": "loneliness",
            "anger": "anger",
            "frustration": "anger",
            "stress": "stress",
            "overwhelmed": "stress"
        }
        
        category = emotion_category_map.get(emotion.lower(), "general")
        
        return self.retrieve_relevant_knowledge(
            query=f"如何应对{emotion}",
            emotion_categories=[category, "general"],
            top_k=top_k
        )


# 全局实例
rag_service = RAGService()
