import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from schemas import StreamChunk, SearchConfig, SearchType
from stateful_agent import StatefulSearchAgent, ConversationManager

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    function: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

@dataclass
class Workflow:
    """工作流定义"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def total_duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class StreamingWorkflowEngine:
    """流式工作流引擎"""
    
    def __init__(self, conversation_manager: ConversationManager):
        self.conversation_manager = conversation_manager
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, Callable] = {}
        
        # 注册默认工作流模板
        self._register_default_templates()
    
    def _register_default_templates(self):
        """注册默认工作流模板"""
        self.workflow_templates.update({
            "comprehensive_search": self._create_comprehensive_search_workflow,
            "multi_source_analysis": self._create_multi_source_analysis_workflow,
            "research_report": self._create_research_report_workflow,
            "competitive_analysis": self._create_competitive_analysis_workflow,
            "trend_analysis": self._create_trend_analysis_workflow
        })
    
    async def execute_workflow_stream(self, 
                                    workflow_template: str,
                                    params: Dict[str, Any],
                                    agent_id: str,
                                    conversation_id: Optional[str] = None) -> AsyncGenerator[StreamChunk, None]:
        """执行工作流并返回流式结果"""
        
        # 创建工作流
        workflow = await self._create_workflow(workflow_template, params)
        self.active_workflows[workflow.workflow_id] = workflow
        
        # 获取代理
        agent = self.conversation_manager.get_agent(agent_id)
        if not agent:
            yield StreamChunk(
                chunk_type="complete",
                content={"error": f"Agent {agent_id} not found"},
                chunk_id=f"error_{int(time.time())}"
            )
            return
        
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            
            # 发送开始信号
            yield StreamChunk(
                chunk_type="text",
                content=f"🚀 开始执行工作流: {workflow.name}",
                chunk_id=f"start_{workflow.workflow_id}"
            )
            
            # 执行工作流步骤
            async for chunk in self._execute_workflow_steps(workflow, agent, conversation_id):
                yield chunk
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # 发送完成信号
            yield StreamChunk(
                chunk_type="complete",
                content={
                    "workflow_id": workflow.workflow_id,
                    "status": workflow.status.value,
                    "duration": workflow.total_duration,
                    "steps_completed": len([s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED])
                },
                chunk_id=f"complete_{workflow.workflow_id}"
            )
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            yield StreamChunk(
                chunk_type="complete",
                content={"error": f"工作流执行失败: {str(e)}"},
                chunk_id=f"error_{workflow.workflow_id}"
            )
        finally:
            # 清理完成的工作流
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
    
    async def _create_workflow(self, template_name: str, params: Dict[str, Any]) -> Workflow:
        """创建工作流实例"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        workflow_id = str(uuid.uuid4())
        creator = self.workflow_templates[template_name]
        return creator(workflow_id, params)
    
    async def _execute_workflow_steps(self, 
                                    workflow: Workflow, 
                                    agent: StatefulSearchAgent,
                                    conversation_id: Optional[str]) -> AsyncGenerator[StreamChunk, None]:
        """执行工作流步骤"""
        
        # 构建依赖图
        dependency_graph = self._build_dependency_graph(workflow.steps)
        
        # 执行步骤
        completed_steps = set()
        step_results = {}
        
        while len(completed_steps) < len(workflow.steps):
            # 找到可以执行的步骤
            ready_steps = []
            for step in workflow.steps:
                if (step.step_id not in completed_steps and 
                    step.status == WorkflowStatus.PENDING and
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            if not ready_steps:
                # 检查是否有循环依赖或其他问题
                pending_steps = [s for s in workflow.steps if s.status == WorkflowStatus.PENDING]
                if pending_steps:
                    raise RuntimeError("Workflow deadlock detected - circular dependencies or missing steps")
                break
            
            # 并行执行准备好的步骤
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(
                    self._execute_step(step, agent, conversation_id, step_results)
                )
                tasks.append((step, task))
            
            # 等待步骤完成并发送流式更新
            for step, task in tasks:
                try:
                    yield StreamChunk(
                        chunk_type="text",
                        content=f"⚙️ 执行步骤: {step.name}",
                        chunk_id=f"step_{step.step_id}"
                    )
                    
                    result = await task
                    step.result = result
                    step.status = WorkflowStatus.COMPLETED
                    step_results[step.step_id] = result
                    completed_steps.add(step.step_id)
                    
                    yield StreamChunk(
                        chunk_type="result",
                        content={
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "result": result,
                            "duration": step.duration
                        },
                        chunk_id=f"result_{step.step_id}"
                    )
                    
                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    
                    yield StreamChunk(
                        chunk_type="result",
                        content={
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "error": str(e)
                        },
                        chunk_id=f"error_{step.step_id}"
                    )
    
    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies
        return graph
    
    async def _execute_step(self, 
                          step: WorkflowStep, 
                          agent: StatefulSearchAgent,
                          conversation_id: Optional[str],
                          previous_results: Dict[str, Any]) -> Any:
        """执行单个步骤"""
        step.status = WorkflowStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # 准备参数
            params = step.params.copy()
            params['agent'] = agent
            params['conversation_id'] = conversation_id
            params['previous_results'] = previous_results
            
            # 执行步骤函数
            result = await step.function(**params)
            
            step.end_time = datetime.now()
            return result
            
        except Exception as e:
            step.end_time = datetime.now()
            step.error = str(e)
            raise
    
    # 工作流模板创建方法
    def _create_comprehensive_search_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
        """创建综合搜索工作流"""
        query = params.get('query', '')
        
        steps = [
            WorkflowStep(
                step_id="search_general",
                name="通用搜索",
                function=self._search_step,
                params={"query": query, "search_type": "general"}
            ),
            WorkflowStep(
                step_id="search_news",
                name="新闻搜索",
                function=self._search_step,
                params={"query": query, "search_type": "news"}
            ),
            WorkflowStep(
                step_id="search_academic",
                name="学术搜索",
                function=self._search_step,
                params={"query": query, "search_type": "academic"}
            ),
            WorkflowStep(
                step_id="synthesize_results",
                name="结果综合",
                function=self._synthesize_step,
                params={"query": query},
                dependencies=["search_general", "search_news", "search_academic"]
            ),
            WorkflowStep(
                step_id="generate_summary",
                name="生成摘要",
                function=self._summary_step,
                params={},
                dependencies=["synthesize_results"]
            )
        ]
        
        return Workflow(
            workflow_id=workflow_id,
            name="综合搜索分析",
            steps=steps
        )
    
    def _create_multi_source_analysis_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
        """创建多源分析工作流"""
        topic = params.get('topic', '')
        
        steps = [
            WorkflowStep(
                step_id="collect_sources",
                name="收集信息源",
                function=self._collect_sources_step,
                params={"topic": topic}
            ),
            WorkflowStep(
                step_id="analyze_sentiment",
                name="情感分析",
                function=self._sentiment_analysis_step,
                params={},
                dependencies=["collect_sources"]
            ),
            WorkflowStep(
                step_id="extract_key_points",
                name="提取关键点",
                function=self._extract_key_points_step,
                params={},
                dependencies=["collect_sources"]
            ),
            WorkflowStep(
                step_id="cross_reference",
                name="交叉引用",
                function=self._cross_reference_step,
                params={},
                dependencies=["analyze_sentiment", "extract_key_points"]
            ),
            WorkflowStep(
                step_id="generate_report",
                name="生成报告",
                function=self._generate_report_step,
                params={"topic": topic},
                dependencies=["cross_reference"]
            )
        ]
        
        return Workflow(
            workflow_id=workflow_id,
            name="多源信息分析",
            steps=steps
        )
    
    def _create_research_report_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
        """创建研究报告工作流"""
        topic = params.get('topic', '')
        
        steps = [
            WorkflowStep(
                step_id="literature_review",
                name="文献综述",
                function=self._literature_review_step,
                params={"topic": topic}
            ),
            WorkflowStep(
                step_id="current_trends",
                name="当前趋势分析",
                function=self._trends_analysis_step,
                params={"topic": topic}
            ),
            WorkflowStep(
                step_id="expert_opinions",
                name="专家观点收集",
                function=self._expert_opinions_step,
                params={"topic": topic}
            ),
            WorkflowStep(
                step_id="market_analysis",
                name="市场分析",
                function=self._market_analysis_step,
                params={"topic": topic},
                dependencies=["current_trends"]
            ),
            WorkflowStep(
                step_id="compile_report",
                name="编译报告",
                function=self._compile_report_step,
                params={"topic": topic},
                dependencies=["literature_review", "current_trends", "expert_opinions", "market_analysis"]
            )
        ]
        
        return Workflow(
            workflow_id=workflow_id,
            name="研究报告生成",
            steps=steps
        )
    
    def _create_competitive_analysis_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
        """创建竞争分析工作流"""
        company = params.get('company', '')
        industry = params.get('industry', '')
        
        steps = [
            WorkflowStep(
                step_id="company_profile",
                name="公司概况",
                function=self._company_profile_step,
                params={"company": company}
            ),
            WorkflowStep(
                step_id="competitor_identification",
                name="竞争对手识别",
                function=self._competitor_identification_step,
                params={"company": company, "industry": industry}
            ),
            WorkflowStep(
                step_id="market_position",
                name="市场定位分析",
                function=self._market_position_step,
                params={"company": company},
                dependencies=["company_profile", "competitor_identification"]
            ),
            WorkflowStep(
                step_id="swot_analysis",
                name="SWOT分析",
                function=self._swot_analysis_step,
                params={"company": company},
                dependencies=["market_position"]
            ),
            WorkflowStep(
                step_id="strategic_recommendations",
                name="战略建议",
                function=self._strategic_recommendations_step,
                params={"company": company},
                dependencies=["swot_analysis"]
            )
        ]
        
        return Workflow(
            workflow_id=workflow_id,
            name="竞争分析报告",
            steps=steps
        )
    
    def _create_trend_analysis_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Workflow:
        """创建趋势分析工作流"""
        domain = params.get('domain', '')
        timeframe = params.get('timeframe', '1year')
        
        steps = [
            WorkflowStep(
                step_id="historical_data",
                name="历史数据收集",
                function=self._historical_data_step,
                params={"domain": domain, "timeframe": timeframe}
            ),
            WorkflowStep(
                step_id="pattern_recognition",
                name="模式识别",
                function=self._pattern_recognition_step,
                params={},
                dependencies=["historical_data"]
            ),
            WorkflowStep(
                step_id="emerging_trends",
                name="新兴趋势识别",
                function=self._emerging_trends_step,
                params={"domain": domain}
            ),
            WorkflowStep(
                step_id="trend_correlation",
                name="趋势关联分析",
                function=self._trend_correlation_step,
                params={},
                dependencies=["pattern_recognition", "emerging_trends"]
            ),
            WorkflowStep(
                step_id="future_projection",
                name="未来预测",
                function=self._future_projection_step,
                params={"domain": domain},
                dependencies=["trend_correlation"]
            )
        ]
        
        return Workflow(
            workflow_id=workflow_id,
            name="趋势分析报告",
            steps=steps
        )
    
    # 步骤执行函数
    async def _search_step(self, query: str, search_type: str, agent: StatefulSearchAgent, **kwargs) -> Dict[str, Any]:
        """搜索步骤"""
        config = SearchConfig(
            search_type=SearchType(search_type),
            max_results=10,
            include_summary=True
        )
        result = await agent.search_tools.smart_search(query, config)
        return result.dict()
    
    async def _synthesize_step(self, query: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """结果综合步骤"""
        # 综合多个搜索结果
        all_results = []
        for step_id, result in previous_results.items():
            if isinstance(result, dict) and 'results' in result:
                all_results.extend(result['results'])
        
        return {
            "query": query,
            "total_results": len(all_results),
            "synthesized_results": all_results[:20],  # 取前20个结果
            "summary": f"综合了 {len(all_results)} 个搜索结果"
        }
    
    async def _summary_step(self, previous_results: Dict[str, Any], agent: StatefulSearchAgent, **kwargs) -> Dict[str, Any]:
        """摘要生成步骤"""
        synthesized = previous_results.get('synthesize_results', {})
        summary_text = synthesized.get('summary', '')
        
        if summary_text:
            result = await agent.summary_tool.summarize_text(summary_text, 300)
            return result.dict()
        
        return {"summary": "无法生成摘要"}
    
    # 其他步骤函数的简化实现
    async def _collect_sources_step(self, topic: str, **kwargs) -> Dict[str, Any]:
        return {"topic": topic, "sources": ["source1", "source2", "source3"]}
    
    async def _sentiment_analysis_step(self, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"sentiment": "neutral", "confidence": 0.7}
    
    async def _extract_key_points_step(self, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"key_points": ["point1", "point2", "point3"]}
    
    async def _cross_reference_step(self, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"cross_references": ["ref1", "ref2"]}
    
    async def _generate_report_step(self, topic: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"report": f"关于{topic}的分析报告", "sections": ["introduction", "analysis", "conclusion"]}
    
    async def _literature_review_step(self, topic: str, **kwargs) -> Dict[str, Any]:
        return {"literature_count": 50, "key_papers": ["paper1", "paper2"]}
    
    async def _trends_analysis_step(self, topic: str, **kwargs) -> Dict[str, Any]:
        return {"trends": ["trend1", "trend2"], "growth_rate": "15%"}
    
    async def _expert_opinions_step(self, topic: str, **kwargs) -> Dict[str, Any]:
        return {"experts": ["expert1", "expert2"], "opinions": ["opinion1", "opinion2"]}
    
    async def _market_analysis_step(self, topic: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"market_size": "1B", "growth_potential": "high"}
    
    async def _compile_report_step(self, topic: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"final_report": f"完整的{topic}研究报告", "page_count": 25}
    
    async def _company_profile_step(self, company: str, **kwargs) -> Dict[str, Any]:
        return {"company": company, "revenue": "1B", "employees": 1000}
    
    async def _competitor_identification_step(self, company: str, industry: str, **kwargs) -> Dict[str, Any]:
        return {"competitors": ["comp1", "comp2", "comp3"], "industry": industry}
    
    async def _market_position_step(self, company: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"market_share": "15%", "position": "leader"}
    
    async def _swot_analysis_step(self, company: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1"],
            "opportunities": ["opportunity1"],
            "threats": ["threat1"]
        }
    
    async def _strategic_recommendations_step(self, company: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"recommendations": ["rec1", "rec2", "rec3"]}
    
    async def _historical_data_step(self, domain: str, timeframe: str, **kwargs) -> Dict[str, Any]:
        return {"data_points": 365, "timeframe": timeframe, "domain": domain}
    
    async def _pattern_recognition_step(self, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"patterns": ["pattern1", "pattern2"], "confidence": 0.8}
    
    async def _emerging_trends_step(self, domain: str, **kwargs) -> Dict[str, Any]:
        return {"emerging_trends": ["trend1", "trend2"], "domain": domain}
    
    async def _trend_correlation_step(self, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"correlations": [{"trend1": "trend2", "correlation": 0.7}]}
    
    async def _future_projection_step(self, domain: str, previous_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {"projection": "增长趋势", "confidence": 0.6, "timeframe": "next_year"}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "duration": workflow.total_duration,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "duration": step.duration,
                    "error": step.error
                }
                for step in workflow.steps
            ]
        }
    
    def list_workflow_templates(self) -> List[str]:
        """列出可用的工作流模板"""
        return list(self.workflow_templates.keys())

# 异步任务队列
class AsyncTaskQueue:
    """异步任务队列"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.queue = asyncio.Queue()
        self.running_tasks = set()
        self.completed_tasks = {}
        self.failed_tasks = {}
        self._worker_tasks = []
    
    async def start_workers(self):
        """启动工作线程"""
        for i in range(self.max_concurrent_tasks):
            task = asyncio.create_task(self._worker(f"worker_{i}"))
            self._worker_tasks.append(task)
    
    async def stop_workers(self):
        """停止工作线程"""
        for task in self._worker_tasks:
            task.cancel()
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
    
    async def _worker(self, worker_name: str):
        """工作线程"""
        while True:
            try:
                task_item = await self.queue.get()
                task_id, coro = task_item
                
                self.running_tasks.add(task_id)
                
                try:
                    result = await coro
                    self.completed_tasks[task_id] = result
                except Exception as e:
                    self.failed_tasks[task_id] = str(e)
                finally:
                    self.running_tasks.discard(task_id)
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_name} error: {e}")
    
    async def submit_task(self, task_id: str, coro) -> str:
        """提交任务"""
        await self.queue.put((task_id, coro))
        return task_id
    
    def get_task_status(self, task_id: str) -> str:
        """获取任务状态"""
        if task_id in self.completed_tasks:
            return "completed"
        elif task_id in self.failed_tasks:
            return "failed"
        elif task_id in self.running_tasks:
            return "running"
        else:
            return "pending"
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """获取任务结果"""
        return self.completed_tasks.get(task_id)
    
    def get_task_error(self, task_id: str) -> Optional[str]:
        """获取任务错误"""
        return self.failed_tasks.get(task_id)