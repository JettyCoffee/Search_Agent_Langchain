#!/usr/bin/env python3
"""
arXiv搜索工具
封装arXiv API搜索功能，实现为LangChain工具
"""

import urllib.request
import xml.etree.ElementTree as ET
import time
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool, Tool

class ArxivSearchTool:
    """封装arXiv API搜索功能的工具类"""
    
    def __init__(self):
        """初始化arXiv API工具"""
        self.base_url = "http://export.arxiv.org/api/query"
        
    def search(self, query: str, max_results: int = 5) -> str:
        """
        搜索arXiv论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            包含搜索结果的字符串
        """
        try:
            # 格式化查询，确保它适合arXiv API
            formatted_query = query.replace(' ', '+')
            
            # 构建arXiv API查询URL
            search_query = f'search_query=all:{formatted_query}&start=0&max_results={max_results}&sortBy=relevance'
            url = f'{self.base_url}?{search_query}'
            
            # 发送请求
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
            
            # 解析XML响应
            root = ET.fromstring(data)
            
            # 提取命名空间
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # 获取总结果数
            total_results = root.find('.//opensearch:totalResults', namespaces).text
            
            # 获取文章条目
            entries = root.findall('.//atom:entry', namespaces)
            
            # 如果没有结果，返回提示
            if not entries:
                return f"在arXiv上没有找到与'{query}'相关的论文。"
            
            # 格式化结果
            results = []
            for i, entry in enumerate(entries, 1):
                title = entry.find('./atom:title', namespaces).text.strip()
                authors = [author.find('./atom:name', namespaces).text for author in entry.findall('./atom:author', namespaces)]
                summary = entry.find('./atom:summary', namespaces).text.strip()
                published = entry.find('./atom:published', namespaces).text.split('T')[0]  # 只保留日期部分
                
                # 获取PDF链接
                pdf_link = None
                links = entry.findall('./atom:link', namespaces)
                for link in links:
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        break
                
                # 提取主要分类
                categories = [category.get('term') for category in entry.findall('./atom:category', namespaces)]
                primary_category = categories[0] if categories else "N/A"
                
                # 构建论文信息字符串
                paper_info = (
                    f"论文 {i}:\n"
                    f"标题: {title}\n"
                    f"作者: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}\n"
                    f"发布日期: {published}\n"
                    f"主要分类: {primary_category}\n"
                    f"摘要: {summary[:300]}{'...' if len(summary) > 300 else ''}\n"
                    f"链接: {pdf_link or 'N/A'}\n"
                )
                results.append(paper_info)
            
            # 合并结果
            response = (
                f"在arXiv上找到了{len(entries)}篇与'{query}'相关的论文（共{total_results}个结果）：\n\n" + 
                "\n".join(results)
            )
            
            return response
            
        except Exception as e:
            return f"搜索arXiv时发生错误: {str(e)}"
    
    def get_tool(self) -> Tool:
        """获取LangChain工具实例"""
        return Tool(
            name="arXiv_search",
            func=self.search,
            description="在arXiv上搜索学术论文。适用于查找关于科学和学术主题的最新研究论文。输入应为搜索关键词，例如'large language models'。"
        ) 