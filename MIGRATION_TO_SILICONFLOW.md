# 迁移到 SiliconFlow API 说明

## 概述

本项目已从 OpenAI API 迁移到 SiliconFlow API。SiliconFlow 是一个国内的 AI API 服务提供商，提供与 OpenAI 兼容的接口，使用 Qwen 等优秀的开源大模型。

## 主要变更

### 1. 配置文件变更

**环境变量** (`.env` 文件):
- `OPENAI_API_KEY` → `SILICONFLOW_API_KEY`
- 新增 `SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1`
- `OPENAI_MODEL=gpt-4` → `SILICONFLOW_MODEL=Qwen/Qwen2.5-7B-Instruct`

### 2. 代码变更

**config.py**:
- 配置项名称更新为 `siliconflow_*`
- 添加了 base_url 配置项

**llm_service.py**:
- OpenAI 客户端初始化时添加 `base_url` 参数
- 模型名称从配置中读取

**main.py**:
- 健康检查接口返回 `siliconflow_configured` 而非 `openai_configured`

### 3. 文档更新

所有文档已更新，包括：
- README.md
- PROJECT_SUMMARY.md
- START.md
- docs/USAGE.md
- docs/ARCHITECTURE.md
- docs/PRESENTATION.md
- docs/DEMO_GUIDE.md

## 如何获取 SiliconFlow API Key

1. 访问 [SiliconFlow 官网](https://siliconflow.cn)
2. 注册账号
3. 在控制台中创建 API Key
4. 将 API Key 配置到 `.env` 文件中

## 配置步骤

1. 复制环境变量模板：
```bash
cd backend
cp .env.example .env
```

2. 编辑 `.env` 文件，配置你的 API Key：
```env
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Qwen/Qwen2.5-7B-Instruct
```

3. 安装依赖并启动：
```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖（如果还没有安装）
pip install -r requirements.txt

# 启动后端
python main.py
```

## 支持的模型

SiliconFlow 支持多种开源模型，包括但不限于：
- Qwen/Qwen2.5-7B-Instruct
- Qwen/Qwen2.5-14B-Instruct
- 其他 Qwen 系列模型

可以根据需要在 `.env` 文件中修改 `SILICONFLOW_MODEL` 配置。

## 兼容性说明

由于 SiliconFlow 提供与 OpenAI 兼容的 API 接口，代码迁移非常简单：
- 使用相同的 Python SDK (`openai`)
- API 调用方式完全一致
- 只需修改 API Key 和 base URL

## 优势

使用 SiliconFlow API 的优势：
1. **国内访问速度快** - 无需科学上网
2. **价格更优惠** - 相比 OpenAI API 更具性价比
3. **优秀的开源模型** - Qwen 等模型在中文理解上表现出色
4. **简单迁移** - API 兼容，迁移成本低

## 注意事项

1. 首次使用时，请确保 API Key 有足够的配额
2. 不同模型的能力和成本可能有差异，请根据实际需求选择
3. 如遇到问题，可以查看后端日志获取详细错误信息

## 问题排查

如果遇到 API 调用失败：
1. 检查 `.env` 文件中的 `SILICONFLOW_API_KEY` 是否正确
2. 确认 `SILICONFLOW_BASE_URL` 配置正确
3. 检查网络连接
4. 查看 API 配额是否充足
5. 查看后端终端的错误日志

## 回退到 OpenAI

如果需要回退到 OpenAI API，可以：
1. 将配置项改回 `OPENAI_*`
2. 在代码中移除 `base_url` 参数
3. 使用 `git` 恢复到迁移前的版本

---

更新日期：2024年
