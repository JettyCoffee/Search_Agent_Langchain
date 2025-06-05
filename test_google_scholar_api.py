#!/usr/bin/env python3
"""
Google Scholar API 连接测试脚本
用于测试 Google Scholar API (通过SERP API)是否能正常连接和获取学术数据
"""

import os
import sys
import json
import requests
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GoogleScholarAPITester:
    def __init__(self, api_key=None):
        """初始化 Google Scholar API 测试类"""
        # 检查API密钥
        self.api_key = api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            print("⚠️ 未找到 SERP_API_KEY 环境变量，请先设置 API 密钥")
            sys.exit(1)
            
        # 设置API基础URL
        self.api_base = "https://serpapi.com/search"
        
        # 设置请求参数
        self.params = {
            "api_key": self.api_key,
            "engine": "google_scholar",
        }

    def test_basic_connection(self):
        """测试基本连接"""
        print("🔍 测试基本连接...")
        try:
            # 构建一个简单的请求来测试连接
            test_params = self.params.copy()
            test_params["q"] = "test"
            
            response = requests.get(
                self.api_base,
                params=test_params
            )
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                if "organic_results" in data or "search_metadata" in data:
                    print(f"✅ 连接成功！收到有效响应")
                    return True
                else:
                    print("❌ 连接失败：响应格式不符合预期")
                    print(f"   响应内容: {json.dumps(data, indent=2)[:200]}...")
                    return False
            else:
                print(f"❌ 连接失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False

    def test_search_query(self):
        """测试搜索查询功能"""
        print("\n🔍 测试搜索查询功能...")
        try:
            # 构建搜索查询
            search_params = self.params.copy()
            search_params["q"] = "large language models"
            
            response = requests.get(
                self.api_base,
                params=search_params
            )
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                
                if organic_results:
                    print(f"✅ 搜索查询成功！找到 {len(organic_results)} 条结果")
                    # 显示第一条结果作为示例
                    first_result = organic_results[0]
                    print(f"   示例结果: {first_result.get('title', '无标题')}")
                    if "publication_info" in first_result:
                        pub_info = first_result["publication_info"]
                        print(f"   出版信息: {pub_info.get('summary', '无信息')}")
                    return True
                else:
                    print("❌ 搜索查询失败：未找到结果")
                    print(f"   原始响应: {json.dumps(data, indent=2)[:200]}...")
                    return False
            else:
                print(f"❌ 搜索查询失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 搜索查询失败：{e}")
            return False

    def test_author_search(self):
        """测试作者搜索功能"""
        print("\n🔍 测试作者搜索功能...")
        try:
            # 构建作者搜索查询
            author_params = self.params.copy()
            author_params["q"] = "author:Hinton"  # 搜索Geoffrey Hinton的论文
            
            response = requests.get(
                self.api_base,
                params=author_params
            )
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                
                if organic_results:
                    print(f"✅ 作者搜索成功！找到 {len(organic_results)} 条结果")
                    # 显示第一条结果作为示例
                    first_result = organic_results[0]
                    print(f"   示例论文: {first_result.get('title', '无标题')}")
                    if "publication_info" in first_result:
                        pub_info = first_result["publication_info"]
                        print(f"   出版信息: {pub_info.get('summary', '无信息')}")
                    return True
                else:
                    print("❌ 作者搜索失败：未找到结果")
                    print(f"   原始响应: {json.dumps(data, indent=2)[:200]}...")
                    return False
            else:
                print(f"❌ 作者搜索失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 作者搜索失败：{e}")
            return False

    def test_citation_extraction(self):
        """测试引用提取功能"""
        print("\n🔍 测试引用提取功能...")
        try:
            # 先搜索一篇知名论文
            search_params = self.params.copy()
            search_params["q"] = "Attention is All You Need"
            
            response = requests.get(
                self.api_base,
                params=search_params
            )
            
            if response.status_code != 200:
                print(f"❌ 引用提取失败：无法搜索论文，HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
            data = response.json()
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                print("❌ 引用提取失败：未找到目标论文")
                return False
                
            # 尝试获取第一篇论文的引用链接
            first_paper = organic_results[0]
            if "inline_links" not in first_paper or "cited_by" not in first_paper.get("inline_links", {}):
                print("❌ 引用提取失败：未找到引用信息")
                return False
                
            cited_by_link = first_paper["inline_links"]["cited_by"]["link"]
            cited_by_count = first_paper["inline_links"]["cited_by"].get("total", 0)
            
            print(f"✅ 引用提取成功！")
            print(f"   论文: {first_paper.get('title', '无标题')}")
            print(f"   被引用次数: {cited_by_count}")
            print(f"   引用链接: {cited_by_link}")
            return True
                
        except Exception as e:
            print(f"❌ 引用提取失败：{e}")
            return False

    def test_advanced_search(self):
        """测试高级搜索功能"""
        print("\n🔍 测试高级搜索功能...")
        try:
            # 构建高级搜索查询（例如按时间范围过滤）
            advanced_params = self.params.copy()
            advanced_params["q"] = "deep learning"
            advanced_params["as_ylo"] = "2020"  # 2020年及以后的论文
            
            response = requests.get(
                self.api_base,
                params=advanced_params
            )
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                
                if organic_results:
                    print(f"✅ 高级搜索成功！找到 {len(organic_results)} 条结果")
                    # 显示第一条结果作为示例
                    first_result = organic_results[0]
                    print(f"   示例论文: {first_result.get('title', '无标题')}")
                    if "publication_info" in first_result:
                        pub_info = first_result["publication_info"]
                        print(f"   出版信息: {pub_info.get('summary', '无信息')}")
                    return True
                else:
                    print("❌ 高级搜索失败：未找到结果")
                    print(f"   原始响应: {json.dumps(data, indent=2)[:200]}...")
                    return False
            else:
                print(f"❌ 高级搜索失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 高级搜索失败：{e}")
            return False

    def test_rate_limit(self):
        """测试API速率限制"""
        print("\n🔍 测试API速率限制...")
        try:
            # 发送3个连续请求，检查是否受到速率限制
            success_count = 0
            for i in range(3):
                print(f"   发送请求 {i+1}/3...")
                test_params = self.params.copy()
                test_params["q"] = f"test query {i}"
                
                response = requests.get(
                    self.api_base,
                    params=test_params
                )
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    print(f"   请求 {i+1} 失败：HTTP状态码 {response.status_code}")
                    print(f"   错误信息: {response.text}")
                
                # 短暂暂停，避免触发严格的速率限制
                if i < 2:  # 不需要在最后一次请求后暂停
                    print("   暂停1秒...")
                    time.sleep(1)
            
            if success_count == 3:
                print(f"✅ 速率限制测试通过！成功发送 {success_count}/3 个请求")
                return True
            else:
                print(f"⚠️ 速率限制测试部分通过：成功 {success_count}/3 个请求")
                return success_count > 0  # 如果至少有一个成功，仍然算部分成功
                
        except Exception as e:
            print(f"❌ 速率限制测试失败：{e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Google Scholar API 连接测试\n")
        print("=" * 50)
        
        tests = [
            ("基本连接测试", self.test_basic_connection),
            ("搜索查询测试", self.test_search_query),
            ("作者搜索测试", self.test_author_search),
            ("引用提取测试", self.test_citation_extraction),
            ("高级搜索测试", self.test_advanced_search),
            ("速率限制测试", self.test_rate_limit)
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
            print("🎉 所有测试通过！Google Scholar API 连接正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查网络连接或 API 状态")
            return False


def main():
    """主函数"""
    # 可以从命令行参数获取API密钥
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    
    tester = GoogleScholarAPITester(api_key=api_key)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
