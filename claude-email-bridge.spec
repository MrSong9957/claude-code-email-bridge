# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
用于打包 Claude Email Bridge 为桌面应用
"""

block_cipher = None

a = Analysis(
    ['gui/tkinter_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含示例配置文件
        ('.env.example', '.'),
    ],
    hiddenimports=[
        # tkinter 相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        # 项目模块
        'config',
        'config.settings',
        'mail',
        'mail.receiver',
        'mail.sender',
        'mail.parser',
        'queue',
        'queue.manager',
        'core',
        'core.executor',
        'gui',
        'gui.mail_providers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Claude Email Bridge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI应用不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico'  # 需要准备图标文件
)
