"""版本信息"""
import subprocess
import os
import sys

def get_version() -> str:
    """
    获取版本号

    优先级：
    1. 从 git tag 获取（开发环境）
    2. 从 exe 文件版本信息获取（打包后）
    3. 从环境变量获取（构建时）
    4. 返回默认值 "0.0.0"

    Returns:
        版本号字符串
    """
    # 1. 尝试从 git tag 获取版本（开发环境）
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            timeout=2
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip("v")
            if version:
                return version
    except Exception:
        pass

    # 2. 尝试从 exe 文件版本信息获取（打包后）
    if getattr(sys, 'frozen', False):
        try:
            import win32api
            exe_path = sys.executable
            info = win32api.GetFileVersionInfo(exe_path, '\\')
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}"
            if version != "0.0.0":
                return version
        except Exception:
            pass

    # 3. 尝试从环境变量获取（构建时）
    version = os.environ.get("APP_VERSION", "0.0.0")
    return version

__version__ = get_version()

