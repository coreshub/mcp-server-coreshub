"""
CoreshubMCP服务器 - 提供轻量、可扩展的MCP服务框架
"""
import argparse
import asyncio
import importlib
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """设置日志"""
    handlers = []

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    ))
    handlers.append(console_handler)

    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        handlers.append(file_handler)

    # 配置根日志记录器
    logging.basicConfig(
        level=level,
        handlers=handlers
    )


def discover_plugins() -> None:
    """发现并加载所有插件"""
    # 获取当前路径
    current_path = Path(__file__).parent
    # 获取插件路径
    plugins_path = current_path / "plugins"

    # 如果插件目录不存在则创建
    if not plugins_path.exists():
        plugins_path.mkdir(exist_ok=True)
        return

    for plugin_file in plugins_path.glob("*.py"):
        if plugin_file.name.startswith("__"):
            continue

        # 导入插件模块
        module_name = f"coreshub_mcp_server.plugins.{plugin_file.stem}"
        try:
            importlib.import_module(module_name)
            logging.info(f"加载插件: {module_name}")
        except Exception as e:
            logging.error(f"加载插件失败: {module_name}, 错误: {str(e)}")


def init_environment() -> None:
    """初始化和验证环境变量"""
    from coreshub_mcp_server.settings import settings

    required_envs = {
        "CORESHUB_BASE_URL": settings.base_url,
        "QY_ACCESS_KEY_ID": settings.access_key,
        "QY_SECRET_ACCESS_KEY": settings.secret_key,
        "CORESHUB_USER_ID": settings.user_id
    }
    logging.info(f"required_envs: {required_envs}")

    missing_envs = [key for key, value in required_envs.items() if not value]
    if missing_envs:
        logging.error(f"缺少必需的环境变量: {', '.join(missing_envs)}")
        sys.exit(1)

    logging.info("环境变量验证通过")


def main() -> None:
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="CoreshubMCP服务器"
    )
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--list-plugins", action="store_true", help="列出所有已加载的插件")
    parser.add_argument("--log-file", type=str, help="日志文件路径")

    args = parser.parse_args()

    # 设置日志级别
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level, args.log_file)

    # 初始化和验证环境变量
    # init_environment()

    # 发现并加载所有插件
    discover_plugins()

    # 如果指定了--list-plugins参数，则列出所有已加载的插件并退出
    if args.list_plugins:
        from .base_plugin import ToolRegistry

        tool_classes = ToolRegistry.get_all_tool_classes()
        prompt_classes = ToolRegistry.get_all_prompt_classes()

        print("已加载的工具插件:")
        for name, cls in tool_classes.items():
            print(f"  - {name}: {cls.tool_description}")

        print("\n已加载的提示插件:")
        for name, cls in prompt_classes.items():
            print(f"  - {name}: {cls.prompt_description}")

        return

    # 运行服务器（延迟导入，确保所有工具都已注册）
    from .server import serve

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.info("服务器已停止")
    except Exception as e:
        logging.error(f"服务器异常: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
