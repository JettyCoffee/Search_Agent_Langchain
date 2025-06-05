#!/usr/bin/env python3
"""
Claude API 连接测试脚本
用于测试 Claude API 是否能正常连接和获取数据
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ClaudeAPITester:
    def __init__(self, api_key=None, api_base=None):
        """初始化 Claude API 测试类"""
        # 检查API密钥
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY") or "sk-ALXXaygI4QIkj315355f4e2cA38c47A9B589D2D0F71b09D5"
        if not self.api_key:
            print("⚠️ 未找到 CLAUDE_API_KEY 环境变量，请先设置 API 密钥")
            sys.exit(1)
            
        # 设置API基础URL
        self.api_base = api_base or os.getenv("CLAUDE_API_BASE") or "https://api.mjdjourney.cn/v1"
        
        # 设置请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def test_basic_connection(self):
        """测试基本连接"""
        print("🔍 测试基本连接...")
        try:
            # 构建一个简单的请求来测试连接
            response = requests.get(
                f"{self.api_base}/models",
                headers=self.headers
            )
            
            # 检查响应状态
            if response.status_code == 200:
                models = response.json()
                model_names = [model.get("id") for model in models.get("data", [])]
                
                if model_names:
                    print(f"✅ 连接成功！找到 {len(model_names)} 个可用模型")
                    print(f"   示例模型: {model_names[:3]}")
                    return True
                else:
                    print("❌ 连接失败：未找到可用模型")
                    return False
            else:
                print(f"❌ 连接失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False

    def test_text_generation(self):
        """测试文本生成功能"""
        print("\n🔍 测试文本生成功能...")
        try:
            # 使用 chat/completions 接口生成文本
            data = {
                "model": "claude-3-7-sonnet-20250219",  # 使用提供的模型名称
                "messages": [
                    {"role": "user", "content": "用中文介绍一下你自己，不超过50个字"}
                ],
                "max_tokens": 100
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    print(f"✅ 文本生成成功！")
                    print(f"   响应: {content[:200]}")
                    return True
                else:
                    print("❌ 文本生成失败：未收到有效响应内容")
                    print(f"   原始响应: {result}")
                    return False
            else:
                print(f"❌ 文本生成失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 文本生成失败：{e}")
            return False

    def test_token_counting(self):
        """测试 Token 计数功能"""
        print("\n🔍 测试 Token 计数功能...")
        try:
            # 许多API提供商使用chat/completions接口并返回token使用情况
            data = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": "用中文介绍一下你自己，不超过50个字"}
                ],
                "max_tokens": 1  # 最小化输出以便测试
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                usage = result.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                if total_tokens > 0:
                    print(f"✅ Token 计数成功！")
                    print(f"   提示 Token 数: {prompt_tokens}")
                    print(f"   完成 Token 数: {completion_tokens}")
                    print(f"   总 Token 数: {total_tokens}")
                    return True
                else:
                    print("❌ Token 计数失败：未收到有效的 Token 计数")
                    print(f"   原始响应: {result}")
                    return False
            else:
                print(f"❌ Token 计数失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token 计数失败：{e}")
            return False

    def test_chat_functionality(self):
        """测试聊天功能"""
        print("\n🔍 测试聊天功能...")
        try:
            # 发送第一条消息
            data1 = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": "用中文讲个笑话"}
                ],
                "max_tokens": 200
            }
            
            response1 = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data1
            )
            
            if response1.status_code != 200:
                print(f"❌ 聊天功能测试失败：HTTP状态码 {response1.status_code}")
                print(f"   错误信息: {response1.text}")
                return False
                
            result1 = response1.json()
            content1 = result1.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 发送第二条消息（基于上下文）
            data2 = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": "用中文讲个笑话"},
                    {"role": "assistant", "content": content1},
                    {"role": "user", "content": "这个笑话的主题是什么？"}
                ],
                "max_tokens": 100
            }
            
            response2 = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data2
            )
            
            if response2.status_code != 200:
                print(f"❌ 聊天功能测试失败：HTTP状态码 {response2.status_code}")
                print(f"   错误信息: {response2.text}")
                return False
                
            result2 = response2.json()
            content2 = result2.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if content1 and content2:
                print(f"✅ 聊天功能测试成功！")
                print(f"   第一条响应: {content1[:100]}...")
                print(f"   第二条响应: {content2[:100]}...")
                return True
            else:
                print("❌ 聊天功能测试失败：未收到有效响应")
                return False
                
        except Exception as e:
            print(f"❌ 聊天功能测试失败：{e}")
            return False

    def test_streaming(self):
        """测试流式响应功能"""
        print("\n🔍 测试流式响应功能...")
        try:
            # 使用 streaming 参数
            data = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": "用中文写一首简短的诗"}
                ],
                "max_tokens": 150,
                "stream": True
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                stream=True  # 使用requests的流式传输
            )
            
            # 检查响应状态
            if response.status_code == 200:
                print(f"✅ 流式响应测试成功！")
                print(f"   流式响应数据片段:")
                
                # 读取前几个数据块作为示例
                full_response = ""
                for i, chunk in enumerate(response.iter_lines()):
                    if chunk and chunk.strip():
                        # 过滤掉空行
                        chunk_data = chunk.decode('utf-8')
                        if chunk_data.startswith('data: '):
                            chunk_data = chunk_data[6:]  # 移除 "data: " 前缀
                        
                        if chunk_data != "[DONE]" and chunk_data:
                            try:
                                parsed = json.loads(chunk_data)
                                delta = parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                full_response += delta
                                
                                # 只显示前3个数据块
                                if i < 3:
                                    print(f"   片段 {i+1}: {chunk_data[:50]}...")
                            except json.JSONDecodeError:
                                print(f"   无法解析JSON: {chunk_data}")
                    
                    # 只处理前10个数据块，避免输出过多
                    if i >= 10:
                        print("   ...更多数据省略...")
                        break
                
                print(f"   完整响应: {full_response[:100]}...")
                return True
            else:
                print(f"❌ 流式响应测试失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 流式响应测试失败：{e}")
            return False

    def test_json_output(self):
        """测试JSON格式输出功能"""
        print("\n🔍 测试JSON格式输出功能...")
        try:
            # 请求JSON格式的输出
            data = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": "以JSON格式返回三个中国城市及其人口。格式为{\"cities\": [{\"name\": \"城市名\", \"population\": \"人口数\"}]}"}
                ],
                "max_tokens": 200,
                "response_format": {"type": "json_object"}  # 指定JSON输出格式
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    try:
                        # 尝试解析JSON响应
                        json_content = json.loads(content)
                        print(f"✅ JSON格式输出测试成功！")
                        print(f"   JSON响应: {json.dumps(json_content, ensure_ascii=False, indent=2)[:200]}...")
                        return True
                    except json.JSONDecodeError:
                        print(f"❌ JSON格式输出测试失败：返回的不是有效JSON")
                        print(f"   原始响应: {content[:200]}")
                        return False
                else:
                    print("❌ JSON格式输出测试失败：未收到有效响应内容")
                    print(f"   原始响应: {result}")
                    return False
            else:
                print(f"❌ JSON格式输出测试失败：HTTP状态码 {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ JSON格式输出测试失败：{e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Claude API 连接测试\n")
        print("=" * 50)
        
        tests = [
            ("基本连接测试", self.test_basic_connection),
            ("文本生成测试", self.test_text_generation),
            ("Token 计数测试", self.test_token_counting),
            ("聊天功能测试", self.test_chat_functionality),
            ("流式响应测试", self.test_streaming),
            ("JSON格式输出测试", self.test_json_output)
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
            print("🎉 所有测试通过！Claude API 连接正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查网络连接或 API 状态")
            return False


def main():
    """主函数"""
    # 可以从命令行参数获取API密钥和基础URL
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    api_base = sys.argv[2] if len(sys.argv) > 2 else None
    
    tester = ClaudeAPITester(api_key=api_key, api_base=api_base)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
