# 智能搜索Agent (Intelligent Search Agent)

一个智能搜索系统，能够根据用户问题智能选择搜索源，并使用AI进行结果汇总。

## 版本

本系统提供两个版本：
- **Claude版本**: 使用Claude API进行问题分析和结果汇总
- **Gemini版本**: 使用Google Gemini API进行问题分析和结果汇总 (推荐使用)

## 功能特点

- 🧠 **智能问题分析**：使用Claude AI分析用户问题，自动判断问题类型
- 🔍 **多源并行搜索**：支持同时搜索多个数据源
- 📚 **丰富的数据源**：
  - arXiv：最新学术论文和预印本
  - Wikipedia：百科知识和概念解释
  - Google Scholar：学术文献和引用统计
- 🤖 **AI智能汇总**：使用Google Gemini或Claude API对搜索结果进行智能整合和总结
- 📊 **JSON格式输出**：所有处理流程和结果均以JSON格式输出
- 🐛 **完整的DEBUG信息**：详细记录每个处理阶段的信息

## 系统架构

```
用户查询
    ↓
查询意图分析 (Gemini/Claude AI)
    ↓
智能选择搜索源
    ↓
并行搜索执行
    ├── arXiv API
    ├── Wikipedia API
    └── Google Scholar API
    ↓
结果汇总 (Gemini/Claude AI)
    ↓
JSON格式输出
```

## 安装要求

1. Python 3.8+
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

### API密钥设置

#### Gemini版本（推荐）:
1. **Google Gemini API**（必需）：
   - 在环境变量中设置 `GOOGLE_API_KEY`
   - 从 [Google AI Studio](https://ai.google.dev/) 获取API密钥

2. **Google Scholar API**（可选）：
   - 在环境变量中设置 `SERP_API_KEY`
   - 从 [SerpAPI](https://serpapi.com) 获取API密钥
   - 如未设置，将跳过Google Scholar搜索

#### Claude版本:
1. **Claude API**（必需）：
   - 在环境变量中设置 `CLAUDE_API_KEY`
   - 或在代码中直接配置

2. **Google Scholar API**（可选）：
   - 同上

## 使用方法

### 1. 交互式使用

#### Gemini版本（推荐）
```bash
python run_gemini_search_agent.py
```

#### Claude版本
```bash
python run_search_agent.py
```

### 2. 编程使用

#### Gemini版本（推荐）
```python
from gemini_search_agent import IntelligentSearchAgent

# 创建Agent
agent = IntelligentSearchAgent(google_api_key="your-google-api-key")

# 执行搜索
result = agent.search("大语言模型的最新研究进展")
```

#### Claude版本
```python
from intelligent_search_agent_simple import IntelligentSearchAgent

# 创建Agent
agent = IntelligentSearchAgent(claude_api_key="your-claude-api-key")

# 执行搜索
result = agent.search("大语言模型的最新研究进展")
```

### 3. 搜索结果格式
结果包含：
- `status`: 状态（success/error）
- `query`: 原始查询
- `analysis`: 查询分析结果
- `search_results`: 各数据源的搜索结果
- `summary`: AI的汇总结果
- `debug_logs`: 完整的调试日志

## 输出格式示例

```json
{
  "status": "success",
  "query": "大语言模型的最新研究进展",
  "analysis": {
    "query_type": "学术",
    "recommended_sources": ["arxiv", "google_scholar"],
    "search_keywords": ["large language model", "LLM", "研究进展"],
    "reasoning": "这是一个关于人工智能领域最新研究的学术查询"
  },
  "search_results": {
    "arxiv": [...],
    "google_scholar": [...]
  },
  "summary": "根据最新的研究...",
  "debug_logs": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "stage": "query_analysis_start",
      "data": {...}
    }
  ]
}
```

## 调试信息

系统会记录以下阶段的DEBUG信息：
- `query_analysis_start/complete/error`：查询分析阶段
- `parallel_search_start/complete`：并行搜索阶段
- `arxiv_search_start/complete/error`：arXiv搜索
- `wikipedia_search_start/complete/error`：Wikipedia搜索
- `google_scholar_search_start/complete/error`：Google Scholar搜索
- `summarization_start/complete/error`：结果汇总阶段

## 注意事项

1. **API限制**：各API都有访问频率限制，请合理使用
2. **网络要求**：需要稳定的网络连接访问各API服务
3. **结果准确性**：AI生成的汇总仅供参考，重要信息请查证原始来源
4. **隐私保护**：所有查询和结果都在本地处理，但会通过API发送到相应服务

## 错误处理

- 如果某个搜索源失败，系统会继续使用其他可用源
- 所有错误都会记录在debug_logs中
- 即使部分搜索失败，仍会基于成功的结果生成汇总

## 扩展开发

可以通过以下方式扩展系统：
1. 添加新的搜索源（如PubMed、Semantic Scholar等）
2. 自定义查询分析逻辑
3. 优化结果汇总策略
4. 添加结果缓存机制 