# CoreshubMCP服务器


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

## 2、运行

### 2.1、在命令行运行

#### （1）首先配置环境变量

可以在代码中配置，在settings.py中配置

```python
class Settings:
    access_key = os.getenv("QY_ACCESS_KEY_ID","基石智算的AK")
    secret_key = os.getenv("QY_SECRET_ACCESS_KEY","基石智算的SK")
    user_id = os.getenv("CORESHUB_USER_ID","基石智算的账户ID")
```

或者在本机系统环境变量配置

```bash
export QY_ACCESS_KEY_ID="基石智算的AK"
export QY_SECRET_ACCESS_KEY="基石智算的SK"
export CORESHUB_USER_ID="基石智算的账户ID"
```

#### （2）在项目根目录使用 [`uv`](https://docs.astral.sh/uv/)直接运行

```bash
uv run src/coreshub_mcp_server
```
#### 命令行参数

- `--debug`: 启用调试模式，输出详细日志
- `--list-plugins`: 列出所有已加载的插件
- `--log-file`: 指定日志文件路径




### 2.2、在Cherry Studio中运行

在Cherry Studio的设置——MCP服务器——添加服务器，进入编辑模式

命令填写:
```bash
sh
```

参数填写:
```bash
-c
cd 项目根目录路径 && uv run src/coreshub_mcp_server
```

环境变量填写:
```bash
QY_ACCESS_KEY_ID=基石智算的AK
QY_SECRET_ACCESS_KEY=基石智算的SK
CORESHUB_USER_ID=基石智算的账户ID
```



## 3、开发

### 3.1、添加新工具

在 `src/coreshub_mcp_server/plugins` 目录下创建新的Python文件，然后实现 `BaseTool` 和/或 `BasePrompt` 的子类。工具和提示现在是分离的概念，可以根据需要只实现其中一种或两种。

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



