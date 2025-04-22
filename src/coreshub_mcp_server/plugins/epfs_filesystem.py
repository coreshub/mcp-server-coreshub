import json
from typing import List, Dict, Any

import requests
from coreshub_mcp_server.base_plugin import BaseTool
from coreshub_mcp_server.settings import settings
from coreshub_mcp_server.utils.signature import get_signature
from mcp.types import TextContent


class GetEpfsFilesystemTool(BaseTool):
    tool_name = "get_epfs_filesystem"
    tool_description = "返回已经创建的epfs文件系统"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "区域标识，从上下文获取，选项：xb3,xb2,hb2",
                    "default": "xb3",
                    "required": "True"
                },
                "owner": {
                    "type": "string",
                    "description": "用户名",
                    "default": settings.user_id,
                    "required": "True"
                },
                "user_id": {
                    "type": "string",
                    "description": "容器实例的拥有者ID，可以从上下文字段user_id获取",
                    "default": settings.user_id,
                    "required": "True"
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        user_id = arguments.get("user_id", settings.user_id)
        limit = arguments.get("limit", 10)
        offset = arguments.get("offset", 0)

        url_path = f"/epfs/api/filesystem"

        params = {
            "zone": zone,
            "owner": owner,
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }

        signed_query = get_signature(
            method="GET",
            url=url_path,
            ak=settings.access_key,
            sk=settings.secret_key,
            params=params
        )

        full_url = f"{settings.base_url}{url_path}?{signed_query}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                filesystems = response.json()
                formatted_data = json.dumps(filesystems, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"epfs文件系统:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取epfs文件系统失败: HTTP {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


class GetEpfsBillInfoTool(BaseTool):
    tool_name = "get_epfs_bill_info"
    tool_description = "返回epfs文件系统的账单信息"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "resource_id": {
                    "type": "string",
                    "description": "资源ID,从上下文resource_id字段获取",
                    "required": "True"
                },
                "zone": {
                    "type": "string",
                    "description": "区域标识，从上下文获取，选项：xb3,xb2,hb2",
                    "default": "xb3",
                    "required": "True"
                },
                "owner": {
                    "type": "string",
                    "description": "用户名",
                    "default": settings.user_id,
                    "required": "True"
                },
                "user_id": {
                    "type": "string",
                    "description": "容器实例的拥有者ID，从上下文字段user_id获取",
                    "default": settings.user_id,
                    "required": "True"
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        user_id = arguments.get("user_id", settings.user_id)
        resource_id = arguments.get("resource_id", "")
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit", 10)

        url_path = f"/epfs/api/bill/info"

        params = {
            "zone": zone,
            "owner": owner,
            "user_id": user_id,
            "resource_id": resource_id,
            "offset": offset,
            "limit": limit
        }

        signed_query = get_signature(
            method="GET",
            url=url_path,
            ak=settings.access_key,
            sk=settings.secret_key,
            params=params
        )

        full_url = f"{settings.base_url}{url_path}?{signed_query}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                bill_info = response.json()
                formatted_data = json.dumps(bill_info, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"epfs文件系统账单信息:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取epfs文件系统账单信息失败: HTTP {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


# 注册工具和提示
GetEpfsFilesystemTool.register()
GetEpfsBillInfoTool.register()
