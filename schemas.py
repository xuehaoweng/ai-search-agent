from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from datetime import datetime
from enum import Enum

# 基础搜索结果
class BaseSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float] = Field(default=None, description="相关性评分 0-1")

# 新闻类型结果
class NewsResult(BaseSearchResult):
    publish_date: Optional[str] = Field(default=None, description="发布日期")
    source: Optional[str] = Field(default=None, description="新闻来源")
    category: Optional[str] = Field(default=None, description="新闻分类")
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = Field(default=None, description="情感倾向")

# 学术论文结果
class AcademicResult(BaseSearchResult):
    authors: Optional[List[str]] = Field(default=None, description="作者列表")
    publication_year: Optional[int] = Field(default=None, description="发表年份")
    journal: Optional[str] = Field(default=None, description="期刊名称")
    citation_count: Optional[int] = Field(default=None, description="引用次数")
    doi: Optional[str] = Field(default=None, description="DOI")
    abstract: Optional[str] = Field(default=None, description="摘要")

# 产品信息结果
class ProductResult(BaseSearchResult):
    price: Optional[str] = Field(default=None, description="价格")
    rating: Optional[float] = Field(default=None, description="评分")
    brand: Optional[str] = Field(default=None, description="品牌")
    category: Optional[str] = Field(default=None, description="产品类别")
    availability: Optional[str] = Field(default=None, description="库存状态")
    features: Optional[List[str]] = Field(default=None, description="主要特性")

# 技术文档结果
class TechDocResult(BaseSearchResult):
    doc_type: Optional[str] = Field(default=None, description="文档类型")
    version: Optional[str] = Field(default=None, description="版本")
    last_updated: Optional[str] = Field(default=None, description="最后更新时间")
    programming_language: Optional[str] = Field(default=None, description="编程语言")
    difficulty_level: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(default=None, description="难度级别")

# 问答类型结果
class QAResult(BaseModel):
    question: str = Field(description="问题")
    answer: str = Field(description="答案")
    confidence: Optional[float] = Field(default=None, description="置信度")
    sources: Optional[List[BaseSearchResult]] = Field(default=None, description="信息来源")

# 搜索结果类型枚举
class SearchType(str, Enum):
    GENERAL = "general"
    NEWS = "news"
    ACADEMIC = "academic"
    PRODUCT = "product"
    TECH_DOC = "tech_doc"
    QA = "qa"

# 统一的搜索响应
class SearchResponse(BaseModel):
    search_type: SearchType = Field(description="搜索类型")
    query: str = Field(description="搜索查询")
    results: List[Union[BaseSearchResult, NewsResult, AcademicResult, ProductResult, TechDocResult]] = Field(description="搜索结果列表")
    summary: str = Field(description="结果摘要")
    total_results: Optional[int] = Field(default=None, description="总结果数")
    search_time: Optional[float] = Field(default=None, description="搜索耗时（秒）")
    suggestions: Optional[List[str]] = Field(default=None, description="相关搜索建议")

# 多轮对话上下文
class ConversationContext(BaseModel):
    conversation_id: str = Field(description="对话ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    history: List[dict] = Field(default_factory=list, description="对话历史")
    current_topic: Optional[str] = Field(default=None, description="当前话题")
    preferences: Optional[dict] = Field(default_factory=dict, description="用户偏好")
    last_search_type: Optional[SearchType] = Field(default=None, description="上次搜索类型")

# 工具调用结果
class ToolResult(BaseModel):
    tool_name: str = Field(description="工具名称")
    input_data: dict = Field(description="输入数据")
    output_data: dict = Field(description="输出数据")
    execution_time: Optional[float] = Field(default=None, description="执行时间")
    success: bool = Field(description="是否成功")
    error_message: Optional[str] = Field(default=None, description="错误信息")

# 流式响应块
class StreamChunk(BaseModel):
    chunk_type: Literal["text", "result", "tool_call", "summary", "complete"] = Field(description="块类型")
    content: Union[str, dict] = Field(description="块内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    chunk_id: Optional[str] = Field(default=None, description="块ID")

# 高级搜索配置
class SearchConfig(BaseModel):
    search_type: SearchType = Field(default=SearchType.GENERAL, description="搜索类型")
    max_results: int = Field(default=5, description="最大结果数")
    include_summary: bool = Field(default=True, description="是否包含摘要")
    include_translation: bool = Field(default=False, description="是否包含翻译")
    target_language: Optional[str] = Field(default=None, description="目标语言")
    enable_streaming: bool = Field(default=False, description="是否启用流式响应")
    use_cache: bool = Field(default=True, description="是否使用缓存")
    timeout: int = Field(default=30, description="超时时间（秒）")