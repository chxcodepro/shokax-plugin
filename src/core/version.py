"""版本信息"""
import subprocess
import os

def get_version() -> str:
    """
    从 git tag 获取版本号

    Returns:
        版本号字符串，如果获取失败返回 "0.0.0"
    """
    try:
        # 尝试从 git tag 获取版本
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            timeout=2
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip("v")
            return version if version else "0.0.0"
    except Exception:
        pass

    # 如果是打包后的 exe，尝试从环境变量获取
    version = os.environ.get("APP_VERSION", "0.0.0")
    return version

__version__ = get_version()

