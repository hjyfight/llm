# 使用说明文档

## 快速开始

### 环境要求

- **Node.js**: 16.x 或更高版本
- **Python**: 3.10 或更高版本
- **OpenAI API Key**: 需要有效的OpenAI API密钥

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd sentiment-analysis-llm-app
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 OPENAI_API_KEY
```

**.env 文件配置示例：**

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./sentiment_analysis.db
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

**启动后端服务：**

```bash
python main.py
```

后端服务将在 `http://localhost:8000` 启动

访问API文档：`http://localhost:8000/docs`

#### 3. 前端设置

打开新终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端应用将在 `http://localhost:3000` 自动打开

## 功能使用指南

### 1. 情感分析

**步骤：**

1. 在主界面的"💭 情感分析"标签中
2. 在文本框中输入你想分析的内容（如日记、心情描述等）
3. 点击"开始分析"按钮
4. 等待几秒钟，系统将返回详细的分析结果

**示例文本：**

```
今天的工作压力很大，虽然完成了任务，但总觉得不够好。
明天还有一个重要的presentation，有点担心。
```

**分析结果包括：**

- **情感分类**: 积极/消极/中性，带置信度
- **识别的情绪**: 具体情绪标签（如焦虑、压力、疲惫）及强度
- **情感强度**: 总体情感强度的可视化进度条
- **详细分析**: LLM生成的深度分析
- **可能原因**: 情感产生的原因分析
- **个性化建议**: 基于分析结果和历史数据的建议

**技巧：**

- 输入越详细，分析越准确
- 描述具体的情境和感受
- 可以多次使用，系统会记录历史并提供个性化建议

### 2. 历史记录

**功能说明：**

查看所有历史的情感分析记录，按时间倒序排列。

**使用方法：**

1. 点击"📝 历史记录"标签
2. 浏览所有历史记录
3. 每条记录显示：
   - 时间戳
   - 原始文本
   - 情感分类
   - 主要情绪

**用途：**

- 回顾过去的情感状态
- 对比不同时期的心情
- 发现情感模式

### 3. 统计分析

**功能说明：**

基于历史数据的可视化统计分析。

**包含内容：**

1. **统计卡片**
   - 总记录数
   - 平均情感强度
   - 积极情感次数
   - 消极情感次数

2. **情感分布饼图**
   - 积极、中性、消极的占比
   - 直观了解整体情感状态

3. **情感趋势折线图**
   - 显示情感得分随时间的变化
   - Y轴：-1(消极) 到 1(积极)
   - X轴：日期

4. **最常见情绪**
   - Top 5 情绪及其平均强度
   - 了解自己最常出现的情绪

**使用技巧：**

- 至少有5-10条记录后再查看统计，数据更有意义
- 定期查看趋势，了解情感变化
- 如果发现持续的消极趋势，应该引起重视

### 4. 健康评估

**功能说明：**

基于最近30天的情感数据，进行综合的心理健康评估。

**评估内容：**

1. **总体健康得分** (0-100)
   - 80-100: 心理状态良好
   - 60-79: 基本健康，有改善空间
   - 40-59: 需要关注，建议采取行动
   - 0-39: 高风险，强烈建议寻求专业帮助

2. **风险等级**
   - 低风险（绿色）
   - 中等风险（黄色）
   - 高风险（红色）

3. **主要关注点**
   - 识别当前的主要心理健康问题
   - 例如：持续焦虑、睡眠问题、社交孤立等

4. **改善建议**
   - 具体、可操作的改善措施
   - 专业的心理健康建议

5. **详细分析**
   - LLM生成的全面分析报告
   - 包括积极方面和需要改进的方面

**使用建议：**

- 每周查看一次评估报告
- 认真阅读改善建议并尝试实施
- 如果评估显示高风险，请及时寻求专业帮助
- 评估仅供参考，不能替代专业诊断

### 5. 知识库查询（开发中）

目前知识库主要在后台支持建议生成，未来版本将开放独立的知识查询功能。

## API使用指南

### 基础URL

```
http://localhost:8000
```

### 主要端点

#### 1. 健康检查

```bash
GET /api/health

# 响应
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "openai_configured": true
}
```

#### 2. 情感分析

```bash
POST /api/sentiment/analyze
Content-Type: application/json

{
  "text": "要分析的文本",
  "user_id": "用户ID（可选，默认default_user）"
}

# 响应
{
  "id": 1,
  "user_id": "default_user",
  "text": "要分析的文本",
  "sentiment": "positive",
  "confidence": 0.85,
  "emotions": [
    {"name": "joy", "intensity": 0.8},
    {"name": "excitement", "intensity": 0.6}
  ],
  "intensity": 0.75,
  "analysis": "详细分析...",
  "causes": "原因分析...",
  "suggestions": "个性化建议...",
  "created_at": "2024-01-01T12:00:00"
}
```

#### 3. 获取历史记录

```bash
GET /api/sentiment/history/{user_id}?limit=50

# 响应
[
  {
    "id": 1,
    "user_id": "default_user",
    "text": "...",
    "sentiment": "positive",
    ...
  },
  ...
]
```

#### 4. 获取统计数据

```bash
GET /api/sentiment/stats/{user_id}?days=30

# 响应
{
  "total_records": 25,
  "positive_count": 15,
  "negative_count": 7,
  "neutral_count": 3,
  "average_intensity": 0.65,
  "most_common_emotions": [
    {"name": "joy", "intensity": 0.7},
    ...
  ],
  "trends": [
    {
      "date": "2024-01-01",
      "sentiment_score": 0.5,
      "emotion_distribution": {"joy": 0.6, "anxiety": 0.3}
    },
    ...
  ]
}
```

#### 5. 心理健康评估

```bash
GET /api/health/assessment/{user_id}?days=30

# 响应
{
  "overall_score": 75,
  "risk_level": "low",
  "key_concerns": ["压力管理", "睡眠质量"],
  "recommendations": [
    "建议1...",
    "建议2..."
  ],
  "detailed_analysis": "详细评估分析..."
}
```

#### 6. 知识库检索

```bash
GET /api/knowledge/search?emotion=anxiety

# 或

GET /api/knowledge/search?query=如何应对焦虑

# 响应
{
  "results": [
    {
      "content": "焦虑管理技巧...",
      "metadata": {"category": "anxiety", "technique": "breathing"},
      "distance": 0.85
    },
    ...
  ]
}
```

### 使用curl示例

```bash
# 健康检查
curl http://localhost:8000/api/health

# 情感分析
curl -X POST http://localhost:8000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "今天心情不错", "user_id": "test_user"}'

# 获取历史
curl http://localhost:8000/api/sentiment/history/test_user

# 获取统计
curl http://localhost:8000/api/sentiment/stats/test_user?days=7

# 健康评估
curl http://localhost:8000/api/health/assessment/test_user?days=30
```

### 使用Python请求示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 情感分析
response = requests.post(
    f"{BASE_URL}/api/sentiment/analyze",
    json={
        "text": "今天工作很累，但完成了目标，有点成就感",
        "user_id": "user123"
    }
)
result = response.json()
print(f"情感: {result['sentiment']}")
print(f"建议: {result['suggestions']}")

# 获取统计
stats_response = requests.get(
    f"{BASE_URL}/api/sentiment/stats/user123?days=30"
)
stats = stats_response.json()
print(f"总记录: {stats['total_records']}")
print(f"积极: {stats['positive_count']}, 消极: {stats['negative_count']}")
```

## 常见问题

### Q1: 后端启动失败，显示 "No module named 'xxx'"

**A:** 确保已经激活虚拟环境并安装了所有依赖：

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Q2: 前端无法连接后端，显示 CORS 错误

**A:** 检查：
1. 后端服务是否正常运行（访问 http://localhost:8000/docs）
2. 前端的API_BASE_URL是否正确（在App.js中）
3. 后端CORS配置是否正确（main.py中）

### Q3: OpenAI API 调用失败

**A:** 检查：
1. .env文件中的OPENAI_API_KEY是否正确
2. API Key是否有足够的配额
3. 网络是否可以访问OpenAI API
4. 尝试使用 gpt-3.5-turbo 替代 gpt-4（更便宜，但效果稍差）

### Q4: 情感分析结果不准确

**A:** 可能的原因：
1. 输入文本太短或太模糊
2. 使用了模型不熟悉的语言或俚语
3. 可以尝试提供更多上下文信息

**改善方法：**
- 输入更详细的描述
- 包含具体的事件和感受
- 使用多次分析积累历史数据

### Q5: 数据库文件在哪里？

**A:** 
- SQLite数据库：`backend/sentiment_analysis.db`
- ChromaDB向量库：`backend/chroma_db/`

如需重置数据，删除这些文件即可。

### Q6: 如何切换用户？

**A:** 目前前端使用固定的 "default_user"。如需切换用户，可以：
1. 在代码中修改 userId 变量（App.js）
2. 或通过API直接指定不同的 user_id

未来版本将添加用户管理功能。

### Q7: 成本如何控制？

**A:** 
1. 使用 gpt-3.5-turbo 而非 gpt-4
2. 实现缓存机制避免重复分析
3. 设置API调用频率限制
4. 监控OpenAI账户使用情况

参考成本（2024年1月）：
- GPT-4: ~$0.03 per 1K tokens
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- 平均每次分析约 500-1000 tokens

### Q8: 可以离线使用吗？

**A:** 
目前依赖OpenAI API，需要网络连接。

未来计划：
- 支持本地模型（如LLaMA、ChatGLM）
- 私有化部署方案
- 离线模式（功能受限）

### Q9: 数据隐私如何保证？

**A:** 
1. 所有数据本地存储在SQLite数据库
2. 仅在分析时发送文本到OpenAI（不包含用户身份信息）
3. 可以选择自行部署私有模型
4. 定期备份和清理敏感数据

### Q10: 如何贡献代码或报告问题？

**A:** 
- 提交Issue: 描述问题或功能建议
- 提交Pull Request: 贡献代码改进
- 联系维护者讨论重大改动

## 最佳实践

### 1. 日常使用建议

- **每天记录**: 养成每天记录心情的习惯
- **详细描述**: 具体描述事件和感受，而非简单的"开心"或"难过"
- **定期回顾**: 每周查看一次统计和评估
- **采取行动**: 根据建议尝试改善情绪

### 2. 文本输入技巧

**好的输入示例：**

```
今天早上开会时，老板批评了我的方案。虽然知道他是对事不对人，
但还是觉得很受挫，担心自己能力不够。下午独自待了一会儿，
逐渐平复了心情，重新审视了方案，发现确实有改进空间。
现在感觉好多了，准备明天重新提交优化后的方案。
```

**不好的输入示例：**

```
心情不好
```

### 3. 何时寻求专业帮助

如果出现以下情况，请尽快寻求专业心理咨询：

- ⚠️ 持续两周以上的抑郁或焦虑
- ⚠️ 有自伤或自杀想法
- ⚠️ 严重影响日常生活、工作或人际关系
- ⚠️ 物质滥用问题
- ⚠️ 经历创伤事件后的持续困扰

**紧急求助热线：**
- 全国心理援助热线: 400-161-9995
- 北京心理危机干预热线: 010-82951332
- 上海心理热线: 021-12320-5

## 开发与调试

### 开发模式

```bash
# 后端 - 自动重载
cd backend
python main.py

# 前端 - 热更新
cd frontend
npm start
```

### 查看日志

```bash
# 后端日志
# 直接在终端查看

# 前端日志
# 打开浏览器开发者工具的Console
```

### 数据库管理

```bash
# 使用SQLite命令行工具
sqlite3 backend/sentiment_analysis.db

# 查看表结构
.schema sentiment_records

# 查询数据
SELECT * FROM sentiment_records ORDER BY created_at DESC LIMIT 10;

# 清空数据
DELETE FROM sentiment_records;

# 退出
.quit
```

### 调试技巧

1. **后端调试**
   - 使用print()或logging输出
   - 使用FastAPI的/docs界面测试API
   - 使用Postman或curl测试接口

2. **前端调试**
   - 使用React DevTools
   - 在浏览器Console查看网络请求
   - 使用console.log()输出状态

3. **LLM调试**
   - 检查Prompt设计
   - 查看LLM返回的原始响应
   - 调整temperature参数
   - 尝试不同的模型

## 性能优化

### 后端优化

```python
# 1. 启用缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analysis(text_hash):
    return llm_service.analyze_sentiment(text)

# 2. 批处理
async def batch_analyze(texts):
    tasks = [analyze_sentiment(text) for text in texts]
    return await asyncio.gather(*tasks)

# 3. 数据库索引
# 已在models.py中配置
```

### 前端优化

```javascript
// 1. 使用React.memo避免不必要的重渲染
const MemoizedComponent = React.memo(ExpensiveComponent);

// 2. 懒加载
const LazyChart = React.lazy(() => import('./Chart'));

// 3. 防抖输入
const debouncedAnalyze = debounce(handleAnalyze, 500);
```

## 下一步

1. **熟悉基础功能**: 使用情感分析和历史记录
2. **积累数据**: 连续使用1-2周
3. **查看统计**: 了解自己的情感模式
4. **定期评估**: 每周进行一次健康评估
5. **采取行动**: 根据建议改善心理状态

**记住：** 这是一个辅助工具，不能替代专业心理咨询。如有需要，请寻求专业帮助！
