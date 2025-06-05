#!/usr/bin/env python3
"""
交互式运行智能搜索Agent
允许用户输入查询并获取回答
"""

import os
import sys
import json
import argparse
import logging
from langchain_search_agent import LangChainSearchAgent

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行智能搜索Agent')
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
    parser.add_argument('-q', '--query', type=str, help='要搜索的查询')
    parser.add_argument('-o', '--output', type=str, help='将结果保存到指定的JSON文件')
    args = parser.parse_args()
    
    try:
        # 创建Agent
        agent = LangChainSearchAgent(debug=args.debug)
        
        if args.query:
            # 单次查询模式
            query = args.query
            result = process_query(agent, query, debug=args.debug)
            
            # 保存结果（如果指定）
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"结果已保存到 {args.output}")
        else:
            # 交互式模式
            run_interactive_mode(agent, args.debug)
    
    except Exception as e:
        logger.error(f"运行错误: {e}")
        sys.exit(1)

def process_query(agent, query, debug=False):
    """处理单个查询"""
    print(f"\n🔍 正在处理查询: {query}")
    print("请稍等，这可能需要一些时间...\n")
    
    # 运行查询
    result = agent.run(query)
    
    # 打印结果
    print("\n" + "="*80)
    print(f"📝 回答:")
    print("-"*80)
    print(result["answer"])
    
    # 打印调试信息
    if debug and "debug_info" in result:
        print("\n" + "="*80)
        print("🛠️ 调试信息:")
        print("-"*80)
        print("工具使用步骤:")
        for i, step in enumerate(result["debug_info"]["intermediate_steps"], 1):
            print(f"\n步骤 {i}:")
            print(f"使用工具: {step['tool']}")
            print(f"工具输入: {step['tool_input']}")
            print(f"工具输出: {step['tool_output'][:200]}..." if len(step['tool_output']) > 200 else step['tool_output'])
    
    return result

def run_interactive_mode(agent, debug=False):
    """运行交互式模式"""
    print("\n🤖 智能搜索Agent交互模式")
    print("=" * 80)
    print("输入您的查询，或输入 'exit' 退出")
    print("=" * 80)
    
    while True:
        try:
            # 获取用户输入
            query = input("\n🔍 请输入您的查询: ")
            
            # 检查是否退出
            if query.lower() in ('exit', 'quit', 'q', '退出'):
                print("\n👋 感谢使用智能搜索Agent！")
                break
                
            # 处理查询
            if query.strip():
                process_query(agent, query, debug=debug)
            
        except KeyboardInterrupt:
            print("\n\n👋 已中断，感谢使用智能搜索Agent！")
            break
        except Exception as e:
            print(f"\n❌ 处理查询时发生错误: {e}")

if __name__ == "__main__":
    main() 