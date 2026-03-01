import json
from typing import List, Dict, Any

import requests
from coreshub_mcp_server.base_plugin import BaseTool, BasePrompt
from coreshub_mcp_server.settings import settings
from coreshub_mcp_server.utils.signature import get_signature
from coreshub_mcp_server.utils.zones import get_zone_schema_description, get_default_zone
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS
from mcp.types import TextContent, GetPromptResult


class GetContainerInfoTool(BaseTool):
    tool_name = "get_container_info"
    tool_description = "返回已经创建的容器实例，也可根据参数进行查询"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["zone"],
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "返回结果的最大数量",
                    "default": 10,
                },
                "offset": {
                    "type": "integer",
                    "description": "分页偏移量",
                    "default": 0,
                },
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "name": {
                    "type": "string",
                    "description": "按照实例名字进行模糊搜索",
                    "default": "",
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", get_default_zone())
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit", 10)
        name = arguments.get("name", "")

        url_path = f"/aicp/notebooks/namespaces/{settings.user_id.lower()}/notebooks"
        params = {
            "limit": limit,
            "offset": offset,
            "zone": zone,
            "name": name,
        }
        signed_query = get_signature(method="GET", url=url_path, ak=settings.access_key, sk=settings.secret_key,
                                     params=params)
        full_url = f"{settings.base_url}{url_path}?{signed_query}"

        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                notebooks_data = response.json()
                formatted_data = json.dumps(notebooks_data, ensure_ascii=False, indent=2)
                if notebooks_data.get("counts") == 0:
                    return [TextContent(type="text",
                                        text=f"容器实例信息:\n{formatted_data}\n询问：需要参数:\n{self.model_json_schema()},请根据需要修改参数")]
                return [TextContent(type="text", text=f"容器实例信息:\n{formatted_data}")]
            else:
                return [
                    TextContent(type="text", text=f"获取容器实例失败: HTTP {response.status_code}\n{response.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


class GetContainerInfoPrompt(BasePrompt):
    prompt_name = "get_notebooks_info"
    prompt_description = "返回已经创建的容器实例"
    prompt_arguments = []

    async def execute_prompt(self, arguments: Dict[str, Any] = None) -> GetPromptResult:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"暂不支持该提示: {self.prompt_name}"))


class GetSSHInfoTool(BaseTool):
    tool_name = "get_ssh_info"
    tool_description = "该函数可查看实例的远程访问、开放端口等信息，返回特定实例的SSH信息"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["namespace", "uuid", "zone", "owner", "user_id", "services"],
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "容器实例的命名空间,从上下文字段namespace获取",
                    "default": settings.user_id.lower(),
                },
                "uuid": {
                    "type": "string",
                    "description": "容器实例的uuid，可以从上下文uuid中获取",
                },
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "owner": {
                    "type": "string",
                    "description": "容器实例的拥有者，可以从上下文字段user_id获取",
                    "default": settings.user_id,
                },
                "user_id": {
                    "type": "string",
                    "description": "容器实例的拥有者ID，可以从上下文字段user_id获取",
                },
                "services": {
                    "type": "array",
                    "description": "要开启的服务列表",
                    "default": ["ssh", "custom", "node_port"],
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", get_default_zone())
        owner = arguments.get("owner", settings.user_id)
        user_id = arguments.get("user_id", settings.user_id)
        services = arguments.get("services", ["ssh", "custom", "node_port"])
        namespace = arguments.get("namespace", settings.user_id.lower())
        uuid = arguments.get("uuid")

        url_path = f"/aicp/notebooks/namespaces/{namespace}/notebooks/{uuid}/servers"

        params = {
            "zone": zone,
            "owner": owner,
            "user_id": user_id,
            "services": services,
        }

        signed_query = get_signature(
            method="GET",
            url=url_path,
            ak=settings.access_key,
            sk=settings.secret_key,
            params=params,
        )
        full_url = f"{settings.base_url}{url_path}?{signed_query}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                ssh_info = response.json()
                formatted_data = json.dumps(ssh_info, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"SSH信息:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取SSH信息失败: HTTP {response.status_code}\n{response.text}\n需要从get_container_info获取容器实例信息，然后询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


# 注册工具和提示
GetContainerInfoTool.register()
# GetContainerInfoPrompt.register()
GetSSHInfoTool.register()
