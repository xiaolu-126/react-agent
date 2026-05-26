from __future__ import annotations

import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from src.agent.react_agent import ReActAgent
from src.agent.system_prompt_manager import SystemPromptManager
from src.agent.prompt_manager import PromptManager, PromptTemplate
from src.tools.knowledge_base import KnowledgeBase
from . import schemas

router = APIRouter()


def _get_agent() -> ReActAgent:
    """获取全局 Agent 实例"""
    from src.agent.react_agent import ReActAgent
    global _agent_instance
    if "_agent_instance" not in globals() or globals()["_agent_instance"] is None:
        globals()["_agent_instance"] = ReActAgent()
    return globals()["_agent_instance"]


def _get_system_prompt_manager() -> SystemPromptManager:
    """获取系统提示词管理器"""
    return SystemPromptManager()


def _get_prompt_manager() -> PromptManager:
    """获取提示词管理器"""
    return PromptManager()


def _get_knowledge_base() -> KnowledgeBase:
    """获取知识库实例"""
    try:
        from src.utils.config import get_config
        config = get_config()
        return KnowledgeBase(
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "agent_documents"),
            persist_directory=config.chroma_db_path,
        )
    except Exception:
        return KnowledgeBase()


import os


# ==================== 聊天 API ====================

@router.post("/chat", response_model=schemas.ChatResponse, summary="发送聊天消息")
async def chat(request: schemas.ChatRequest):
    """发送消息给 Agent，获取回复（非流式）"""
    try:
        agent = _get_agent()
        reply = agent.run(
            input=request.message,
            streamer_name=request.streamer_name,
            user_preferences=request.user_preferences,
            stream=False,
        )
        return schemas.ChatResponse(reply=reply, conversation_id="default")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream", summary="流式聊天")
async def chat_stream(request: schemas.ChatRequest):
    """发送消息给 Agent，通过 SSE 获取流式回复"""
    agent = _get_agent()

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            full_text = ""
            async for chunk in agent.stream(
                input=request.message,
                streamer_name=request.streamer_name,
                user_preferences=request.user_preferences,
            ):
                full_text += chunk
                yield {"event": "chunk", "data": chunk}
            yield {"event": "done", "data": full_text}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


# ==================== 生成推荐 API ====================

@router.post("/generate", response_model=schemas.GenerateResponse, summary="生成主播推荐理由")
async def generate_recommendation(request: schemas.GenerateRequest):
    """根据主播名称生成推荐理由"""
    try:
        prompt_manager = _get_prompt_manager()
        agent = _get_agent()

        prompt = prompt_manager.format_prompt(
            "streamer_recommendation",
            streamer_name=request.streamer_name,
            streamer_tags=request.tags or "",
            streamer_content=request.content or "",
            user_preferences=request.preferences or "",
        )

        reply = agent.run(
            input=prompt,
            streamer_name=request.streamer_name,
            user_preferences=request.preferences,
            stream=False,
        )

        return schemas.GenerateResponse(
            streamer_name=request.streamer_name,
            recommendation=reply,
            sources=[],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream", summary="流式生成主播推荐理由")
async def generate_recommendation_stream(request: schemas.GenerateRequest):
    """根据主播名称流式生成推荐理由"""
    agent = _get_agent()

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            full_text = ""
            async for chunk in agent.stream(
                input=f"请推荐主播 {request.streamer_name}",
                streamer_name=request.streamer_name,
                user_preferences=request.preferences,
            ):
                full_text += chunk
                yield {"event": "chunk", "data": chunk}
            yield {"event": "done", "data": full_text}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


# ==================== 模型管理 API ====================

@router.get("/models", response_model=schemas.ModelListResponse, summary="获取模型列表")
async def list_models():
    """获取所有可用的模型列表"""
    try:
        agent = _get_agent()
        manager = agent.model_manager
        available = manager.get_available_models()
        current = manager.get_current_model()

        models = []
        for m in available:
            m_id = m.value if hasattr(m, "value") else str(m)
            c_id = current.value if hasattr(current, "value") else str(current)
            models.append(schemas.ModelInfo(
                name=m_id,
                display_name=manager.get_model_display_name(m),
                is_current=(m_id == c_id),
            ))

        return schemas.ModelListResponse(
            models=models,
            current=c_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/switch", response_model=schemas.ModelInfo, summary="切换模型")
async def switch_model(request: schemas.SwitchModelRequest):
    """切换到指定模型"""
    try:
        model_type_str = request.model_type.lower()
        agent = _get_agent()
        agent.switch_model(model_type_str)

        model_names = {
            "openai": "GPT-4 / GPT-3.5",
            "anthropic": "Claude 3",
            "dashscope": "通义千问",
            "qianfan": "文心一言",
            "deepseek": "DeepSeek",
        }

        display = model_names.get(model_type_str, model_type_str)

        return schemas.ModelInfo(
            name=model_type_str,
            display_name=display,
            is_current=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/add", response_model=schemas.ModelInfo, status_code=201, summary="添加自定义模型")
async def add_model(request: schemas.AddModelRequest):
    """添加自定义模型（OpenAI 兼容接口）"""
    try:
        agent = _get_agent()
        manager = agent.model_manager
        model_key = manager.add_custom_model(
            model_type=request.model_type,
            model_name=request.model_name,
            api_key=request.api_key,
            api_base=request.api_base,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return schemas.ModelInfo(
            name=model_key,
            display_name=request.model_name,
            is_current=False,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_type}", summary="删除模型")
async def delete_model(model_type: str):
    """删除指定模型（不能删除当前正在使用的模型）"""
    try:
        agent = _get_agent()
        manager = agent.model_manager
        manager.remove_model(model_type)
        return {"message": f"模型 '{model_type}' 已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 系统提示词管理 API ====================

@router.get("/system-prompts", response_model=schemas.SystemPromptListResponse, summary="获取系统提示词列表")
async def list_system_prompts():
    """获取所有可用的系统提示词"""
    try:
        manager = _get_system_prompt_manager()
        agent = _get_agent()
        prompts = manager.list_prompts()

        prompt_list = []
        for p in prompts:
            prompt_list.append(schemas.SystemPromptInfo(
                name=p["name"],
                description=p["description"],
                category=p["category"],
                is_current=(p["name"] == agent.system_prompt_name),
            ))

        return schemas.SystemPromptListResponse(
            prompts=prompt_list,
            current=agent.system_prompt_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-prompts/{name}", response_model=schemas.SystemPromptContentResponse, summary="获取系统提示词内容")
async def get_system_prompt(name: str):
    """获取指定系统提示词的内容"""
    try:
        manager = _get_system_prompt_manager()
        content = manager.get_system_prompt(name)
        file_path = manager.get_prompt_file_path(name)
        return schemas.SystemPromptContentResponse(
            name=name,
            content=content,
            file_path=str(file_path) if file_path else "",
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-prompts/switch", response_model=schemas.SystemPromptInfo, summary="切换系统提示词")
async def switch_system_prompt(request: schemas.SwitchSystemPromptRequest):
    """切换到指定系统提示词"""
    try:
        manager = _get_system_prompt_manager()
        prompts = manager.list_prompts()
        names = [p["name"] for p in prompts]

        if request.prompt_name not in names:
            raise HTTPException(status_code=404, detail=f"系统提示词 '{request.prompt_name}' 不存在")

        agent = _get_agent()
        agent.switch_system_prompt(request.prompt_name)

        meta = manager.index[request.prompt_name]
        return schemas.SystemPromptInfo(
            name=request.prompt_name,
            description=meta["description"],
            category=meta["category"],
            is_current=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-prompts", response_model=schemas.SystemPromptInfo, status_code=201, summary="创建系统提示词")
async def create_system_prompt(request: schemas.CreateSystemPromptRequest):
    """创建新的系统提示词（会创建对应的 .md 文件）"""
    try:
        manager = _get_system_prompt_manager()
        success = manager.add_prompt(
            name=request.name,
            file_content=request.content,
            description=request.description,
            category=request.category,
        )
        if not success:
            raise HTTPException(status_code=409, detail=f"系统提示词 '{request.name}' 已存在")

        return schemas.SystemPromptInfo(
            name=request.name,
            description=request.description,
            category=request.category,
            is_current=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/system-prompts/{name}", response_model=schemas.SystemPromptInfo, summary="编辑系统提示词")
async def edit_system_prompt(name: str, request: schemas.EditSystemPromptRequest):
    """编辑系统提示词的内容或元数据"""
    try:
        manager = _get_system_prompt_manager()
        success = manager.edit_prompt(
            name=name,
            file_content=request.content,
            description=request.description,
            category=request.category,
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"系统提示词 '{name}' 不存在")

        meta = manager.index[name]
        return schemas.SystemPromptInfo(
            name=name,
            description=meta["description"],
            category=meta["category"],
            is_current=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/system-prompts/{name}", summary="删除系统提示词")
async def delete_system_prompt(name: str):
    """删除自定义系统提示词（预设提示词不可删除）"""
    try:
        manager = _get_system_prompt_manager()
        success = manager.delete_prompt(name)
        if not success:
            raise HTTPException(status_code=404, detail=f"系统提示词 '{name}' 不存在或不可删除")
        return {"message": f"系统提示词 '{name}' 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/custom-prompts/{name}", response_model=schemas.CustomPromptInfo, summary="编辑自定义提示词")
async def edit_custom_prompt(name: str, request: schemas.EditCustomPromptRequest):
    """编辑自定义提示词模板内容、描述、变量等"""
    try:
        pm = _get_prompt_manager()
        template = pm.get_template(name)
        if not template:
            raise HTTPException(status_code=404, detail=f"自定义提示词 '{name}' 不存在")

        if name in ["streamer_recommendation", "content_summary", "question_answering"]:
            raise HTTPException(status_code=400, detail="内置模板不可编辑")

        success = pm.edit_template(
            name=name,
            template=request.template,
            input_variables=request.input_variables,
            description=request.description,
            category=request.category,
        )
        if not success:
            raise HTTPException(status_code=500, detail="编辑失败")

        updated = pm.get_template(name)
        return schemas.CustomPromptInfo(
            name=updated.name,
            description=updated.description or "",
            category=updated.category or "default",
            input_variables=updated.input_variables or [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 自定义提示词格式化 API ====================

@router.get("/knowledge/status", response_model=schemas.KnowledgeStatusResponse, summary="知识库状态")
async def knowledge_status():
    """获取知识库状态信息"""
    try:
        kb = _get_knowledge_base()
        return schemas.KnowledgeStatusResponse(
            document_count=kb.get_document_count(),
            collection_name=kb.collection_name,
            persist_directory=kb.persist_directory,
            embedding_model=str(type(kb.embedding_model).__name__) if kb.embedding_model else "未配置",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/search", response_model=schemas.KnowledgeSearchResponse, summary="搜索知识库")
async def knowledge_search(request: schemas.KnowledgeSearchRequest):
    """在知识库中搜索相关内容"""
    try:
        kb = _get_knowledge_base()
        docs = kb.similarity_search(query=request.query, k=request.k)

        results = []
        for doc in docs:
            results.append(schemas.KnowledgeSearchResult(
                content=doc.page_content,
                metadata=doc.metadata,
            ))

        return schemas.KnowledgeSearchResponse(results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/upload", response_model=schemas.KnowledgeUploadResponse, summary="上传文档到知识库")
async def knowledge_upload(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    """上传文件到知识库（支持 pdf, txt, md, yaml 等格式），可附带元数据（JSON 字符串）"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        allowed_extensions = {".pdf", ".txt", ".md", ".yaml", ".yml", ".json", ".csv"}
        ext = Path(file.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {ext}，支持: {', '.join(allowed_extensions)}",
            )

        temp_dir = Path("/tmp/knowledge_uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / file.filename

        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        parsed_metadata = None
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
                if not isinstance(parsed_metadata, dict):
                    raise ValueError("metadata must be a JSON object")
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"元数据格式错误: {str(e)}")

        kb = _get_knowledge_base()
        doc_ids = kb.add_document_from_path(str(temp_path), metadata=parsed_metadata)

        return schemas.KnowledgeUploadResponse(
            file_name=file.filename,
            document_ids=doc_ids,
            chunk_count=len(doc_ids),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/documents", response_model=schemas.KnowledgeDocumentListResponse, summary="获取文档列表")
async def knowledge_documents(limit: int = 50, offset: int = 0):
    """获取知识库中文档列表（分页）"""
    try:
        kb = _get_knowledge_base()
        result = kb.get_documents(limit=limit, offset=offset)

        documents = []
        for i, doc_id in enumerate(result.get("ids", [])):
            content = result["documents"][i] if i < len(result["documents"]) else ""
            metadata = result["metadatas"][i] if i < len(result["metadatas"]) else {}
            documents.append(schemas.KnowledgeDocumentInfo(
                id=doc_id,
                content=content[:200],
                metadata=metadata,
            ))

        return schemas.KnowledgeDocumentListResponse(
            documents=documents,
            total=result["total"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/documents/{doc_id}", summary="删除单个文档")
async def knowledge_delete_document(doc_id: str):
    """删除知识库中指定 ID 的文档"""
    try:
        kb = _get_knowledge_base()
        kb.delete_documents([doc_id])
        return {"message": f"文档 {doc_id} 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/clear", summary="清空知识库")
async def knowledge_clear():
    """清空整个知识库"""
    try:
        kb = _get_knowledge_base()
        kb.clear()
        return {"message": "知识库已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 知识库管理 API ====================

@router.get("/knowledge/files", response_model=schemas.KnowledgeFileListResponse, summary="获取知识库文件列表")
async def knowledge_files():
    """获取按文件分组的文件列表"""
    try:
        kb = _get_knowledge_base()
        files = kb.get_files()
        file_list = [
            schemas.KnowledgeFileInfo(source=f["source"], chunk_count=f["chunk_count"])
            for f in files
        ]
        return schemas.KnowledgeFileListResponse(files=file_list, total=len(file_list))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/files/{source}", response_model=schemas.KnowledgeFileDetailResponse, summary="获取文件文档块详情")
async def knowledge_file_detail(source: str):
    """获取指定文件的所有文档块"""
    try:
        kb = _get_knowledge_base()
        result = kb.get_file_chunks(source)
        documents = []
        for i, doc_id in enumerate(result.get("ids", [])):
            meta = (result.get("metadatas") or [{}] * len(result["ids"]))[i] or {}
            documents.append(schemas.KnowledgeDocumentInfo(
                id=doc_id,
                content=(result.get("documents") or [""] * len(result["ids"]))[i],
                metadata=meta,
            ))
        return schemas.KnowledgeFileDetailResponse(
            source=source,
            chunk_count=len(documents),
            documents=documents,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/files/{source}", response_model=schemas.KnowledgeDeleteFileResponse, summary="删除文件（所有文档块）")
async def knowledge_delete_file(source: str):
    """删除指定文件的所有文档块"""
    try:
        kb = _get_knowledge_base()
        deleted = kb.delete_file(source)
        return schemas.KnowledgeDeleteFileResponse(
            source=source,
            deleted_chunks=deleted,
            message=f"文件 '{source}' 已删除，共删除 {deleted} 个文档块",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 自定义提示词管理 API ====================

@router.get("/custom-prompts", response_model=schemas.CustomPromptListResponse, summary="获取自定义提示词列表")
async def list_custom_prompts():
    """获取所有自定义提示词模板"""
    try:
        pm = _get_prompt_manager()
        templates = pm.list_templates()

        prompt_list = []
        for t in templates:
            prompt_list.append(schemas.CustomPromptInfo(
                name=t.name,
                description=t.description or "",
                category=t.category or "default",
                input_variables=t.input_variables or [],
            ))

        return schemas.CustomPromptListResponse(prompts=prompt_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custom-prompts/{name}", response_model=schemas.CustomPromptInfo, summary="获取自定义提示词详情")
async def get_custom_prompt(name: str):
    """获取指定自定义提示词模板的详情"""
    try:
        pm = _get_prompt_manager()
        template = pm.get_template(name)
        if not template:
            raise HTTPException(status_code=404, detail=f"自定义提示词 '{name}' 不存在")

        return schemas.CustomPromptInfo(
            name=template.name,
            description=template.description or "",
            category=template.category or "default",
            input_variables=template.input_variables or [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom-prompts", status_code=201, summary="创建自定义提示词")
async def create_custom_prompt(request: schemas.CreateCustomPromptRequest):
    """创建新的自定义提示词模板"""
    try:
        pm = _get_prompt_manager()
        success = pm.add_template(
            name=request.name,
            template_text=request.template,
            description=request.description,
            category=request.category,
            input_variables=request.input_variables,
        )
        if not success:
            raise HTTPException(status_code=409, detail=f"自定义提示词 '{request.name}' 已存在")

        return {"message": f"自定义提示词 '{request.name}' 已创建", "name": request.name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/custom-prompts/{name}", summary="编辑自定义提示词")
async def edit_custom_prompt(name: str, request: schemas.CreateCustomPromptRequest):
    """编辑自定义提示词模板"""
    try:
        pm = _get_prompt_manager()
        template = pm.get_template(name)
        if not template:
            raise HTTPException(status_code=404, detail=f"自定义提示词 '{name}' 不存在")

        pm.add_template(
            name=request.name,
            template_text=request.template,
            description=request.description,
            category=request.category,
            input_variables=request.input_variables,
        )

        return {"message": f"自定义提示词 '{name}' 已更新", "name": request.name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/custom-prompts/{name}", summary="删除自定义提示词")
async def delete_custom_prompt(name: str):
    """删除自定义提示词模板"""
    try:
        pm = _get_prompt_manager()
        success = pm.delete_template(name)
        if not success:
            raise HTTPException(status_code=404, detail=f"自定义提示词 '{name}' 不存在或不可删除")
        return {"message": f"自定义提示词 '{name}' 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom-prompts/format", response_model=schemas.FormatPromptResponse, summary="格式化提示词")
async def format_prompt(request: schemas.FormatPromptRequest):
    """使用变量值格式化指定的提示词模板"""
    try:
        pm = _get_prompt_manager()
        template = pm.get_template(request.prompt_name)
        if not template:
            raise HTTPException(status_code=404, detail=f"提示词 '{request.prompt_name}' 不存在")

        formatted = pm.format_prompt(request.prompt_name, **request.variables)

        return schemas.FormatPromptResponse(
            prompt_name=request.prompt_name,
            formatted=formatted,
            variables=list(request.variables.keys()),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/{name}", response_model=schemas.TemplateInfoResponse, summary="获取模板信息")
async def get_prompt_template(name: str):
    """获取指定模板的详细信息（变量列表、原始内容等）"""
    try:
        pm = _get_prompt_manager()
        data = pm.get_template_data(name)
        if not data:
            raise HTTPException(status_code=404, detail=f"模板 '{name}' 不存在")
        return schemas.TemplateInfoResponse(
            name=data.name,
            description=data.description or "",
            category=data.category or "",
            input_variables=data.input_variables or [],
            template_content=data.template or "",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/generate/stream", summary="基于模板流式生成内容")
async def generate_from_template_stream(request: schemas.GeneratePromptRequest):
    """使用指定模板和变量值，流式生成内容"""
    agent = _get_agent()
    pm = _get_prompt_manager()

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            formatted = pm.format_prompt(request.template_name, **request.variables)
            if not formatted:
                yield {"event": "error", "data": f"模板 '{request.template_name}' 格式化失败"}
                return

            full_text = ""
            async for chunk in agent.stream(input=formatted):
                full_text += chunk
                yield {"event": "chunk", "data": chunk}
            yield {"event": "done", "data": full_text}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


# ==================== 状态信息 API ====================

@router.get("/status", response_model=schemas.AgentStatusResponse, summary="获取 Agent 状态")
async def agent_status():
    """获取 Agent 的当前状态信息"""
    try:
        agent = _get_agent()
        manager = agent.model_manager

        available = manager.get_available_models()
        current_model = manager.get_current_model()
        c_model = current_model.value if hasattr(current_model, "value") else str(current_model)
        avail_models = [m.value if hasattr(m, "value") else str(m) for m in available]

        history = agent.get_conversation_history()

        try:
            kb_count = agent.knowledge_base.get_document_count() if agent.knowledge_base else 0
        except Exception:
            kb_count = 0

        return schemas.AgentStatusResponse(
            current_model=c_model,
            available_models=avail_models,
            current_system_prompt=agent.system_prompt_name,
            conversation_length=len(history) if history else 0,
            knowledge_base_count=kb_count,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=schemas.HistoryResponse, summary="获取对话历史")
async def conversation_history():
    """获取当前会话的对话历史"""
    try:
        agent = _get_agent()
        history = agent.get_conversation_history()

        messages = []
        for msg in history:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": msg.get("content", "")})

        return schemas.HistoryResponse(messages=messages, total=len(messages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/clear", summary="清空对话记忆")
async def clear_memory():
    """清空当前会话的对话记忆"""
    try:
        agent = _get_agent()
        agent.clear_memory()
        return {"message": "对话记忆已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))