#!/usr/bin/env python3
"""
智能搜索Agent
使用LangChain框架，根据输入问题智能选择搜索源，最后调用Claude汇总结果
"""

import os
import json
import asyncio
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from langchain.tools import Tool
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Mapping, Optional

# 导入已有的API测试类
from test_arxiv_api import ArxivAPITester
from test_claude_api import ClaudeAPITester
from test_gemini_api import GeminiAPITester
from test_google_scholar_api import GoogleScholarAPITester
from test_wikipedia_api import WikipediaAPITester

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebugInfo:
    """DEBUG信息收集器"""
    def __init__(self):
        self.logs = []
    
    def add_log(self, stage: str, data: Dict[str, Any]):
        """添加DEBUG日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "data": data
        }
        self.logs.append(log_entry)
        logger.debug(json.dumps(log_entry, ensure_ascii=False, indent=2))
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """获取所有日志"""
        return self.logs

class ClaudeLLM(LLM):
    """Claude LLM包装器 (使用OpenAI客户端)"""
    api_key: str
    api_base: str = "https://api.mjdjourney.cn/v1"
    model: str = "claude-3-7-sonnet-20250219"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            self.import_error = None
        except ImportError as e:
            self.import_error = e
            logger.error(f"OpenAI库导入失败，请安装: pip install openai. 错误: {e}")
    
    @property
    def _llm_type(self) -> str:
        return "claude"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """使用OpenAI客户端调用Claude API"""
        try:
            # 检查是否成功导入了OpenAI
            if hasattr(self, 'import_error') and self.import_error:
                return f"调用失败: 无法导入OpenAI库 - {str(self.import_error)}"
            
            # 使用OpenAI客户端
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            # 从响应中提取文本
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            return f"调用失败: {str(e)}"

class SearchAPIs:
    """搜索API集合"""
    def __init__(self, debug_info: DebugInfo):
        self.debug_info = debug_info
        self.arxiv = ArxivAPITester()
        self.wikipedia = WikipediaAPITester()
        self.google_scholar = GoogleScholarAPITester()
        
    def search_arxiv(self, query: str) -> str:
        """搜索arXiv论文"""
        self.debug_info.add_log("arxiv_search_start", {"query": query})
        try:

            
            # 构建查询
            encoded_query = urllib.parse.quote(query)
            url = f'{self.arxiv.base_url}?search_query=all:{encoded_query}&start=0&max_results=5'
            
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
            
            root = ET.fromstring(data)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entries = root.findall('.//atom:entry', namespaces)
            results = []
            
            for entry in entries:
                title = entry.find('./atom:title', namespaces).text.strip()
                summary = entry.find('./atom:summary', namespaces).text.strip()
                authors = [author.find('./atom:name', namespaces).text 
                          for author in entry.findall('./atom:author', namespaces)]
                published = entry.find('./atom:published', namespaces).text
                
                results.append({
                    "title": title,
                    "summary": summary[:200] + "...",
                    "authors": authors[:3],
                    "published": published
                })
            
            self.debug_info.add_log("arxiv_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return json.dumps(results, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"arXiv搜索失败: {str(e)}"
            self.debug_info.add_log("arxiv_search_error", {"error": str(e)})
            return error_msg
    
    def search_wikipedia(self, query: str) -> str:
        """搜索Wikipedia"""
        self.debug_info.add_log("wikipedia_search_start", {"query": query})
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 5
            }
            
            response = self.wikipedia.session.get(
                self.wikipedia.base_url, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'query' in data and 'search' in data['query']:
                for item in data['query']['search']:
                    results.append({
                        "title": item.get('title', ''),
                        "snippet": item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                    })
            
            self.debug_info.add_log("wikipedia_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return json.dumps(results, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Wikipedia搜索失败: {str(e)}"
            self.debug_info.add_log("wikipedia_search_error", {"error": str(e)})
            return error_msg
    
    def search_google_scholar(self, query: str) -> str:
        """搜索Google Scholar"""
        self.debug_info.add_log("google_scholar_search_start", {"query": query})
        try:
            if not hasattr(self.google_scholar, 'api_key') or not self.google_scholar.api_key:
                return "Google Scholar API密钥未设置"
            
            params = self.google_scholar.params.copy()
            params["q"] = query
            
            response = requests.get(
                self.google_scholar.api_base,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", [])[:5]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "publication_info": item.get("publication_info", {}).get("summary", ""),
                    "cited_by": item.get("inline_links", {}).get("cited_by", {}).get("total", 0)
                })
            
            self.debug_info.add_log("google_scholar_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return json.dumps(results, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Google Scholar搜索失败: {str(e)}"
            self.debug_info.add_log("google_scholar_search_error", {"error": str(e)})
            return error_msg

class IntelligentSearchAgent:
    """智能搜索Agent主类"""
    
    def __init__(self, claude_api_key: str):
        self.debug_info = DebugInfo()
        self.claude_llm = ClaudeLLM(api_key=claude_api_key)
        self.search_apis = SearchAPIs(self.debug_info)
        
        # 创建搜索工具
        self.tools = [
            Tool(
                name="search_arxiv",
                func=self.search_apis.search_arxiv,
                description="搜索arXiv学术论文数据库，适合查找最新的科研论文、预印本、人工智能、计算机科学等学术内容"
            ),
            Tool(
                name="search_wikipedia", 
                func=self.search_apis.search_wikipedia,
                description="搜索Wikipedia百科全书，适合查找通用知识、概念解释、历史事件、人物传记等内容"
            ),
            Tool(
                name="search_google_scholar",
                func=self.search_apis.search_google_scholar,
                description="搜索Google Scholar学术搜索，适合查找各类学术文献、引用情况、学术期刊论文等"
            )
        ]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询意图，决定使用哪些搜索源"""
        self.debug_info.add_log("query_analysis_start", {"query": query})
        
        # 使用Claude分析问题
        analysis_prompt = f"""
        请分析以下问题，判断应该使用哪些搜索源来获取信息：
        
        问题：{query}
        
        可用的搜索源：
        1. arXiv - 学术论文、预印本、科研成果
        2. Wikipedia - 通用知识、概念解释、历史事件
        3. Google Scholar - 学术文献、期刊论文、引用统计
        
        请以JSON格式返回分析结果：
        {{
            "query_type": "学术/通用/混合",
            "recommended_sources": ["source1", "source2"],
            "search_keywords": ["关键词1", "关键词2"],
            "reasoning": "选择理由"
        }}
        """
        
        try:
            response = self.claude_llm._call(analysis_prompt)
            # 尝试解析JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis_result = json.loads(json_match.group())
            else:
                # 如果解析失败，使用默认策略
                analysis_result = {
                    "query_type": "混合",
                    "recommended_sources": ["arxiv", "wikipedia"],
                    "search_keywords": [query],
                    "reasoning": "默认搜索策略"
                }
            
            self.debug_info.add_log("query_analysis_complete", analysis_result)
            return analysis_result
            
        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            self.debug_info.add_log("query_analysis_error", {"error": str(e)})
            return {
                "query_type": "混合",
                "recommended_sources": ["arxiv", "wikipedia"],
                "search_keywords": [query],
                "reasoning": "分析失败，使用默认策略"
            }
    
    def parallel_search(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """并行搜索多个数据源"""
        self.debug_info.add_log("parallel_search_start", {
            "query": query,
            "sources": sources
        })
        
        search_results = {}
        
        # 使用线程池并行搜索
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {}
            
            for source in sources:
                if source == "arxiv" and hasattr(self.search_apis, 'search_arxiv'):
                    future = executor.submit(self.search_apis.search_arxiv, query)
                    future_to_source[future] = "arxiv"
                elif source == "wikipedia" and hasattr(self.search_apis, 'search_wikipedia'):
                    future = executor.submit(self.search_apis.search_wikipedia, query)
                    future_to_source[future] = "wikipedia"
                elif source == "google_scholar" and hasattr(self.search_apis, 'search_google_scholar'):
                    future = executor.submit(self.search_apis.search_google_scholar, query)
                    future_to_source[future] = "google_scholar"
            
            # 收集结果
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    search_results[source] = json.loads(result) if isinstance(result, str) and result.startswith('[') else result
                except Exception as e:
                    search_results[source] = f"搜索失败: {str(e)}"
        
        self.debug_info.add_log("parallel_search_complete", {
            "sources_searched": list(search_results.keys()),
            "total_results": sum(len(r) if isinstance(r, list) else 0 for r in search_results.values())
        })
        
        return search_results
    
    def summarize_results(self, query: str, search_results: Dict[str, Any]) -> str:
        """使用Claude汇总搜索结果"""
        self.debug_info.add_log("summarization_start", {
            "query": query,
            "sources_count": len(search_results)
        })
        
        # 构建汇总提示
        summary_prompt = f"""
        基于以下搜索结果，请为用户问题提供一个全面、准确的回答。
        
        用户问题：{query}
        
        搜索结果：
        {json.dumps(search_results, ensure_ascii=False, indent=2)}
        
        请提供：
        1. 直接回答用户问题
        2. 整合各个来源的信息
        3. 标注信息来源
        4. 如果有学术论文，请特别提及
        
        请用中文回答。
        """
        
        try:
            summary = self.claude_llm._call(summary_prompt)
            self.debug_info.add_log("summarization_complete", {
                "summary_length": len(summary)
            })
            return summary
        except Exception as e:
            error_msg = f"汇总失败: {str(e)}"
            self.debug_info.add_log("summarization_error", {"error": str(e)})
            return error_msg
    
    def search(self, query: str) -> Dict[str, Any]:
        """执行智能搜索的主方法"""
        self.debug_info.add_log("search_start", {"query": query})
        
        try:
            # 1. 分析查询
            analysis = self.analyze_query(query)
            
            # 2. 并行搜索
            search_results = self.parallel_search(
                query, 
                analysis.get("recommended_sources", ["arxiv", "wikipedia"])
            )
            
            # 3. 汇总结果
            summary = self.summarize_results(query, search_results)
            
            # 4. 构建最终响应
            final_response = {
                "status": "success",
                "query": query,
                "analysis": analysis,
                "search_results": search_results,
                "summary": summary,
                "debug_logs": self.debug_info.get_logs()
            }
            
            self.debug_info.add_log("search_complete", {
                "query": query,
                "total_debug_logs": len(self.debug_info.get_logs())
            })
            
            return final_response
            
        except Exception as e:
            error_response = {
                "status": "error",
                "query": query,
                "error": str(e),
                "debug_logs": self.debug_info.get_logs()
            }
            self.debug_info.add_log("search_error", {"error": str(e)})
            return error_response

def main():
    """主函数 - 演示使用"""
    # 获取Claude API密钥
    claude_api_key = os.getenv("CLAUDE_API_KEY") or "sk-ALXXaygI4QIkj315355f4e2cA38c47A9B589D2D0F71b09D5"
    
    # 创建智能搜索Agent
    agent = IntelligentSearchAgent(claude_api_key)
    
    # 测试查询
    test_queries = [
        "大语言模型的最新研究进展",
        "量子计算的基本原理是什么",
        "深度学习在医疗领域的应用"
    ]
    
    for query in test_queries[:1]:  # 只测试第一个查询
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        
        # 执行搜索
        result = agent.search(query)
        
        # 打印JSON格式的结果
        print("\n完整结果 (JSON格式):")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 单独打印汇总
        print(f"\n{'='*60}")
        print("汇总回答:")
        print('='*60)
        print(result.get("summary", "无汇总"))

if __name__ == "__main__":
    main() 