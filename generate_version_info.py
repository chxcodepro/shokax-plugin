"""生成 PyInstaller 版本信息文件"""
import os
import sys

def generate_version_info(version: str):
    """生成版本信息文件"""
    # 解析版本号
    parts = version.split('.')
    major = parts[0] if len(parts) > 0 else '0'
    minor = parts[1] if len(parts) > 1 else '0'
    patch = parts[2] if len(parts) > 2 else '0'

    version_tuple = f"({major}, {minor}, {patch}, 0)"
    version_string = f"{major}.{minor}.{patch}.0"

    content = f"""# UTF-8
#
# For more details about fixed file info:
# See https://learn.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'chxcodepro'),
        StringStruct(u'FileDescription', u'shokaX plugin - Text snippet tool'),
        StringStruct(u'FileVersion', u'{version_string}'),
        StringStruct(u'InternalName', u'shokaX plugin'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 chxcodepro'),
        StringStruct(u'OriginalFilename', u'shokaX plugin.exe'),
        StringStruct(u'ProductName', u'shokaX plugin'),
        StringStruct(u'ProductVersion', u'{version_string}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    with open('file_version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Generated file_version_info.txt with version {version_string}")

if __name__ == '__main__':
    version = os.environ.get('APP_VERSION', '0.0.0')
    generate_version_info(version)
