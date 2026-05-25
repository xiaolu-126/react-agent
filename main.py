#!/usr/bin/env python3
"""
LangGraph 智能 Agent - 主程序入口
基于 Click 的命令行界面
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from functools import wraps

import click
from dotenv import load_dotenv

# 导入项目模块
from src.agent.react_agent import ReActAgent
from src.utils.config import get_config


class ColorFormatter:
    """彩色输出格式化器"""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def header(cls, text: str) -> str:
        return f"{cls.HEADER}{text}{cls.ENDC}"

    @classmethod
    def info(cls, text: str) -> str:
        return f"{cls.OKCYAN}{text}{cls.ENDC}"

    @classmethod
    def success(cls, text: str) -> str:
        return f"{cls.OKGREEN}{text}{cls.ENDC}"

    @classmethod
    def warning(cls, text: str) -> str:
        return f"{cls.WARNING}{text}{cls.ENDC}"

    @classmethod
    def error(cls, text: str) -> str:
        return f"{cls.FAIL}{text}{cls.ENDC}"

    @classmethod
    def bold(cls, text: str) -> str:
        return f"{cls.BOLD}{text}{cls.ENDC}"


def print_header(title: str):
    """打印带边框的标题"""
    width = 80
    click.echo(ColorFormatter.header("=" * width))
    click.echo(ColorFormatter.header(title.center(width)))
    click.echo(ColorFormatter.header("=" * width))


def handle_exceptions(func):
    """异常处理装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            click.echo("\n" + ColorFormatter.warning("操作已取消"))
            return
        except Exception as e:
            click.echo(ColorFormatter.error(f"错误: {str(e)}"))
            sys.exit(1)

    return wrapper


def ensure_config():
    """确保配置文件存在"""
    config_dir = Path("config")
    env_example = config_dir / ".env.example"
    env_file = config_dir / ".env"
    
    if not env_file.exists() and env_example.exists():
        click.echo(ColorFormatter.warning("未找到配置文件，正在创建..."))
        import shutil
        shutil.copy(env_example, env_file)
        click.echo(ColorFormatter.success(f"✓ 已创建 {env_file}"))
        click.echo(ColorFormatter.info("请编辑该文件填入您的 API 密钥\n"))
    elif not env_file.exists():
        click.echo(ColorFormatter.warning("未找到 .env.example 文件，请手动创建配置文件"))


# 全局 Agent 实例
_agent: Optional[ReActAgent] = None

def get_agent() -> ReActAgent:
    """获取或初始化 Agent 实例"""
    global _agent
    if _agent is None:
        get_config()
        _agent = ReActAgent()
    return _agent

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    LangGraph 智能 Agent - 专业的主播推荐助手

    提供交互式聊天、文档管理和模型切换等功能。
    """
    ensure_config()
    get_config()


@cli.command()
@handle_exceptions
def chat():
    """
    交互式聊天模式

    进入与 Agent 的持续对话，可以随时退出。
    """
    print_header("交互式聊天模式")
    click.echo(ColorFormatter.info("输入 'quit' 或 'exit' 退出，'clear' 清空对话历史\n"))
    
    agent = get_agent()
    click.echo(ColorFormatter.success("Agent 已就绪！"))
    click.echo(ColorFormatter.info("有什么可以帮助您的吗？\n"))
    
    while True:
        try:
            user_input = click.prompt(ColorFormatter.bold("> 用户"), prompt_suffix=": ")
        except click.exceptions.Abort:
            click.echo("\n")
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            click.echo(ColorFormatter.info("再见！"))
            break
        
        if user_input.lower() == 'clear':
            agent.clear_memory()
            click.echo(ColorFormatter.success("对话历史已清空"))
            continue
        
        if not user_input.strip():
            continue
        
        click.echo()
        click.echo(ColorFormatter.bold("> Agent") + ": ", nl=False)
        
        # 调用 Agent 流式响应
        try:
            for chunk in agent.stream(user_input):
                click.echo(chunk, nl=False)
            click.echo("\n")
        except Exception as e:
            click.echo(ColorFormatter.error(f"\n出错了: {str(e)}"))
            click.echo(ColorFormatter.info("请确保已在 .env 文件中配置了正确的 API 密钥"))
            click.echo()


@cli.command()
@click.argument('streamer_name')
@click.option('--preferences', '-p', help='用户偏好描述')
@click.option('--stream/--no-stream', default=True, help='是否使用流式输出（默认：流式）')
@handle_exceptions
def generate(streamer_name: str, preferences: Optional[str], stream: bool):
    """
    生成主播推荐理由

    根据主播名称生成详细的推荐理由。

    STREAMER_NAME: 主播昵称或名称
    """
    print_header("生成主播推荐理由")
    
    click.echo(ColorFormatter.info(f"主播: {streamer_name}"))
    if preferences:
        click.echo(ColorFormatter.info(f"用户偏好: {preferences}"))
    click.echo()
    
    agent = get_agent()
    
    # 构建用户输入
    user_input = f"请给我推荐主播：{streamer_name}"
    if preferences:
        user_input += f"\n用户偏好：{preferences}"
    
    click.echo(ColorFormatter.bold("> Agent 推荐理由") + ":\n")
    
    try:
        if stream:
            # 流式输出
            for chunk in agent.stream(user_input, streamer_name=streamer_name, user_preferences=preferences):
                click.echo(chunk, nl=False)
            click.echo()
        else:
            # 非流式输出
            response = agent.run(user_input, streamer_name=streamer_name, user_preferences=preferences)
            click.echo(response)
    except Exception as e:
        click.echo(ColorFormatter.error(f"\n出错了: {str(e)}"))
        click.echo(ColorFormatter.info("请确保已在 .env 文件中配置了正确的 API 密钥"))
    click.echo()


@cli.command('upload-docs')
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='是否递归遍历目录（默认：是）')
@click.option('--metadata', '-m', multiple=True, help='附加元数据，格式 key=value')
@handle_exceptions
def upload_docs(path: str, recursive: bool, metadata: List[str]):
    """
    上传文档到知识库

    支持单个文件或整个目录的文档上传。

    PATH: 文件或目录路径
    """
    from src.tools.knowledge_base import KnowledgeBase
    from src.tools.document_loader import load_documents
    
    print_header("上传文档到知识库")
    
    path_obj = Path(path)
    
    # 解析元数据
    meta_dict = {}
    for item in metadata:
        if '=' in item:
            key, value = item.split('=', 1)
            meta_dict[key.strip()] = value.strip()
    
    # 初始化知识库
    kb = KnowledgeBase()
    
    if path_obj.is_file():
        click.echo(ColorFormatter.info(f"上传文件: {path}"))
        docs = load_documents(str(path_obj))
        kb.add_documents(docs, metadata=meta_dict)
        click.echo(ColorFormatter.success(f"✓ 文件已成功添加到知识库，共 {len(docs)} 个文档片段"))
    elif path_obj.is_dir():
        click.echo(ColorFormatter.info(f"上传目录: {path}"))
        if recursive:
            click.echo(ColorFormatter.info("模式: 递归遍历"))
        
        all_docs = []
        file_patterns = ["*.pdf", "*.txt", "*.md"]
        for pattern in file_patterns:
            if recursive:
                files = list(path_obj.rglob(pattern))
            else:
                files = list(path_obj.glob(pattern))
            
            for file_path in files:
                try:
                    docs = load_documents(str(file_path))
                    all_docs.extend(docs)
                except Exception as e:
                    click.echo(ColorFormatter.warning(f"  跳过文件 {file_path}: {str(e)}"))
        
        if all_docs:
            kb.add_documents(all_docs, metadata=meta_dict)
            click.echo(ColorFormatter.success(f"✓ 目录中的文件已成功添加到知识库，共 {len(all_docs)} 个文档片段"))
        else:
            click.echo(ColorFormatter.warning("未找到可处理的文件"))
    
    if meta_dict:
        click.echo(ColorFormatter.info(f"\n附加元数据: {meta_dict}"))
    
    click.echo(ColorFormatter.success(f"\n知识库已更新"))


@cli.command('list-models')
@handle_exceptions
def list_models():
    """
    列出所有可用模型

    显示已配置的所有模型类型及其状态。
    """
    from src.models.model_manager import ModelManager
    
    print_header("可用模型列表")
    
    manager = ModelManager()
    available_models = manager.get_available_models()
    current_model = manager.get_current_model()
    
    model_names = {
        "openai": "GPT-4 / GPT-3.5",
        "anthropic": "Claude 3",
        "dashscope": "通义千问",
        "qianfan": "文心一言",
        "deepseek": "DeepSeek",
    }
    
    for model_type in available_models:
        model_id = model_type.value if hasattr(model_type, 'value') else str(model_type)
        model_name = model_names.get(model_id, model_id)
        current_model_id = current_model.value if hasattr(current_model, 'value') else str(current_model)
        if model_id == current_model_id:
            click.echo(ColorFormatter.success(f"  • {model_id} - {model_name} [当前使用]"))
        else:
            click.echo(ColorFormatter.info(f"  - {model_id} - {model_name}"))
    
    click.echo()
    click.echo(ColorFormatter.info("使用 'switch-model' 命令切换模型"))


@cli.command('switch-model')
@click.argument('model_type', type=click.Choice(['openai', 'anthropic', 'dashscope', 'qianfan', 'deepseek'], case_sensitive=False))
@handle_exceptions
def switch_model(model_type: str):
    """
    切换当前使用的模型

    MODEL_TYPE: 模型类型（openai/anthropic/dashscope/qianfan/deepseek）
    """
    print_header("切换模型")
    
    agent = get_agent()
    agent.switch_model(model_type.lower())
    
    click.echo(ColorFormatter.success(f"✓ 已切换到模型: {model_type.lower()}"))
    click.echo(ColorFormatter.info("注意：请确保已在配置文件中设置了对应模型的 API 密钥"))


@cli.command()
@handle_exceptions
def status():
    """
    查看当前状态

    显示配置、模型和知识库等信息。
    """
    from src.models.model_manager import ModelManager
    
    print_header("系统状态")
    
    config_dir = Path("config")
    env_file = config_dir / ".env"
    
    click.echo(ColorFormatter.bold("配置文件:"))
    if env_file.exists():
        click.echo(f"  位置: {env_file.absolute()}")
    else:
        click.echo(ColorFormatter.warning("  未找到 .env 文件"))
    
    click.echo()
    click.echo(ColorFormatter.bold("模型信息:"))
    manager = ModelManager()
    click.echo(f"  当前使用: {ColorFormatter.success(manager.current_model_type)}")
    click.echo(f"  可用模型: {', '.join(manager.get_available_models())}")
    
    click.echo()
    click.echo(ColorFormatter.bold("知识库:"))
    chroma_dir = Path("data") / "chroma_db"
    if chroma_dir.exists():
        click.echo(f"  状态: 已初始化")
        click.echo(f"  持久化路径: {chroma_dir.absolute()}")
    else:
        click.echo(ColorFormatter.warning("  知识库尚未初始化"))
    
    click.echo()


def main():
    """程序入口"""
    cli()


if __name__ == "__main__":
    main()
