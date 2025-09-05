#!/usr/bin/env python3
"""
SSL 证书问题诊断和修复脚本
"""

import os
import asyncio
import ssl
from dotenv import load_dotenv

load_dotenv()

async def test_ssl_solutions():
    """测试不同的 SSL 解决方案"""
    print("🔍 SSL 证书问题诊断...")
    
    try:
        import httpx
        
        # 方案1: 跳过 SSL 验证（仅用于测试）
        print("\n🔧 方案1: 跳过 SSL 验证测试...")
        try:
            async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                response = await client.get("https://httpbin.org/get")
                if response.status_code == 200:
                    print("✅ 跳过 SSL 验证后网络连接正常")
                    
                    # 测试 OpenAI API（跳过 SSL 验证）
                    openai_key = os.getenv('OPENAI_API_KEY')
                    if openai_key:
                        try:
                            response = await client.get(
                                "https://api.openai.com/v1/models",
                                headers={"Authorization": f"Bearer {openai_key}"}
                            )
                            print(f"✅ OpenAI API 连接成功 (跳过SSL验证): {response.status_code}")
                        except Exception as e:
                            print(f"❌ OpenAI API 仍然失败: {e}")
                else:
                    print(f"❌ 网络连接失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 跳过 SSL 验证测试失败: {e}")
        
        # 方案2: 使用自定义 SSL 上下文
        print("\n🔧 方案2: 自定义 SSL 上下文测试...")
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with httpx.AsyncClient(verify=ssl_context, timeout=15.0) as client:
                response = await client.get("https://httpbin.org/get")
                if response.status_code == 200:
                    print("✅ 自定义 SSL 上下文连接正常")
        except Exception as e:
            print(f"❌ 自定义 SSL 上下文测试失败: {e}")
        
        # 方案3: 检查系统时间
        print("\n🔧 方案3: 系统时间检查...")
        import datetime
        current_time = datetime.datetime.now()
        print(f"当前系统时间: {current_time}")
        if current_time.year < 2024:
            print("⚠️ 系统时间可能不正确，这可能导致 SSL 证书验证失败")
        else:
            print("✅ 系统时间正常")
            
    except ImportError:
        print("❌ httpx 库未安装")

async def test_domestic_apis():
    """测试国内 API 连接"""
    print("\n🌐 测试国内 API 连接...")
    
    try:
        import httpx
        
        # 测试智谱AI
        zhipu_key = os.getenv('ZHIPU_API_KEY')
        if zhipu_key:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                        headers={
                            "Authorization": f"Bearer {zhipu_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "glm-4-flash",
                            "messages": [{"role": "user", "content": "你好"}],
                            "max_tokens": 10
                        }
                    )
                    if response.status_code in [200, 400, 401]:
                        print("✅ 智谱AI API 连接正常")
                    else:
                        print(f"⚠️ 智谱AI API 响应: {response.status_code}")
            except Exception as e:
                print(f"❌ 智谱AI API 连接失败: {e}")
        
        # 测试 DeepSeek
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {deepseek_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [{"role": "user", "content": "你好"}],
                            "max_tokens": 10
                        }
                    )
                    if response.status_code in [200, 400, 401]:
                        print("✅ DeepSeek API 连接正常")
                    else:
                        print(f"⚠️ DeepSeek API 响应: {response.status_code}")
            except Exception as e:
                print(f"❌ DeepSeek API 连接失败: {e}")
                
    except ImportError:
        print("❌ httpx 库未安装")

if __name__ == "__main__":
    asyncio.run(test_ssl_solutions())
    asyncio.run(test_domestic_apis())