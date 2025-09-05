#!/usr/bin/env python3
"""
高级AI搜索代理使用示例
演示各种功能的使用方法
"""

import asyncio
import json
from advanced_main import AdvancedSearchSystem
from schemas import SearchConfig, SearchType

async def example_simple_search():
    """示例1: 简单搜索"""
    print("=" * 50)
    print("示例1: 简单搜索")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        # 不同类型的搜索
        queries = [
            ("生成式AI最新进展", "news"),
            ("机器学习算法研究", "academic"),
            ("iPhone 15 Pro价格", "product"),
            ("Python异步编程教程", "tech_doc")
        ]
        
        for query, search_type in queries:
            print(f"\n🔍 搜索: {query} (类型: {search_type})")
            result = await system.simple_search(query, search_type)
            
            print(f"📊 找到 {result.get('total_results', 0)} 个结果")
            print(f"📝 摘要: {result.get('summary', '无摘要')[:100]}...")
            
            # 显示前2个结果
            for i, item in enumerate(result.get('results', [])[:2]):
                print(f"  {i+1}. {item.get('title', '无标题')}")
                print(f"     {item.get('url', '无链接')}")
    
    finally:
        await system.stop()

async def example_conversational_search():
    """示例2: 对话式搜索"""
    print("=" * 50)
    print("示例2: 对话式搜索")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        # 开始对话
        conversation_id = await system.default_agent.start_conversation()
        
        # 多轮对话
        questions = [
            "什么是大语言模型？",
            "它们是如何训练的？",
            "有哪些著名的模型？",
            "未来发展趋势如何？"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n👤 问题{i}: {question}")
            result = await system.conversational_search(question, conversation_id)
            
            if 'error' not in result:
                print(f"🤖 回答: {result['response'][:200]}...")
                print(f"💬 对话轮次: {result['message_count']}")
                print(f"🏷️ 当前话题: {result.get('current_topic', '未知')}")
                
                # 显示建议
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print(f"💡 建议: {', '.join(suggestions[:2])}")
            else:
                print(f"❌ 错误: {result['error']}")
        
        # 结束对话
        await system.default_agent.end_conversation(conversation_id)
    
    finally:
        await system.stop()

async def example_streaming_search():
    """示例3: 流式搜索"""
    print("=" * 50)
    print("示例3: 流式搜索")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        query = "人工智能在医疗领域的应用"
        print(f"🔍 流式搜索: {query}")
        print("-" * 30)
        
        async for chunk in system.streaming_search(query):
            if chunk.chunk_type == "text":
                print(f"📝 {chunk.content}")
            elif chunk.chunk_type == "result":
                print(f"📊 获取到搜索结果")
            elif chunk.chunk_type == "summary":
                print(f"🤖 AI分析:")
                print(f"   {chunk.content[:300]}...")
            elif chunk.chunk_type == "complete":
                content = chunk.content
                if isinstance(content, dict) and 'suggestions' in content:
                    suggestions = content['suggestions']
                    print(f"💡 相关建议: {', '.join(suggestions[:3])}")
    
    finally:
        await system.stop()

async def example_workflow_comprehensive():
    """示例4: 综合搜索工作流"""
    print("=" * 50)
    print("示例4: 综合搜索工作流")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        params = {"query": "区块链技术发展现状"}
        print(f"🚀 执行综合搜索工作流")
        print(f"📋 参数: {params}")
        print("-" * 30)
        
        async for chunk in system.workflow_search("comprehensive_search", params):
            if chunk.chunk_type == "text":
                print(f"📝 {chunk.content}")
            elif chunk.chunk_type == "result":
                content = chunk.content
                if isinstance(content, dict):
                    step_name = content.get('step_name', '未知步骤')
                    if 'error' in content:
                        print(f"❌ {step_name}: {content['error']}")
                    else:
                        duration = content.get('duration', 0)
                        print(f"✅ {step_name}: 完成 ({duration:.2f}s)")
            elif chunk.chunk_type == "complete":
                content = chunk.content
                if isinstance(content, dict) and 'error' not in content:
                    print(f"\n🎉 工作流完成！")
                    print(f"⏱️ 总耗时: {content.get('duration', 0):.2f}秒")
                    print(f"✅ 完成步骤: {content.get('steps_completed', 0)}")
                else:
                    print(f"\n❌ 工作流失败: {content.get('error', '未知错误')}")
    
    finally:
        await system.stop()

async def example_workflow_research_report():
    """示例5: 研究报告工作流"""
    print("=" * 50)
    print("示例5: 研究报告生成工作流")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        params = {"topic": "量子计算技术"}
        print(f"📊 生成研究报告")
        print(f"📋 主题: {params['topic']}")
        print("-" * 30)
        
        workflow_results = []
        
        async for chunk in system.workflow_search("research_report", params):
            if chunk.chunk_type == "text":
                print(f"📝 {chunk.content}")
            elif chunk.chunk_type == "result":
                content = chunk.content
                if isinstance(content, dict):
                    workflow_results.append(content)
                    step_name = content.get('step_name', '未知步骤')
                    if 'error' not in content:
                        print(f"✅ {step_name}: 完成")
            elif chunk.chunk_type == "complete":
                content = chunk.content
                if isinstance(content, dict) and 'error' not in content:
                    print(f"\n📋 研究报告生成完成！")
                    print(f"📄 包含 {len(workflow_results)} 个部分")
                    
                    # 显示报告结构
                    for i, result in enumerate(workflow_results, 1):
                        step_name = result.get('step_name', f'部分{i}')
                        print(f"  {i}. {step_name}")
    
    finally:
        await system.stop()

async def example_competitive_analysis():
    """示例6: 竞争分析工作流"""
    print("=" * 50)
    print("示例6: 竞争分析工作流")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        params = {
            "company": "特斯拉",
            "industry": "电动汽车"
        }
        print(f"🏢 竞争分析")
        print(f"📋 公司: {params['company']}")
        print(f"🏭 行业: {params['industry']}")
        print("-" * 30)
        
        analysis_results = {}
        
        async for chunk in system.workflow_search("competitive_analysis", params):
            if chunk.chunk_type == "text":
                print(f"📝 {chunk.content}")
            elif chunk.chunk_type == "result":
                content = chunk.content
                if isinstance(content, dict):
                    step_name = content.get('step_name', '未知步骤')
                    step_result = content.get('result', {})
                    analysis_results[step_name] = step_result
                    
                    if 'error' not in content:
                        print(f"✅ {step_name}: 完成")
                        
                        # 显示关键信息
                        if step_name == "SWOT分析" and isinstance(step_result, dict):
                            strengths = step_result.get('strengths', [])
                            if strengths:
                                print(f"   💪 优势: {', '.join(strengths[:2])}")
            elif chunk.chunk_type == "complete":
                content = chunk.content
                if isinstance(content, dict) and 'error' not in content:
                    print(f"\n📊 竞争分析完成！")
                    print(f"📈 分析维度: {len(analysis_results)}")
    
    finally:
        await system.stop()

async def example_trend_analysis():
    """示例7: 趋势分析工作流"""
    print("=" * 50)
    print("示例7: 趋势分析工作流")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        params = {
            "domain": "人工智能",
            "timeframe": "2years"
        }
        print(f"📈 趋势分析")
        print(f"📋 领域: {params['domain']}")
        print(f"⏰ 时间范围: {params['timeframe']}")
        print("-" * 30)
        
        trend_data = {}
        
        async for chunk in system.workflow_search("trend_analysis", params):
            if chunk.chunk_type == "text":
                print(f"📝 {chunk.content}")
            elif chunk.chunk_type == "result":
                content = chunk.content
                if isinstance(content, dict):
                    step_name = content.get('step_name', '未知步骤')
                    step_result = content.get('result', {})
                    trend_data[step_name] = step_result
                    
                    if 'error' not in content:
                        print(f"✅ {step_name}: 完成")
                        
                        # 显示趋势信息
                        if step_name == "未来预测" and isinstance(step_result, dict):
                            projection = step_result.get('projection', '')
                            confidence = step_result.get('confidence', 0)
                            print(f"   🔮 预测: {projection} (置信度: {confidence:.1%})")
            elif chunk.chunk_type == "complete":
                content = chunk.content
                if isinstance(content, dict) and 'error' not in content:
                    print(f"\n📊 趋势分析完成！")
                    print(f"📈 分析步骤: {len(trend_data)}")
    
    finally:
        await system.stop()

async def example_custom_config():
    """示例8: 自定义配置"""
    print("=" * 50)
    print("示例8: 自定义搜索配置")
    print("=" * 50)
    
    system = AdvancedSearchSystem()
    await system.start()
    
    try:
        # 创建自定义配置
        config = SearchConfig(
            search_type=SearchType.ACADEMIC,
            max_results=3,
            include_summary=True,
            include_translation=False,
            enable_streaming=False,
            timeout=30
        )
        
        query = "深度学习在自然语言处理中的应用"
        print(f"🔍 自定义学术搜索: {query}")
        print(f"⚙️ 配置: 最大结果={config.max_results}, 类型={config.search_type.value}")
        print("-" * 30)
        
        # 使用自定义配置进行搜索
        result = await system.default_agent.search_tools.smart_search(query, config)
        
        print(f"📊 搜索类型: {result.search_type}")
        print(f"📈 结果数量: {result.total_results}")
        print(f"⏱️ 搜索耗时: {result.search_time:.2f}秒")
        print(f"📝 摘要: {result.summary[:200]}...")
        
        # 显示学术结果的特殊字段
        for i, item in enumerate(result.results[:2], 1):
            print(f"\n📄 结果{i}: {item.title}")
            if hasattr(item, 'authors') and item.authors:
                print(f"   👥 作者: {', '.join(item.authors)}")
            if hasattr(item, 'publication_year') and item.publication_year:
                print(f"   📅 年份: {item.publication_year}")
            if hasattr(item, 'journal') and item.journal:
                print(f"   📚 期刊: {item.journal}")
    
    finally:
        await system.stop()

async def run_all_examples():
    """运行所有示例"""
    examples = [
        ("简单搜索", example_simple_search),
        ("对话式搜索", example_conversational_search),
        ("流式搜索", example_streaming_search),
        ("综合搜索工作流", example_workflow_comprehensive),
        ("研究报告工作流", example_workflow_research_report),
        ("竞争分析工作流", example_competitive_analysis),
        ("趋势分析工作流", example_trend_analysis),
        ("自定义配置", example_custom_config),
    ]
    
    print("🚀 高级AI搜索代理 - 功能演示")
    print("=" * 60)
    
    for name, example_func in examples:
        try:
            print(f"\n🎯 开始演示: {name}")
            await example_func()
            print(f"✅ {name} 演示完成")
        except Exception as e:
            print(f"❌ {name} 演示失败: {e}")
        
        print("\n" + "=" * 60)
    
    print("🎉 所有演示完成！")

async def interactive_demo():
    """交互式演示"""
    print("🎮 交互式演示模式")
    print("=" * 30)
    
    examples = {
        "1": ("简单搜索", example_simple_search),
        "2": ("对话式搜索", example_conversational_search),
        "3": ("流式搜索", example_streaming_search),
        "4": ("综合搜索工作流", example_workflow_comprehensive),
        "5": ("研究报告工作流", example_workflow_research_report),
        "6": ("竞争分析工作流", example_competitive_analysis),
        "7": ("趋势分析工作流", example_trend_analysis),
        "8": ("自定义配置", example_custom_config),
        "9": ("运行所有示例", run_all_examples),
    }
    
    while True:
        print("\n📋 可用演示:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print("  0. 退出")
        
        choice = input("\n请选择演示 (0-9): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        
        if choice in examples:
            name, example_func = examples[choice]
            try:
                print(f"\n🎯 开始演示: {name}")
                await example_func()
                print(f"✅ {name} 演示完成")
            except Exception as e:
                print(f"❌ {name} 演示失败: {e}")
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(run_all_examples())