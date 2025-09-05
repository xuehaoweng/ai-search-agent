#!/usr/bin/env python3
"""
使用国内 API 的版本 - 解决网络连接问题
支持：智谱AI、DeepSeek、硅基流动等
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

def create_model_config():
    """根据可用的 API 密钥创建模型配置"""
    
    # 选项1: 智谱AI (推荐，免费额度大)
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    if zhipu_key:
        print("🤖 使用智谱AI GLM-4-Flash 模型")
        client = AsyncOpenAI(
            api_key=zhipu_key,
            base_url='https://open.bigmodel.cn/api/paas/v4',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('glm-4-flash', provider=OpenAIProvider(openai_client=client))
    
    # 选项2: DeepSeek (便宜，性能好)
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print("🤖 使用 DeepSeek Chat 模型")
        client = AsyncOpenAI(
            api_key=deepseek_key,
            base_url='https://api.deepseek.com',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('deepseek-chat', provider=OpenAIProvider(openai_client=client))
    
    # 选项3: 硅基流动 (免费)
    siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
    if siliconflow_key:
        print("🤖 使用硅基流动 Qwen2.5 模型")
        client = AsyncOpenAI(
            api_key=siliconflow_key,
            base_url='https://api.siliconflow.cn/v1',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('Qwen/Qwen2.5-7B-Instruct', provider=OpenAIProvider(openai_client=client))
    
    # 选项4: 月之暗面 (Kimi)
    moonshot_key = os.getenv('MOONSHOT_API_KEY')
    if moonshot_key:
        print("🤖 使用月之暗面 Moonshot 模型")
        client = AsyncOpenAI(
            api_key=moonshot_key,
            base_url='https://api.moonshot.cn/v1',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('moonshot-v1-8k', provider=OpenAIProvider(openai_client=client))
    
    # 如果都没有，提示用户
    print("❌ 未找到任何可用的 API 密钥")
    print("请在 .env 文件中添加以下任一密钥:")
    print("  ZHIPU_API_KEY=your-zhipu-key      # 智谱AI (推荐)")
    print("  DEEPSEEK_API_KEY=your-deepseek-key  # DeepSeek")
    print("  SILICONFLOW_API_KEY=your-sf-key     # 硅基流动 (免费)")
    print("  MOONSHOT_API_KEY=your-moonshot-key  # 月之暗面")
    return None

# 创建模型
model = create_model_config()
if not model:
    exit(1)

# 创建代理
web_agent = Agent(
    system_prompt="你是一个研究助手。用实时网络数据回答问题，并提供详细解释主题的主要内容",
    tools=[Tool(search_tool, takes_ctx=False)],
    output_type=SearchResults,
    model=model
)

async def main():
    query = "生成式AI的最新进展是什么？"
    
    try:
        print("🤖 正在处理您的查询，请稍候...")
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
        
        # 提供解决建议
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            print("\n💡 网络连接问题解决建议:")
            print("1. 检查网络连接是否正常")
            print("2. 尝试使用 VPN 或代理")
            print("3. 检查防火墙设置")
            print("4. 稍后重试")
        elif "api" in str(e).lower() or "key" in str(e).lower():
            print("\n💡 API 密钥问题解决建议:")
            print("1. 检查 .env 文件中的 API 密钥是否正确")
            print("2. 确认 API 密钥有足够的余额")
            print("3. 检查 API 密钥的权限设置")

if __name__ == '__main__':
    asyncio.run(main())