# shokaX Plugin

[![Release](https://img.shields.io/github/v/release/chxcodepro/shokax-plugin)](https://github.com/chxcodepro/shokax-plugin/releases)
[![License](https://img.shields.io/github/license/chxcodepro/shokax-plugin)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/chxcodepro/shokax-plugin)

A lightweight text snippet tool with IME-style popup panel for quick text insertion and wrapping.

## ✨ Features

- **🎯 Quick Access**: Trigger popup panel with global hotkey (default: `Ctrl+Space`)
- **📝 Text Wrapping**: Select text and wrap it with predefined templates
- **🔄 Auto Update**: Automatic update checking from GitHub Releases
- **🚀 Easy Installation**: Interactive installer with startup options
- **⌨️ Dual Input**: Support both keyboard (1-9, arrows, Enter/Esc) and mouse operations
- **🎨 Multiple Templates**: Built-in templates for alerts, collapsible sections, and styled blocks

## 📦 Installation

### Option 1: Download Installer (Recommended)

1. Download the latest `shokaX_plugin_setup_v*.exe` from [Releases](https://github.com/chxcodepro/shokax-plugin/releases)
2. Run the installer and follow the setup wizard
3. Optionally enable "Start on boot" during installation

### Option 2: Portable Executable

1. Download `shokaX plugin.exe` from [Releases](https://github.com/chxcodepro/shokax-plugin/releases)
2. Run directly without installation

### Option 3: Run from Source

```bash
# Clone the repository
git clone https://github.com/chxcodepro/shokax-plugin.git
cd shokax-plugin

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## 🎮 Usage

1. **Launch**: Start the application from desktop shortcut or system tray
2. **Trigger**: Press `Ctrl+Space` (customizable in main window) to show popup panel
3. **Select**: Use number keys (1-9) or arrow keys to navigate, press Enter to confirm
4. **Text Wrapping**: Select text in any application, trigger the panel, and choose a template to wrap the selected text

### Available Templates

- **Alerts**: Primary, Info, Warning, Success, Danger styles
- **Collapsible**: Expandable sections with different themes
- **Blocks**: Styled content blocks

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Windows OS
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) (for building installer)

### Project Structure

```
shokax-plugin/
├── src/
│   ├── core/           # Core functionality
│   │   ├── hotkey.py   # Global hotkey listener
│   │   ├── output.py   # Text output and cursor positioning
│   │   ├── updater.py  # Update checker
│   │   └── version.py  # Version management
│   ├── ui/             # User interface
│   │   ├── main_window.py   # Main window and system tray
│   │   └── popup_panel.py   # Popup selection panel
│   ├── config/         # Configuration
│   │   └── menu_config.py   # Menu data and templates
│   └── main.py         # Application entry point
├── build.spec          # PyInstaller build configuration
├── installer.iss       # Inno Setup installer script
└── requirements.txt    # Python dependencies
```

### Build Commands

```bash
# Build standalone executable
python -m PyInstaller build.spec --noconfirm

# Build installer (requires Inno Setup)
iscc installer.iss
```

### Architecture

```
App (src/app.py) - Main controller
 ├── MainWindow - Main window + system tray + update checker
 ├── PopupPanel - Popup selection panel
 ├── HotkeyManager - Global hotkey listener (pynput)
 ├── UpdateChecker - GitHub Releases update checker
 └── output_text() - Clipboard paste + cursor positioning + text wrapping

Signal Flow:
  HotkeyManager.triggered → App._on_hotkey → PopupPanel.show_at_cursor
  PopupPanel.output_selected → App._on_output → output_text()
```

## 🚀 Release Process

1. Create a git tag: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions automatically builds and publishes to Releases

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Global hotkey support by [pynput](https://github.com/moses-palmer/pynput)
- Packaged with [PyInstaller](https://www.pyinstaller.org/)
- Installer created with [Inno Setup](https://jrsoftware.org/isinfo.php)

## 📧 Contact

- Author: chxcodepro
- Repository: [https://github.com/chxcodepro/shokax-plugin](https://github.com/chxcodepro/shokax-plugin)
- Issues: [https://github.com/chxcodepro/shokax-plugin/issues](https://github.com/chxcodepro/shokax-plugin/issues)
