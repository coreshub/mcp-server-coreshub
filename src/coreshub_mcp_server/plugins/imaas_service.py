"""
iMaaS 大模型服务代理插件
"""

import json
from typing import List, Dict, Any

import requests
from mcp.types import TextContent

from coreshub_mcp_server.base_plugin import BaseTool
from coreshub_mcp_server.settings import settings
from coreshub_mcp_server.utils.signature import get_signature
from coreshub_mcp_server.utils.zones import get_zone_schema_description, get_default_zone

_MODEL_PATH = "/imaas/api/model"
_APIKEY_PATH = "/imaas/api/apikey"

_DEFAULT_MODEL_TAGS = "txt2txt,txt2img,txt2video,img2video,audio,embedding,rerank,crossmodel"


class GetImaasModelsTool(BaseTool):
    """查看大模型服务广场上可调用的模型列表"""

    tool_name = "get_imaas_models"
    tool_description = (
        "查看 iMaaS 大模型服务广场上所有可调用的模型，"
        "支持按关键字、模型类型标签筛选"
    )

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["zone", "owner"],
            "properties": {
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "owner": {
                    "type": "string",
                    "description": "账户 ID，从上下文 owner/user_id 获取",
                    "default": settings.user_id,
                },
                "key_words": {
                    "type": "string",
                    "description": "按模型名称关键字模糊搜索",
                    "default": "",
                },
                "model_tag": {
                    "type": "string",
                    "description": (
                        "按模型类型标签筛选，逗号分隔多个标签。"
                        "可选值：txt2txt（文本生成）、txt2img（文生图）、txt2video（文生视频）、"
                        "img2video（图生视频）、audio（音频）、embedding（向量嵌入）、"
                        "rerank（重排序）、crossmodel（跨模态）。"
                        "留空表示返回全部类型"
                    ),
                    "default": _DEFAULT_MODEL_TAGS,
                },
                "page": {
                    "type": "integer",
                    "description": "页码，从 1 开始",
                    "default": 1,
                },
                "size": {
                    "type": "integer",
                    "description": "每页返回数量",
                    "default": 100,
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", get_default_zone())
        owner = arguments.get("owner", settings.user_id)
        key_words = arguments.get("key_words", "")
        model_tag = arguments.get("model_tag", _DEFAULT_MODEL_TAGS)
        page = arguments.get("page", 1)
        size = arguments.get("size", 100)

        params = {
            "zone": zone,
            "owner": owner,
            "key_words": key_words,
            "model_tag": model_tag,
            "page": page,
            "size": size,
        }

        signed_query = get_signature(
            method="GET",
            url=_MODEL_PATH,
            ak=settings.access_key,
            sk=settings.secret_key,
            params=params,
        )

        full_url = f"{settings.base_url}{_MODEL_PATH}?{signed_query}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                data = response.json()
                # 过滤 icon 字段（base64 图片，内容庞大，对模型无意义）
                for item in data.get("list", []):
                    item.pop("icon", None)
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"iMaaS 可调用模型列表:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取模型列表失败: HTTP {response.status_code}\n{response.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


class GetImaasApiKeysTool(BaseTool):
    """查看当前账户的 iMaaS API Key 列表"""

    tool_name = "get_imaas_apikeys"
    tool_description = (
        "查看当前账户在 iMaaS 大模型服务中创建的 API Key 列表，"
        "可用于调用模型接口时的鉴权"
    )

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["zone", "owner"],
            "properties": {
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "owner": {
                    "type": "string",
                    "description": "账户 ID，从上下文 owner/user_id 获取",
                    "default": settings.user_id,
                },
                "key_words": {
                    "type": "string",
                    "description": "按 API Key 名称关键字模糊搜索",
                    "default": "",
                },
                "page": {
                    "type": "integer",
                    "description": "页码，从 1 开始",
                    "default": 1,
                },
                "size": {
                    "type": "integer",
                    "description": "每页返回数量",
                    "default": 10,
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        zone = arguments.get("zone", get_default_zone())
        owner = arguments.get("owner", settings.user_id)
        key_words = arguments.get("key_words", "")
        page = arguments.get("page", 1)
        size = arguments.get("size", 10)

        params = {
            "zone": zone,
            "owner": owner,
            "key_words": key_words,
            "page": page,
            "size": size,
        }

        signed_query = get_signature(
            method="GET",
            url=_APIKEY_PATH,
            ak=settings.access_key,
            sk=settings.secret_key,
            params=params,
        )

        full_url = f"{settings.base_url}{_APIKEY_PATH}?{signed_query}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                data = response.json()
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"iMaaS API Key 列表:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取 API Key 列表失败: HTTP {response.status_code}\n{response.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


class GetImaasModelDetailTool(BaseTool):
    """查看单个 iMaaS 模型的详细信息"""

    tool_name = "get_imaas_model_detail"
    tool_description = (
        "获取 iMaaS 大模型服务广场中某个模型的详细信息，"
        "包括模型描述、支持的参数、渠道配置等。"
        "需要先通过 get_imaas_models 获取模型 ID（id 字段）"
    )

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["model_id", "zone", "owner"],
            "properties": {
                "model_id": {
                    "type": "string",
                    "description": "模型 ID，从 get_imaas_models 返回的 id 字段获取，格式如 md-tDz8i3XJ",
                },
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "owner": {
                    "type": "string",
                    "description": "账户 ID，从上下文 owner/user_id 获取",
                    "default": settings.user_id,
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        model_id = arguments.get("model_id", "")
        zone = arguments.get("zone", get_default_zone())
        owner = arguments.get("owner", settings.user_id)

        if not model_id:
            return [TextContent(type="text", text="参数缺失：model_id 不能为空，请先调用 get_imaas_models 获取模型 ID")]

        url_path = f"/imaas/api/model/{model_id}"
        params = {
            "zone": zone,
            "owner": owner,
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
                data = response.json()
                # 过滤 icon 字段（base64 图片，内容庞大，对模型无意义）
                if isinstance(data.get("data"), dict):
                    data["data"].pop("icon", None)
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                return [TextContent(type="text", text=f"iMaaS 模型详情，其中字段price为每1k token的价格，单位为人民币:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取模型详情失败: HTTP {response.status_code}\n{response.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


GetImaasModelsTool.register()
GetImaasApiKeysTool.register()
GetImaasModelDetailTool.register()


class GetImaasTokenMetricsTool(BaseTool):
    """查询 iMaaS 用量统计（Token / 次数 / 时长 / 字数）"""

    tool_name = "get_imaas_token_metrics"
    tool_description = (
        "查询 iMaaS 大模型服务的用量统计数据，支持按时间范围、API Key、模型、"
        "计量类型（输入/输出/缓存命中）、计费单位进行筛选。"
        "推荐使用 aggr_type=range（默认），可同时得到时序折线数据和 result[].sum 区间总量。"
        "时间范围限制：最短 1 分钟，最长 30 天。"
        "start_time / end_time 均为 Unix 时间戳（秒）"
    )

    @staticmethod
    def model_json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["zone", "owner", "start_time"],
            "properties": {
                "zone": {
                    "type": "string",
                    "description": get_zone_schema_description(),
                    "default": get_default_zone(),
                },
                "owner": {
                    "type": "string",
                    "description": "账户 ID，从上下文 owner/user_id 获取",
                    "default": settings.user_id,
                },
                "start_time": {
                    "type": "integer",
                    "description": "查询开始时间，Unix 时间戳（秒）。与 end_time 间隔须在 1 分钟～30 天之间",
                },
                "end_time": {
                    "type": "integer",
                    "description": "查询结束时间，Unix 时间戳（秒），默认当前时间",
                },
                "aggr_type": {
                    "type": "string",
                    "description": (
                        "数据汇总方式，推荐使用 range：\n"
                        "- range（默认）：返回时序折线数据，每个时间点为该时段的增量值，"
                        "同时在 result[].sum 字段提供区间内总量，前端折线图也使用此模式\n"
                        "- sum：使用 Prometheus increase() 查询，返回多个采样点，"
                        "数据含义为滚动区间增量，一般不如 range 直观"
                    ),
                    "enum": ["range", "sum"],
                    "default": "range",
                },
                "api_key": {
                    "type": "string",
                    "description": "按 API Key 筛选，支持多个（逗号分隔）。留空表示所有",
                    "default": "",
                },
                "model": {
                    "type": "string",
                    "description": "按模型名称筛选，支持多个（逗号分隔）。留空表示所有模型",
                    "default": "",
                },
                "token_type": {
                    "type": "string",
                    "description": (
                        "按计量类型筛选，支持多个（逗号分隔）：\n"
                        "- input：输入 token\n"
                        "- output：输出 token\n"
                        "- cached：缓存命中 token\n"
                        "留空表示返回全部类型（input+output+cached 合并）"
                    ),
                    "default": "",
                },
                "unit": {
                    "type": "string",
                    "description": (
                        "计费单位，支持多个（逗号分隔）：\n"
                        "- token：按 token 数计量（文本类模型）\n"
                        "- count：按调用次数计量（图片/视频类模型）\n"
                        "- seconds：按秒数计量（音频/视频类模型）\n"
                        "- words：按字数计量\n"
                        "留空表示所有单位"
                    ),
                    "default": "",
                },
            },
        }

    async def execute_tool(self, arguments: dict) -> List[TextContent]:
        import time as _time

        zone = arguments.get("zone", get_default_zone())
        owner = arguments.get("owner", settings.user_id)
        start_time = arguments.get("start_time")
        end_time = arguments.get("end_time", int(_time.time()))
        aggr_type = arguments.get("aggr_type", "range")
        api_key = arguments.get("api_key", "")
        model = arguments.get("model", "")
        token_type = arguments.get("token_type", "")
        unit = arguments.get("unit", "")

        if not start_time:
            return [TextContent(type="text", text="参数缺失：start_time（Unix 时间戳）不能为空")]

        time_range = end_time - start_time
        if time_range < 60 or time_range > 3600 * 24 * 30:
            return [TextContent(type="text",
                                text=f"时间范围错误：start_time 与 end_time 间隔须在 1 分钟～30 天之间，当前间隔 {time_range} 秒")]

        url_path = "/imaas/api/metrics/tokens"
        params = {
            "zone": zone,
            "owner": owner,
            "start_time": start_time,
            "end_time": end_time,
            "aggr_type": aggr_type,
        }
        # 可选过滤参数，有值才传
        if api_key:
            params["api_key"] = api_key
        if model:
            params["model"] = model
        if token_type:
            params["token_type"] = token_type
        if unit:
            params["unit"] = unit

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
                data = response.json()
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
                aggr_label = "时序折线" if aggr_type == "range" else "区间汇总"
                return [TextContent(type="text", text=f"iMaaS 用量统计（{aggr_label}）:\n{formatted_data}")]
            else:
                return [TextContent(type="text",
                                    text=f"获取用量统计失败: HTTP {response.status_code}\n{response.text}")]
        except Exception as e:
            return [TextContent(type="text", text=f"请求出错: {str(e)}")]


GetImaasTokenMetricsTool.register()
