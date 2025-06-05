#!/usr/bin/env python3
"""
智能搜索Agent图结构 - 基于LangGraph
实现类似Google开源项目的迭代搜索和反思机制
"""

import os
import sys
from typing import List, Dict, Any, TypedDict, Annotated, Sequence
from datetime import datetime
import json
import logging
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import Graph, StateGraph, END
from langchain.tools import Tool

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入工具
from .tools.arxiv_tool import ArxivSearchTool
from .tools.wikipedia_tool import WikipediaSearchTool
from .tools.google_scholar_tool import GoogleScholarSearchTool
from .tools.google_search_tool import GoogleSearchTool


class AgentState(TypedDict):
    """Agent状态"""
    messages: List[BaseMessage]
    next: str


class SearchAgent:
    """智能搜索Agent"""
    
    def __init__(self):
        """初始化Agent"""
        logger.debug("开始初始化SearchAgent")
        
        logger.debug("初始化LLM模型")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,     # 降低温度提高稳定性
            timeout=30,          # 添加30秒超时
            max_output_tokens=2048  # 限制输出长度
        )
        
        # 初始化工具
        logger.debug("开始初始化搜索工具")
        tool_classes = [
            ArxivSearchTool(),
            WikipediaSearchTool(),
            GoogleScholarSearchTool(),
            GoogleSearchTool()
        ]
        
        # 获取工具实例
        logger.debug("获取工具实例")
        self.tools = [tool.get_tool() for tool in tool_classes]
        
        # 构建工具映射
        self.tool_map = {
            tool.name: tool for tool in self.tools
        }
        
        # 构建图结构
        logger.debug("构建工作流图结构")
        self.workflow = self._build_graph()
        logger.debug("SearchAgent初始化完成")
    
    def _build_graph(self) -> Graph:
        """构建Agent的工作流图"""
        
        # 定义节点
        def search_node(state: AgentState) -> AgentState:
            """执行搜索"""
            logger.debug("进入search_node")
            messages = state["messages"]
            
            # 获取最新的用户消息
            last_message = messages[-1].content
            logger.debug(f"处理用户查询: {last_message}")
            
            # 选择合适的工具执行搜索
            results = []
            for tool in self.tools:
                try:
                    logger.debug(f"使用工具 {tool.name} 执行搜索")
                    result = tool.run(last_message)
                    logger.debug(f"工具 {tool.name} 返回结果长度: {len(result)}")
                    results.append(f"{tool.name}: {result}")
                except Exception as e:
                    logger.error(f"工具 {tool.name} 执行失败: {str(e)}", exc_info=True)
            
            # 将结果添加到消息历史
            logger.debug(f"搜索完成，共获得 {len(results)} 个结果")
            messages.append(AIMessage(content="\n\n".join(results)))
            
            return {
                "messages": messages,
                "next": "reflect"
            }
        
        def reflect_node(state: AgentState) -> AgentState:
            """反思和总结"""
            logger.debug("进入reflect_node")
            messages = state["messages"]
            
            # 获取所有搜索结果
            search_results = messages[-1].content
            logger.debug(f"开始总结搜索结果，结果长度: {len(search_results)}")
            
            try:
                # 生成总结
                prompt = f"""请对以下搜索结果进行简明扼要的总结。要求：
                1. 保持客观准确
                2. 突出最重要的信息点
                3. 如果有多个来源的信息，注意整合和对比
                4. 总结控制在1000字以内
                5. 使用清晰的段落结构

                搜索结果内容：
                {search_results}
                """
                
                logger.debug("调用LLM生成总结")
                summary = self.llm.invoke(prompt).content
                logger.debug(f"生成总结完成，总结长度: {len(summary)}")
                
            except Exception as e:
                logger.error(f"生成总结时发生错误: {str(e)}", exc_info=True)
                # 如果生成总结失败，返回一个简单的错误信息
                summary = "抱歉，在总结搜索结果时遇到了技术问题。以下是原始搜索结果：\n\n" + search_results
            
            # 将总结添加到消息历史
            messages.append(AIMessage(content=summary))
            
            return {
                "messages": messages,
                "next": END
            }
        
        # 构建工作流
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("search", search_node)
        workflow.add_node("reflect", reflect_node)
        
        # 设置边
        workflow.set_entry_point("search")
        workflow.add_edge("search", "reflect")
        workflow.add_edge("reflect", END)
        
        return workflow.compile()
    
    def search(self, query: str, max_iterations: int = 3) -> str:
        """执行搜索"""
        logger.debug(f"开始执行搜索，查询: {query}, 最大迭代次数: {max_iterations}")
        
        # 初始化状态
        state = {
            "messages": [HumanMessage(content=query)],
            "next": "search"
        }
        
        # 执行工作流
        for i in range(max_iterations):
            logger.debug(f"开始第 {i+1} 次迭代")
            state = self.workflow.invoke(state)
            if state["next"] == END:
                logger.debug("工作流执行完成")
                break
        
        # 返回最终结果
        final_result = state["messages"][-1].content
        logger.debug(f"搜索完成，返回结果长度: {len(final_result)}")
        return final_result 