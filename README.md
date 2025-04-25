# Coreshub MCP Server

## 1、项目结构

```
src/coreshub_mcp_server/
├── plugins/           # 插件目录，所有工具和提示插件
├── utils/             # 工具函数
│   └── signature.py   # 签名工具函数
├── base_plugin.py     # 工具和提示基类
├── settings.py        # 配置管理
└── server.py          # MCP服务器实现
```

> ##### 开始之前请确保安装好 python 和 uv

## 2、运行

### 场景一：在Cherry Studio中运行

> 注⚠️：为保证工具的正确调用，建议使用32B参数以上的模型服务

#### （1）一键拉取使用

> 在Cherry Studio的设置——MCP服务器——编辑MCP配置

```json
{
  "mcpServers": {
    "coreshub-mcp-server": {
      "type": "stdio",
      "registryUrl": "http://mirrors.aliyun.com/pypi/simple/",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/coreshub/mcp-server-coreshub",
        "coreshub-mcp-server"
      ],
      "env": {
        "QY_ACCESS_KEY_ID": "基石智算的AK",
        "QY_SECRET_ACCESS_KEY": "基石智算的SK",
        "CORESHUB_USER_ID": "基石智算的账户ID"
      }
    }
  }
}
```

#### （2）从github下载到本地后使用

> 在Cherry Studio的设置——MCP服务器——添加服务器，进入编辑模式

##### 对于macOS系统:

类型选择：

```
stdio
```

命令填写:

```bash
sh
```

参数填写:

```bash
-c
cd 项目根目录路径 && uv run coreshub-mcp-server
```

环境变量填写:

```bash
QY_ACCESS_KEY_ID=基石智算的AK
QY_SECRET_ACCESS_KEY=基石智算的SK
CORESHUB_USER_ID=基石智算的账户ID
```

##### 对于windows系统:

类型选择：

```
stdio
```

命令填写:

```bash
cmd
```

参数填写:

```bash
/c
cd 项目根目录路径 && uv run coreshub-mcp-server
```

环境变量填写:

```bash
QY_ACCESS_KEY_ID=基石智算的AK
QY_SECRET_ACCESS_KEY=基石智算的SK
CORESHUB_USER_ID=基石智算的账户ID
```

### 场景二：命令行操作（需实现client）

#### （1）首先配置环境变量

可以在代码中配置，在settings.py中配置

```python
class Settings:
    access_key = os.getenv("QY_ACCESS_KEY_ID", "基石智算的AK")
    secret_key = os.getenv("QY_SECRET_ACCESS_KEY", "基石智算的SK")
    user_id = os.getenv("CORESHUB_USER_ID", "基石智算的账户ID")
```

或者在本机系统环境变量配置

```bash
export QY_ACCESS_KEY_ID="基石智算的AK"
export QY_SECRET_ACCESS_KEY="基石智算的SK"
export CORESHUB_USER_ID="基石智算的账户ID"
```

#### （2）在项目根目录使用 [`uv`](https://docs.astral.sh/uv/)检查服务状态

```bash
uv run src/coreshub_mcp_server
```

##### 	命令行参数

- `--debug`: 启用调试模式，输出详细日志
- `--list-plugins`: 列出所有已加载的插件
- `--log-file`: 指定日志文件路径

## 3、开发

### 1、添加新工具

在 `src/coreshub_mcp_server/plugins` 目录下创建新的Python文件，然后实现 `BaseTool` 和/或 `BasePrompt`
的子类。工具和提示现在是分离的概念，可以根据需要只实现其中一种或两种。

#### （1）工具实现示例:

```python
from coreshub_mcp_server.base_plugin import BaseTool


class MyTool(BaseTool):
    tool_name = "my_tool"
    tool_description = "我的自定义工具"

    @staticmethod
    def model_json_schema():
        return {
            "type": "object",
            "properties": {
                "param": {
                    "type": "string",
                    "description": "参数描述"
                }
            }
        }

    async def execute_tool(self, arguments):
        # 实现工具逻辑
        pass


# 注册工具
MyTool.register()
```

#### （2）提示实现示例:

```python
from coreshub_mcp_server.base_plugin import BasePrompt
from mcp.types import PromptArgument


class MyPrompt(BasePrompt):
    prompt_name = "my_prompt"
    prompt_description = "我的自定义提示"
    prompt_arguments = [
        PromptArgument(
            name="param",
            description="参数描述",
            required=False
        )
    ]

    async def execute_prompt(self, arguments=None):
        # 实现提示逻辑
        pass


# 注册提示
MyPrompt.register()
```

## 4、可用工具

### 1、get_epfs_filesystem   返回已经创建的epfs文件系统

- zone
    - type: string
    - description: 区域标识，从上下文获取，选项：xb3,xb2,hb2
    - default: xb3
    - required: True
- owner
    - type: string
    - description: 用户名
    - default: 基石智算的账户ID
    - required: True
- user_id
    - type: string
    - description: 容器实例的拥有者ID，可以从上下文字段user_id获取
    - default: 基石智算的账户ID
    - required: True

### 2、get_epfs_bill_info   返回epfs文件系统的账单信息

- resource_id
    - type: string
    - description: 资源ID,从上下文resource_id字段获取
    - required: True
- zone
    - type: string
    - description: 区域标识，从上下文获取，选项：xb3,xb2,hb2
    - default: xb3
    - required: True
- owner
    - type: string
    - description: 用户名
    - default: 基石智算的账户ID
    - required: True
- user_id
    - type: string
    - description: 容器实例的拥有者ID，从上下文字段user_id获取
    - default: 基石智算的账户ID
    - required: True

### 3、get_container_info   返回已经创建的容器实例，也可根据参数进行查询

- limit
    - type: integer
    - description: 返回结果的最大数量
    - default: 10
    - required: False
- offset
    - type: integer
    - description: 分页偏移量
    - default: 0
    - required: False
- zone
    - type: string
    - description: 区域标识，从上下文获取，选项：xb3,xb2,hb2
    - default: xb3
    - required: True
- name
    - type: string
    - description: 按照实例名字进行模糊搜索
    - default: ""
    - required: False

### 4、get_ssh_info   返回特定实例的SSH信息

- namespace
    - type: string
    - description: 容器实例的命名空间,从上下文字段namespace获取
    - default: 小写的基石智算账户ID
    - required: True
- uuid
    - type: string
    - description: 容器实例的uuid，可以从上下文uuid中获取
    - required: True
- zone
    - type: string
    - description: 区域标识,从上下文获取
    - default: xb3
    - required: True
- owner
    - type: string
    - description: 容器实例的拥有者，可以从上下文字段user_id获取
    - default: 基石智算的账户ID
    - required: True
- user_id
    - type: string
    - description: 容器实例的拥有者ID，可以从上下文字段user_id获取
    - required: True
- services
    - type: array
    - description: 要开启的服务列表
    - default: ["ssh", "custom", "node_port"]
    - required: True

### 5、get_distributed_training   返回已经创建的分布式训练任务

- end_at
    - type: string
    - description: 结束时间，格式为%Y-%m-%d %H:%M:%S
    - default: 当前时间
    - required: True
- start_at
    - type: string
    - description: 开始时间，格式为%Y-%m-%d %H:%M:%S
    - default: 默认为一周前时间
    - required: True
- limit
    - type: integer
    - description: 每页显示的条数
    - default: 10
    - required: True
- offset
    - type: integer
    - description: 偏移量
    - default: 0
    - required: True
- zone
    - type: string
    - description: 区域
    - default: 默认为xb3，可选xb2,hb2
    - required: True
- owner
    - type: string
    - description: 所有者
    - default: 基石智算的账户ID
    - required: True
- user_id
    - type: string
    - description: 用户ID
    - default: 基石智算的账户ID
    - required: True

### 6、get_distributed_training_detail_log   返回分布式训练任务的详细日志

- end_time
    - type: string
    - description: 结束时间，格式为纳秒时间戳1745304819402256896
    - default: 当前时间
    - required: True
- start_time
    - type: string
    - description: 开始时间，格式为纳秒时间戳1745283219402259200
    - default: 默认为12小时前
    - required: True
- fuzzy
    - type: boolean
    - description: 是否模糊
    - default: True
    - required: False
- reverse
    - type: boolean
    - description: 是否反转
    - default: True
    - required: True
- size
    - type: integer
    - description: 每页显示的条数
    - default: 100
    - required: True
- train_uuid
    - type: string
    - description: 训练ID
    - default: 来自上下文train_uuid，如果上下文没有，则需要询问，从get_distributed_training获取
    - required: True
- zone
    - type: string
    - description: 区域
    - default: 默认为xb3，可选xb2、hb2
    - required: True
- owner
    - type: string
    - description: 所有者
    - default: 基石智算的账户ID
    - required: True
- user_id
    - type: string
    - description: 用户ID
    - default: 基石智算的账户ID
    - required: True

### 7、get_inference_service   返回已经创建的推理服务

- zone
    - type: string
    - description: 区域标识，从上下文获取，选项：xb3,xb2,hb2
    - default: xb3
    - required: True
- owner
    - type: string
    - description: 用户名
    - default: 基石智算的账户ID
    - required: True
- key_words
    - type: string
    - description: 关键字
    - default: ""
    - required: False
- page
    - type: integer
    - description: 页码
    - default: 1
    - required: False
- size
    - type: integer
    - description: 每页数量
    - default: 10
    - required: False

### 8、get_inference_service_log   返回推理服务日志

- zone
    - type: string
    - description: 区域标识，从上下文获取，选项：xb3,xb2,hb2
    - default: xb3
    - required: True
- owner
    - type: string
    - description: 用户名
    - default: 基石智算的账户ID
    - required: True
- service_id
    - type: string
    - description: 服务ID
    - default: 来自上下文service_id，如果上下文没有，则需要询问，从get_inference_service获取
    - required: True
- size
    - type: integer
    - description: 每页数量
    - default: 100
    - required: True
- reverse
    - type: boolean
    - description: 是否反转
    - default: True
    - required: True
- start_time
    - type: string
    - description: 开始UTC时间
    - default: 默认为24小时前时间，格式为%Y-%m-%dT%H:%M:%S.000Z
    - required: False
- end_time
    - type: string
    - description: 结束UTC时间
    - default: 默认为当前时间，格式为%Y-%m-%dT%H:%M:%S.000Z
    - required: False
