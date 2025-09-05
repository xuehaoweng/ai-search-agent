#!/usr/bin/env python3
"""
SSL 证书问题修复版本
适用于企业网络环境或有 SSL 证书验证问题的情况
"""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import ssl
import httpx
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from models import SearchResults
from search import search_tool
from openai import AsyncOpenAI

def create_ssl_fixed_client():
    """创建跳过 SSL 验证的客户端"""
    
    # 检查是否有国内 API 密钥
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    if zhipu_key:
        print("🤖 使用智谱AI (无SSL问题)")
        # 智谱AI 通常没有 SSL 问题
        client = AsyncOpenAI(
            api_key=zhipu_key,
            base_url='https://open.bigmodel.cn/api/paas/v4',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('glm-4-flash', provider=OpenAIProvider(openai_client=client))
    
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print("🤖 使用 DeepSeek (无SSL问题)")
        client = AsyncOpenAI(
            api_key=deepseek_key,
            base_url='https://api.deepseek.com',
            timeout=60.0,
            max_retries=3
        )
        return OpenAIChatModel('deepseek-chat', provider=OpenAIProvider(openai_client=client))
    
    # 如果只有 OpenAI 密钥，尝试跳过 SSL 验证
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("🤖 使用 OpenAI (跳过SSL验证)")
        
        # 创建跳过 SSL 验证的 HTTP 客户端
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        http_client = httpx.AsyncClient(
            verify=False,  # 跳过 SSL 验证
            timeout=60.0
        )
        
        client = AsyncOpenAI(
            api_key=openai_key,
            timeout=60.0,
            max_retries=3,
            http_client=http_client
        )
        return OpenAIChatModel('gpt-3.5-turbo', provider=OpenAIProvider(openai_client=client))
    
    print("❌ 未找到任何可用的 API 密钥")
    return None

# 创建模型
model = create_ssl_fixed_client()
if not model:
    print("请在 .env 文件中添加以下任一密钥:")
    print("  ZHIPU_API_KEY=your-zhipu-key      # 智谱AI (推荐，无SSL问题)")
    print("  DEEPSEEK_API_KEY=your-deepseek-key  # DeepSeek (无SSL问题)")
    print("  OPENAI_API_KEY=your-openai-key      # OpenAI (将跳过SSL验证)")
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
        
        # SSL 相关错误的特殊处理
        if "ssl" in str(e).lower() or "certificate" in str(e).lower():
            print("\n💡 SSL 证书问题解决建议:")
            print("1. 使用国内 API (智谱AI/DeepSeek) 避免 SSL 问题")
            print("2. 检查系统时间是否正确")
            print("3. 更新系统的 CA 证书")
            print("4. 联系网络管理员检查防火墙/代理设置")
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            print("\n💡 网络连接问题解决建议:")
            print("1. 检查网络连接是否正常")
            print("2. 尝试使用 VPN 或代理")
            print("3. 稍后重试")

if __name__ == '__main__':
    asyncio.run(main())