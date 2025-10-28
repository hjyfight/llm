# 系统架构文档

## 整体架构

本系统采用前后端分离架构，使用大语言模型(LLM)进行情感分析，并结合RAG技术提供专业建议。

### 技术栈总览

| 层级 | 技术 | 作用 |
|-----|------|------|
| 前端 | React 18 | UI框架 |
| 前端可视化 | Chart.js | 数据可视化 |
| 后端框架 | FastAPI | Web API服务 |
| 大模型 | SiliconFlow API (Qwen) | 情感分析、建议生成 |
| LLM框架 | LangChain | LLM应用开发 |
| 向量数据库 | ChromaDB | RAG知识检索 |
| 关系数据库 | SQLite | 结构化数据存储 |
| 数据验证 | Pydantic | 数据模型和验证 |

## 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户界面层                              │
│                      (React Frontend)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 情感分析     │  │ 历史记录     │  │ 数据可视化   │          │
│  │ 输入界面     │  │ 查看界面     │  │ 统计图表     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ 健康评估     │  │ 知识库查询   │                            │
│  │ 报告展示     │  │ 界面         │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST API (JSON)
┌─────────────────────────▼───────────────────────────────────────┐
│                        API网关层                                 │
│                     (FastAPI Router)                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ CORS中间件 │ 请求验证 │ 错误处理 │ 日志记录             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  API端点：                                                       │
│  • POST /api/sentiment/analyze      - 情感分析                 │
│  • GET  /api/sentiment/history      - 历史查询                 │
│  • GET  /api/sentiment/stats        - 统计分析                 │
│  • GET  /api/health/assessment      - 健康评估                 │
│  • GET  /api/knowledge/search       - 知识检索                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                       业务逻辑层                                 │
│                   (Business Logic)                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  LLM Service     │  │  RAG Service     │                    │
│  │  情感分析        │  │  知识检索        │                    │
│  │  建议生成        │  │  语义搜索        │                    │
│  │  健康评估        │  │  知识库管理      │                    │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                     │                               │
│  ┌────────▼─────────────────────▼─────────┐                    │
│  │      数据处理与聚合服务                 │                    │
│  │  • 历史数据查询与统计                  │                    │
│  │  • 趋势分析与可视化数据生成            │                    │
│  │  • 情感模式识别                        │                    │
│  └────────────────────────────────────────┘                    │
└─────────┬──────────────────────────┬────────────────────────────┘
          │                          │
┌─────────▼──────────┐   ┌──────────▼────────┐
│   外部服务层        │   │   数据持久化层     │
│                    │   │                   │
│  SiliconFlow API   │   │  SQLite           │
│  ┌──────────────┐  │   │  ┌─────────────┐  │
│  │ Qwen Models  │  │   │  │sentiment_   │  │
│  │  情感分析    │  │   │  │records      │  │
│  │  文本生成    │  │   │  └─────────────┘  │
│  └──────────────┘  │   │                   │
│                    │   │  ChromaDB         │
│                    │   │  ┌─────────────┐  │
│                    │   │  │mental_health│  │
│                    │   │  │_knowledge   │  │
│                    │   │  └─────────────┘  │
└────────────────────┘   └───────────────────┘
```

## 数据流程

### 1. 情感分析流程

```
用户输入文本
    │
    ├─ 前端验证（非空检查）
    │
    ▼
发送POST请求到 /api/sentiment/analyze
    │
    ├─ Pydantic数据验证
    ├─ 提取user_id和text
    │
    ▼
调用 LLM Service
    │
    ├─ 构建Prompt（包含分析指导）
    ├─ 调用GPT-4 API
    ├─ 解析JSON响应
    │   ├─ sentiment (positive/negative/neutral)
    │   ├─ confidence (0-1)
    │   ├─ emotions [{name, intensity}, ...]
    │   ├─ intensity (0-1)
    │   ├─ analysis (文本)
    │   └─ causes (文本)
    │
    ▼
并行处理：
    │
    ├─ 查询用户历史记录（SQLite）
    │   └─ 最近10条记录用于个性化
    │
    ├─ RAG知识检索（ChromaDB）
    │   ├─ 提取主要情绪关键词
    │   ├─ 语义检索相关知识（Top 3）
    │   └─ 返回专业建议
    │
    └─ 生成个性化建议（GPT-4）
        ├─ 输入：情感分析结果 + 用户历史 + 检索知识
        ├─ 生成：个性化、可操作的建议
        └─ 字数：300-500字
    │
    ▼
数据聚合与存储
    │
    ├─ 合并所有分析结果
    ├─ 创建SentimentRecord对象
    ├─ 保存到SQLite数据库
    └─ 返回完整的分析报告
    │
    ▼
前端接收并展示
    │
    ├─ 情感分类徽章
    ├─ 情绪标签列表
    ├─ 情感强度进度条
    ├─ 详细分析文本
    └─ 个性化建议框
```

### 2. 统计分析流程

```
用户请求统计数据
    │
    ▼
GET /api/sentiment/stats/{user_id}?days=30
    │
    ├─ 查询指定时间范围内的所有记录
    │   └─ WHERE user_id = ? AND created_at >= ?
    │
    ▼
数据聚合计算
    │
    ├─ 基础统计
    │   ├─ total_records
    │   ├─ positive_count
    │   ├─ negative_count
    │   └─ neutral_count
    │
    ├─ 情感强度
    │   └─ average_intensity = SUM(intensity) / COUNT(*)
    │
    ├─ 情绪统计
    │   ├─ 解析每条记录的emotions JSON
    │   ├─ 统计每种情绪出现次数和平均强度
    │   └─ 排序返回Top 5
    │
    └─ 趋势计算
        ├─ 按日期分组
        ├─ 计算每天的平均sentiment_score
        │   (positive=1, neutral=0, negative=-1)
        └─ 统计每天的情绪分布
    │
    ▼
返回可视化数据
    │
    ├─ 统计卡片数据（total, average等）
    ├─ 饼图数据（情感分布）
    ├─ 折线图数据（趋势）
    └─ 情绪标签云数据
```

### 3. 健康评估流程

```
用户请求健康评估
    │
    ▼
GET /api/health/assessment/{user_id}?days=30
    │
    ├─ 查询历史记录
    │   └─ 最近30天的所有记录
    │
    ▼
数据预处理
    │
    ├─ 统计基础指标
    │   ├─ 积极/消极/中性占比
    │   └─ 常见情绪频率
    │
    ├─ 提取最近5条记录的详细信息
    │   └─ 作为LLM分析的上下文
    │
    ▼
调用 LLM 进行专业评估
    │
    ├─ 构建评估Prompt
    │   ├─ 历史统计数据
    │   ├─ 最近记录摘要
    │   └─ 评估标准说明
    │
    ├─ GPT-4分析
    │   ├─ 计算overall_score (0-100)
    │   ├─ 判断risk_level (low/medium/high)
    │   ├─ 识别key_concerns
    │   ├─ 生成recommendations
    │   └─ 撰写detailed_analysis
    │
    ▼
返回评估报告
    │
    ├─ 健康得分（大字显示）
    ├─ 风险等级徽章
    ├─ 关注点列表
    ├─ 改善建议列表
    └─ 详细分析文本
```

## 核心模块设计

### 1. LLM Service

**职责：** 封装所有与大语言模型相关的操作

**关键方法：**

```python
class LLMService:
    def __init__(self):
        # 初始化OpenAI客户端
        
    def analyze_sentiment(self, text: str) -> Dict:
        """
        多维度情感分析
        
        输入：用户文本
        输出：{
            sentiment: str,
            confidence: float,
            emotions: List[{name, intensity}],
            intensity: float,
            analysis: str,
            causes: str
        }
        """
        
    def generate_suggestions(self, sentiment_data: Dict, 
                            user_history: List[Dict]) -> str:
        """
        生成个性化建议
        
        输入：情感分析结果 + 用户历史
        输出：建议文本
        """
        
    def assess_mental_health(self, records: List[Dict]) -> Dict:
        """
        心理健康评估
        
        输入：历史记录列表
        输出：{
            overall_score: float,
            risk_level: str,
            key_concerns: List[str],
            recommendations: List[str],
            detailed_analysis: str
        }
        """
```

**Prompt设计原则：**

1. **清晰的角色定义**
   ```
   你是一位专业的心理学家和情感分析专家
   ```

2. **结构化输出**
   ```
   请按照以下JSON格式输出分析结果：{...}
   ```

3. **提供示例和参考**
   ```
   情绪类型参考（不限于）：
   - 积极情绪：快乐、兴奋、满足...
   - 消极情绪：悲伤、焦虑、愤怒...
   ```

4. **注意事项说明**
   ```
   注意事项：
   1. 一段文本可能包含多种情绪
   2. 要考虑文化背景和表达习惯
   3. 注意识别隐含的情绪
   ```

5. **温度参数调优**
   - 情感分析：temperature=0.3（需要稳定性）
   - 建议生成：temperature=0.7（需要创造性）

### 2. RAG Service

**职责：** 管理心理健康知识库，提供语义检索

**关键方法：**

```python
class RAGService:
    def __init__(self):
        # 初始化ChromaDB客户端
        # 创建collection
        # 初始化知识库
        
    def _initialize_knowledge_base(self):
        """
        初始化心理健康知识库
        
        知识条目结构：
        {
            id: str,
            content: str,
            category: str,  # anxiety, sadness, stress等
            technique: str   # breathing, cognitive, behavioral等
        }
        """
        
    def retrieve_relevant_knowledge(self, query: str, 
                                    emotion_categories: List[str], 
                                    top_k: int) -> List[Dict]:
        """
        检索相关知识
        
        检索策略：
        1. 语义检索（Embedding相似度）
        2. 分类过滤（基于emotion_categories）
        3. Top-K排序
        """
        
    def search_by_emotion(self, emotion: str, top_k: int) -> List[Dict]:
        """
        根据情绪类别搜索
        
        映射关系：
        joy -> positive
        anxiety -> anxiety
        sadness -> sadness
        anger -> anger
        stress -> stress
        """
```

**知识库设计：**

- **分类体系：**
  - 焦虑管理 (anxiety)
  - 抑郁支持 (sadness)
  - 压力管理 (stress)
  - 愤怒控制 (anger)
  - 孤独应对 (loneliness)
  - 通用建议 (general)
  - 危机干预 (crisis)

- **技巧类型：**
  - 呼吸练习 (breathing)
  - 认知重构 (cognitive)
  - 行为激活 (behavioral)
  - 时间管理 (time_management)
  - 运动 (exercise)
  - 正念 (mindfulness)
  - 社交支持 (support)

### 3. 数据模型

**SentimentRecord (SQLAlchemy ORM)**

```python
class SentimentRecord(Base):
    __tablename__ = "sentiment_records"
    
    id: int                 # 主键
    user_id: str           # 用户ID（索引）
    text: str              # 原始文本
    
    # 情感分析结果
    sentiment: str         # positive/negative/neutral
    confidence: float      # 0-1
    emotions: str          # JSON: [{name, intensity}, ...]
    intensity: float       # 0-1
    
    # 分析详情
    analysis: str          # 详细分析文本
    causes: str            # 情感原因
    suggestions: str       # 个性化建议
    
    # 元数据
    created_at: datetime   # 创建时间
```

## 性能优化策略

### 1. 缓存机制

```python
# 语义相似度缓存
# 如果用户输入与历史输入相似度 > 0.95，直接返回缓存结果
def get_cached_result(text, user_id):
    # 计算embedding
    # 在历史记录中搜索相似文本
    # 如果找到，返回缓存结果
```

### 2. 异步处理

```python
# FastAPI支持异步
async def analyze_sentiment(request):
    # 主要分析（同步，用户等待）
    result = await llm_service.analyze_sentiment(text)
    
    # 次要任务（异步，后台执行）
    background_tasks.add_task(update_user_stats, user_id)
    background_tasks.add_task(check_risk_alerts, user_id)
```

### 3. 批处理

```python
# 定期批处理任务
# 避免频繁的小任务调用LLM

scheduler.add_job(
    func=generate_daily_reports,
    trigger="cron",
    hour=8
)
```

### 4. 数据库优化

```python
# 索引
CREATE INDEX idx_user_created ON sentiment_records(user_id, created_at);

# 查询优化
# 使用分页
# 只查询需要的字段
```

## 安全性设计

### 1. API安全

- CORS配置（限制允许的域名）
- 请求频率限制（Rate Limiting）
- 输入验证（Pydantic）
- SQL注入防护（ORM）

### 2. 数据隐私

- API Key环境变量管理
- 敏感数据加密存储
- 日志脱敏
- GDPR合规（数据删除接口）

### 3. 错误处理

```python
try:
    result = llm_service.analyze_sentiment(text)
except OpenAIError as e:
    # LLM服务错误
    return fallback_response
except Exception as e:
    # 其他错误
    log_error(e)
    return error_response
```

## 部署架构

### 开发环境

```
localhost:3000  ← React Dev Server
localhost:8000  ← FastAPI (uvicorn --reload)
```

### 生产环境（建议）

```
┌─────────────┐
│  Nginx      │  ← 反向代理、静态文件服务
│  (80/443)   │
└──────┬──────┘
       │
       ├─→ /api/*  ─→  FastAPI (Gunicorn + Uvicorn)
       │                 (多worker)
       │
       └─→ /*      ─→  React Build (静态文件)

数据库：
- SQLite (小规模) / PostgreSQL (大规模)
- ChromaDB (持久化目录)
```

### 扩展性考虑

1. **水平扩展：** 多个FastAPI实例 + 负载均衡
2. **缓存层：** Redis缓存频繁查询的结果
3. **消息队列：** RabbitMQ/Celery处理异步任务
4. **微服务化：** 
   - 情感分析服务
   - RAG检索服务
   - 统计分析服务
   - 用户管理服务

## 监控与日志

### 日志设计

```python
import logging

logger = logging.getLogger(__name__)

# 关键操作记录
logger.info(f"User {user_id} submitted text for analysis")
logger.info(f"LLM analysis completed in {duration}s")
logger.warning(f"Low confidence result: {confidence}")
logger.error(f"LLM API error: {error}")
```

### 监控指标

- API响应时间
- LLM API调用次数和成本
- 错误率
- 用户活跃度
- 数据库查询性能

### 告警机制

- API错误率 > 5% → 告警
- LLM API响应时间 > 10s → 告警
- 数据库连接失败 → 告警
- 磁盘空间不足 → 告警

## 测试策略

### 单元测试

```python
# test_llm_service.py
def test_analyze_sentiment():
    text = "我今天很开心"
    result = llm_service.analyze_sentiment(text)
    assert result['sentiment'] == 'positive'
    assert len(result['emotions']) > 0
```

### 集成测试

```python
# test_api.py
def test_sentiment_analysis_endpoint():
    response = client.post("/api/sentiment/analyze", json={
        "text": "测试文本",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    assert 'sentiment' in response.json()
```

### 性能测试

```bash
# 使用locust或ab进行压力测试
ab -n 1000 -c 10 http://localhost:8000/api/health
```

## 未来架构演进

### 短期（1-3个月）

- 添加Redis缓存层
- 实现请求限流
- 优化数据库查询

### 中期（3-6个月）

- 微服务化拆分
- 引入消息队列
- 实现分布式追踪

### 长期（6-12个月）

- 私有化部署方案
- 模型微调和本地化
- 多租户架构
- 容器化部署（Docker + K8s）
