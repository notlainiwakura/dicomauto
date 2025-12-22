# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for DICOM Tag Updater

block_cipher = None

a = Analysis(
    ['update_dicom_tags.py'],
    pathex=[],
    binaries=[],
    datas=[('dcmutl.py', '.')],  # Include dcmutl.py as data
    hiddenimports=['pydicom', 'dcmutl', 'pydicom.uid', 'pydicom.errors'],
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
    name='DICOMTagUpdater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for command-line interface
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

