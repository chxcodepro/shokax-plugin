## 常用命令

```bash
# 开发运行
python src/main.py

# 安装依赖
pip install -r requirements.txt

# 打包单文件 exe（输出到 dist/shokaX plugin.exe）
python -m PyInstaller build.spec --noconfirm

# 打包安装程序（需要先安装 Inno Setup）
# 1. 先打包 exe
python -m PyInstaller build.spec --noconfirm
# 2. 使用 Inno Setup 编译安装程序
iscc installer.iss
```

## 发布流程

1. 创建 git tag：`git tag v1.0.0`
2. 推送 tag：`git push origin v1.0.0`
3. GitHub Actions 自动打包并发布到 Releases

## 架构概述

仿输入法风格的快捷文本输入工具。默认 Ctrl+空格 触发弹出面板（可在主窗口修改），选择后输出预定义文本并自动定位光标。

### 新功能

- **文字包裹**：选中文字后唤出面板，选择模板会将文字包裹在模板中
- **自动更新**：启动时自动检查 GitHub Releases，支持一键下载更新
- **安装程序**：提供交互式安装程序，支持开机自启动等选项

### 组件关系

```
App (src/app.py) - 控制器，协调各组件
 ├── MainWindow - 主窗口 + 系统托盘 + 更新检查
 ├── PopupPanel - 弹出选择面板
 ├── HotkeyManager - 全局热键 (pynput)
 ├── UpdateChecker - 更新检查器
 └── output_text() - 剪贴板粘贴 + 光标定位 + 文字包裹

信号流：HotkeyManager.triggered → App._on_hotkey → PopupPanel.show_at_cursor
       PopupPanel.output_selected → App._on_output → output_text()
```

### 核心模块

- **menu_config.py**: 菜单数据定义，`get_output(menu_key, sub_key)` 返回 `(text, cursor_offset)`
- **hotkey.py**: pynput 监听全局热键（默认 Ctrl+空格），通过 Qt Signal 通知
- **output.py**: 剪贴板写入 → Ctrl+V 粘贴 → 左键移动光标 → 文字包裹
- **updater.py**: GitHub Releases 更新检查和下载
- **version.py**: 版本管理（从 git tag 读取）

### UI 层

- **popup_panel.py**: 无边框悬浮窗口，键盘(1-9/↑↓/Enter/Esc)和鼠标双操作
- **main_window.py**: 启动/停止控制，关闭时最小化到托盘，更新检查

### 菜单结构

5个主选项，其中提醒/折叠/方块有5个子选项(primary/info/warning/success/danger)。每个输出模板的光标偏移量通过 `cursor_offset` 计算。

