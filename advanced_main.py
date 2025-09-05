#!/usr/bin/env python3
"""
高级AI搜索代理 - 增强版
支持多种搜索类型、有状态对话、流式响应和复杂工作流
"""

import asyncio
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from stateful_agent import StatefulSearchAgent, ConversationManager
from streaming_workflow import StreamingWorkflowEngine, AsyncTaskQueue
from schemas import SearchConfig, SearchType, StreamChunk

# 加载环境变量
load_dotenv()

class AdvancedSearchSystem:
    """高级搜索系统"""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.workflow_engine = StreamingWorkflowEngine(self.conversation_manager)
        self.task_queue = AsyncTaskQueue(max_concurrent_tasks=3)
        
        # 默认模型配置
        self.default_model_config = self._get_model_config()
        
        # 创建默认代理
        self.default_agent = self.conversation_manager.create_agent(
            "default", 
            self.default_model_config
        )
    
    def _get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        # 检查可用的API密钥并选择最佳模型
        zhipu_key = os.getenv('ZHIPU_API_KEY')
        if zhipu_key:
            return {
                'api_key': zhipu_key,
                'base_url': 'https://open.bigmodel.cn/api/paas/v4',
                'model_name': 'glm-4-flash'
            }
        
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            return {
                'api_key': deepseek_key,
                'base_url': 'https://api.deepseek.com',
                'model_name': 'deepseek-chat'
            }
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            return {
                'api_key': openai_key,
                'model_name': 'gpt-3.5-turbo'
            }
        
        raise ValueError("未找到可用的API密钥，请设置 ZHIPU_API_KEY、DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
    
    async def start(self):
        """启动系统"""
        await self.task_queue.start_workers()
        print("🚀 高级AI搜索系统已启动")
        print(f"📊 使用模型: {self.default_model_config.get('model_name')}")
        print(f"🔧 可用工作流模板: {', '.join(self.workflow_engine.list_workflow_templates())}")
    
    async def stop(self):
        """停止系统"""
        await self.task_queue.stop_workers()
        print("🛑 系统已停止")
    
    async def simple_search(self, query: str, search_type: str = "general") -> Dict[str, Any]:
        """简单搜索"""
        config = SearchConfig(
            search_type=SearchType(search_type),
            max_results=5,
            include_summary=True
        )
        
        result = await self.default_agent.search_tools.smart_search(query, config)
        return result.dict()
    
    async def conversational_search(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """对话式搜索"""
        if conversation_id is None:
            conversation_id = await self.default_agent.start_conversation()
        
        result = await self.default_agent.chat(conversation_id, query)
        return result
    
    async def streaming_search(self, query: str, conversation_id: Optional[str] = None):
        """流式搜索"""
        if conversation_id is None:
            conversation_id = await self.default_agent.start_conversation()
        
        async for chunk in self.default_agent.chat_stream(conversation_id, query):
            yield chunk
    
    async def workflow_search(self, workflow_template: str, params: Dict[str, Any]):
        """工作流搜索"""
        async for chunk in self.workflow_engine.execute_workflow_stream(
            workflow_template, params, "default"
        ):
            yield chunk
    
    async def interactive_mode(self):
        """交互模式"""
        print("\n🤖 欢迎使用高级AI搜索代理！")
        print("💡 输入 'help' 查看帮助，输入 'quit' 退出")
        print("=" * 50)
        
        conversation_id = await self.default_agent.start_conversation()
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.startswith('/workflow'):
                    await self._handle_workflow_command(user_input)
                    continue
                
                if user_input.startswith('/stream'):
                    query = user_input[7:].strip()
                    if query:
                        await self._handle_streaming_search(query, conversation_id)
                    else:
                        print("❌ 请提供搜索查询")
                    continue
                
                # 普通对话搜索
                print("\n🤖 AI: ", end="", flush=True)
                result = await self.default_agent.chat(conversation_id, user_input)
                
                if 'error' in result:
                    print(f"❌ {result['error']}")
                else:
                    print(result['response'])
                    
                    # 显示建议
                    if result.get('suggestions'):
                        print(f"\n💡 相关建议: {', '.join(result['suggestions'][:3])}")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
        
        await self.default_agent.end_conversation(conversation_id)
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🔍 高级AI搜索代理 - 帮助信息

基本搜索:
  直接输入问题即可进行智能搜索

特殊命令:
  /stream <查询>     - 流式搜索响应
  /workflow <模板>   - 执行复杂工作流
  help              - 显示此帮助信息
  quit/exit         - 退出程序

可用工作流模板:
  comprehensive_search    - 综合搜索分析
  multi_source_analysis  - 多源信息分析
  research_report        - 研究报告生成
  competitive_analysis   - 竞争分析报告
  trend_analysis         - 趋势分析报告

示例:
  生成式AI的最新进展
  /stream 人工智能发展趋势
  /workflow comprehensive_search topic=机器学习

功能特点:
  ✅ 智能搜索类型识别（新闻、学术、产品等）
  ✅ 多轮对话上下文记忆
  ✅ 流式响应实时反馈
  ✅ 复杂工作流自动化
  ✅ 多工具集成（搜索、摘要、翻译等）
        """
        print(help_text)
    
    async def _handle_workflow_command(self, command: str):
        """处理工作流命令"""
        parts = command.split()
        if len(parts) < 2:
            print("❌ 用法: /workflow <模板名> [参数]")
            print(f"可用模板: {', '.join(self.workflow_engine.list_workflow_templates())}")
            return
        
        template = parts[1]
        
        # 解析参数
        params = {}
        for part in parts[2:]:
            if '=' in part:
                key, value = part.split('=', 1)
                params[key] = value
        
        # 如果没有提供必要参数，使用默认值
        if template in ['comprehensive_search', 'multi_source_analysis', 'research_report'] and 'query' not in params and 'topic' not in params:
            query = input("请输入搜索主题: ").strip()
            if template == 'comprehensive_search':
                params['query'] = query
            else:
                params['topic'] = query
        
        print(f"\n🚀 执行工作流: {template}")
        print("=" * 30)
        
        try:
            async for chunk in self.workflow_engine.execute_workflow_stream(
                template, params, "default"
            ):
                if chunk.chunk_type == "text":
                    print(f"📝 {chunk.content}")
                elif chunk.chunk_type == "result":
                    content = chunk.content
                    if isinstance(content, dict):
                        step_name = content.get('step_name', '未知步骤')
                        if 'error' in content:
                            print(f"❌ {step_name}: {content['error']}")
                        else:
                            print(f"✅ {step_name}: 完成")
                elif chunk.chunk_type == "complete":
                    content = chunk.content
                    if isinstance(content, dict) and 'error' not in content:
                        print(f"\n🎉 工作流完成！")
                        print(f"⏱️ 耗时: {content.get('duration', 0):.2f}秒")
                        print(f"✅ 完成步骤: {content.get('steps_completed', 0)}")
                    else:
                        print(f"\n❌ 工作流失败: {content.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"❌ 工作流执行错误: {e}")
    
    async def _handle_streaming_search(self, query: str, conversation_id: str):
        """处理流式搜索"""
        print(f"\n🔍 流式搜索: {query}")
        print("=" * 30)
        
        try:
            async for chunk in self.default_agent.chat_stream(conversation_id, query):
                if chunk.chunk_type == "text":
                    print(f"📝 {chunk.content}")
                elif chunk.chunk_type == "result":
                    content = chunk.content
                    if isinstance(content, dict):
                        print(f"📊 搜索结果已获取")
                elif chunk.chunk_type == "summary":
                    print(f"\n🤖 AI分析:\n{chunk.content}")
                elif chunk.chunk_type == "complete":
                    content = chunk.content
                    if isinstance(content, dict) and 'suggestions' in content:
                        suggestions = content['suggestions']
                        if suggestions:
                            print(f"\n💡 相关建议: {', '.join(suggestions[:3])}")
        
        except Exception as e:
            print(f"❌ 流式搜索错误: {e}")

# 命令行接口
async def main():
    """主函数"""
    system = AdvancedSearchSystem()
    
    try:
        await system.start()
        
        # 检查命令行参数
        import sys
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "search" and len(sys.argv) > 2:
                # 简单搜索模式
                query = " ".join(sys.argv[2:])
                result = await system.simple_search(query)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            elif command == "workflow" and len(sys.argv) > 3:
                # 工作流模式
                template = sys.argv[2]
                params = {}
                for arg in sys.argv[3:]:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        params[key] = value
                
                async for chunk in system.workflow_search(template, params):
                    if chunk.chunk_type == "complete":
                        print(json.dumps(chunk.content, indent=2, ensure_ascii=False))
            
            elif command == "interactive":
                # 交互模式
                await system.interactive_mode()
            
            else:
                print("用法:")
                print("  python advanced_main.py interactive           # 交互模式")
                print("  python advanced_main.py search <查询>         # 简单搜索")
                print("  python advanced_main.py workflow <模板> <参数> # 工作流搜索")
        
        else:
            # 默认交互模式
            await system.interactive_mode()
    
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())