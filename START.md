# 🚀 快速启动指南

## 第一次使用

### 1. 配置 SiliconFlow API Key

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API Key：
```
SILICONFLOW_API_KEY=your-siliconflow-api-key-here
```

### 2. 安装后端依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

## 启动应用

### 方法1：分别启动（推荐）

**终端1 - 启动后端：**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
访问: http://localhost:8000

**终端2 - 启动前端：**
```bash
cd frontend
npm start
```
自动打开: http://localhost:3000

### 方法2：运行演示脚本（测试功能）

```bash
cd backend
source venv/bin/activate
python demo.py
```

## 验证安装

1. 访问后端API文档: http://localhost:8000/docs
2. 访问前端应用: http://localhost:3000
3. 在前端输入测试文本，点击"开始分析"

## 测试文本建议

```
今天的工作压力很大，感觉有点焦虑和疲惫。虽然完成了任务，
但总觉得不够好，担心明天的presentation。
```

## 常见问题

**Q: 显示 "分析失败，请检查后端服务"**
- 检查后端是否启动
- 检查 .env 中的 SILICONFLOW_API_KEY 是否正确
- 查看后端终端的错误信息

**Q: npm install 很慢**
- 使用国内镜像：`npm install --registry=https://registry.npmmirror.com`

**Q: 想要清空数据重新开始**
- 删除 `backend/sentiment_analysis.db`
- 删除 `backend/chroma_db/` 目录
- 重新启动后端

## 项目文档

- [README.md](README.md) - 项目总览
- [docs/USAGE.md](docs/USAGE.md) - 详细使用说明
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 系统架构
- [docs/PRESENTATION.md](docs/PRESENTATION.md) - 项目汇报内容
- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) - 演示指南

## 需要帮助？

查看后端日志和前端浏览器控制台的错误信息。

祝使用愉快！😊
