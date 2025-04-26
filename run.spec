# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=['C:\\Users\\sachd\\optical_management'],  # Path to your project folder
    binaries=[],
    datas=[
        ('manage.py', '.'),  # Ensure manage.py is copied to the root of the EXE bundle
        ('optical_management/settings.py', 'optical_management'),  # Correct path to settings.py
        ('optical_management/urls.py', 'optical_management'),  # Correct path to urls.py
        ('optical_management/__init__.py', 'optical_management'),  # Include __init__.py if needed
        ('optical_management/wsgi.py', 'optical_management'),  # Include wsgi.py for deployment (if needed)
        ('optical_management/asgi.py', 'optical_management'),
        ('templates/*', 'templates/'),  # Include the templates folder
        ('customers/*', 'customers/'),  # Include the customer folder
        ('db.sqlite3', '.'),  # Include the database file (if applicable)
        # Add other necessary files here (e.g., migrations, static, media)
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',  # Name of the EXE file
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],  # Your app icon
    distpath='dist/run_app',
)
