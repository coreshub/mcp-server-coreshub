from typing import Dict, Any, List, ClassVar, Optional, Type, Set
from abc import ABC, abstractmethod

from mcp import GetPromptResult
from mcp.types import TextContent, Prompt, PromptMessage, PromptArgument


class ToolRegistry:
    """注册表，用于管理所有可用的工具和提示"""
    
    _tool_classes: Dict[str, Type["BaseTool"]] = {}
    _prompt_classes: Dict[str, Type["BasePrompt"]] = {}
    
    @classmethod
    def register_tool(cls, tool_class: Type["BaseTool"]) -> None:
        """注册工具类
        
        Args:
            tool_class: 要注册的工具类
        """
        cls._tool_classes[tool_class.tool_name] = tool_class
    
    @classmethod
    def register_prompt(cls, prompt_class: Type["BasePrompt"]) -> None:
        """注册提示类
        
        Args:
            prompt_class: 要注册的提示类
        """
        cls._prompt_classes[prompt_class.prompt_name] = prompt_class
    
    @classmethod
    def get_tool_class(cls, name: str) -> Optional[Type["BaseTool"]]:
        """获取工具类
        
        Args:
            name: 工具名称
            
        Returns:
            工具类或None
        """
        return cls._tool_classes.get(name)
    
    @classmethod
    def get_prompt_class(cls, name: str) -> Optional[Type["BasePrompt"]]:
        """获取提示类
        
        Args:
            name: 提示名称
            
        Returns:
            提示类或None
        """
        return cls._prompt_classes.get(name)
    
    @classmethod
    def get_all_tool_classes(cls) -> Dict[str, Type["BaseTool"]]:
        """获取所有工具类
        
        Returns:
            所有工具类的字典
        """
        return cls._tool_classes.copy()
    
    @classmethod
    def get_all_prompt_classes(cls) -> Dict[str, Type["BasePrompt"]]:
        """获取所有提示类
        
        Returns:
            所有提示类的字典
        """
        return cls._prompt_classes.copy()


class BaseTool(ABC):
    """工具基类"""
    
    # 工具元数据
    tool_name: ClassVar[str] = ""
    tool_description: ClassVar[str] = ""
    
    def __init__(self):
        """初始化工具"""
        pass
    
    @staticmethod
    @abstractmethod
    def model_json_schema() -> Dict[str, Any]:
        """返回工具的参数模式"""
        raise NotImplementedError("子类必须实现此方法")
    
    @abstractmethod
    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        """执行工具逻辑"""
        raise NotImplementedError("子类必须实现此方法")
    
    @classmethod
    def register(cls) -> None:
        """注册工具"""
        ToolRegistry.register_tool(cls)


class BasePrompt(ABC):
    """提示基类"""
    
    # 提示元数据
    prompt_name: ClassVar[str] = ""
    prompt_description: ClassVar[str] = ""
    prompt_arguments: ClassVar[List[PromptArgument]] = []
    
    def __init__(self):
        """初始化提示"""
        pass
    
    @classmethod
    def get_prompt_definition(cls) -> Prompt:
        """获取提示定义"""
        return Prompt(
            name=cls.prompt_name,
            description=cls.prompt_description,
            arguments=cls.prompt_arguments
        )
    
    @abstractmethod
    async def execute_prompt(self, arguments: Dict[str, Any] = None) -> GetPromptResult:
        """执行提示逻辑"""
        raise NotImplementedError("子类必须实现此方法")
    
    @classmethod
    def register(cls) -> None:
        """注册提示"""
        ToolRegistry.register_prompt(cls)


__all__ = ['BaseTool', 'BasePrompt', 'ToolRegistry']
