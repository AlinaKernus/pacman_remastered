# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['pac-man-1'],  # Add pac-man-1 to Python path
    binaries=[],
    datas=[
        ('Assets', 'Assets'),
        ('pac-man-1', 'pac-man-1'),
        ('res', 'res'),  # Add res folder for tiles
        # settings.json will be created in user directory, not included
    ],
    hiddenimports=[
        'pygame',
        'socketio',
        'requests',
        'engineio',
        'client',
        'GameScene',
        'PacMan',
        'Ghost',
        'FoodPiece',
        'MapGenarator',
        'TileRenderer',
        'Variables',
        'DB_communicator',
        'socketio.client',
        'engineio.client',
        'src.utils.path_helper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_paths.py'],
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
    name='PacmanRemastered',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here: 'icon.ico'
)

