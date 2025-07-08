# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[('whisper.cpp/build/bin/whisper-cli', 'whisper.cpp/build/bin'),
              ('/Users/sergebressloff/.pyenv/versions/qt3d-env/lib/python3.10/site-packages/_cffi_backend.cpython-310-darwin.so', 'lib'),
              ('/Users/sergebressloff/.pyenv/versions/qt3d-env/lib/python3.10/site-packages/scipy/sparse/linalg/_propack/_dpropack.cpython-310-darwin.so', 'scipy/sparse/linalg/_propack')
              ],
    datas=[('viewer_assets/*', 'viewer_assets'),
        ('whisper.cpp/models/ggml-base.en.bin', 'whisper.cpp/models'),
        ('audio', 'audio'),
        ],
    hiddenimports=[
        'sounddevice',
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtCore',
        'PySide6.Qt3DExtras',
        'PySide6.QtOpenGL',
        'shiboken6',
        '_hashlib',
        '_blake2',
        '_sha3',
        '_md5',
        'numpy.core._methods',
        'numpy.lib.format',
        'tokenizers',
        'transformers.models.bert',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='my_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
