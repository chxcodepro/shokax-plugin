"""自动更新模块"""
import requests
import sys
from typing import Optional
from packaging import version
from src.core.version import __version__


class UpdateChecker:
    """更新检查器"""

    REPO_OWNER = "chxcodepro"
    REPO_NAME = "shokax-plugin"
    API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

    @classmethod
    def check_update(cls) -> Optional[dict]:
        """
        检查是否有新版本

        Returns:
            如果有新版本，返回 {
                "version": "x.x.x",
                "setup_url": "setup安装包URL",
                "portable_url": "单文件exe URL",
                "changelog": "更新日志"
            }
            否则返回 None
        """
        try:
            response = requests.get(cls.API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version = data.get("tag_name", "").lstrip("v")
            current_version = __version__

            if version.parse(latest_version) > version.parse(current_version):
                # 查找 setup 和 portable exe 下载链接
                setup_url = None
                portable_url = None

                for asset in data.get("assets", []):
                    name = asset["name"]
                    if "setup" in name.lower() and name.endswith(".exe"):
                        setup_url = asset["browser_download_url"]
                    elif name.endswith(".exe") and "setup" not in name.lower():
                        portable_url = asset["browser_download_url"]

                return {
                    "version": latest_version,
                    "setup_url": setup_url,
                    "portable_url": portable_url,
                    "changelog": data.get("body", ""),
                }

            return None
        except Exception as e:
            print(f"检查更新失败: {e}")
            return None

    @classmethod
    def is_installed_version(cls) -> bool:
        """
        判断当前是否为安装版本

        Returns:
            True: 安装版本（在 Program Files 或 AppData 下）
            False: 便携版本
        """
        if not getattr(sys, 'frozen', False):
            return False

        exe_path = sys.executable.lower()
        # 检查是否在典型的安装目录下
        return any(path in exe_path for path in [
            'program files',
            'program files (x86)',
            r'appdata\local\programs'
        ])

    @classmethod
    def download_update(cls, url: str, save_path: str, progress_callback=None) -> bool:
        """
        下载更新文件

        Args:
            url: 下载链接
            save_path: 保存路径
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            是否下载成功
        """
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            return True
        except Exception as e:
            print(f"下载更新失败: {e}")
            return False
