"""自动更新模块"""
import requests
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
            如果有新版本，返回 {"version": "x.x.x", "download_url": "...", "changelog": "..."}
            否则返回 None
        """
        try:
            response = requests.get(cls.API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version = data.get("tag_name", "").lstrip("v")
            current_version = __version__

            if version.parse(latest_version) > version.parse(current_version):
                # 查找 exe 下载链接
                download_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break

                return {
                    "version": latest_version,
                    "download_url": download_url or data.get("html_url"),
                    "changelog": data.get("body", ""),
                }

            return None
        except Exception as e:
            print(f"检查更新失败: {e}")
            return None

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
