"""
区域配置 - 单一配置来源

维护方式：
    通过环境变量 CORESHUB_ZONES 定义区域，格式为 "zone_id:描述,zone_id:描述"
    例如: CORESHUB_ZONES="xb3:西北3区,xb2:西北2区,hb2:华北2区,sh1:上海1区"

    若未设置环境变量，则使用下方的内置默认值 _DEFAULT_ZONES。

新增区域时：
    只需更新 CORESHUB_ZONES 环境变量（或 _DEFAULT_ZONES），重启 MCP 服务即可，
    无需修改任何插件代码。
"""

import os
from typing import Dict, List

# 内置默认区域（当环境变量未设置时使用）
_DEFAULT_ZONES: Dict[str, str] = {
    "xb3": "西北3区",
    "xb2": "西北2区",
    "hb2": "华北2区",
}


def _load_zones() -> Dict[str, str]:
    """从环境变量解析区域配置，失败则使用默认值"""
    raw = os.getenv("CORESHUB_ZONES", "").strip()
    if not raw:
        return dict(_DEFAULT_ZONES)

    zones: Dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            zone_id, _, desc = entry.partition(":")
            zones[zone_id.strip()] = desc.strip()
        else:
            # 只有 zone_id 没有描述时也接受
            zones[entry] = entry
    return zones if zones else dict(_DEFAULT_ZONES)


# 全局可用区域字典 { zone_id: 描述 }，模块加载时确定
AVAILABLE_ZONES: Dict[str, str] = _load_zones()


def get_zone_ids() -> List[str]:
    """返回所有可用区域 ID 列表"""
    return list(AVAILABLE_ZONES.keys())


def get_default_zone() -> str:
    """返回默认区域（列表第一个）"""
    ids = get_zone_ids()
    return ids[0] if ids else "xb3"


def get_zone_schema_description() -> str:
    """
    返回供 model_json_schema() 中 zone 字段 description 使用的标准描述。

    示例输出：
        "区域标识。可用区域：xb3（西北3区）、xb2（西北2区）、hb2（华北2区）。
         如不确定请调用 available_zones 提示查看完整列表。从上下文获取或手动指定。"
    """
    zone_list = "、".join(
        f"{zid}（{desc}）" for zid, desc in AVAILABLE_ZONES.items()
    )
    return (
        f"区域标识。可用区域：{zone_list}。"
        "如不确定请调用 available_zones 提示查看完整列表，从上下文获取或手动指定。"
    )


def get_zone_prompt_text() -> str:
    """
    返回 available_zones prompt 的正文内容，用于告知模型完整的区域信息。
    """
    lines = [
        "# 可用区域列表",
        "",
        "以下是当前 CoreshHub 平台的可用区域，在调用任何需要 `zone` 参数的工具时，",
        "请从下列区域 ID 中选择正确的值：",
        "",
    ]
    for zid, desc in AVAILABLE_ZONES.items():
        lines.append(f"- `{zid}` — {desc}")
    lines += [
        "",
        "> **提示**：如果用户提到的区域名称（如'上海'、'西北'）不在列表中，",
        "> 请告知用户该区域当前不可用，并列出可选项。",
        "> 若上下文中已有 zone 信息，优先使用上下文中的值。",
    ]
    return "\n".join(lines)
