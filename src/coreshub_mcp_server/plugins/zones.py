"""
区域信息插件 - 提供可用区域的 Prompt，供模型在不确定 zone 参数时主动查询
"""

from typing import Dict, Any

from mcp.types import GetPromptResult, PromptMessage, TextContent

from coreshub_mcp_server.base_plugin import BasePrompt
from coreshub_mcp_server.utils.zones import get_zone_prompt_text


class AvailableZonesPrompt(BasePrompt):
    """
    可用区域提示。

    模型在遇到 zone 参数不确定时，可主动调用此 prompt 获取完整的区域列表说明。
    """

    prompt_name = "available_zones"
    prompt_description = (
        "返回当前平台所有可用区域的列表及说明。"
        "当用户未指定区域或区域信息不明确时，请先调用此提示确认可选区域。"
    )
    prompt_arguments = []

    async def execute_prompt(self, arguments: Dict[str, Any] = None) -> GetPromptResult:
        return GetPromptResult(
            description="可用区域列表",
            messages=[
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text=get_zone_prompt_text(),
                    ),
                )
            ],
        )


AvailableZonesPrompt.register()
