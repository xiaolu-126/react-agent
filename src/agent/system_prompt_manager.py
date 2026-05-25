import os
from pathlib import Path
from typing import Dict, List, Optional, TypedDict
import json


class SystemPromptMeta(TypedDict):
    """系统提示词元数据类型"""
    name: str
    file: str
    description: str
    category: str


class SystemPromptManager:
    """系统提示词管理器
    
    管理 .md 格式的系统提示词文件，支持自定义配置。
    
    文件结构：
    config/system_prompts/
    ├── system_prompts.json          # 索引文件（元数据）
    ├── system_prompts.example.json  # 索引示例
    ├── streamer_recommender.md      # 主播推荐专家
    ├── general_assistant.md         # 通用助手
    ├── code_expert.md               # 代码专家
    └── my_custom.md                 # 用户自定义
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化系统提示词管理器
        
        Args:
            config_dir: 配置目录，默认 config/system_prompts
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config" / "system_prompts"
        
        self.config_dir = config_dir
        self.index_file = self.config_dir / "system_prompts.json"
        self.index: Dict[str, SystemPromptMeta] = {}
        
        self._ensure_config_dir()
        self._load_index()
    
    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self) -> None:
        """加载系统提示词索引文件"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"加载系统提示词索引失败: {e}")
        
        # 如果索引为空，加载默认提示词
        if not self.index:
            self._load_default_index()
    
    def _load_default_index(self) -> None:
        """加载默认系统提示词索引"""
        default_index = {
            "streamer_recommender": {
                "name": "streamer_recommender",
                "file": "streamer_recommender.md",
                "description": "主播推荐专家 - 用于生成主播推荐理由",
                "category": "recommendation"
            },
            "general_assistant": {
                "name": "general_assistant",
                "file": "general_assistant.md",
                "description": "通用AI助手 - 日常对话和问题解答",
                "category": "general"
            },
            "code_expert": {
                "name": "code_expert",
                "file": "code_expert.md",
                "description": "代码专家 - 编程相关问题解答",
                "category": "code"
            }
        }
        
        self.index = default_index
        self._save_index()
    
    def _save_index(self) -> None:
        """保存系统提示词索引文件"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def get_system_prompt(self, name: str = "streamer_recommender") -> str:
        """
        获取系统提示词内容
        
        先从索引获取 .md 文件名，再从文件读取内容。
        
        Args:
            name: 系统提示词名称
            
        Returns:
            系统提示词内容
        """
        if name not in self.index:
            raise ValueError(f"系统提示词 '{name}' 不存在")
        
        meta = self.index[name]
        md_path = self.config_dir / meta["file"]
        
        if not md_path.exists():
            raise FileNotFoundError(f"系统提示词文件不存在: {md_path}")
        
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def list_prompts(self, category: Optional[str] = None) -> List[SystemPromptMeta]:
        """
        列出所有系统提示词
        
        Args:
            category: 可选，按分类筛选
            
        Returns:
            系统提示词元数据列表
        """
        prompts = list(self.index.values())
        if category:
            prompts = [p for p in prompts if p["category"] == category]
        return prompts
    
    def add_prompt(self, name: str, file_content: str, description: str = "", category: str = "custom") -> bool:
        """
        添加自定义系统提示词
        
        会在索引中添加记录，并创建对应的 .md 文件。
        
        Args:
            name: 系统提示词名称
            file_content: .md 文件内容
            description: 描述
            category: 分类
            
        Returns:
            是否添加成功
        """
        if name in self.index:
            print(f"系统提示词 '{name}' 已存在")
            return False
        
        file_name = f"{name}.md"
        md_path = self.config_dir / file_name
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(file_content.strip() + "\n")
        
        self.index[name] = {
            "name": name,
            "file": file_name,
            "description": description,
            "category": category,
        }
        
        self._save_index()
        return True
    
    def edit_prompt(self, name: str, file_content: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None) -> bool:
        """
        编辑系统提示词
        
        可更新 .md 文件内容和索引元数据。
        
        Args:
            name: 系统提示词名称
            file_content: 新的 .md 文件内容
            description: 新的描述
            category: 新的分类
            
        Returns:
            是否编辑成功
        """
        if name not in self.index:
            print(f"系统提示词 '{name}' 不存在")
            return False
        
        meta = self.index[name]
        
        if file_content is not None:
            md_path = self.config_dir / meta["file"]
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(file_content.strip() + "\n")
        
        if description is not None:
            self.index[name]["description"] = description
        
        if category is not None:
            self.index[name]["category"] = category
        
        self._save_index()
        return True
    
    def delete_prompt(self, name: str) -> bool:
        """
        删除自定义系统提示词
        
        Args:
            name: 系统提示词名称
            
        Returns:
            是否删除成功
        """
        default_names = ["streamer_recommender", "general_assistant", "code_expert"]
        if name in default_names:
            print(f"不能删除预设系统提示词 '{name}'")
            return False
        
        if name not in self.index:
            print(f"系统提示词 '{name}' 不存在")
            return False
        
        # 删除对应的 .md 文件
        meta = self.index[name]
        md_path = self.config_dir / meta["file"]
        if md_path.exists():
            md_path.unlink()
        
        del self.index[name]
        self._save_index()
        return True
    
    def get_prompt_file_path(self, name: str) -> Optional[Path]:
        """
        获取系统提示词 .md 文件的路径
        
        Args:
            name: 系统提示词名称
            
        Returns:
            .md 文件的路径
        """
        if name not in self.index:
            return None
        
        return self.config_dir / self.index[name]["file"]


if __name__ == "__main__":
    # 使用示例
    manager = SystemPromptManager()
    
    print("=== 可用系统提示词 ===")
    for prompt in manager.list_prompts():
        print(f"  [{prompt['category']}] {prompt['name']}: {prompt['description']}")
    
    print("\n=== 主播推荐专家 ===")
    print(manager.get_system_prompt("streamer_recommender"))
    
    print("\n=== 添加自定义系统提示词 ===")
    manager.add_prompt(
        name="my_agent",
        file_content="你是一位我的专属助手。\n\n请友好地帮助我。",
        description="我的专属助手",
        category="custom"
    )
    print(f"  已添加: my_agent")
    print(f"  内容: {manager.get_system_prompt('my_agent')}")
    
    # 编辑
    manager.edit_prompt("my_agent", file_content="你是一位升级版的专属助手。\n\n请热情地帮助我。")
    print(f"  编辑后: {manager.get_system_prompt('my_agent')}")
    
    # 删除
    manager.delete_prompt("my_agent")
    print(f"  已删除: my_agent")