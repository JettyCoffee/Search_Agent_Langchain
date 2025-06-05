#!/usr/bin/env python3
"""
Gemini API 连接测试脚本
用于测试 Google Gemini API 是否能正常连接和获取数据
"""

import os
import sys
import json
from dotenv import load_dotenv
from google import genai
from PIL import Image

# 加载环境变量
load_dotenv()

class GeminiAPITester:
    def __init__(self):
        """初始化 Gemini API 测试类"""
        # 检查API密钥
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("⚠️ 未找到 GOOGLE_API_KEY 环境变量，请先设置 API 密钥")
            sys.exit(1)

        # 初始化 Gemini 客户端
        self.client = genai.Client(api_key=self.api_key)

    def test_basic_connection(self):
        """测试基本连接"""
        print("🔍 测试基本连接...")
        try:
            # 获取可用模型列表
            models = self.client.models.list()
            model_names = [model.name for model in models]
            
            if model_names:
                print(f"✅ 连接成功！找到 {len(model_names)} 个可用模型")
                print(f"   示例模型: {model_names[:3]}")
                return True
            else:
                print("❌ 连接失败：未找到可用模型")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False

    def test_text_generation(self):
        """测试文本生成功能"""
        print("\n🔍 测试文本生成功能...")
        try:
            # 使用 gemini-2.0-flash-001 模型生成文本
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents='用中文介绍一下你自己，不超过50个字'
            )
            
            if response and response.text:
                print(f"✅ 文本生成成功！")
                print(f"   响应: {response.text[:200]}")
                return True
            else:
                print("❌ 文本生成失败：未收到有效响应")
                return False
                
        except Exception as e:
            print(f"❌ 文本生成失败：{e}")
            return False

    def test_token_counting(self):
        """测试 Token 计数功能"""
        print("\n🔍 测试 Token 计数功能...")
        try:
            # 计算输入文本的 token 数
            response = self.client.models.count_tokens(
                model='gemini-2.0-flash-001',
                contents='用中文介绍一下你自己，不超过50个字'
            )
            
            if response and hasattr(response, 'total_tokens'):
                print(f"✅ Token 计数成功！")
                print(f"   总 Token 数: {response.total_tokens}")
                return True
            else:
                print("❌ Token 计数失败：未收到有效响应")
                return False
                
        except Exception as e:
            print(f"❌ Token 计数失败：{e}")
            return False

    def test_chat_functionality(self):
        """测试聊天功能"""
        print("\n🔍 测试聊天功能...")
        try:
            # 创建聊天会话
            chat = self.client.chats.create(model='gemini-2.0-flash-001')
            
            # 发送第一条消息
            response1 = chat.send_message('用中文讲个笑话')
            
            # 发送第二条消息（基于上下文）
            response2 = chat.send_message('这个笑话的主题是什么？')
            
            if response1.text and response2.text:
                print(f"✅ 聊天功能测试成功！")
                print(f"   第一条响应: {response1.text[:100]}...")
                print(f"   第二条响应: {response2.text[:100]}...")
                return True
            else:
                print("❌ 聊天功能测试失败：未收到有效响应")
                return False
                
        except Exception as e:
            print(f"❌ 聊天功能测试失败：{e}")
            return False

    def test_google_search(self):
        """测试Google搜索功能"""
        print("\n🔍 测试Google搜索功能...")
        try:
            # 使用 gemini-2.0-flash 模型与Google搜索功能
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents='中国最近的一次载人航天发射是什么时候？',
                config={"tools": [{"google_search": {}}]}
            )
            
            if response and response.text:
                print(f"✅ Google搜索功能测试成功！")
                print(f"   响应: {response.text[:200]}")
                
                # 打印搜索元数据
                if hasattr(response.candidates[0], 'grounding_metadata') and response.candidates[0].grounding_metadata:
                    metadata = response.candidates[0].grounding_metadata
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        print(f"   搜索查询: {metadata.web_search_queries}")
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        sources = [chunk.web.title for chunk in metadata.grounding_chunks if hasattr(chunk, 'web')]
                        print(f"   信息来源: {', '.join(sources)}")
                return True
            else:
                print("❌ Google搜索功能测试失败：未收到有效响应")
                return False
                
        except Exception as e:
            print(f"❌ Google搜索功能测试失败：{e}")
            return False
            
    def test_arxiv_api(self):
        """测试arXiv API论文查询功能"""
        print("\n🔍 测试arXiv API论文查询功能...")
        try:
            import urllib.request
            import xml.etree.ElementTree as ET
            
            # 构建arXiv API查询URL
            query = 'search_query=cat:cs.AI+AND+ti:large+language+model&start=0&max_results=5'
            url = f'http://export.arxiv.org/api/query?{query}'
            
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
            print(f"❌ arXiv API论文查询测试失败：{e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Gemini API 连接测试\n")
        print("=" * 50)
        
        tests = [
            ("基本连接测试", self.test_basic_connection),
            ("文本生成测试", self.test_text_generation),
            ("Token 计数测试", self.test_token_counting),
            ("聊天功能测试", self.test_chat_functionality),
            ("Google搜索功能测试", self.test_google_search),
            ("arXiv API论文查询测试", self.test_arxiv_api)
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
            print("🎉 所有测试通过！Gemini API 连接正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查网络连接或 API 状态")
            return False


def main():
    """主函数"""
    tester = GeminiAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
