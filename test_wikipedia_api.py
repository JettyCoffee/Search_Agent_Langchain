#!/usr/bin/env python3
"""
Wikipedia API连接测试脚本
用于测试Wikipedia API是否能正常连接和获取数据
"""

import requests
import json
import sys
from urllib.parse import quote


class WikipediaAPITester:
    def __init__(self):
        self.base_url = "https://zh.wikipedia.org/w/api.php"
        self.session = requests.Session()
        # 设置User-Agent以避免被封禁
        self.session.headers.update({
            'User-Agent': 'Wikipedia API Tester/1.0 (https://example.com/contact) requests/2.28.1'
        })

    def test_basic_connection(self):
        """测试基本连接"""
        print("🔍 测试基本连接...")
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'meta': 'siteinfo',
                'siprop': 'general'
            }
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'query' in data and 'general' in data['query']:
                site_name = data['query']['general'].get('sitename', 'Unknown')
                print(f"✅ 连接成功！站点名称: {site_name}")
                return True
            else:
                print("❌ 连接失败：响应格式不正确")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败：无法连接到Wikipedia服务器")
            return False
        except requests.exceptions.Timeout:
            print("❌ 连接失败：请求超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 连接失败：{e}")
            return False
        except json.JSONDecodeError:
            print("❌ 连接失败：响应不是有效的JSON格式")
            return False

    def test_search_functionality(self):
        """测试搜索功能"""
        print("\n🔍 测试搜索功能...")
        try:
            # 测试搜索"人工智能"
            search_query = "人工智能"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': 5
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'query' in data and 'search' in data['query']:
                results = data['query']['search']
                print(f"✅ 搜索成功！找到 {len(results)} 个结果")
                
                for i, result in enumerate(results[:3], 1):
                    title = result.get('title', 'Unknown')
                    snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                    print(f"   {i}. {title}")
                    if snippet:
                        print(f"      摘要: {snippet[:100]}...")
                return True
            else:
                print("❌ 搜索失败：响应格式不正确")
                return False
                
        except Exception as e:
            print(f"❌ 搜索失败：{e}")
            return False

    def test_page_content(self):
        """测试页面内容获取"""
        print("\n🔍 测试页面内容获取...")
        try:
            # 获取"北京"页面的内容摘要
            page_title = "北京"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': page_title,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'exsectionformat': 'plain'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'query' in data and 'pages' in data['query']:
                pages = data['query']['pages']
                for page_id, page_data in pages.items():
                    if page_id != '-1':  # -1表示页面不存在
                        title = page_data.get('title', 'Unknown')
                        extract = page_data.get('extract', '')
                        print(f"✅ 页面内容获取成功！页面: {title}")
                        if extract:
                            print(f"   摘要: {extract[:200]}...")
                        return True
                
                print("❌ 页面内容获取失败：页面不存在")
                return False
            else:
                print("❌ 页面内容获取失败：响应格式不正确")
                return False
                
        except Exception as e:
            print(f"❌ 页面内容获取失败：{e}")
            return False

    def test_api_limits(self):
        """测试API限制"""
        print("\n🔍 测试API限制...")
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'meta': 'userinfo'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'query' in data and 'userinfo' in data['query']:
                userinfo = data['query']['userinfo']
                user_groups = userinfo.get('groups', [])
                rate_limits = userinfo.get('ratelimits', {})
                
                print("✅ API限制信息获取成功！")
                print(f"   用户组: {', '.join(user_groups)}")
                if rate_limits:
                    print(f"   速率限制: {rate_limits}")
                else:
                    print("   速率限制: 标准限制（匿名用户）")
                return True
            else:
                print("❌ API限制信息获取失败")
                return False
                
        except Exception as e:
            print(f"❌ API限制信息获取失败：{e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Wikipedia API连接测试\n")
        print("=" * 50)
        
        tests = [
            ("基本连接测试", self.test_basic_connection),
            ("搜索功能测试", self.test_search_functionality),
            ("页面内容获取测试", self.test_page_content),
            ("API限制测试", self.test_api_limits)
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
            print("🎉 所有测试通过！Wikipedia API连接正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查网络连接或API状态")
            return False


def main():
    """主函数"""
    tester = WikipediaAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
