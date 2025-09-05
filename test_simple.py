#!/usr/bin/env python3
"""
简化的连接测试脚本
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_basic_connection():
    """测试基本的网络连接"""
    print("🔍 开始网络连接诊断...")
    
    # 检查环境变量
    openai_key = os.getenv('OPENAI_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')
    
    print(f"📋 环境变量检查:")
    print(f"   OPENAI_API_KEY: {'✅ 已设置' if openai_key else '❌ 未设置'}")
    print(f"   TAVILY_API_KEY: {'✅ 已设置' if tavily_key else '❌ 未设置'}")
    
    # 测试基本的 HTTP 连接
    try:
        import httpx
        print("\n🌐 测试网络连接...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试基本网络连接
            try:
                response = await client.get("https://httpbin.org/get")
                print("✅ 基本网络连接正常")
            except Exception as e:
                print(f"❌ 基本网络连接失败: {e}")
                return
            
            # 测试 OpenAI API 连接
            if openai_key:
                try:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {openai_key}"},
                        timeout=15.0
                    )
                    if response.status_code == 200:
                        print("✅ OpenAI API 连接正常")
                    else:
                        print(f"⚠️ OpenAI API 响应异常: {response.status_code}")
                except Exception as e:
                    print(f"❌ OpenAI API 连接失败: {e}")
            
            # 测试 Tavily API 连接
            if tavily_key:
                try:
                    response = await client.post(
                        "https://api.tavily.com/search",
                        json={"api_key": tavily_key, "query": "test", "max_results": 1},
                        timeout=15.0
                    )
                    if response.status_code in [200, 400]:  # 400 可能是参数问题，但连接正常
                        print("✅ Tavily API 连接正常")
                    else:
                        print(f"⚠️ Tavily API 响应异常: {response.status_code}")
                except Exception as e:
                    print(f"❌ Tavily API 连接失败: {e}")
    
    except ImportError:
        print("❌ httpx 库未安装，请运行: pip install httpx")
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")

async def test_simple_ai():
    """测试简单的 AI 对话（不使用工具）"""
    print("\n🤖 测试简单 AI 对话...")
    
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from openai import AsyncOpenAI
        
        # 创建简单的客户端
        custom_client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            timeout=30.0,
            max_retries=2
        )
        
        model = OpenAIChatModel('gpt-3.5-turbo', provider=OpenAIProvider(openai_client=custom_client))
        
        # 创建简单的代理（不使用工具）
        simple_agent = Agent(
            system_prompt="你是一个友好的助手，用中文回答问题。",
            model=model
        )
        
        print("正在测试简单对话...")
        response = await simple_agent.run("你好，请简单介绍一下自己")
        print(f"✅ AI 回答: {response.data}")
        
    except Exception as e:
        print(f"❌ AI 对话测试失败: {e}")
        print("建议:")
        print("1. 检查 API 密钥是否正确")
        print("2. 检查网络连接")
        print("3. 尝试使用代理或 VPN")

if __name__ == "__main__":
    asyncio.run(test_basic_connection())
    asyncio.run(test_simple_ai())