# AI 搜索代理 (AI Search Agent)

基于 PydanticAI 和 Tavily 构建的智能搜索助手，能够实时搜索网络信息并提供结构化的回答。

## ✨ 功能特点

- 🤖 **智能对话**：基于 DeepSeek 大语言模型的智能对话能力
- 🔍 **实时搜索**：集成 Tavily 搜索引擎，获取最新网络信息
- 📊 **结构化输出**：使用 Pydantic 模型确保输出格式一致性
- 🛠️ **工具调用**：支持 AI 代理自主调用搜索工具
- 🎯 **类型安全**：基于 PydanticAI 框架，提供完整的类型检查

## 🏗️ 项目结构

```
ai-search-agent/
├── main.py          # 主程序入口
├── schema.py        # Pydantic 数据模型定义
├── search.py        # 搜索功能实现
├── requirements.txt # 项目依赖
├── .env            # 环境变量配置（需要创建）
├── .gitignore      # Git 忽略文件
└── README.md       # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

确保你的系统已安装 Python 3.9+

```bash
# 克隆项目
git clone <your-repo-url>
cd ai-search-agent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并添加以下配置：

```env
# OpenAI API 密钥（用于 DeepSeek 模型）
OPENAI_API_KEY=your-openai-api-key

# Tavily 搜索 API 密钥
TAVILY_API_KEY=your-tavily-api-key
```

### 4. 运行程序

```bash
python main.py
```

## 🔧 配置说明

### API 密钥获取

1. **OpenAI API Key**：
   - 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 创建新的 API 密钥

2. **Tavily API Key**：
   - 访问 [Tavily](https://tavily.com/)
   - 注册账户并获取 API 密钥

### 模型配置

项目默认使用 DeepSeek Chat 模型，你也可以切换到其他兼容 OpenAI API 的模型：

```python
# 使用 OpenAI GPT-4
model = OpenAIChatModel('gpt-4', provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))

# 使用其他兼容模型
model = OpenAIChatModel('your-model-name', provider=OpenAIProvider(
    base_url='https://your-api-endpoint.com/v1',
    api_key=os.getenv('YOUR_API_KEY')
))
```

## 📋 核心组件

### 1. 数据模型 (schema.py)

定义了搜索结果的数据结构：

```python
class SearchResult(BaseModel):
    title: str      # 搜索结果标题
    url: str        # 搜索结果链接
    snippet: str    # 搜索结果摘要

class SearchResults(BaseModel):
    results: List[SearchResult]           # 搜索结果列表
    main_content: str                     # AI 生成的主要内容
```

### 2. 搜索功能 (search.py)

实现了与 Tavily API 的集成：

```python
async def tavily_search(query: str) -> dict:
    # 调用 Tavily API 进行高级搜索
    # 返回最多 5 个相关结果
```

### 3. 主程序 (main.py)

创建 AI 代理并处理用户查询：

```python
web_agent = Agent(
    system_prompt="你是一个研究助手...",
    tools=[Tool(search_tool, takes_ctx=False)],
    output_type=SearchResults,
    model=model
)
```

## 🛠️ 自定义开发

### 添加新的工具

```python
@web_agent.tool
async def your_custom_tool(query: str) -> str:
    """你的自定义工具描述"""
    # 实现你的工具逻辑
    return "工具执行结果"
```

### 修改输出格式

在 `models.py` 中定义新的 Pydantic 模型：

```python
class CustomOutput(BaseModel):
    field1: str
    field2: List[str]
    field3: Optional[int] = None
```

### 更换搜索引擎

在 `search.py` 中实现新的搜索函数：

```python
async def your_search_engine(query: str) -> dict:
    # 实现你的搜索逻辑
    pass
```

## 📝 使用示例

运行程序后，AI 代理会自动：

1. 接收用户查询："生成式AI的最新进展是什么？"
2. 调用搜索工具获取相关信息
3. 分析搜索结果
4. 生成结构化的回答

输出示例：
```
标题: 生成式AI的最新突破
链接: https://example.com/ai-news
摘要: 最新的生成式AI技术在多个领域取得重大进展...
---
主要内容: 根据最新的搜索结果，生成式AI在2024年取得了显著进展...
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [PydanticAI](https://github.com/pydantic/pydantic-ai) - 强大的 AI 代理框架
- [Tavily](https://tavily.com/) - 优秀的搜索 API 服务
- [DeepSeek](https://www.deepseek.com/) - 高质量的大语言模型

## 📞 支持

如果你在使用过程中遇到问题，请：

1. 查看 [常见问题](#)
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 描述你的问题

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！