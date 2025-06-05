# 智能搜索Agent - 全栈应用

基于LangGraph和Google Gemini的智能搜索助手，实现了类似Google开源项目的迭代搜索和反思机制。

![Search Agent Demo](./demo.png)

## 🌟 功能特点

- 💬 **全栈应用**：React前端 + FastAPI后端
- 🧠 **智能搜索**：基于LangGraph的高级Agent架构
- 🔍 **动态查询生成**：使用Gemini智能分析并生成搜索查询
- 🌐 **多源搜索**：整合arXiv、Wikipedia、Google Scholar和Google Search
- 🤔 **反思机制**：自动识别信息差距并进行补充搜索
- 📄 **引用来源**：所有信息都标注可靠来源
- 🔄 **迭代优化**：最多3轮迭代搜索，确保信息完整性

## 🏗️ 项目结构

```
Search_Agent/
├── backend/                # 后端服务
│   ├── src/
│   │   ├── agent/         # LangGraph Agent实现
│   │   │   └── graph.py   # 核心Agent逻辑
│   │   └── api/           # FastAPI服务
│   │       └── server.py  # API接口
│   └── requirements.txt   # Python依赖
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── App.jsx       # 主应用
│   │   └── main.jsx      # 入口文件
│   └── package.json      # Node.js依赖
├── tools/                # 搜索工具集
│   ├── arxiv_tool.py     # arXiv搜索
│   ├── wikipedia_tool.py # Wikipedia搜索
│   ├── google_scholar_tool.py # Google Scholar搜索
│   └── google_search_tool.py  # Google搜索
└── Makefile             # 开发命令

```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- Google API Key（用于Gemini和Google搜索）
- SERP API Key（用于Google Scholar）

### 1. 克隆项目

```bash
git clone <repository-url>
cd Search_Agent
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
GEMINI_API_KEY=your_gemini_api_key
SERP_API_KEY=your_serp_api_key
```

### 3. 安装依赖

```bash
# 安装所有依赖
make install

# 或分别安装
make install-backend  # 安装后端依赖
make install-frontend # 安装前端依赖
```

### 4. 运行开发服务器

```bash
# 同时启动前后端
make dev

# 或分别启动
make backend  # 只启动后端 (http://localhost:8000)
make frontend # 只启动前端 (http://localhost:5173)
```

## 🔧 Agent工作原理

![Agent Flow](./agent_flow.png)

1. **查询生成**：基于用户输入，使用Gemini生成3-5个搜索查询
2. **网络搜索**：并行搜索多个数据源
3. **反思分析**：评估搜索结果是否充分回答用户问题
4. **迭代改进**：如发现信息差距，生成新查询并继续搜索
5. **答案生成**：整合所有信息，生成带引用的完整答案

## 📡 API文档

### 搜索接口

```http
POST /api/search
Content-Type: application/json

{
    "query": "用户的问题",
    "max_iterations": 3
}
```

响应格式：

```json
{
    "success": true,
    "query": "用户的问题",
    "answer": "AI生成的答案",
    "search_results": {...},
    "iterations": 2,
    "timestamp": "2024-01-01T00:00:00"
}
```

### WebSocket接口

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.send(JSON.stringify({ query: "用户的问题" }));
```

## 🛠️ 技术栈

### 后端
- **LangGraph** - Agent工作流框架
- **FastAPI** - 高性能Web框架
- **Google Gemini** - 大语言模型
- **LangChain** - LLM应用框架

### 前端
- **React** - UI框架
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Axios** - HTTP客户端

## 📝 开发指南

### 添加新的搜索工具

1. 在 `tools/` 目录创建新的工具文件
2. 继承 `BaseTool` 类并实现搜索逻辑
3. 在 `backend/src/agent/graph.py` 中注册新工具

### 自定义Agent行为

修改 `backend/src/agent/graph.py` 中的：
- `generate_queries()` - 查询生成策略
- `reflect()` - 反思逻辑
- `max_iterations` - 最大迭代次数

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- Google Gemini团队
- LangChain和LangGraph社区
- 所有开源贡献者 