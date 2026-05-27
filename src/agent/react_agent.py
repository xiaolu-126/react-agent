from __future__ import annotations

import json
from typing import Annotated, List, Dict, Any, Optional, TypedDict, Sequence, Literal
from operator import add

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.errors import GraphRecursionError

from src.models.model_manager import ModelManager
from src.agent.prompt_manager import PromptManager
from src.agent.memory import ChatMemoryManager
from src.agent.system_prompt_manager import SystemPromptManager
from src.tools.knowledge_base import KnowledgeBase
from src.tools.web_search import WebSearch, web_search
from src.utils.logger import get_logger

logger = get_logger("agent")


class AgentState(TypedDict):
    """ReAct Agent 的状态结构
    
    Attributes:
        messages: 对话历史消息列表
        input: 用户输入
        streamer_name: 主播名称（如果有的话）
        tools: 可用工具列表
        tool_calls: 工具调用历史
        observations: 观察结果列表
        final_output: 最终输出
        user_preferences: 用户偏好信息
    """
    messages: Annotated[Sequence[BaseMessage], add]
    input: str
    streamer_name: Optional[str]
    tools: List[Any]
    tool_calls: List[Dict[str, Any]]
    observations: List[str]
    final_output: Optional[str]
    user_preferences: Optional[str]


class ReActAgent:
    """基于 LangGraph 的 ReAct Agent 实现
    
    该 Agent 能够：
    - 根据用户输入自主决定调用哪些工具
    - 支持知识库检索和网络搜索
    - 生成高质量的主播推荐理由
    - 提供流式输出接口
    - 支持多模型切换
    - 管理对话记忆
    """
    
    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        prompt_manager: Optional[PromptManager] = None,
        memory_manager: Optional[ChatMemoryManager] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        web_search: Optional[WebSearch] = None,
        system_prompt_manager: Optional[SystemPromptManager] = None,
        system_prompt_name: str = "streamer_recommender",
        max_iterations: int = 25,
    ):
        """初始化 ReAct Agent
        
        Args:
            model_manager: 模型管理器
            prompt_manager: 提示词管理器
            memory_manager: 对话记忆管理器
            knowledge_base: 知识库
            web_search: 网络搜索工具
            system_prompt_manager: 系统提示词管理器
            system_prompt_name: 系统提示词名称
            max_iterations: 最大迭代次数
        """
        self.model_manager = model_manager or ModelManager()
        self.prompt_manager = prompt_manager or PromptManager()
        self.memory_manager = memory_manager or ChatMemoryManager()
        self.knowledge_base = knowledge_base
        self.web_search = web_search or WebSearch()
        self.system_prompt_manager = system_prompt_manager or SystemPromptManager()
        self.system_prompt_name = system_prompt_name
        self.max_iterations = max_iterations
        
        self._tools = self._setup_tools()
        self._graph = self._build_graph()
        self._compiled_graph = self._graph.compile()
    
    def _setup_tools(self) -> List[Any]:
        """设置可用工具
        
        Returns:
            工具列表
        """
        tools = []
        
        @tool
        def knowledge_base_search(
            query: str = ...,
            k: int = 4
        ) -> str:
            """从知识库中搜索相关信息
            
            Args:
                query: 搜索查询
                k: 返回结果数量
                
            Returns:
                知识库搜索结果
            """
            if not self.knowledge_base:
                return "知识库未初始化，请先初始化知识库。"
            
            try:
                docs = self.knowledge_base.similarity_search(query, k=k)
                if not docs:
                    return "知识库中未找到相关信息。"
                
                result = "知识库搜索结果：\n"
                for i, doc in enumerate(docs, 1):
                    result += f"{i}. {doc.page_content}\n"
                    if doc.metadata:
                        result += f"   元数据: {json.dumps(doc.metadata, ensure_ascii=False)}\n"
                return result
            except Exception as e:
                return f"知识库搜索失败: {str(e)}"
        
        tools.append(web_search)
        tools.append(knowledge_base_search)
        
        return tools
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词
        
        从 SystemPromptManager 加载，支持自定义 .md 文件。
        
        Returns:
            系统提示词
        """
        try:
            return self.system_prompt_manager.get_system_prompt(self.system_prompt_name)
        except (ValueError, FileNotFoundError) as e:
            logger.warning("系统提示词 '%s' 加载失败: %s，使用默认提示词", self.system_prompt_name, e)
            return f"""你是一个专业的主播推荐助手。你的任务是根据用户提供的主播昵称生成高质量的推荐理由。

推荐理由应该包括：
- 主播的基本信息
- 主播的特点和风格
- 为什么推荐这个主播
- 适合什么样的观众

请使用中文回答，并保持友好和专业的语气。"""
    
    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Agent 思考节点
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        llm = self.model_manager.get_chat_model()
        llm_with_tools = llm.bind_tools(self._tools)
        
        messages = [SystemMessage(content=self._get_system_prompt())]
        
        if state["messages"]:
            # 过滤历史消息：只保留 ToolMessage 和带工具调用的 AIMessage
            # 避免已生成的最终回答被再次传递给 LLM 导致重复
            filtered_messages = []
            for msg in state["messages"]:
                if isinstance(msg, ToolMessage):
                    filtered_messages.append(msg)
                elif isinstance(msg, AIMessage):
                    # 只保留带工具调用的 AIMessage
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        filtered_messages.append(msg)
            messages.extend(filtered_messages)
            logger.info("Agent 继续推理 | 原始消息数=%d | 过滤后=%d", 
                        len(state["messages"]), len(filtered_messages))
        else:
            messages.append(HumanMessage(content=state["input"]))
            logger.info("Agent 开始推理 | input=%.80s", state["input"])
        
        response = llm_with_tools.invoke(messages)
        
        content_preview = str(response.content)[:100] if response.content else "(无文本内容)"
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_names = [tc.get("name", "?") for tc in response.tool_calls]
            logger.info(
                "LLM 响应 | tool_calls=%d | tools=%s | content_preview=%.80s",
                len(response.tool_calls), tool_names, content_preview,
            )
        else:
            logger.info(
                "LLM 响应 | 最终输出 | content_len=%d | preview=%.80s",
                len(response.content or ""), content_preview,
            )
        
        return {
            "messages": [response],
        }
    
    def _should_continue(self, state: AgentState) -> Literal["action", "observation", "__end__"]:
        """决定是否继续迭代
        
        Args:
            state: 当前状态
            
        Returns:
            下一个节点名称或结束
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_names = [tc.get("name", "?") for tc in last_message.tool_calls]
            logger.info("继续迭代 | 工具=%s → action", tool_names)
            return "action"
        else:
            logger.info("迭代结束 → __end__")
            return "__end__"
    
    def _action_node(self, state: AgentState) -> Dict[str, Any]:
        """工具调用节点

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        tool_node = ToolNode(self._tools)
        try:
            result = tool_node.invoke(state)
        except Exception as e:
            logger.error("ToolNode.invoke 异常: %s", e, exc_info=True)
            raise

        new_tool_calls = []
        if state["tool_calls"]:
            new_tool_calls.extend(state["tool_calls"])

        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls"):
            for tc in last_message.tool_calls:
                new_tool_calls.append({
                    "name": tc["name"],
                    "args": tc["args"],
                    "id": tc["id"],
                })
                logger.info(
                    "工具调用 | name=%s | args=%s",
                    tc["name"], json.dumps(tc["args"], ensure_ascii=False),
                )

        if result and "messages" in result:
            for tm in result["messages"]:
                if isinstance(tm, ToolMessage):
                    content_preview = str(tm.content)[:200] if tm.content else "(空)"
                    logger.info(
                        "工具结果 | name=%s | content=%.180s",
                        getattr(tm, "name", "?"), content_preview,
                    )
        
        return {
            "messages": result["messages"],
            "tool_calls": new_tool_calls,
        }
    
    def _observation_node(self, state: AgentState) -> Dict[str, Any]:
        """观察结果节点
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        new_observations = []
        if state["observations"]:
            new_observations.extend(state["observations"])
        
        messages = state["messages"]
        for msg in messages:
            if isinstance(msg, ToolMessage):
                new_observations.append(msg.content)
                logger.info(
                    "观察记录 | content=%.150s",
                    str(msg.content)[:150] if msg.content else "(空)",
                )
        
        logger.info("本轮工具结果数=%d | 累计观察数=%d",
                     sum(1 for m in messages if isinstance(m, ToolMessage)),
                     len(new_observations))
        
        return {
            "observations": new_observations,
        }
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图
        
        Returns:
            编译后的状态图
        """
        graph = StateGraph(AgentState)
        
        graph.add_node("agent", self._agent_node)
        graph.add_node("action", self._action_node)
        graph.add_node("observation", self._observation_node)
        
        graph.set_entry_point("agent")
        
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "action": "action",
                "observation": "observation",
                "__end__": END,
            },
        )
        
        graph.add_edge("action", "observation")
        graph.add_edge("observation", "agent")
        
        return graph
    
    def run(
        self,
        input: str,
        streamer_name: Optional[str] = None,
        user_preferences: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """运行 Agent

        Args:
            input: 用户输入
            streamer_name: 主播名称
            user_preferences: 用户偏好
            stream: 是否使用流式输出

        Returns:
            Agent 的回复
        """
        logger.info("Agent 开始处理请求 | streamer=%s | input=%.80s", streamer_name or "N/A", input)
        initial_state: AgentState = {
            "messages": self.memory_manager.get_chat_history(),
            "input": input,
            "streamer_name": streamer_name,
            "tools": self._tools,
            "tool_calls": [],
            "observations": [],
            "final_output": None,
            "user_preferences": user_preferences,
        }
        
        self.memory_manager.add_user_message(input)

        try:
            if stream:
                output = ""
                last_ai_kwargs: dict = {}
                for chunk in self._compiled_graph.stream(initial_state, {"recursion_limit": self.max_iterations}):
                    for key, value in chunk.items():
                        if key == "agent" and "messages" in value:
                            for msg in value["messages"]:
                                if isinstance(msg, AIMessage) and msg.content:
                                    is_intermediate = hasattr(msg, "tool_calls") and msg.tool_calls
                                    if not is_intermediate:
                                        logger.info(
                                            "流式检测到 Agent 输出 | content_len=%d",
                                            len(msg.content),
                                        )
                                        # 使用 = 而不是 +=，避免多个 AIMessage 内容累加导致重复
                                        output = msg.content
                                        last_ai_kwargs = msg.additional_kwargs
                print()
            else:
                result = self._compiled_graph.invoke(initial_state, {"recursion_limit": self.max_iterations})
                messages = result["messages"]
                output = ""
                last_ai_kwargs: dict = {}
                for msg in messages:
                    if isinstance(msg, AIMessage) and msg.content:
                        has_tc = hasattr(msg, "tool_calls") and msg.tool_calls
                        logger.info(
                            "invoke 结果中的 AIMessage | content_len=%d | tool_calls=%s",
                            len(msg.content), has_tc,
                        )
                        if not has_tc:
                            output = msg.content
                        last_ai_kwargs = msg.additional_kwargs
        except GraphRecursionError:
            logger.warning("Agent 达到递归限制，基于已有信息生成回复")
            output = self._build_fallback_output(initial_state)
            last_ai_kwargs = {}

        # 去重：如果输出内容重复出现两次完全相同的内容，只保留第一次
        output = self._deduplicate_output(output)
        
        self.memory_manager.add_ai_message(output, additional_kwargs=last_ai_kwargs)
        logger.info("Agent 处理完成 | output_length=%d | output=%.120s", len(output), output)
        return output
    
    def stream(self, input: str, streamer_name: Optional[str] = None, user_preferences: Optional[str] = None):
        """流式输出接口

        Args:
            input: 用户输入
            streamer_name: 主播名称
            user_preferences: 用户偏好

        Yields:
            输出内容的块
        """
        logger.info("Agent 流式处理开始 | streamer=%s | input=%.80s", streamer_name or "N/A", input)
        initial_state: AgentState = {
            "messages": self.memory_manager.get_chat_history(),
            "input": input,
            "streamer_name": streamer_name,
            "tools": self._tools,
            "tool_calls": [],
            "observations": [],
            "final_output": None,
            "user_preferences": user_preferences,
        }
        
        try:
            self.memory_manager.add_user_message(input)

            full_output = ""
            for chunk in self._compiled_graph.stream(initial_state, {"recursion_limit": self.max_iterations}):
                for key, value in chunk.items():
                    if key == "agent" and "messages" in value:
                        for msg in value["messages"]:
                            if isinstance(msg, AIMessage) and msg.content:
                                is_intermediate = hasattr(msg, "tool_calls") and msg.tool_calls
                                if not is_intermediate:
                                    before_len = len(full_output)
                                    full_output += msg.content
                                    logger.info(
                                        "流式获取到 Agent 输出 | added_len=%d | total=%d",
                                        len(full_output) - before_len,
                                        len(full_output),
                                    )
            
            # 收集完整内容后再去重和 yield
            if full_output:
                final = self._deduplicate_output(full_output)
                logger.info(
                    "流式处理完成 | 原始=%d | 去重后=%d",
                    len(full_output),
                    len(final),
                )
                # 一次性 yield 去重后的完整内容
                yield final
                self.memory_manager.add_ai_message(final)
        except GraphRecursionError:
            logger.warning("流式 Agent 达到递归限制")
            fallback = self._build_fallback_output(initial_state)
            yield fallback
            self.memory_manager.add_ai_message(fallback)

    def _deduplicate_output(self, text: str) -> str:
        """检测并移除完全重复的输出（通用多策略）"""
        if not text or len(text) < 20:
            return text
        n = len(text)

        # 策略1: 搜索通用标记第二次出现（处理"🎙️ xxx 🎙️ xxx"这类重复）
        markers = ["🎙️", "主播", "推荐", "🎤", "推荐主播", "推荐理由"]
        for marker in markers:
            first_pos = text.find(marker)
            if first_pos >= 0:
                second_pos = text.find(marker, first_pos + 1)
                if second_pos > first_pos:
                    candidate = text[:second_pos].strip()
                    after_second = text[second_pos:].strip()
                    if after_second.startswith(candidate) or after_second == candidate or candidate in after_second:
                        logger.info(
                            "去重策略1（标记重复）生效 | marker=%s | first_len=%d | total=%d",
                            marker, len(candidate), n,
                        )
                        return candidate

        # 策略2: 自动检测重复模式 - 搜索文本开头的单词/短语第二次出现
        # 取开头的字符作为锚点，从中点开始搜索第二次出现
        anchor_len = min(15, n // 4)
        anchor = text[:anchor_len].strip()
        if len(anchor) >= 5:
            second_pos = text.find(anchor, anchor_len)
            if second_pos > 0 and second_pos < n - anchor_len:
                # 找到第二次出现，检查是否是完整重复
                first_part = text[:second_pos].strip()
                after_second = text[second_pos:].strip()
                if after_second.startswith(first_part) or after_second == first_part:
                    logger.info(
                        "去重策略2（自动锚点）生效 | first_len=%d | pos=%d | total=%d",
                        len(first_part), second_pos, n,
                    )
                    return first_part

        # 策略3: 从中点附近搜索第二个副本的起点
        mid = n // 2
        prefix_len = min(25, n // 3)
        prefix = text[:prefix_len]
        second_start = text.find(prefix, mid - prefix_len)
        if 0 < second_start < n - prefix_len:
            first_part = text[:second_start]
            after = text[second_start:]
            if after.startswith(first_part) or after.strip() == first_part.strip():
                logger.info(
                    "去重策略3（前缀匹配）生效 | first_len=%d | pos=%d | total=%d",
                    len(first_part), second_start, n,
                )
                return first_part.rstrip()

        # 策略4: 检测文本是否由两个相同的部分组成
        # 检查中点附近的分割点
        for offset in range(-50, 51):
            split = mid + offset
            if split < n // 4 or split > n * 3 // 4:
                continue
            first = text[:split].strip()
            second = text[split:].strip()
            if len(first) < 20 or len(second) < 20:
                continue
            # 检查两个部分是否相同
            if first == second or first == second[:len(first)] or second == first[:len(second)]:
                logger.info(
                    "去重策略4（中点分割）生效 | first_len=%d | offset=%d | total=%d",
                    len(first), offset, n,
                )
                return first

        # 策略5: 相似度检测 - 扫描所有位置
        quarter = n // 4
        for split in range(quarter, n - quarter):
            first = text[:split]
            second = text[split:]
            if len(first) < 30 or len(second) < 30:
                continue
            check_len = min(len(first), len(second))
            if first[:check_len].strip() == second[:check_len].strip():
                similarity = sum(1 for a, b in zip(first[:check_len], second[:check_len]) if a == b) / check_len
                if similarity > 0.8:
                    logger.info(
                        "去重策略5（相似度检测）生效 | first_len=%d | similarity=%.2f | total=%d",
                        len(first), similarity, n,
                    )
                    return first.rstrip()

        logger.info("去重未命中 | total_len=%d", n)
        return text

    def _build_fallback_output(self, state: AgentState) -> str:
        """当 Agent 达到递归限制时生成降级回复"""
        streamer = state.get("streamer_name", "") or ""
        observations = state.get("observations", [])
        tool_calls = state.get("tool_calls", [])

        parts = []
        if streamer:
            parts.append(f"关于 {streamer}")
        if observations:
            parts.append(f"我已查阅了相关信息")
        parts.append("由于信息处理较复杂，请稍后再试或换一种提问方式")

        logger.info(
            "fallback | streamer=%s | tool_calls=%d | observations=%d",
            streamer, len(tool_calls), len(observations),
        )
        return "，".join(parts) + "。"

    def get_conversation_history(self):
        """获取对话历史
        
        Returns:
            对话历史
        """
        return self.memory_manager.get_conversation_history()
    
    def clear_memory(self):
        """清空对话记忆"""
        self.memory_manager.clear()
    
    def switch_model(self, model_type):
        """切换模型
        
        Args:
            model_type: 模型类型
        """
        self.model_manager.set_current_model(model_type)
    
    def switch_system_prompt(self, system_prompt_name: str):
        """切换系统提示词
        
        Args:
            system_prompt_name: 系统提示词名称
        """
        if system_prompt_name not in self.system_prompt_manager.index:
            raise ValueError(f"系统提示词 '{system_prompt_name}' 不存在")
        self.system_prompt_name = system_prompt_name
