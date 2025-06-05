#!/usr/bin/env python3
"""
Wikipedia搜索工具
封装Wikipedia API搜索功能，实现为LangChain工具
"""

import requests
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool, Tool

class WikipediaSearchTool:
    """封装Wikipedia API搜索功能的工具类"""
    
    def __init__(self):
        """初始化Wikipedia API工具"""
        self.base_url = "https://en.wikipedia.org/w/api.php"  # 英文维基百科API
        self.session = requests.Session()
        # 设置User-Agent避免被封禁
        self.session.headers.update({
            'User-Agent': 'LangChain-Agent/1.0 (Educational Research Assistant) Python/3.x'
        })
        
    def search_and_get_content(self, query: str, max_results: int = 3) -> str:
        """
        搜索并获取Wikipedia内容
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            包含搜索结果的字符串
        """
        try:
            # 首先进行搜索
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': max_results,
                'srprop': 'snippet'
            }
            
            search_response = self.session.get(self.base_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            
            search_data = search_response.json()
            search_results = search_data.get('query', {}).get('search', [])
            
            if not search_results:
                return f"在Wikipedia上没有找到与'{query}'相关的内容。"
            
            # 获取页面详细内容
            results = []
            for i, result in enumerate(search_results, 1):
                title = result.get('title')
                page_id = result.get('pageid')
                
                # 获取页面内容
                content_params = {
                    'action': 'query',
                    'format': 'json',
                    'pageids': page_id,
                    'prop': 'extracts',
                    'exintro': True,  # 只获取介绍部分
                    'explaintext': True,  # 纯文本格式
                    'exsectionformat': 'plain'
                }
                
                content_response = self.session.get(self.base_url, params=content_params, timeout=10)
                content_response.raise_for_status()
                
                content_data = content_response.json()
                page_data = content_data.get('query', {}).get('pages', {}).get(str(page_id), {})
                extract = page_data.get('extract', '无内容')
                
                # 裁剪过长的内容
                if len(extract) > 1000:
                    extract = extract[:997] + "..."
                
                # 构建页面信息字符串
                page_url = f"https://en.wikipedia.org/?curid={page_id}"
                page_info = (
                    f"结果 {i}: {title}\n"
                    f"内容摘要: {extract}\n"
                    f"链接: {page_url}\n"
                )
                results.append(page_info)
            
            # 合并结果
            response = (
                f"在Wikipedia上找到了{len(search_results)}个与'{query}'相关的结果：\n\n" + 
                "\n".join(results)
            )
            
            return response
            
        except requests.exceptions.RequestException as e:
            return f"搜索Wikipedia时发生网络错误: {str(e)}"
        except Exception as e:
            return f"搜索Wikipedia时发生错误: {str(e)}"
    
    def get_tool(self) -> Tool:
        """获取LangChain工具实例"""
        return Tool(
            name="Wikipedia_search",
            func=self.search_and_get_content,
            description="在Wikipedia上搜索百科知识。适用于查找关于概念、人物、历史事件等基础知识。输入应为简洁明确的搜索关键词，例如'Albert Einstein'。"
        ) 