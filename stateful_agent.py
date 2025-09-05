import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import time
from dataclasses import dataclass, field

from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI

from schemas import (
    SearchResponse, SearchType, ConversationContext, 
    StreamChunk, SearchConfig, ToolResult
)
from tools import AdvancedSearchTools, SummaryTool, TranslationTool, DataLookupTool

@dataclass
class ConversationState:
    """对话状态管理"""
    conversation_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    current_topic: Optional[str] = None
    search_history: List[Dict] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)
    context_summary: str = ""
    active_tools: List[str] = field(default_factory=list)

class StatefulSearchAgent:
    """有状态的搜索代理"""
    
    def __init__(self, model_config: Dict[str, Any]):
        # 初始化模型
        self.model = self._create_model(model_config)
        
        # 初始化工具
        self.search_tools = AdvancedSearchTools()
        self.summary_tool = SummaryTool()
        self.translation_tool = TranslationTool()
        self.data_lookup_tool = DataLookupTool()
        
        # 状态管理
        self.conversations: Dict[str, ConversationState] = {}
        self.session_timeout = timedelta(hours=2)  # 会话超时时间
        
        # 创建AI代理
        self.agent = Agent(
            system_prompt=self._get_system_prompt(),
            tools=[
                Tool(self._smart_search_wrapper, takes_ctx=True),
                Tool(self._summarize_wrapper, takes_ctx=True),
                Tool(self._translate_wrapper, takes_ctx=True),
                Tool(self._lookup_company_wrapper, takes_ctx=True),
                Tool(self._lookup_stock_wrapper, takes_ctx=True),
            ],
            model=self.model
        )
    
    def _create_model(self, config: Dict[str, Any]) -> OpenAIChatModel:
        """创建模型"""
        api_key = config.get('api_key')
        base_url = config.get('base_url')
        model_name = config.get('model_name', 'gpt-3.5-turbo')
        
        if base_url:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0,
                max_retries=3
            )
        else:
            client = AsyncOpenAI(
                api_key=api_key,
                timeout=60.0,
                max_retries=3
            )
        
        return OpenAIChatModel(model_name, provider=OpenAIProvider(openai_client=client))
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个高级的AI搜索助手，具有以下能力：

1. **智能搜索**: 根据用户查询自动选择最合适的搜索类型（新闻、学术、产品、技术文档等）
2. **多轮对话**: 记住对话历史，理解上下文和用户意图
3. **工具调用**: 可以调用搜索、摘要、翻译、数据查找等工具
4. **个性化**: 根据用户偏好和历史记录提供定制化服务

工作原则：
- 始终以用户需求为中心
- 提供准确、相关、及时的信息
- 主动询问不明确的需求
- 记住对话上下文，避免重复询问
- 根据查询类型选择最合适的搜索策略
- 提供结构化、易理解的回答

可用工具：
- smart_search: 智能搜索（自动选择搜索类型）
- summarize: 文本摘要
- translate: 文本翻译
- lookup_company: 查找公司信息
- lookup_stock: 查找股票信息

请用中文回答，保持专业和友好的语调。"""
    
    async def start_conversation(self, user_id: Optional[str] = None) -> str:
        """开始新对话"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id
        )
        return conversation_id
    
    async def end_conversation(self, conversation_id: str):
        """结束对话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    async def chat(self, 
                   conversation_id: str, 
                   message: str, 
                   config: Optional[SearchConfig] = None) -> Dict[str, Any]:
        """处理对话消息"""
        
        # 获取或创建对话状态
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id
            )
        
        state = self.conversations[conversation_id]
        state.last_activity = datetime.now()
        state.message_count += 1
        
        # 构建上下文
        context = self._build_context(state, message)
        
        try:
            # 调用AI代理
            response = await self.agent.run(
                message,
                context=context
            )
            
            # 更新对话状态
            await self._update_conversation_state(state, message, response)
            
            # 构建响应
            result = {
                "conversation_id": conversation_id,
                "response": response.output if hasattr(response, 'output') else str(response),
                "message_count": state.message_count,
                "current_topic": state.current_topic,
                "suggestions": await self._generate_followup_suggestions(state, message),
                "tools_used": state.active_tools[-3:] if state.active_tools else []
            }
            
            return result
            
        except Exception as e:
            return {
                "conversation_id": conversation_id,
                "error": f"处理消息时发生错误: {str(e)}",
                "message_count": state.message_count
            }
    
    async def chat_stream(self, 
                         conversation_id: str, 
                         message: str, 
                         config: Optional[SearchConfig] = None) -> AsyncGenerator[StreamChunk, None]:
        """流式对话"""
        
        # 获取对话状态
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id
            )
        
        state = self.conversations[conversation_id]
        state.last_activity = datetime.now()
        state.message_count += 1
        
        # 发送开始块
        yield StreamChunk(
            chunk_type="text",
            content="🤖 正在分析您的问题...",
            chunk_id=f"start_{int(time.time())}"
        )
        
        # 构建上下文
        context = self._build_context(state, message)
        
        try:
            # 模拟流式响应（实际应该使用真正的流式API）
            yield StreamChunk(
                chunk_type="text",
                content="🔍 正在搜索相关信息...",
                chunk_id=f"search_{int(time.time())}"
            )
            
            # 执行搜索
            if config is None:
                config = SearchConfig()
            
            search_result = await self.search_tools.smart_search(message, config)
            
            yield StreamChunk(
                chunk_type="result",
                content=search_result.dict(),
                chunk_id=f"result_{int(time.time())}"
            )
            
            # 生成AI回答
            yield StreamChunk(
                chunk_type="text",
                content="📝 正在生成回答...",
                chunk_id=f"generate_{int(time.time())}"
            )
            
            # 调用AI代理
            response = await self.agent.run(
                f"基于以下搜索结果回答用户问题：{message}\n\n搜索结果：{search_result.summary}",
                context=context
            )
            
            # 发送最终回答
            yield StreamChunk(
                chunk_type="summary",
                content=response.output if hasattr(response, 'output') else str(response),
                chunk_id=f"summary_{int(time.time())}"
            )
            
            # 更新状态
            await self._update_conversation_state(state, message, response)
            
            # 发送完成信号
            yield StreamChunk(
                chunk_type="complete",
                content={
                    "conversation_id": conversation_id,
                    "message_count": state.message_count,
                    "suggestions": await self._generate_followup_suggestions(state, message)
                },
                chunk_id=f"complete_{int(time.time())}"
            )
            
        except Exception as e:
            yield StreamChunk(
                chunk_type="complete",
                content={"error": f"处理消息时发生错误: {str(e)}"},
                chunk_id=f"error_{int(time.time())}"
            )
    
    def _build_context(self, state: ConversationState, current_message: str) -> Dict[str, Any]:
        """构建对话上下文"""
        return {
            "conversation_id": state.conversation_id,
            "user_id": state.user_id,
            "message_count": state.message_count,
            "current_topic": state.current_topic,
            "search_history": state.search_history[-5:],  # 最近5次搜索
            "user_preferences": state.user_preferences,
            "context_summary": state.context_summary,
            "current_message": current_message
        }
    
    async def _update_conversation_state(self, state: ConversationState, message: str, response: Any):
        """更新对话状态"""
        # 更新话题
        state.current_topic = await self._extract_topic(message)
        
        # 添加到搜索历史
        state.search_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": message,
            "response_type": type(response).__name__
        })
        
        # 更新上下文摘要
        state.context_summary = await self._update_context_summary(state, message)
        
        # 清理过期数据
        await self._cleanup_old_data(state)
    
    async def _extract_topic(self, message: str) -> str:
        """提取对话主题"""
        # 简单的主题提取逻辑
        keywords = message.lower().split()
        if any(word in keywords for word in ['ai', '人工智能', 'artificial intelligence']):
            return "人工智能"
        elif any(word in keywords for word in ['python', '编程', 'programming']):
            return "编程技术"
        elif any(word in keywords for word in ['新闻', 'news']):
            return "新闻资讯"
        elif any(word in keywords for word in ['产品', 'product', '购买']):
            return "产品信息"
        else:
            return "综合查询"
    
    async def _update_context_summary(self, state: ConversationState, message: str) -> str:
        """更新上下文摘要"""
        # 简化的上下文摘要更新
        if not state.context_summary:
            return f"用户询问关于{state.current_topic}的问题"
        else:
            return f"{state.context_summary}；继续讨论{state.current_topic}"
    
    async def _cleanup_old_data(self, state: ConversationState):
        """清理过期数据"""
        # 只保留最近的搜索历史
        if len(state.search_history) > 20:
            state.search_history = state.search_history[-20:]
    
    async def _generate_followup_suggestions(self, state: ConversationState, message: str) -> List[str]:
        """生成后续建议"""
        topic = state.current_topic or "相关主题"
        return [
            f"了解更多关于{topic}的信息",
            f"{topic}的最新发展",
            f"{topic}的应用案例",
            "切换到其他话题"
        ]
    
    # 工具包装器方法
    async def _smart_search_wrapper(self, query: str, search_type: str = "general", max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """智能搜索工具包装器"""
        config = SearchConfig(
            search_type=SearchType(search_type),
            max_results=max_results,
            include_summary=True
        )
        
        result = await self.search_tools.smart_search(query, config)
        
        # 记录工具使用
        context = kwargs.get('context', {})
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].active_tools.append("smart_search")
        
        return result.dict()
    
    async def _summarize_wrapper(self, text: str, max_length: int = 200, **kwargs) -> Dict[str, Any]:
        """摘要工具包装器"""
        result = await self.summary_tool.summarize_text(text, max_length)
        
        # 记录工具使用
        context = kwargs.get('context', {})
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].active_tools.append("summarize")
        
        return result.dict()
    
    async def _translate_wrapper(self, text: str, target_language: str, source_language: str = "auto", **kwargs) -> Dict[str, Any]:
        """翻译工具包装器"""
        result = await self.translation_tool.translate(text, target_language, source_language)
        
        # 记录工具使用
        context = kwargs.get('context', {})
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].active_tools.append("translate")
        
        return result.dict()
    
    async def _lookup_company_wrapper(self, company_name: str, **kwargs) -> Dict[str, Any]:
        """公司信息查找工具包装器"""
        result = await self.data_lookup_tool.lookup_company_info(company_name)
        
        # 记录工具使用
        context = kwargs.get('context', {})
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].active_tools.append("lookup_company")
        
        return result.dict()
    
    async def _lookup_stock_wrapper(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """股票信息查找工具包装器"""
        result = await self.data_lookup_tool.lookup_stock_price(symbol)
        
        # 记录工具使用
        context = kwargs.get('context', {})
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].active_tools.append("lookup_stock")
        
        return result.dict()
    
    async def get_conversation_stats(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话统计信息"""
        if conversation_id not in self.conversations:
            return None
        
        state = self.conversations[conversation_id]
        return {
            "conversation_id": conversation_id,
            "user_id": state.user_id,
            "created_at": state.created_at.isoformat(),
            "last_activity": state.last_activity.isoformat(),
            "message_count": state.message_count,
            "current_topic": state.current_topic,
            "search_count": len(state.search_history),
            "active_tools": list(set(state.active_tools)),
            "session_duration": str(state.last_activity - state.created_at)
        }
    
    async def cleanup_expired_conversations(self):
        """清理过期对话"""
        current_time = datetime.now()
        expired_conversations = []
        
        for conv_id, state in self.conversations.items():
            if current_time - state.last_activity > self.session_timeout:
                expired_conversations.append(conv_id)
        
        for conv_id in expired_conversations:
            del self.conversations[conv_id]
        
        return len(expired_conversations)

# 会话管理器
class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        self.agents: Dict[str, StatefulSearchAgent] = {}
    
    def create_agent(self, agent_id: str, model_config: Dict[str, Any]) -> StatefulSearchAgent:
        """创建新的代理实例"""
        agent = StatefulSearchAgent(model_config)
        self.agents[agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[StatefulSearchAgent]:
        """获取代理实例"""
        return self.agents.get(agent_id)
    
    async def cleanup_all_expired(self):
        """清理所有过期对话"""
        total_cleaned = 0
        for agent in self.agents.values():
            cleaned = await agent.cleanup_expired_conversations()
            total_cleaned += cleaned
        return total_cleaned