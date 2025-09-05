import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from tavily import TavilyClient
import os
from schemas import (
    SearchResponse, SearchType, BaseSearchResult, NewsResult, 
    AcademicResult, ProductResult, TechDocResult, QAResult,
    ToolResult, SearchConfig
)

class AdvancedSearchTools:
    """高级搜索工具集"""
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def smart_search(self, query: str, config: SearchConfig) -> SearchResponse:
        """智能搜索 - 根据查询内容自动选择搜索类型"""
        start_time = time.time()
        
        # 智能判断搜索类型
        if not config.search_type or config.search_type == SearchType.GENERAL:
            config.search_type = self._detect_search_type(query)
        
        # 执行搜索
        if config.search_type == SearchType.NEWS:
            results = await self._search_news(query, config.max_results)
        elif config.search_type == SearchType.ACADEMIC:
            results = await self._search_academic(query, config.max_results)
        elif config.search_type == SearchType.PRODUCT:
            results = await self._search_products(query, config.max_results)
        elif config.search_type == SearchType.TECH_DOC:
            results = await self._search_tech_docs(query, config.max_results)
        else:
            results = await self._search_general(query, config.max_results)
        
        # 生成摘要
        summary = await self._generate_summary(query, results) if config.include_summary else ""
        
        # 翻译（如果需要）
        if config.include_translation and config.target_language:
            summary = await self._translate_text(summary, config.target_language)
            results = await self._translate_results(results, config.target_language)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            search_type=config.search_type,
            query=query,
            results=results,
            summary=summary,
            total_results=len(results),
            search_time=search_time,
            suggestions=await self._generate_suggestions(query)
        )
    
    def _detect_search_type(self, query: str) -> SearchType:
        """智能检测搜索类型"""
        query_lower = query.lower()
        
        # 新闻关键词
        news_keywords = ['新闻', '最新', '今日', '昨日', '报道', '发布', '宣布', '事件', 'news', 'latest', 'breaking']
        if any(keyword in query_lower for keyword in news_keywords):
            return SearchType.NEWS
        
        # 学术关键词
        academic_keywords = ['论文', '研究', '学术', '期刊', '引用', '作者', 'paper', 'research', 'academic', 'journal', 'doi']
        if any(keyword in query_lower for keyword in academic_keywords):
            return SearchType.ACADEMIC
        
        # 产品关键词
        product_keywords = ['价格', '购买', '产品', '评价', '品牌', '型号', 'price', 'buy', 'product', 'review', 'brand']
        if any(keyword in query_lower for keyword in product_keywords):
            return SearchType.PRODUCT
        
        # 技术文档关键词
        tech_keywords = ['教程', '文档', '代码', '编程', 'api', 'sdk', 'tutorial', 'documentation', 'code', 'programming']
        if any(keyword in query_lower for keyword in tech_keywords):
            return SearchType.TECH_DOC
        
        return SearchType.GENERAL
    
    async def _search_general(self, query: str, max_results: int) -> List[BaseSearchResult]:
        """通用搜索"""
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            
            results = []
            for item in response.get("results", []):
                results.append(BaseSearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:300],
                    relevance_score=item.get("score", 0.0)
                ))
            return results
        except Exception as e:
            print(f"搜索错误: {e}")
            return []
    
    async def _search_news(self, query: str, max_results: int) -> List[NewsResult]:
        """新闻搜索"""
        try:
            # 使用Tavily的新闻搜索
            response = self.tavily_client.search(
                query=f"{query} 新闻",
                search_depth="advanced",
                max_results=max_results,
                include_domains=["news.sina.com.cn", "news.163.com", "news.qq.com", "xinhuanet.com"]
            )
            
            results = []
            for item in response.get("results", []):
                # 简单的情感分析
                sentiment = self._analyze_sentiment(item.get("content", ""))
                
                results.append(NewsResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:300],
                    relevance_score=item.get("score", 0.0),
                    publish_date=self._extract_date(item.get("content", "")),
                    source=self._extract_source(item.get("url", "")),
                    category="科技" if "科技" in query else "综合",
                    sentiment=sentiment
                ))
            return results
        except Exception as e:
            print(f"新闻搜索错误: {e}")
            return []
    
    async def _search_academic(self, query: str, max_results: int) -> List[AcademicResult]:
        """学术搜索"""
        try:
            # 针对学术内容的搜索
            academic_query = f"{query} 论文 研究 academic paper"
            response = self.tavily_client.search(
                query=academic_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["arxiv.org", "scholar.google.com", "ieee.org", "acm.org"]
            )
            
            results = []
            for item in response.get("results", []):
                results.append(AcademicResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:300],
                    relevance_score=item.get("score", 0.0),
                    authors=self._extract_authors(item.get("content", "")),
                    publication_year=self._extract_year(item.get("content", "")),
                    journal=self._extract_journal(item.get("content", "")),
                    abstract=item.get("content", "")[:500]
                ))
            return results
        except Exception as e:
            print(f"学术搜索错误: {e}")
            return []
    
    async def _search_products(self, query: str, max_results: int) -> List[ProductResult]:
        """产品搜索"""
        try:
            product_query = f"{query} 产品 价格 评价"
            response = self.tavily_client.search(
                query=product_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["taobao.com", "jd.com", "tmall.com", "amazon.cn"]
            )
            
            results = []
            for item in response.get("results", []):
                results.append(ProductResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:300],
                    relevance_score=item.get("score", 0.0),
                    price=self._extract_price(item.get("content", "")),
                    rating=self._extract_rating(item.get("content", "")),
                    brand=self._extract_brand(item.get("content", "")),
                    category="电子产品",
                    availability="有库存"
                ))
            return results
        except Exception as e:
            print(f"产品搜索错误: {e}")
            return []
    
    async def _search_tech_docs(self, query: str, max_results: int) -> List[TechDocResult]:
        """技术文档搜索"""
        try:
            tech_query = f"{query} 文档 教程 API documentation"
            response = self.tavily_client.search(
                query=tech_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["github.com", "stackoverflow.com", "docs.python.org", "developer.mozilla.org"]
            )
            
            results = []
            for item in response.get("results", []):
                results.append(TechDocResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:300],
                    relevance_score=item.get("score", 0.0),
                    doc_type="API文档" if "api" in item.get("url", "").lower() else "教程",
                    programming_language=self._detect_programming_language(item.get("content", "")),
                    difficulty_level="intermediate"
                ))
            return results
        except Exception as e:
            print(f"技术文档搜索错误: {e}")
            return []
    
    async def _generate_summary(self, query: str, results: List[Any]) -> str:
        """生成搜索结果摘要"""
        if not results:
            return "未找到相关结果。"
        
        # 简单的摘要生成逻辑
        total_results = len(results)
        first_result = results[0] if results else None
        
        summary = f"找到 {total_results} 个相关结果。"
        if first_result:
            summary += f" 最相关的结果是：{first_result.title}。"
            summary += f" {first_result.snippet[:100]}..."
        
        return summary
    
    async def _translate_text(self, text: str, target_language: str) -> str:
        """翻译文本（简化实现）"""
        # 这里可以集成真实的翻译API，如Google Translate、百度翻译等
        if target_language.lower() in ['en', 'english']:
            return f"[Translated to English] {text}"
        elif target_language.lower() in ['zh', 'chinese', '中文']:
            return f"[翻译为中文] {text}"
        return text
    
    async def _translate_results(self, results: List[Any], target_language: str) -> List[Any]:
        """翻译搜索结果"""
        # 简化实现，实际应该调用翻译API
        for result in results:
            if hasattr(result, 'title'):
                result.title = await self._translate_text(result.title, target_language)
            if hasattr(result, 'snippet'):
                result.snippet = await self._translate_text(result.snippet, target_language)
        return results
    
    async def _generate_suggestions(self, query: str) -> List[str]:
        """生成相关搜索建议"""
        # 简单的建议生成逻辑
        suggestions = [
            f"{query} 最新进展",
            f"{query} 详细介绍",
            f"{query} 应用案例",
            f"{query} 技术原理",
            f"{query} 发展趋势"
        ]
        return suggestions[:3]
    
    # 辅助方法
    def _analyze_sentiment(self, text: str) -> str:
        """简单情感分析"""
        positive_words = ['好', '优秀', '成功', '增长', '提升', '突破']
        negative_words = ['坏', '失败', '下降', '问题', '危机', '困难']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def _extract_date(self, text: str) -> Optional[str]:
        """提取日期"""
        import re
        date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'
        match = re.search(date_pattern, text)
        return match.group() if match else None
    
    def _extract_source(self, url: str) -> Optional[str]:
        """提取新闻源"""
        if 'sina.com' in url:
            return '新浪新闻'
        elif '163.com' in url:
            return '网易新闻'
        elif 'qq.com' in url:
            return '腾讯新闻'
        elif 'xinhua' in url:
            return '新华网'
        return None
    
    def _extract_authors(self, text: str) -> Optional[List[str]]:
        """提取作者信息"""
        # 简化实现
        if '作者' in text:
            return ['未知作者']
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """提取发表年份"""
        import re
        year_pattern = r'20\d{2}'
        match = re.search(year_pattern, text)
        return int(match.group()) if match else None
    
    def _extract_journal(self, text: str) -> Optional[str]:
        """提取期刊名称"""
        # 简化实现
        return "未知期刊"
    
    def _extract_price(self, text: str) -> Optional[str]:
        """提取价格信息"""
        import re
        price_pattern = r'[¥$]\d+\.?\d*'
        match = re.search(price_pattern, text)
        return match.group() if match else None
    
    def _extract_rating(self, text: str) -> Optional[float]:
        """提取评分"""
        import re
        rating_pattern = r'(\d+\.?\d*)\s*分'
        match = re.search(rating_pattern, text)
        return float(match.group(1)) if match else None
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """提取品牌信息"""
        brands = ['苹果', '华为', '小米', '三星', 'Apple', 'Huawei', 'Xiaomi', 'Samsung']
        for brand in brands:
            if brand in text:
                return brand
        return None
    
    def _detect_programming_language(self, text: str) -> Optional[str]:
        """检测编程语言"""
        languages = {
            'python': ['python', 'py', 'import', 'def'],
            'javascript': ['javascript', 'js', 'function', 'var', 'const'],
            'java': ['java', 'class', 'public', 'static'],
            'go': ['golang', 'go', 'func', 'package'],
            'rust': ['rust', 'fn', 'let', 'mut']
        }
        
        text_lower = text.lower()
        for lang, keywords in languages.items():
            if any(keyword in text_lower for keyword in keywords):
                return lang
        return None

# 摘要工具
class SummaryTool:
    """文本摘要工具"""
    
    async def summarize_text(self, text: str, max_length: int = 200) -> ToolResult:
        """生成文本摘要"""
        start_time = time.time()
        
        try:
            # 简单的摘要算法（实际应该使用更高级的NLP模型）
            sentences = text.split('。')
            if len(sentences) <= 3:
                summary = text
            else:
                # 取前两句和最后一句
                summary = '。'.join(sentences[:2] + sentences[-1:])
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name="summarize_text",
                input_data={"text": text[:100] + "...", "max_length": max_length},
                output_data={"summary": summary},
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            return ToolResult(
                tool_name="summarize_text",
                input_data={"text": text[:100] + "...", "max_length": max_length},
                output_data={},
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

# 翻译工具
class TranslationTool:
    """翻译工具"""
    
    async def translate(self, text: str, target_language: str, source_language: str = "auto") -> ToolResult:
        """翻译文本"""
        start_time = time.time()
        
        try:
            # 简化的翻译实现（实际应该调用真实的翻译API）
            if target_language.lower() in ['en', 'english']:
                translated = f"[EN] {text}"
            elif target_language.lower() in ['zh', 'chinese', '中文']:
                translated = f"[中文] {text}"
            else:
                translated = text
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name="translate",
                input_data={
                    "text": text,
                    "target_language": target_language,
                    "source_language": source_language
                },
                output_data={"translated_text": translated},
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            return ToolResult(
                tool_name="translate",
                input_data={
                    "text": text,
                    "target_language": target_language,
                    "source_language": source_language
                },
                output_data={},
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

# 数据查找工具
class DataLookupTool:
    """数据查找工具"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def lookup_company_info(self, company_name: str) -> ToolResult:
        """查找公司信息"""
        start_time = time.time()
        
        try:
            # 模拟公司信息查找
            company_data = {
                "name": company_name,
                "industry": "科技",
                "founded": "2000",
                "employees": "1000+",
                "revenue": "未知"
            }
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name="lookup_company_info",
                input_data={"company_name": company_name},
                output_data=company_data,
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            return ToolResult(
                tool_name="lookup_company_info",
                input_data={"company_name": company_name},
                output_data={},
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def lookup_stock_price(self, symbol: str) -> ToolResult:
        """查找股票价格"""
        start_time = time.time()
        
        try:
            # 模拟股票价格查找
            stock_data = {
                "symbol": symbol,
                "price": "100.00",
                "change": "+2.5%",
                "volume": "1,000,000",
                "market_cap": "10B"
            }
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name="lookup_stock_price",
                input_data={"symbol": symbol},
                output_data=stock_data,
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            return ToolResult(
                tool_name="lookup_stock_price",
                input_data={"symbol": symbol},
                output_data={},
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )