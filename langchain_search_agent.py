#!/usr/bin/env python3
"""
智能搜索Agent - 基于LangChain框架
使用Gemini作为主要LLM，自主选择和使用多种搜索工具
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import BaseTool
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain

# 导入自定义工具
import sys
sys.path.append('.')  # 确保可以导入同级目录的模块
from tools.arxiv_tool import ArxivSearchTool
from tools.wikipedia_tool import WikipediaSearchTool
from tools.google_scholar_tool import GoogleScholarSearchTool
from tools.google_search_tool import GoogleSearchTool

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 加载环境变量
load_dotenv()

class LangChainSearchAgent:
    """LangChain框架的智能搜索Agent"""
    
    def __init__(self, debug: bool = False):
        """
        初始化智能搜索Agent
        
        Args:
            debug: 是否启用调试模式
        """
        self.debug = debug
        
        # 检查API密钥
        self._check_api_keys()
        
        # 初始化LLM (Gemini)
        self.llm = self._initialize_llm()
        
        # 创建工具集
        self.tools = self._create_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        logger.info("智能搜索Agent初始化完成")
        
    def _check_api_keys(self):
        """检查必要的API密钥"""
        required_keys = {
            "GOOGLE_API_KEY": "Google API Key (Gemini和Google搜索)",
            "SERP_API_KEY": "SERP API Key (Google Scholar搜索)"
        }
        
        missing_keys = []
        for key, description in required_keys.items():
            if not os.getenv(key):
                missing_keys.append(f"{key} ({description})")
        
        if missing_keys:
            logger.error(f"缺少以下API密钥: {', '.join(missing_keys)}")
            logger.error("请在.env文件中设置所有必要的API密钥")
            sys.exit(1)
    
    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM (Gemini)"""
        try:
            # 使用Gemini-Pro作为主要思考模型
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.1,  # 低温度以获得更确定性的回答
                convert_system_message_to_human=True,
            )
            return llm
        except Exception as e:
            logger.error(f"初始化LLM失败: {e}")
            sys.exit(1)
    
    def _create_tools(self) -> List[BaseTool]:
        """创建Agent可用的工具集"""
        try:
            tools = [
                ArxivSearchTool().get_tool(),
                WikipediaSearchTool().get_tool(),
                GoogleScholarSearchTool().get_tool(),
                GoogleSearchTool().get_tool()
            ]
            return tools
        except Exception as e:
            logger.error(f"创建工具集失败: {e}")
            sys.exit(1)
    
    def _create_agent(self) -> AgentExecutor:
        """创建Agent"""
        # Agent系统提示
        system_prompt = """你是一个高级研究助手，能够智能地分析研究问题并搜索相关信息。
        
你将获得一个用户查询，你的任务是：
1. 深入分析查询，识别关键概念、实体和关系
2. 确定最适合回答该查询的信息源(arXiv、Wikipedia、Google Scholar、Google Search)
3. 使用选定的工具搜索相关信息
4. 综合搜索结果，提供全面且有条理的回答

非常重要：
- 用户可能使用中文提问，你需要将查询翻译成英文后再进行搜索
- 搜索时，优先选择最合适的信息源，而不是使用所有工具
- 学术/科研问题优先使用arXiv和Google Scholar
- 百科知识优先使用Wikipedia
- 时事新闻和一般问题优先使用Google Search
- 确保所有返回的内容都基于搜索结果，而非你的先验知识
- 返回中文答复给用户
"""
        
        # 创建Agent提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建Agent
        try:
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            # 创建Agent执行器
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                verbose=self.debug,
                handle_parsing_errors=True,
                max_iterations=5,  # 限制最大迭代次数
                return_intermediate_steps=self.debug  # 调试模式下返回中间步骤
            )
            return agent_executor
        except Exception as e:
            logger.error(f"创建Agent失败: {e}")
            sys.exit(1)
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        运行Agent来回答查询
        
        Args:
            query: 用户查询
            
        Returns:
            包含回答和元数据的字典
        """
        logger.info(f"处理查询: {query}")
        try:
            # 执行Agent
            result = self.agent.invoke({"input": query})
            
            # 构建返回结果
            response = {
                "query": query,
                "answer": result.get("output", "未找到回答"),
                "success": True
            }
            
            # 如果启用了调试模式，添加中间步骤
            if self.debug and "intermediate_steps" in result:
                response["debug_info"] = {
                    "intermediate_steps": [
                        {
                            "tool": step[0].tool,
                            "tool_input": step[0].tool_input,
                            "tool_output": step[1]
                        }
                        for step in result["intermediate_steps"]
                    ]
                }
            
            return response
        
        except Exception as e:
            logger.error(f"运行Agent时发生错误: {e}")
            return {
                "query": query,
                "answer": f"处理查询时发生错误: {str(e)}",
                "success": False
            }


def main():
    """主函数，用于测试"""
    # 测试查询
    test_query = "大语言模型的最新研究进展是什么？"
    
    # 创建Agent
    agent = LangChainSearchAgent(debug=True)
    
    # 运行查询
    result = agent.run(test_query)
    
    # 打印结果
    print("\n" + "="*50)
    print("查询:", result["query"])
    print("-"*50)
    print("回答:", result["answer"])
    
    # 打印调试信息
    if "debug_info" in result:
        print("\n" + "="*50)
        print("调试信息:")
        print(json.dumps(result["debug_info"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main() 