import datetime
import json
from typing import List, Dict, Any

import requests
from mcp.types import TextContent

from coreshub_mcp_server.base_plugin import BaseTool
from coreshub_mcp_server.settings import settings
from coreshub_mcp_server.utils.signature import get_signature


class GetDistributedTrainingTool(BaseTool):
    tool_name = "get_distributed_training"
    tool_description = "返回已经创建的分布式训练任务"

    @staticmethod
    def get_current_time() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_start_week_time() -> str:
        return (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "end_at": {
                    "type": "string",
                    "description": "结束时间",
                    "default": f"结束时间默认当前时间:{GetDistributedTrainingTool.get_current_time()}",
                    "required": "True"
                },
                "start_at": {
                    "type": "string",
                    "description": "开始时间",
                    "default": f"开始时间默认一周前:{GetDistributedTrainingTool.get_start_week_time()}",
                    "required": "True"
                },
                "limit": {
                    "type": "integer",
                    "description": "每页显示的条数",
                    "default": 10,
                    "required": "True"
                },
                "offset": {
                    "type": "integer",
                    "description": "偏移量",
                    "default": 0,
                    "required": "True"
                },
                "zone": {
                    "type": "string",
                    "description": "区域",
                    "default": "默认为xb3，可选xb2,hb2",
                    "required": "True"
                },
                "owner": {
                    "type": "string",
                    "description": "所有者",
                    "default": settings.user_id,
                    "required": "True"
                },
                "user_id": {
                    "type": "string",
                    "description": "用户ID",
                    "default": settings.user_id,
                    "required": "True"
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        end_at = arguments.get("end_at", self.get_current_time())
        start_at = arguments.get("start_at", self.get_start_week_time())
        limit = arguments.get("limit", 10)
        offset = arguments.get("offset", 0)
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        user_id = arguments.get("user_id", settings.user_id)

        url_path = f"/aicp/trains/namespaces/{user_id.lower()}/trains"

        params = {
            "zone": zone,
            "owner": owner,
            "user_id": user_id,
            "end_at": end_at,
            "start_at": start_at,
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
                data = response.json()
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"分布式训练任务:\n{formatted_data}")]
            else:
                return [TextContent(
                    text=f"获取分布式训练任务失败: {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(text=f"获取分布式训练任务失败: {e}")]


class GetDistributedTrainingDetailLogTool(BaseTool):
    tool_name = "get_distributed_training_detail_log"
    tool_description = "返回分布式训练任务的详细日志"

    @staticmethod
    def get_current_time() -> str:
        # 1745303982000000000,纳秒时间戳
        return int(datetime.datetime.now().timestamp() * 1000000000)

    @staticmethod
    def get_start_time() -> str:
        return int((datetime.datetime.now() - datetime.timedelta(hours=12)).timestamp() * 1000000000)

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "end_time": {
                    "type": "string",
                    "description": "结束时间",
                    "default": f"结束时间默认当前时间:{GetDistributedTrainingDetailLogTool.get_current_time()}",
                    "required": "True"
                },
                "start_time": {
                    "type": "string",
                    "description": "开始时间",
                    "default": f"开始时间默认12小时前:{GetDistributedTrainingDetailLogTool.get_start_time()}",
                    "required": "True"
                },
                "fuzzy": {
                    "type": "boolean",
                    "description": "是否模糊",
                    "default": True,
                    "required": "False"
                },
                "reverse": {
                    "type": "boolean",
                    "description": "是否反转",
                    "default": True,
                    "required": "True"
                },
                "size": {
                    "type": "integer",
                    "description": "每页显示的条数",
                    "default": 100,
                    "required": "True"
                },
                "train_uuid": {
                    "type": "string",
                    "description": "训练ID",
                    "default": "来自上下文train_uuid，如果上下文没有，则需要询问，从get_distributed_training获取",
                    "required": "True"
                },
                "zone": {
                    "type": "string",
                    "description": "区域",
                    "default": "默认为xb3，可选xb2、hb2",
                    "required": "True"
                },
                "owner": {
                    "type": "string",
                    "description": "所有者",
                    "default": settings.user_id,
                    "required": "True"
                },
                "user_id": {
                    "type": "string",
                    "description": "用户ID",
                    "default": settings.user_id,
                    "required": "True"
                }
            }
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        end_time = arguments.get("end_time", self.get_current_time())
        start_time = arguments.get("start_time", self.get_start_time())
        fuzzy = arguments.get("fuzzy", True)
        reverse = arguments.get("reverse", True)
        size = arguments.get("size", 100)
        train_uuid = arguments.get("train_uuid", "")
        zone = arguments.get("zone", "xb3")
        owner = arguments.get("owner", settings.user_id)
        user_id = arguments.get("user_id", settings.user_id)

        url_path = f"/aicp/trains/namespaces/{user_id.lower()}/endpoints/pytorchjobs/logs"

        params = {
            "zone": zone,
            "owner": owner,
            "user_id": user_id,
            "end_time": end_time,
            "start_time": start_time,
            "fuzzy": fuzzy,
            "reverse": reverse,
            "size": size,
            "train_uuid": train_uuid
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
                data = response.json()
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"分布式训练任务的详细日志:\n{formatted_data}")]
            else:
                return [TextContent(
                    text=f"获取分布式训练任务的详细日志失败: {response.status_code}\n{response.text}\n需要询问参数:\n{self.model_json_schema()},请根据需要修改参数")]
        except Exception as e:
            return [TextContent(text=f"获取分布式训练任务的详细日志失败: {e}")]


GetDistributedTrainingTool.register()
GetDistributedTrainingDetailLogTool.register()
