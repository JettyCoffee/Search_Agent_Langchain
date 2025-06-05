#!/usr/bin/env python3
"""
智能搜索Agent - 简化版
不依赖LangChain框架，直接实现智能搜索功能
"""

import os
import json
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# 导入已有的API测试类
from test_arxiv_api import ArxivAPITester
from test_wikipedia_api import WikipediaAPITester
from test_google_scholar_api import GoogleScholarAPITester

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

class ClaudeAPI:
    """Claude API调用器 (使用OpenAI客户端)"""
    def __init__(self, api_key: str, api_base: str = "https://api.mjdjourney.cn/v1"):
        self.api_key = api_key
        self.api_base = api_base
        self.model = "claude-3-7-sonnet-20250219"
        
        # 导入OpenAI库（懒加载，避免全局导入）
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
    
    def call(self, prompt: str, max_tokens: int = 2000) -> str:
        """使用OpenAI客户端调用Claude API"""
        try:
            # 检查是否成功导入了OpenAI
            if self.import_error:
                return f"调用失败: 无法导入OpenAI库 - {str(self.import_error)}"
            
            # 使用OpenAI客户端
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
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
    
    def search_arxiv(self, query: str) -> Dict[str, Any]:
        """搜索arXiv论文"""
        self.debug_info.add_log("arxiv_search_start", {"query": query})
        try:
            # 构建查询
            encoded_query = urllib.parse.quote(query)
            url = f'{self.arxiv.base_url}?search_query=all:{encoded_query}&start=0&max_results=5'
            
            with urllib.request.urlopen(url, timeout=20) as response:
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
                
                # 获取arXiv ID和链接
                id_elem = entry.find('./atom:id', namespaces)
                arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else ""
                
                results.append({
                    "title": title,
                    "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                    "authors": authors[:3],
                    "published": published,
                    "arxiv_id": arxiv_id,
                    "link": f"https://arxiv.org/abs/{arxiv_id}"
                })
            
            self.debug_info.add_log("arxiv_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            error_msg = f"arXiv搜索失败: {str(e)}"
            self.debug_info.add_log("arxiv_search_error", {"error": str(e)})
            return {"status": "error", "error": error_msg}
    
    def search_wikipedia(self, query: str) -> Dict[str, Any]:
        """搜索Wikipedia"""
        self.debug_info.add_log("wikipedia_search_start", {"query": query})
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 5,
                'srprop': 'snippet|titlesnippet|size|wordcount|timestamp'
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
                        "snippet": item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
                        "size": item.get('size', 0),
                        "wordcount": item.get('wordcount', 0),
                        "timestamp": item.get('timestamp', ''),
                        "link": f"https://zh.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', ''))}"
                    })
            
            self.debug_info.add_log("wikipedia_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            error_msg = f"Wikipedia搜索失败: {str(e)}"
            self.debug_info.add_log("wikipedia_search_error", {"error": str(e)})
            return {"status": "error", "error": error_msg}
    
    def search_google_scholar(self, query: str) -> Dict[str, Any]:
        """搜索Google Scholar"""
        self.debug_info.add_log("google_scholar_search_start", {"query": query})
        try:
            if not hasattr(self.google_scholar, 'api_key') or not self.google_scholar.api_key:
                return {"status": "error", "error": "Google Scholar API密钥未设置"}
            
            params = self.google_scholar.params.copy()
            params["q"] = query
            
            response = requests.get(
                self.google_scholar.api_base,
                params=params,
                timeout=20
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", [])[:5]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                    "publication_info": item.get("publication_info", {}).get("summary", ""),
                    "cited_by": item.get("inline_links", {}).get("cited_by", {}).get("total", 0),
                    "authors": [author.get("name", "") for author in item.get("publication_info", {}).get("authors", [])][:3]
                })
            
            self.debug_info.add_log("google_scholar_search_complete", {
                "query": query,
                "results_count": len(results)
            })
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            error_msg = f"Google Scholar搜索失败: {str(e)}"
            self.debug_info.add_log("google_scholar_search_error", {"error": str(e)})
            return {"status": "error", "error": error_msg}

class IntelligentSearchAgent:
    """智能搜索Agent主类"""
    
    def __init__(self, claude_api_key: str):
        self.debug_info = DebugInfo()
        self.claude_api = ClaudeAPI(api_key=claude_api_key)
        self.search_apis = SearchAPIs(self.debug_info)
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询意图，决定使用哪些搜索源"""
        self.debug_info.add_log("query_analysis_start", {"query": query})
        
        # 使用Claude分析问题
        analysis_prompt = f"""
        请分析以下问题，判断应该使用哪些搜索源来获取信息：
        
        问题：{query}
        
        可用的搜索源：
        1. arxiv - 学术论文、预印本、科研成果
        2. wikipedia - 通用知识、概念解释、历史事件  
        3. google_scholar - 学术文献、期刊论文、引用统计
        
        请以JSON格式返回分析结果：
        {{
            "query_type": "学术/通用/混合",
            "recommended_sources": ["source1", "source2"],
            "search_keywords": ["关键词1", "关键词2"],
            "reasoning": "选择理由"
        }}
        """
        
        try:
            response = self.claude_api.call(analysis_prompt)
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
                if source == "arxiv":
                    future = executor.submit(self.search_apis.search_arxiv, query)
                    future_to_source[future] = "arxiv"
                elif source == "wikipedia":
                    future = executor.submit(self.search_apis.search_wikipedia, query)
                    future_to_source[future] = "wikipedia"
                elif source == "google_scholar":
                    future = executor.submit(self.search_apis.search_google_scholar, query)
                    future_to_source[future] = "google_scholar"
            
            # 收集结果
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    search_results[source] = result
                except Exception as e:
                    search_results[source] = {"status": "error", "error": str(e)}
        
        self.debug_info.add_log("parallel_search_complete", {
            "sources_searched": list(search_results.keys()),
            "success_count": sum(1 for r in search_results.values() if r.get("status") == "success")
        })
        
        return search_results
    
    def summarize_results(self, query: str, search_results: Dict[str, Any]) -> str:
        """使用Claude汇总搜索结果"""
        self.debug_info.add_log("summarization_start", {
            "query": query,
            "sources_count": len(search_results)
        })
        
        # 准备搜索结果摘要
        results_summary = {}
        for source, data in search_results.items():
            if data.get("status") == "success":
                results_summary[source] = data.get("results", [])
        
        # 构建汇总提示
        summary_prompt = f"""
        基于以下搜索结果，请为用户问题提供一个全面、准确的回答。

        用户问题：{query}

        搜索结果：
        {json.dumps(results_summary, ensure_ascii=False, indent=2)}

        请提供：
        1. 直接回答用户问题（开门见山）
        2. 整合各个来源的信息（准确引用）
        3. 如果有学术论文，请特别提及标题和作者
        4. 如果有Wikipedia内容，说明基础概念
        5. 标注每个重要信息的来源

        请用中文回答，确保准确性和可读性。
        """
        
        try:
            summary = self.claude_api.call(summary_prompt, max_tokens=3000)
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
                "timestamp": datetime.now().isoformat(),
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
                "timestamp": datetime.now().isoformat(),
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
    print("🚀 初始化智能搜索Agent...")
    agent = IntelligentSearchAgent(claude_api_key)
    
    # 测试查询
    test_query = "大语言模型的最新研究进展"
    
    print(f"\n📌 测试查询: {test_query}")
    print("="*60)
    
    # 执行搜索
    result = agent.search(test_query)
    
    # 保存完整结果到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_result_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {filename}")
    
    # 打印汇总
    print(f"\n{'='*60}")
    print("🤖 Claude AI 汇总结果:")
    print('='*60)
    print(result.get("summary", "无汇总"))
    
    # 打印搜索统计
    print(f"\n{'='*60}")
    print("📊 搜索统计:")
    print('='*60)
    if "search_results" in result:
        for source, data in result["search_results"].items():
            if data.get("status") == "success":
                count = len(data.get("results", []))
                print(f"✅ {source}: 找到 {count} 条结果")
            else:
                print(f"❌ {source}: {data.get('error', '未知错误')}")

if __name__ == "__main__":
    main() 