#!/usr/bin/env python3
"""
arXiv API 论文查询测试脚本
用于测试 arXiv API 是否能正常连接和获取论文数据
"""

import sys
import urllib.request
import xml.etree.ElementTree as ET
import time

class ArxivAPITester:
    def __init__(self):
        """初始化 arXiv API 测试类"""
        self.base_url = "http://export.arxiv.org/api/query"
        
    def test_basic_query(self):
        """测试基本查询功能"""
        print("🔍 测试基本查询功能...")
        try:
            # 构建arXiv API查询URL
            query = 'search_query=cat:cs.AI+AND+ti:large+language+model&start=0&max_results=5'
            url = f'{self.base_url}?{query}'
            
            # 发送请求
            print(f"   发送请求到: {url}")
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
            print(f"   总结果数: {total_results}")
            
            # 获取文章条目
            entries = root.findall('.//atom:entry', namespaces)
            print(f"   获取到 {len(entries)} 篇论文")
            
            # 打印论文信息
            for i, entry in enumerate(entries, 1):
                title = entry.find('./atom:title', namespaces).text.strip()
                published = entry.find('./atom:published', namespaces).text
                authors = [author.find('./atom:name', namespaces).text for author in entry.findall('./atom:author', namespaces)]
                categories = [category.get('term') for category in entry.findall('./atom:category', namespaces)]
                
                print(f"\n   论文 {i}:")
                print(f"   标题: {title}")
                print(f"   发布日期: {published}")
                print(f"   作者: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
                print(f"   分类: {', '.join(categories)}")
                
            return True
                
        except Exception as e:
            print(f"❌ 基本查询测试失败：{e}")
            return False
    
    def test_advanced_query(self):
        """测试高级查询功能"""
        print("\n🔍 测试高级查询功能...")
        try:
            # 构建多条件查询
            query = 'search_query=cat:cs.CV+AND+cat:cs.AI+AND+submittedDate:[20230101+TO+20231231]&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
            url = f'{self.base_url}?{query}'
            
            # 发送请求
            print(f"   发送请求到: {url}")
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
            print(f"   总结果数: {total_results}")
            
            # 获取文章条目
            entries = root.findall('.//atom:entry', namespaces)
            print(f"   获取到 {len(entries)} 篇论文")
            
            # 打印论文信息
            for i, entry in enumerate(entries, 1):
                title = entry.find('./atom:title', namespaces).text.strip()
                published = entry.find('./atom:published', namespaces).text
                authors = [author.find('./atom:name', namespaces).text for author in entry.findall('./atom:author', namespaces)]
                
                # 获取摘要
                summary = entry.find('./atom:summary', namespaces).text.strip()
                summary_short = summary[:100] + "..." if len(summary) > 100 else summary
                
                # 获取DOI (如果有)
                doi_element = entry.find('./arxiv:doi', namespaces)
                doi = doi_element.text if doi_element is not None else "N/A"
                
                # 获取PDF链接
                pdf_link = None
                links = entry.findall('./atom:link', namespaces)
                for link in links:
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        break
                
                print(f"\n   论文 {i}:")
                print(f"   标题: {title}")
                print(f"   发布日期: {published}")
                print(f"   作者: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
                print(f"   摘要: {summary_short}")
                print(f"   DOI: {doi}")
                print(f"   PDF链接: {pdf_link}")
                
            return True
                
        except Exception as e:
            print(f"❌ 高级查询测试失败：{e}")
            return False
    
    def test_pagination(self):
        """测试分页查询功能"""
        print("\n🔍 测试分页查询功能...")
        try:
            # 定义查询参数
            query_base = 'search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending'
            results_per_page = 2
            
            # 进行多次分页查询
            for page in range(2):
                start = page * results_per_page
                
                # 构建带分页的查询URL
                query = f'{query_base}&start={start}&max_results={results_per_page}'
                url = f'{self.base_url}?{query}'
                
                # 发送请求
                print(f"\n   第{page+1}页查询，发送请求到: {url}")
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
                
                # 获取总结果数和当前页信息
                total_results = root.find('.//opensearch:totalResults', namespaces).text
                start_index = root.find('.//opensearch:startIndex', namespaces).text
                items_per_page = root.find('.//opensearch:itemsPerPage', namespaces).text
                
                print(f"   总结果数: {total_results}")
                print(f"   当前起始索引: {start_index}")
                print(f"   每页条目数: {items_per_page}")
                
                # 获取文章条目
                entries = root.findall('.//atom:entry', namespaces)
                print(f"   本页获取到 {len(entries)} 篇论文")
                
                # 打印论文信息
                for i, entry in enumerate(entries, 1):
                    title = entry.find('./atom:title', namespaces).text.strip()
                    published = entry.find('./atom:published', namespaces).text
                    
                    print(f"   论文 {start+i}:")
                    print(f"   标题: {title}")
                    print(f"   发布日期: {published}")
                
                # API限制，避免请求过快
                if page < 1:  # 如果不是最后一页，等待一下
                    print("   等待3秒以符合API限制...")
                    time.sleep(3)
            
            return True
                
        except Exception as e:
            print(f"❌ 分页查询测试失败：{e}")
            return False
    
    def test_specific_id(self):
        """测试通过ID查询论文"""
        print("\n🔍 测试通过ID查询论文...")
        try:
            # 使用ID直接查询论文
            paper_id = "2305.10403"  # GPT-4论文ID
            query = f'id_list={paper_id}'
            url = f'{self.base_url}?{query}'
            
            # 发送请求
            print(f"   发送请求到: {url}")
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
            
            # 获取论文条目
            entry = root.find('.//atom:entry', namespaces)
            
            if entry is not None:
                # 获取详细信息
                title = entry.find('./atom:title', namespaces).text.strip()
                published = entry.find('./atom:published', namespaces).text
                updated = entry.find('./atom:updated', namespaces).text
                summary = entry.find('./atom:summary', namespaces).text.strip()
                authors = [author.find('./atom:name', namespaces).text for author in entry.findall('./atom:author', namespaces)]
                categories = [category.get('term') for category in entry.findall('./atom:category', namespaces)]
                
                # 获取评论、DOI等额外信息
                comment_element = entry.find('./arxiv:comment', namespaces)
                comment = comment_element.text if comment_element is not None else "N/A"
                
                journal_ref_element = entry.find('./arxiv:journal_ref', namespaces)
                journal_ref = journal_ref_element.text if journal_ref_element is not None else "N/A"
                
                doi_element = entry.find('./arxiv:doi', namespaces)
                doi = doi_element.text if doi_element is not None else "N/A"
                
                # 打印详细信息
                print(f"\n   论文详情:")
                print(f"   ID: {paper_id}")
                print(f"   标题: {title}")
                print(f"   发布日期: {published}")
                print(f"   更新日期: {updated}")
                print(f"   作者: {', '.join(authors)}")
                print(f"   分类: {', '.join(categories)}")
                print(f"   评论: {comment}")
                print(f"   期刊引用: {journal_ref}")
                print(f"   DOI: {doi}")
                print(f"   摘要摘录: {summary[:150]}...")
                
                return True
            else:
                print(f"❌ 未找到ID为 {paper_id} 的论文")
                return False
                
        except Exception as e:
            print(f"❌ ID查询测试失败：{e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 arXiv API 论文查询测试\n")
        print("=" * 50)
        
        tests = [
            ("基本查询测试", self.test_basic_query),
            ("高级查询测试", self.test_advanced_query),
            ("分页查询测试", self.test_pagination),
            ("ID查询测试", self.test_specific_id)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {e}")
                results.append((test_name, False))
        
        # 打印总结
        print("\n" + "=" * 50)
        print("📊 测试结果总结:")
        
        passed = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{len(results)} 项测试通过")
        
        if passed == len(results):
            print("🎉 所有测试通过！arXiv API 连接正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查网络连接或 API 状态")
            return False


def main():
    """主函数"""
    tester = ArxivAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
