from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1)
    streamer_name: Optional[str] = Field(None, description="主播名称（可选）")
    user_preferences: Optional[str] = Field(None, description="用户偏好（可选）")


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str = Field(..., description="AI 回复")
    conversation_id: str = Field(default="default", description="对话 ID")


class StreamEvent(BaseModel):
    """流式事件"""
    event: str = Field(..., description="事件类型: chunk/done/error")
    data: str = Field("", description="事件数据")


class TemplateInfoRequest(BaseModel):
    """模板查询请求"""
    name: str = Field(..., description="模板名称")


class TemplateInfoResponse(BaseModel):
    """模板信息响应"""
    name: str = Field(..., description="模板名称")
    description: str = Field(default="", description="模板描述")
    category: str = Field(default="", description="模板分类")
    input_variables: List[str] = Field(default_factory=list, description="输入变量列表")
    template_content: str = Field(default="", description="模板原始内容")


class GeneratePromptRequest(BaseModel):
    """基于模板生成请求"""
    template_name: str = Field(..., description="模板名称")
    variables: Dict[str, str] = Field(default_factory=dict, description="模板变量值")


class GeneratePromptResponse(BaseModel):
    """基于模板生成响应"""
    template_name: str = Field(..., description="模板名称")
    result: str = Field(..., description="生成结果")
    formatted_prompt: str = Field(default="", description="格式化后的完整提示词")


class GenerateRequest(BaseModel):
    """生成推荐理由请求"""
    streamer_name: str = Field(..., description="主播名称", min_length=1)
    tags: Optional[str] = Field(None, description="主播标签")
    content: Optional[str] = Field(None, description="主播内容")
    preferences: Optional[str] = Field(None, description="用户偏好")


class GenerateResponse(BaseModel):
    """生成推荐理由响应"""
    streamer_name: str = Field(..., description="主播名称")
    recommendation: str = Field(..., description="推荐理由")
    sources: List[str] = Field(default_factory=list, description="信息来源")


class ModelInfo(BaseModel):
    """模型信息"""
    name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    is_current: bool = Field(default=False, description="是否当前使用")


class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: List[ModelInfo] = Field(..., description="模型列表")
    current: str = Field(..., description="当前模型")


class SwitchModelRequest(BaseModel):
    """切换模型请求"""
    model_type: str = Field(..., description="模型类型: openai/anthropic/dashscope/qianfan/deepseek")


class AddModelRequest(BaseModel):
    """添加模型请求"""
    model_type: str = Field(..., description="自定义模型标识（如 my-model）")
    model_name: str = Field(..., description="模型名称（如 gpt-4o-mini）")
    api_key: str = Field(..., description="API 密钥")
    api_base: Optional[str] = Field(None, description="API 基础 URL（可选）")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2048, ge=1, description="最大 Token 数")


class DeleteModelRequest(BaseModel):
    """删除模型请求"""
    model_type: str = Field(..., description="要删除的模型类型")


class SystemPromptInfo(BaseModel):
    """系统提示词信息"""
    name: str = Field(..., description="提示词名称")
    description: str = Field(..., description="描述")
    category: str = Field(..., description="分类")
    is_current: bool = Field(default=False, description="是否当前使用")


class SystemPromptListResponse(BaseModel):
    """系统提示词列表响应"""
    prompts: List[SystemPromptInfo] = Field(..., description="提示词列表")
    current: str = Field(..., description="当前提示词")


class SwitchSystemPromptRequest(BaseModel):
    """切换系统提示词请求"""
    prompt_name: str = Field(..., description="系统提示词名称")


class SystemPromptContentResponse(BaseModel):
    """系统提示词内容响应"""
    name: str = Field(..., description="提示词名称")
    content: str = Field(..., description="提示词内容")
    file_path: str = Field(..., description="文件路径")


class CreateSystemPromptRequest(BaseModel):
    """创建系统提示词请求"""
    name: str = Field(..., description="提示词名称", min_length=1)
    content: str = Field(..., description="提示词内容", min_length=1)
    description: str = Field(default="", description="描述")
    category: str = Field(default="custom", description="分类")


class EditSystemPromptRequest(BaseModel):
    """编辑系统提示词请求"""
    content: Optional[str] = Field(None, description="提示词内容")
    description: Optional[str] = Field(None, description="描述")
    category: Optional[str] = Field(None, description="分类")


class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str = Field(..., description="搜索查询", min_length=1)
    k: int = Field(default=4, ge=1, le=20, description="返回结果数量")


class KnowledgeSearchResult(BaseModel):
    """知识库搜索结果"""
    content: str = Field(..., description="内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    score: Optional[float] = Field(None, description="相似度分数")


class KnowledgeSearchResponse(BaseModel):
    """知识库搜索响应"""
    results: List[KnowledgeSearchResult] = Field(..., description="搜索结果")
    total: int = Field(0, description="结果数量")


class KnowledgeUploadResponse(BaseModel):
    """知识库上传响应"""
    file_name: str = Field(..., description="文件名")
    document_ids: List[str] = Field(..., description="文档 ID 列表")
    chunk_count: int = Field(0, description="分块数量")


class KnowledgeStatusResponse(BaseModel):
    """知识库状态响应"""
    document_count: int = Field(0, description="文档数量")
    collection_name: str = Field(..., description="集合名称")
    persist_directory: Optional[str] = Field(None, description="持久化目录")
    embedding_model: str = Field("未配置", description="嵌入模型")


class KnowledgeDocumentInfo(BaseModel):
    """知识库文档信息"""
    id: str = Field(..., description="文档 ID")
    content: str = Field(..., description="文档内容摘要")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class KnowledgeDocumentListResponse(BaseModel):
    """知识库文档列表响应"""
    documents: List[KnowledgeDocumentInfo] = Field(..., description="文档列表")
    total: int = Field(0, description="文档总数")


class KnowledgeDeleteDocumentRequest(BaseModel):
    """删除知识库文档请求"""
    ids: List[str] = Field(..., description="要删除的文档 ID 列表")


class KnowledgeFileInfo(BaseModel):
    """知识库文件信息"""
    source: str = Field(..., description="文件名")
    chunk_count: int = Field(0, description="文档块数量")


class KnowledgeFileListResponse(BaseModel):
    """知识库文件列表响应"""
    files: List[KnowledgeFileInfo] = Field(..., description="文件列表")
    total: int = Field(0, description="文件总数")


class KnowledgeFileDetailResponse(BaseModel):
    """知识库文件详情响应"""
    source: str = Field(..., description="文件名")
    chunk_count: int = Field(0, description="文档块数量")
    documents: List[KnowledgeDocumentInfo] = Field(..., description="文档块列表")


class KnowledgeDeleteFileResponse(BaseModel):
    """删除知识库文件响应"""
    source: str = Field(..., description="文件名")
    deleted_chunks: int = Field(0, description="删除的文档块数量")
    message: str = Field(..., description="操作消息")


class CustomPromptInfo(BaseModel):
    """自定义提示词信息"""
    name: str = Field(..., description="模板名称")
    description: str = Field(default="", description="描述")
    category: str = Field(default="custom", description="分类")
    input_variables: List[str] = Field(default_factory=list, description="输入变量")
    template: str = Field(default="", description="模板内容")


class CustomPromptListResponse(BaseModel):
    """自定义提示词列表响应"""
    prompts: List[CustomPromptInfo] = Field(..., description="提示词列表")


class CreateCustomPromptRequest(BaseModel):
    """创建自定义提示词请求"""
    name: str = Field(..., description="模板名称", min_length=1)
    template: str = Field(..., description="模板内容，支持 {变量名}", min_length=1)
    description: str = Field(default="", description="描述")
    category: str = Field(default="custom", description="分类")
    input_variables: Optional[List[str]] = Field(None, description="输入变量，自动从模板提取")


class EditCustomPromptRequest(BaseModel):
    """编辑自定义提示词请求"""
    template: Optional[str] = Field(None, description="模板内容")
    input_variables: Optional[List[str]] = Field(None, description="输入变量列表")
    description: Optional[str] = Field(None, description="模板描述")
    category: Optional[str] = Field(None, description="模板分类")


class FormatPromptRequest(BaseModel):
    """格式化提示词请求"""
    prompt_name: str = Field(..., description="提示词名称")
    variables: Dict[str, str] = Field(..., description="变量值")


class FormatPromptResponse(BaseModel):
    """格式化提示词响应"""
    prompt_name: str = Field(..., description="提示词名称")
    formatted: str = Field(..., description="格式化后的提示词")
    variables: List[str] = Field(..., description="使用的变量")


class AgentStatusResponse(BaseModel):
    """Agent 状态响应"""
    current_model: str = Field(..., description="当前模型")
    available_models: List[str] = Field(..., description="可用模型列表")
    current_system_prompt: str = Field(..., description="当前系统提示词")
    conversation_length: int = Field(0, description="对话历史长度")
    knowledge_base_count: int = Field(0, description="知识库文档数量")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误")


class HistoryResponse(BaseModel):
    """对话历史响应"""
    messages: List[Dict[str, str]] = Field(..., description="消息列表")
    total: int = Field(..., description="消息总数")