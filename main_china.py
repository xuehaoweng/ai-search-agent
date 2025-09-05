#!/usr/bin/env python3
"""
适用于中国大陆网络环境的版本
使用国内可访问的 API 服务
"""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from models import SearchResults
from search import search_tool
from openai import AsyncOpenAI

# 使用智谱AI（国内可访问）
custom_client = AsyncOpenAI(
    api_key=os.getenv('ZHIPU_API_KEY'),
    base_url='https://open.bigmodel.cn/api/paas/v4',
    timeout=60.0,
    max_retries=3
)

model = OpenAIChatModel('glm-4-flash', provider=OpenAIProvider(openai_client=custom_client))

web_agent = Agent(
    system_prompt="你是一个研究助手。用实时网络数据回答问题，并提供详细解释主题的主要内容",
    tools=[Tool(search_tool, takes_ctx=False)],
    output_type=SearchResults,
    model=model
)

async def main():
    query = "生成式AI的最新进展是什么？"
    
    try:
        print("🤖 正在使用智谱AI处理您的查询，请稍候...")
        response = await web_agent.run(query)
        
        print("📊 搜索结果:")
        for result in response.data.results:
            print(f"标题: {result.title}")
            print(f"链接: {result.url}")
            print(f"摘要: {result.snippet}")
            print("---")
        
        print("\n📝 AI 分析:")
        print(response.data.main_content)
        
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        
        print("\n🔧 解决建议:")
        print("1. 检查 ZHIPU_API_KEY 是否正确")
        print("2. 确认智谱AI账户余额")
        print("3. 检查网络连接")

if __name__ == '__main__':
    print("📝 使用说明:")
    print("1. 需要在 .env 文件中添加: ZHIPU_API_KEY=your-zhipu-api-key")
    print("2. 智谱AI注册地址: https://bigmodel.cn")
    print("3. glm-4-flash 是免费模型\n")
    
    asyncio.run(main())