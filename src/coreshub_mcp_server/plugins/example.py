"""
系统信息工具和提示 - 提供系统环境信息
"""

import json
import platform
import sys
from typing import Dict, Any, List

from coreshub_mcp_server.base_plugin import BaseTool, BasePrompt
from mcp.types import GetPromptResult, PromptMessage, TextContent, PromptArgument


class SystemInfoTool(BaseTool):
    """系统信息工具 - 返回当前系统的基本信息"""

    tool_name = "system_info"
    tool_description = "返回当前系统的基本信息，包括操作系统、Python版本等"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "include_python_path": {
                    "type": "boolean",
                    "description": "是否包含Python路径信息",
                    "default": False
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        include_python_path = arguments.get("include_python_path", False)

        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
        }

        if include_python_path:
            system_info["python_path"] = sys.path

        formatted_info = json.dumps(system_info, indent=2, ensure_ascii=False)
        return [TextContent(type="text", text=f"系统信息:\n{formatted_info}")]


class SystemInfoPrompt(BasePrompt):
    """系统信息提示 - 提供系统基本信息的提示"""

    prompt_name = "system_info"
    prompt_description = "返回当前系统的基本信息"
    prompt_arguments = [
        PromptArgument(
            name="include_python_path",
            description="是否包含Python路径信息",
            required=False
        )
    ]

    async def execute_prompt(self, arguments: Dict[str, Any] = None) -> GetPromptResult:
        include_python_path = False
        if arguments and "include_python_path" in arguments:
            include_python_path = arguments["include_python_path"]

        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "python_version": sys.version.split()[0],
        }

        if include_python_path:
            system_info["python_path"] = str(sys.path)

        formatted_info = json.dumps(system_info, indent=2, ensure_ascii=False)

        return GetPromptResult(
            description="系统信息",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"请提供系统信息:")
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(type="text", text=formatted_info)
                )
            ],
        )


# 注册工具和提示
# SystemInfoTool.register()
# SystemInfoPrompt.register()
