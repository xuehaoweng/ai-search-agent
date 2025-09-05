from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

async def tavily_search(query: str) -> dict:
    search_response = client.search(query=query, search_depth="advanced", max_results=5)
    return {
        "results": [
            {
                "title": res["title"],
                "url": res["url"],
                "snippet": res["content"][:150]
            }
            for res in search_response["results"]
        ]
    }

# 封装成函数以定义搜索工具
async def search_tool(query: str):
    return await tavily_search(query)