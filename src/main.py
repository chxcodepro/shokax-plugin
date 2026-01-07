"""程序入口"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import App


def main():
    app = App()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
