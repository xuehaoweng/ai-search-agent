from pydantic import BaseModel, Field
from typing import List

# 每个单独的搜索结果
class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

# 最终代理输出
class SearchResults(BaseModel):
    results: List[SearchResult]
    main_content: str = Field(description="博客的主要内容")