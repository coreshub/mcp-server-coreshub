from coreshub_mcp_server.base_plugin import ToolRegistry
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    TextContent,
    Tool,
)


async def serve() -> None:
    """运行 MCP 服务器。"""
    server = Server("mcp-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """列出所有可用工具"""
        tool_classes = ToolRegistry.get_all_tool_classes()
        return [
            Tool(
                name=tool_class.tool_name,
                description=tool_class.tool_description,
                inputSchema=tool_class.model_json_schema(),
            ) for tool_class in tool_classes.values()
        ]

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        """调用工具"""
        tool_class = ToolRegistry.get_tool_class(name)
        if not tool_class:
            return [TextContent(type="text", text=f"未知工具: {name}")]

        tool = tool_class()
        return await tool.execute_tool(arguments)

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """列出所有可用提示"""
        prompt_classes = ToolRegistry.get_all_prompt_classes()
        return [
            prompt_class().get_prompt_definition()
            for prompt_class in prompt_classes.values()
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        """获取提示"""
        prompt_class = ToolRegistry.get_prompt_class(name)
        if not prompt_class:
            raise ValueError(f"未知提示: {name}")

        prompt = prompt_class()
        return await prompt.execute_prompt(arguments)

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
