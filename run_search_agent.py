#!/usr/bin/env python3
"""
智能搜索Agent交互式运行程序
"""

import os
import json
import sys
from datetime import datetime
try:
    from intelligent_search_agent import IntelligentSearchAgent
except ImportError:
    # 如果LangChain版本导入失败，使用简化版
    from intelligent_search_agent_simple import IntelligentSearchAgent

def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║            智能搜索Agent - Intelligent Search Agent      ║
    ║                                                          ║
    ║  整合 arXiv、Wikipedia、Google Scholar 的智能搜索系统    ║
    ║  使用 Claude AI 进行智能分析和汇总                       ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_search_progress(stage: str):
    """打印搜索进度"""
    stages = {
        "analyzing": "🔍 正在分析查询意图...",
        "searching": "🌐 正在并行搜索多个数据源...",
        "summarizing": "📝 正在使用Claude AI汇总结果...",
        "complete": "✅ 搜索完成！"
    }
    print(f"\n{stages.get(stage, stage)}")

def save_results(query: str, results: dict):
    """保存搜索结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到: {filename}")
    return filename

def display_results(results: dict, show_debug: bool = False):
    """显示搜索结果"""
    print("\n" + "="*60)
    print("搜索结果汇总")
    print("="*60)
    
    # 显示查询分析
    if "analysis" in results:
        analysis = results["analysis"]
        print(f"\n📊 查询分析:")
        print(f"   类型: {analysis.get('query_type', 'N/A')}")
        print(f"   推荐源: {', '.join(analysis.get('recommended_sources', []))}")
        print(f"   关键词: {', '.join(analysis.get('search_keywords', []))}")
        print(f"   理由: {analysis.get('reasoning', 'N/A')}")
    
    # 显示搜索结果统计
    if "search_results" in results:
        print(f"\n📈 搜索结果统计:")
        for source, data in results["search_results"].items():
            if isinstance(data, list):
                print(f"   {source}: 找到 {len(data)} 条结果")
            else:
                print(f"   {source}: {data}")
    
    # 显示AI汇总
    if "summary" in results:
        print(f"\n🤖 Claude AI 汇总:")
        print("-"*60)
        print(results["summary"])
        print("-"*60)
    
    # 显示调试信息（如果需要）
    if show_debug and "debug_logs" in results:
        print(f"\n🐛 调试信息 (共 {len(results['debug_logs'])} 条日志):")
        for log in results["debug_logs"][-5:]:  # 只显示最后5条
            print(f"   [{log['timestamp']}] {log['stage']}: {log['data']}")

def main():
    """主函数"""
    print_banner()
    
    # 获取API密钥
    claude_api_key = os.getenv("CLAUDE_API_KEY") or "sk-ALXXaygI4QIkj315355f4e2cA38c47A9B589D2D0F71b09D5"
    
    # 创建智能搜索Agent
    print("⚙️  正在初始化智能搜索Agent...")
    try:
        agent = IntelligentSearchAgent(claude_api_key)
        print("✅ Agent初始化成功！")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        sys.exit(1)
    
    # 主循环
    while True:
        print("\n" + "-"*60)
        print("请输入您的查询（输入 'exit' 退出，'help' 查看帮助）:")
        query = input("🔍 > ").strip()
        
        if query.lower() == 'exit':
            print("\n👋 感谢使用智能搜索Agent，再见！")
            break
        
        if query.lower() == 'help':
            print("\n📚 使用帮助:")
            print("   - 输入任何问题进行智能搜索")
            print("   - 系统会自动分析问题类型并选择合适的搜索源")
            print("   - 支持的搜索源: arXiv(学术论文)、Wikipedia(百科知识)、Google Scholar(学术文献)")
            print("   - 输入 'debug' 开启调试模式")
            print("   - 输入 'exit' 退出程序")
            continue
        
        if query.lower() == 'debug':
            show_debug = True
            print("🐛 调试模式已开启")
            continue
        
        if not query:
            print("⚠️  请输入有效的查询内容")
            continue
        
        # 执行搜索
        try:
            print_search_progress("analyzing")
            
            # 执行搜索（这里会自动显示进度）
            results = agent.search(query)
            
            print_search_progress("complete")
            
            # 显示结果
            display_results(results, show_debug=False)
            
            # 询问是否保存结果
            save_choice = input("\n是否保存搜索结果？(y/n): ").strip().lower()
            if save_choice == 'y':
                save_results(query, results)
            
        except KeyboardInterrupt:
            print("\n⚠️  搜索被用户中断")
            continue
        except Exception as e:
            print(f"\n❌ 搜索过程中发生错误: {e}")
            print("请检查网络连接和API配置")
            continue

if __name__ == "__main__":
    main() 