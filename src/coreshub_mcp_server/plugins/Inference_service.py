import datetime
import json
from typing import List, Dict, Any

import requests
from coreshub_mcp_server.base_plugin import BaseTool
from coreshub_mcp_server.settings import settings
from coreshub_mcp_server.utils.signature import get_signature
from mcp.types import TextContent


class GetInferenceServiceTool(BaseTool):
    tool_name = "get_inference_service"
    tool_description = "返回已经创建的推理服务"

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
                "key_words": {
                    "type": "string",
                    "description": "关键字",
                    "default": "",
                    "required": "False"
                },
                "page": {
                    "type": "integer",
                    "description": "页码",
                    "default": 1,
                    "required": "False"
                },
                "size": {
                    "type": "integer",
                    "description": "每页数量",
                    "default": 10,
                    "required": "False"
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        key_words = arguments.get("key_words", "")
        page = arguments.get("page", 1)
        size = arguments.get("size", 10)

        url_path = f"/maas/api/inference_service"

        params = {
            "zone": zone,
            "owner": owner,
            "key_words": key_words,
            "page": page,
            "size": size
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
                inference_services = response.json()
                formatted_data = json.dumps(inference_services, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"推理服务:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取推理服务失败: HTTP {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


class GetInferenceServiceLogTool(BaseTool):
    tool_name = "get_inference_service_log"
    tool_description = "获取具体一个推理服务的日志"

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        # 获取当前UTC时间
        return {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "开始UTC时间",
                    "default": f"开始时间默认24小时前{BaseTool.get_formatted_time(time_format='%Y-%m-%dT%H:%M:%S.000Z', offset_days=-1, use_utc=True)}",
                    "required": "非必须"
                },
                "end_time": {
                    "type": "string",
                    "description": "结束UTC时间",
                    "default": f"结束时间默认当前时间{BaseTool.get_formatted_time(time_format='%Y-%m-%dT%H:%M:%S.000Z', use_utc=True)}",
                    "required": "非必须"
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
                "service_id": {
                    "type": "string",
                    "description": "服务ID",
                    "default": "来自上下文service_id，如果上下文没有，则需要询问，从get_inference_service获取",
                    "required": "True"
                },
                "size": {
                    "type": "integer",
                    "description": "每页数量",
                    "default": 100,
                    "required": "True"
                },
                "reverse": {
                    "type": "boolean",
                    "description": "是否反转",
                    "default": True,
                    "required": "True"
                }

            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        service_id = arguments.get("service_id", "")
        size = arguments.get("size", 100)
        reverse = arguments.get("reverse", True)
        start_time = arguments.get("start_time", None)
        end_time = arguments.get("end_time", None)

        url_path = f"/maas/api/inference_service/{service_id}/log"

        params = {
            "zone": zone,
            "owner": owner,
            "service_id": service_id,
            "size": size,
            "reverse": reverse
        }
        if end_time:
            params["end_time"] = end_time
        if start_time:
            params["start_time"] = start_time

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
                log = response.json()
                formatted_data = json.dumps(log, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"推理服务日志:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取推理服务日志失败: HTTP {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


GetInferenceServiceTool.register()
GetInferenceServiceLogTool.register()
