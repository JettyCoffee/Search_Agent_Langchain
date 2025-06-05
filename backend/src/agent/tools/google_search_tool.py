#!/usr/bin/env python3
"""
Google搜索工具
封装使用Gemini API的google_search功能，实现为LangChain工具
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.tools import BaseTool, Tool

# 加载环境变量
load_dotenv()

class GoogleSearchTool:
    """封装Google搜索功能的工具类"""
    
    def __init__(self):
        """初始化Google搜索工具"""
        # 获取API密钥
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("未找到GOOGLE_API_KEY环境变量")
        
        # 初始化Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def search(self, query: str) -> str:
        """
        使用Google搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            包含搜索结果的字符串
        """
        try:
            # 使用Gemini模型进行搜索
            response = self.model.generate_content(
                contents=f"请搜索并总结以下问题的最新信息: {query}",
                generation_config={
                    "temperature": 0.1
                },
                tools=[{"google_search": {}}]
            )
            
            if not response or not response.text:
                return f"使用Google搜索'{query}'时没有获得结果。"
            
            result = response.text
            
            # 提取搜索元数据（如果有）
            sources = []
            if (hasattr(response, 'candidates') and response.candidates and
                hasattr(response.candidates[0], 'grounding_metadata') and 
                response.candidates[0].grounding_metadata):
                metadata = response.candidates[0].grounding_metadata
                if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            source = {
                                "title": chunk.web.title,
                                "url": chunk.web.url
                            }
                            sources.append(source)
            
            # 添加来源信息
            if sources:
                result += "\n\n信息来源:\n"
                for i, source in enumerate(sources, 1):
                    result += f"{i}. {source['title']} - {source['url']}\n"
            
            return result
            
        except Exception as e:
            return f"使用Google搜索时发生错误: {str(e)}"
    
    def get_tool(self) -> Tool:
        """获取LangChain工具实例"""
        return Tool(
            name="Google_Search",
            func=self.search,
            description="使用Google搜索获取互联网上的最新信息。适用于查找新闻、时事、产品信息和其他实时数据。比Wikipedia更新，但可能不如学术数据库权威。输入应为简洁明确的搜索关键词。"
        ) 