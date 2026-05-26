from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import yaml
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


from src.utils.logger import get_logger

logger = get_logger("agent")


class PromptTemplateData(BaseModel):
    """提示词模板数据模型"""
    name: str = Field(..., description="模板名称")
    template: str = Field(..., description="提示词模板内容")
    input_variables: List[str] = Field(default_factory=list, description="输入变量列表")
    description: str = Field(default="", description="模板描述")
    category: str = Field(default="default", description="模板分类")


class PromptManager:
    """
    提示词管理器
    
    功能：
    - 管理预设提示词模板
    - 支持自定义、编辑和保存提示词
    - 支持 JSON/YAML 格式存储
    - 提供提示词调试功能
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化提示词管理器
        
        Args:
            config_dir: 配置目录路径，默认为项目根目录下的 config/prompts
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config" / "prompts"
        
        self.config_dir = config_dir
        self.custom_prompts_file = self.config_dir / "custom_prompts.json"
        self.templates: Dict[str, PromptTemplateData] = {}
        
        self._ensure_config_dir()
        self._load_default_prompts()
        self._load_custom_prompts()
    
    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_default_prompts(self) -> None:
        """加载预设提示词模板"""
        default_prompts = [
            PromptTemplateData(
                name="streamer_recommendation",
                category="recommendation",
                description="生成主播推荐理由",
                input_variables=["streamer_name", "streamer_tags", "streamer_content", "user_preferences"],
                template="""你是一位专业的主播推荐专家。请根据以下信息生成主播推荐理由。

主播信息：
- 姓名：{streamer_name}
- 标签：{streamer_tags}
- 内容特点：{streamer_content}

用户偏好：{user_preferences}

请生成一段有说服力的推荐理由，突出主播的特色，并说明为什么这位主播适合该用户。推荐理由应该积极、友好、吸引人。

推荐理由："""
            ),
            PromptTemplateData(
                name="content_summary",
                category="content",
                description="内容摘要生成",
                input_variables=["content"],
                template="""请为以下内容生成简洁的摘要：

{content}

摘要："""
            ),
            PromptTemplateData(
                name="question_answering",
                category="qa",
                description="问答系统提示词",
                input_variables=["context", "question"],
                template="""基于以下上下文回答问题：

上下文：
{context}

问题：{question}

请基于提供的上下文回答问题。如果上下文中没有相关信息，请说明无法回答。

回答："""
            )
        ]
        
        for prompt in default_prompts:
            self.templates[prompt.name] = prompt
    
    def _load_custom_prompts(self) -> None:
        """加载自定义提示词模板"""
        if self.custom_prompts_file.exists():
            try:
                with open(self.custom_prompts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for name, prompt_data in data.items():
                        self.templates[name] = PromptTemplateData(**prompt_data)
            except Exception as e:
                logger.error("加载自定义提示词失败: %s", e)
    
    def _save_custom_prompts(self) -> None:
        """保存自定义提示词模板"""
        custom_templates = {
            name: prompt.model_dump()
            for name, prompt in self.templates.items()
            if name not in self._get_default_template_names()
        }
        
        with open(self.custom_prompts_file, "w", encoding="utf-8") as f:
            json.dump(custom_templates, f, ensure_ascii=False, indent=2)
    
    def _get_default_template_names(self) -> List[str]:
        """获取预设模板名称列表"""
        return ["streamer_recommendation", "content_summary", "question_answering"]
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取 LangChain PromptTemplate 对象
        
        Args:
            name: 模板名称
            
        Returns:
            PromptTemplate 对象，如果不存在则返回 None
        """
        if name not in self.templates:
            return None
        
        prompt_data = self.templates[name]
        return PromptTemplate(
            template=prompt_data.template,
            input_variables=prompt_data.input_variables
        )
    
    def get_template_data(self, name: str) -> Optional[PromptTemplateData]:
        """
        获取提示词模板数据
        
        Args:
            name: 模板名称
            
        Returns:
            PromptTemplateData 对象，如果不存在则返回 None
        """
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplateData]:
        """
        列出所有提示词模板
        
        Args:
            category: 分类筛选，可选
            
        Returns:
            提示词模板数据列表
        """
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    def add_template(
        self,
        name: str,
        template: str,
        input_variables: Optional[List[str]] = None,
        description: str = "",
        category: str = "default"
    ) -> bool:
        """
        添加自定义提示词模板
        
        Args:
            name: 模板名称
            template: 模板内容
            input_variables: 输入变量列表
            description: 模板描述
            category: 模板分类
            
        Returns:
            是否添加成功
        """
        if name in self.templates:
            logger.warning("模板 %s 已存在，请使用 edit_template 修改", name)
            return False
        
        if input_variables is None:
            input_variables = self._extract_variables(template)
        
        self.templates[name] = PromptTemplateData(
            name=name,
            template=template,
            input_variables=input_variables,
            description=description,
            category=category
        )
        
        self._save_custom_prompts()
        return True
    
    def edit_template(
        self,
        name: str,
        template: Optional[str] = None,
        input_variables: Optional[List[str]] = None,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> bool:
        """
        编辑提示词模板
        
        Args:
            name: 模板名称
            template: 新的模板内容
            input_variables: 新的输入变量列表
            description: 新的描述
            category: 新的分类
            
        Returns:
            是否编辑成功
        """
        if name not in self.templates:
            logger.warning("模板 %s 不存在，编辑失败", name)
            return False
        
        prompt_data = self.templates[name]
        
        if template is not None:
            prompt_data.template = template
            if input_variables is None:
                input_variables = self._extract_variables(template)
        
        if input_variables is not None:
            prompt_data.input_variables = input_variables
        
        if description is not None:
            prompt_data.description = description
        
        if category is not None:
            prompt_data.category = category
        
        self._save_custom_prompts()
        return True
    
    def delete_template(self, name: str) -> bool:
        """
        删除自定义提示词模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        if name in self._get_default_template_names():
            logger.warning("不能删除预设模板 %s", name)
            return False

        if name not in self.templates:
            logger.warning("模板 %s 不存在，删除失败", name)
            return False
        
        del self.templates[name]
        self._save_custom_prompts()
        return True
    
    def format_prompt(self, template_name: str, **kwargs: Any) -> Optional[str]:
        """
        格式化提示词

        Args:
            template_name: 模板名称
            **kwargs: 模板变量值

        Returns:
            格式化后的提示词，如果失败则返回 None
        """
        template = self.get_template(template_name)
        if template is None:
            return None

        try:
            return template.format(**kwargs)
        except Exception as e:
            logger.error("格式化提示词失败: %s", e)
            return None
    
    def debug_prompt(self, name: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        调试提示词，显示完整信息
        
        Args:
            name: 模板名称
            **kwargs: 模板变量值
            
        Returns:
            调试信息字典，包含模板信息、变量、格式化结果等
        """
        prompt_data = self.get_template_data(name)
        if prompt_data is None:
            return None
        
        formatted_prompt = self.format_prompt(name, **kwargs)
        
        return {
            "template_name": prompt_data.name,
            "description": prompt_data.description,
            "category": prompt_data.category,
            "template_content": prompt_data.template,
            "input_variables": prompt_data.input_variables,
            "provided_variables": list(kwargs.keys()),
            "missing_variables": [var for var in prompt_data.input_variables if var not in kwargs],
            "extra_variables": [var for var in kwargs.keys() if var not in prompt_data.input_variables],
            "formatted_prompt": formatted_prompt
        }
    
    def export_templates(self, file_path: Path, format: str = "json") -> bool:
        """
        导出所有提示词模板
        
        Args:
            file_path: 导出文件路径
            format: 导出格式，支持 json 或 yaml
            
        Returns:
            是否导出成功
        """
        data = {name: prompt.model_dump() for name, prompt in self.templates.items()}
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if format == "json":
                    json.dump(data, f, ensure_ascii=False, indent=2)
                elif format == "yaml":
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                else:
                    logger.warning("不支持的导出格式: %s", format)
                    return False
            return True
        except Exception as e:
            logger.error("导出模板失败: %s", e)
            return False
    
    def import_templates(self, file_path: Path, overwrite: bool = False) -> int:
        """
        导入提示词模板
        
        Args:
            file_path: 导入文件路径
            overwrite: 是否覆盖已存在的模板
            
        Returns:
            成功导入的模板数量
        """
        if not file_path.exists():
            logger.warning("文件不存在: %s", file_path)
            return 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            count = 0
            for name, prompt_data in data.items():
                if name in self.templates and not overwrite:
                    logger.info("跳过已存在的模板: %s", name)
                    continue

                self.templates[name] = PromptTemplateData(**prompt_data)
                count += 1

            self._save_custom_prompts()
            return count
        except Exception as e:
            logger.error("导入模板失败: %s", e)
            return 0
    
    def _extract_variables(self, template: str) -> List[str]:
        """
        从模板中提取变量名
        
        Args:
            template: 模板内容
            
        Returns:
            变量名列表
        """
        import re
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        return list(set(matches))
