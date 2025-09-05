from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from models import SearchResults
from search import search_tool

model = OpenAIChatModel('deepseek-chat', provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))

web_agent = Agent(
    system_prompt="你是一个研究助手。用实时网络数据回答问题，并提供详细解释主题的主要内容",
    tools=[Tool(search_tool, takes_ctx=False)],
    output_type=SearchResults,
    model=model
)

async def main():
    query = "生成式AI的最新进展是什么？"
    response = await web_agent.run(query)
    for result in response.data.results:
        print(f"{result.title}\n{result.url}\n{result.snippet}\n---")
    print(response.data.main_content)

if __name__ == '__main__':
    asyncio.run(main())