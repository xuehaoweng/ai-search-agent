#!/usr/bin/env python3
"""
网络连接测试脚本
用于检查 API 连接是否正常
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_openai_connection():
    """测试 OpenAI API 连接"""
    print("🔍 测试 OpenAI API 连接...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY 环境变量")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                print("✅ OpenAI API 连接正常")
                return True
            else:
                print(f"❌ OpenAI API 连接失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
    except httpx.ConnectTimeout:
        print("❌ OpenAI API 连接超时")
        return False
    except Exception as e:
        print(f"❌ OpenAI API 连接错误: {e}")
        return False

async def test_tavily_connection():
    """测试 Tavily API 连接"""
    print("🔍 测试 Tavily API 连接...")
    
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("❌ 未找到 TAVILY_API_KEY 环境变量")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": "test",
                    "max_results": 1
                }
            )
            
            if response.status_code == 200:
                print("✅ Tavily API 连接正常")
                return True
            else:
                print(f"❌ Tavily API 连接失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
    except httpx.ConnectTimeout:
        print("❌ Tavily API 连接超时")
        return False
    except Exception as e:
        print(f"❌ Tavily API 连接错误: {e}")
        return False

async def test_basic_connectivity():
    """测试基本网络连接"""
    print("🔍 测试基本网络连接...")
    
    test_urls = [
        "https://www.google.com",
        "https://api.openai.com",
        "https://api.tavily.com"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in test_urls:
            try:
                response = await client.get(url)
                print(f"✅ {url} - 连接正常 ({response.status_code})")
            except httpx.ConnectTimeout:
                print(f"❌ {url} - 连接超时")
            except Exception as e:
                print(f"❌ {url} - 连接错误: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始网络连接测试...\n")
    
    # 测试基本网络连接
    await test_basic_connectivity()
    print()
    
    # 测试 API 连接
    openai_ok = await test_openai_connection()
    tavily_ok = await test_tavily_connection()
    
    print("\n📊 测试结果总结:")
    print(f"OpenAI API: {'✅ 正常' if openai_ok else '❌ 异常'}")
    print(f"Tavily API: {'✅ 正常' if tavily_ok else '❌ 异常'}")
    
    if openai_ok and tavily_ok:
        print("\n🎉 所有连接测试通过！可以运行主程序。")
    else:
        print("\n⚠️  存在连接问题，请检查:")
        print("1. 网络连接是否正常")
        print("2. API 密钥是否正确")
        print("3. 是否需要使用代理")
        print("4. 防火墙设置")

if __name__ == "__main__":
    asyncio.run(main())