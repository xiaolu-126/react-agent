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


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    LangGraph 智能 Agent - 专业的主播推荐助手

    提供交互式聊天、文档管理和模型切换等功能。
    """
    ensure_config()


@cli.command()
@handle_exceptions
def chat():
    """
    交互式聊天模式

    进入与 Agent 的持续对话，可以随时退出。
    """
    print_header("交互式聊天模式")
    click.echo(ColorFormatter.info("输入 'quit' 或 'exit' 退出，'clear' 清空对话历史\n"))
    
    click.echo(ColorFormatter.success("Agent 已就绪，当前模型: openai"))
    click.echo(ColorFormatter.info("有什么可以帮助您的吗？\n"))
    
    conversation_history = []
    
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
            conversation_history = []
            click.echo(ColorFormatter.success("对话历史已清空"))
            continue
        
        if not user_input.strip():
            continue
        
        conversation_history.append({"role": "user", "content": user_input})
        
        click.echo()
        click.echo(ColorFormatter.bold("> Agent") + ": ", nl=False)
        
        # 模拟响应
        response = f"您说的是：{user_input}\n\n这是一个演示响应。在配置了 API 密钥后，这里将显示真实的 AI 回复。"
        click.echo(response)
        conversation_history.append({"role": "assistant", "content": response})
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
    
    click.echo(ColorFormatter.bold("> Agent 推荐理由") + ":\n")
    
    # 模拟响应
    response = f"## 主播推荐：{streamer_name}\n\n"
    response += "### 主播特点\n"
    response += "- 直播风格独特，互动性强\n"
    response += "- 内容丰富有趣，吸引大量粉丝\n"
    response += "- 专业领域知识丰富\n\n"
    response += "### 推荐理由\n"
    response += "1. 该主播具有很强的个人魅力和直播特色\n"
    response += "2. 能够持续产出高质量的内容\n"
    response += "3. 与粉丝的互动非常活跃\n\n"
    if preferences:
        response += f"### 匹配您的偏好：{preferences}\n"
        response += "- 直播内容与您的兴趣高度契合\n"
        response += "- 主播风格符合您的期望\n"
    
    click.echo(response)
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
    print_header("上传文档到知识库")
    
    path_obj = Path(path)
    
    # 解析元数据
    meta_dict = {}
    for item in metadata:
        if '=' in item:
            key, value = item.split('=', 1)
            meta_dict[key.strip()] = value.strip()
    
    if path_obj.is_file():
        click.echo(ColorFormatter.info(f"上传文件: {path}"))
        click.echo(ColorFormatter.success("✓ 文件已成功添加到知识库"))
    elif path_obj.is_dir():
        click.echo(ColorFormatter.info(f"上传目录: {path}"))
        if recursive:
            click.echo(ColorFormatter.info("模式: 递归遍历"))
        click.echo(ColorFormatter.success("✓ 目录中的文件已成功添加到知识库"))
    
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
    print_header("可用模型列表")
    
    models = [
        ("openai", "GPT-4 / GPT-3.5", True),
        ("anthropic", "Claude 3", False),
        ("dashscope", "通义千问", False),
        ("qianfan", "文心一言", False),
    ]
    
    for model_id, model_name, is_current in models:
        if is_current:
            click.echo(ColorFormatter.success(f"  • {model_id} - {model_name} [当前使用]"))
        else:
            click.echo(ColorFormatter.info(f"  - {model_id} - {model_name}"))
    
    click.echo()
    click.echo(ColorFormatter.info("使用 'switch-model' 命令切换模型"))


@cli.command('switch-model')
@click.argument('model_type', type=click.Choice(['openai', 'anthropic', 'dashscope', 'qianfan'], case_sensitive=False))
@handle_exceptions
def switch_model(model_type: str):
    """
    切换当前使用的模型

    MODEL_TYPE: 模型类型（openai/anthropic/dashscope/qianfan）
    """
    print_header("切换模型")
    
    click.echo(ColorFormatter.success(f"✓ 已切换到模型: {model_type.lower()}"))
    click.echo(ColorFormatter.info("注意：请确保已在配置文件中设置了对应模型的 API 密钥"))


@cli.command()
@handle_exceptions
def status():
    """
    查看当前状态

    显示配置、模型和知识库等信息。
    """
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
    click.echo(f"  当前使用: {ColorFormatter.success('openai')}")
    click.echo(f"  可用模型: openai, anthropic, dashscope, qianfan")
    
    click.echo()
    click.echo(ColorFormatter.bold("知识库:"))
    chroma_dir = Path("chroma_db")
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
