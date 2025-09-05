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

# 创建自定义客户端，增加超时时间
custom_client = AsyncOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=60.0,  # 增加超时时间到60秒
    max_retries=3   # 设置重试次数
)

model = OpenAIChatModel('deepseek-chat', provider=OpenAIProvider(openai_client=custom_client))

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
        if "timeout" in str(e).lower() or "ConnectTimeout" in str(e):
            print("\n🔧 解决建议:")
            print("1. 检查网络连接是否正常")
            print("2. 确认 API 密钥是否正确")
            print("3. 尝试使用代理或 VPN")
            print("4. 稍后重试")
        elif "api" in str(e).lower():
            print("\n🔧 解决建议:")
            print("1. 检查 API 密钥是否有效")
            print("2. 确认账户是否有足够余额")
            print("3. 检查 API 配额限制")

if __name__ == '__main__':
    asyncio.run(main())