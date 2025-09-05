# 🚀 高级AI搜索代理 (Advanced AI Search Agent)

基于 PydanticAI 构建的下一代智能搜索助手，支持多种搜索类型、有状态对话、流式响应和复杂工作流自动化。

## ✨ 核心功能

### 🎯 **智能搜索系统**
- **多类型搜索**: 自动识别并执行新闻、学术、产品、技术文档等专业搜索
- **智能分类**: 根据查询内容自动选择最合适的搜索策略
- **结构化结果**: 提供标准化的搜索结果格式，便于后续处理

### 🧠 **有状态对话代理**
- **上下文记忆**: 记住完整对话历史，理解用户意图变化
- **个性化服务**: 根据用户偏好和历史记录提供定制化建议
- **多轮交互**: 支持复杂的多轮对话，无需重复背景信息

### 🌊 **流式响应系统**
- **实时反馈**: 搜索过程中提供实时状态更新
- **渐进式结果**: 边搜索边展示，提升用户体验
- **异步处理**: 高效的异步工作流，支持并发操作

### 🔧 **工具生态系统**
- **搜索工具**: 多源智能搜索引擎
- **摘要工具**: 自动文本摘要生成
- **翻译工具**: 多语言翻译支持
- **数据查找**: 公司信息、股票价格等结构化数据查询

### 📊 **复杂工作流**
- **综合搜索分析**: 多角度信息收集和分析
- **研究报告生成**: 自动化学术研究报告
- **竞争分析**: 企业竞争态势分析
- **趋势分析**: 行业发展趋势预测

## 🏗️ 系统架构

```
advanced-ai-search-agent/
├── 📄 核心文件
│   ├── advanced_main.py      # 增强版主程序
│   ├── main.py              # 基础版主程序
│   ├── stateful_agent.py    # 有状态代理系统
│   ├── streaming_workflow.py # 流式工作流引擎
│   ├── tools.py             # 工具集合
│   ├── schemas.py           # 数据模型定义
│   ├── search.py            # 基础搜索功能
│   └── schema.py            # 兼容性数据模型
├── 📋 配置文件
│   ├── requirements.txt     # 项目依赖
│   ├── .env                # 环境变量（需创建）
│   └── .gitignore          # Git忽略规则
└── 📚 文档
    ├── README.md           # 基础文档
    └── README_ADVANCED.md  # 高级功能文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd advanced-ai-search-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件并添加以下配置：

```env
# 推荐：国内API（网络稳定，响应快）
ZHIPU_API_KEY=your-zhipu-api-key          # 智谱AI GLM-4-Flash
DEEPSEEK_API_KEY=sk-your-deepseek-key     # DeepSeek Chat

# 可选：国外API
OPENAI_API_KEY=sk-your-openai-key         # OpenAI GPT

# 搜索API
TAVILY_API_KEY=tvly-your-tavily-key       # Tavily搜索引擎
```

### 3. 运行方式

#### 🎮 交互模式（推荐）
```bash
python advanced_main.py interactive
```

#### 🔍 命令行搜索
```bash
# 简单搜索
python advanced_main.py search "生成式AI最新进展"

# 工作流搜索
python advanced_main.py workflow comprehensive_search query="人工智能发展趋势"
```

#### 📝 基础版本
```bash
python main.py
```

## 💡 使用示例

### 基础搜索
```python
from advanced_main import AdvancedSearchSystem

system = AdvancedSearchSystem()
await system.start()

# 简单搜索
result = await system.simple_search("ChatGPT最新功能", "news")
print(result)
```

### 对话式搜索
```python
# 开始对话
conversation_id = await system.default_agent.start_conversation()

# 多轮对话
result1 = await system.conversational_search("什么是生成式AI？", conversation_id)
result2 = await system.conversational_search("它有哪些应用场景？", conversation_id)  # 理解上下文
result3 = await system.conversational_search("未来发展趋势如何？", conversation_id)   # 继续上下文
```

### 流式搜索
```python
async for chunk in system.streaming_search("人工智能发展历史"):
    if chunk.chunk_type == "text":
        print(f"状态: {chunk.content}")
    elif chunk.chunk_type == "result":
        print(f"结果: {chunk.content}")
    elif chunk.chunk_type == "summary":
        print(f"分析: {chunk.content}")
```

### 复杂工作流
```python
# 综合搜索分析
async for chunk in system.workflow_search("comprehensive_search", {
    "query": "量子计算发展现状"
}):
    print(chunk.content)

# 研究报告生成
async for chunk in system.workflow_search("research_report", {
    "topic": "区块链技术应用"
}):
    print(chunk.content)
```

## 🔧 高级配置

### 搜索类型配置
```python
from schemas import SearchConfig, SearchType

config = SearchConfig(
    search_type=SearchType.ACADEMIC,  # 学术搜索
    max_results=10,                   # 最大结果数
    include_summary=True,             # 包含摘要
    include_translation=True,         # 包含翻译
    target_language="en",             # 目标语言
    enable_streaming=True,            # 启用流式
    timeout=60                        # 超时时间
)
```

### 自定义工作流
```python
from streaming_workflow import StreamingWorkflowEngine, WorkflowStep

# 创建自定义工作流
def create_custom_workflow(workflow_id: str, params: Dict[str, Any]) -> Workflow:
    steps = [
        WorkflowStep(
            step_id="step1",
            name="数据收集",
            function=custom_data_collection,
            params={"source": params.get("source")}
        ),
        WorkflowStep(
            step_id="step2", 
            name="数据分析",
            function=custom_data_analysis,
            dependencies=["step1"]
        )
    ]
    return Workflow(workflow_id=workflow_id, name="自定义分析", steps=steps)
```

## 📊 可用工作流模板

### 1. 综合搜索分析 (`comprehensive_search`)
**用途**: 多角度全面搜索分析
**参数**: `query` - 搜索主题
**步骤**: 通用搜索 → 新闻搜索 → 学术搜索 → 结果综合 → 摘要生成

### 2. 多源信息分析 (`multi_source_analysis`)
**用途**: 多信息源交叉验证分析
**参数**: `topic` - 分析主题
**步骤**: 信息源收集 → 情感分析 → 关键点提取 → 交叉引用 → 报告生成

### 3. 研究报告生成 (`research_report`)
**用途**: 自动化学术研究报告
**参数**: `topic` - 研究主题
**步骤**: 文献综述 → 趋势分析 → 专家观点 → 市场分析 → 报告编译

### 4. 竞争分析报告 (`competitive_analysis`)
**用途**: 企业竞争态势分析
**参数**: `company`, `industry` - 公司名称和行业
**步骤**: 公司概况 → 竞争对手识别 → 市场定位 → SWOT分析 → 战略建议

### 5. 趋势分析报告 (`trend_analysis`)
**用途**: 行业发展趋势预测
**参数**: `domain`, `timeframe` - 领域和时间范围
**步骤**: 历史数据 → 模式识别 → 新兴趋势 → 趋势关联 → 未来预测

## 🛠️ 开发指南

### 添加新的搜索类型
```python
# 在 schemas.py 中添加新的结果类型
class CustomResult(BaseSearchResult):
    custom_field: Optional[str] = None

# 在 tools.py 中实现搜索逻辑
async def _search_custom(self, query: str, max_results: int) -> List[CustomResult]:
    # 实现自定义搜索逻辑
    pass
```

### 添加新的工具
```python
# 创建新工具类
class NewTool:
    async def process(self, data: str) -> ToolResult:
        # 实现工具逻辑
        return ToolResult(
            tool_name="new_tool",
            input_data={"data": data},
            output_data={"result": "processed"},
            success=True
        )
```

### 创建自定义工作流
```python
def _create_custom_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
    steps = [
        # 定义工作流步骤
    ]
    return Workflow(workflow_id=workflow_id, name="自定义工作流", steps=steps)
```

## 🔍 API参考

### 核心类

#### `AdvancedSearchSystem`
主系统类，提供所有高级功能的统一接口。

**方法**:
- `simple_search(query, search_type)` - 简单搜索
- `conversational_search(query, conversation_id)` - 对话搜索
- `streaming_search(query, conversation_id)` - 流式搜索
- `workflow_search(template, params)` - 工作流搜索

#### `StatefulSearchAgent`
有状态的搜索代理，支持多轮对话和上下文记忆。

**方法**:
- `start_conversation(user_id)` - 开始对话
- `chat(conversation_id, message)` - 发送消息
- `chat_stream(conversation_id, message)` - 流式对话
- `end_conversation(conversation_id)` - 结束对话

#### `StreamingWorkflowEngine`
流式工作流引擎，支持复杂的多步骤自动化任务。

**方法**:
- `execute_workflow_stream(template, params, agent_id)` - 执行工作流
- `list_workflow_templates()` - 列出可用模板
- `get_workflow_status(workflow_id)` - 获取工作流状态

## 🎯 性能优化

### 并发处理
- 支持多个搜索任务并行执行
- 异步工作流引擎，提高处理效率
- 智能任务队列管理

### 缓存机制
- 搜索结果缓存，避免重复查询
- 对话上下文缓存，提升响应速度
- 工作流结果缓存，支持断点续传

### 资源管理
- 自动清理过期对话
- 内存使用优化
- 连接池管理

## 🔒 安全考虑

- API密钥安全存储
- 输入验证和清理
- 错误信息脱敏
- 访问频率限制

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   - 检查网络连接
   - 验证API密钥
   - 尝试使用国内API

2. **搜索结果为空**
   - 检查Tavily API密钥
   - 尝试不同的搜索关键词
   - 检查搜索类型设置

3. **工作流执行失败**
   - 查看具体错误信息
   - 检查参数格式
   - 验证依赖关系

### 调试模式
```bash
# 启用详细日志
export DEBUG=1
python advanced_main.py interactive
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PydanticAI](https://github.com/pydantic/pydantic-ai) - 强大的AI代理框架
- [Tavily](https://tavily.com/) - 优秀的搜索API服务
- [OpenAI](https://openai.com/) - GPT模型支持
- [智谱AI](https://open.bigmodel.cn/) - GLM模型支持
- [DeepSeek](https://platform.deepseek.com/) - DeepSeek模型支持

---

🚀 **开始你的智能搜索之旅吧！** 如有问题，请提交Issue或联系维护者。