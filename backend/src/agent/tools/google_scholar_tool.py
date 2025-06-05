#!/usr/bin/env python3
"""
Google Scholar搜索工具
封装通过SERP API进行Google Scholar搜索的功能，实现为LangChain工具
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain.tools import BaseTool, Tool

# 加载环境变量
load_dotenv()

class GoogleScholarSearchTool:
    """封装Google Scholar搜索功能的工具类"""
    
    def __init__(self):
        """初始化Google Scholar搜索工具"""
        # 获取API密钥
        self.api_key = os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("未找到SERP_API_KEY环境变量")
            
        # 设置API基础URL
        self.api_base = "https://serpapi.com/search"
        
    def search(self, query: str, max_results: int = 5) -> str:
        """
        在Google Scholar上搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            包含搜索结果的字符串
        """
        try:
            # 构建请求参数
            params = {
                "api_key": self.api_key,
                "engine": "google_scholar",
                "q": query,
                "num": max_results
            }
            
            # 发送请求
            response = requests.get(self.api_base, params=params)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                return f"在Google Scholar上没有找到与'{query}'相关的学术文献。"
            
            # 格式化结果
            results = []
            for i, result in enumerate(organic_results, 1):
                title = result.get('title', '无标题')
                link = result.get('link', '#')
                snippet = result.get('snippet', '无摘要')
                
                # 提取出版信息
                pub_info = result.get('publication_info', {}).get('summary', '无出版信息')
                
                # 提取引用信息
                citations = None
                if 'inline_links' in result and 'cited_by' in result['inline_links']:
                    cited_by = result['inline_links']['cited_by']
                    citations = cited_by.get('total', 'N/A')
                
                # 构建论文信息字符串
                paper_info = (
                    f"结果 {i}: {title}\n"
                    f"出版信息: {pub_info}\n"
                    f"摘要: {snippet[:200]}{'...' if len(snippet) > 200 else ''}\n"
                )
                
                if citations is not None:
                    paper_info += f"被引用次数: {citations}\n"
                    
                paper_info += f"链接: {link}\n"
                
                results.append(paper_info)
            
            # 合并结果
            response = (
                f"在Google Scholar上找到了{len(organic_results)}篇与'{query}'相关的学术文献：\n\n" + 
                "\n".join(results)
            )
            
            return response
            
        except requests.exceptions.RequestException as e:
            return f"搜索Google Scholar时发生网络错误: {str(e)}"
        except Exception as e:
            return f"搜索Google Scholar时发生错误: {str(e)}"
    
    def get_tool(self) -> Tool:
        """获取LangChain工具实例"""
        return Tool(
            name="Google_Scholar_search",
            func=self.search,
            description="在Google Scholar上搜索学术文献。适用于查找关于科研、学术研究的高引用量文章和综述。可以获取包括引用次数在内的丰富学术信息。输入应为搜索关键词，例如'language model evaluation'。"
        ) 