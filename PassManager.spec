# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import sys

block_cipher = None

# ========================================================
# 1) EXCLUSIONS : modules lourds non utilisés par PassManager
# ========================================================
excludes = [
    # Bibliothèques scientifiques non utilisées
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    
    # Frameworks GUI alternatifs
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
    'kivy',
    
    # Modules tkinter NON utilisés (vérifiés)
    'tkinter.test',
    'tkinter.tix',
    'tkinter.dnd',
    'tkinter.scrolledtext',
    # NOTE : On ne peut PAS exclure :
    # - tkinter.commondialog (requis par filedialog)
    # - tkinter.font (requis par messagebox)
    # - tkinter.colorchooser (peut être utilisé)
    # - tkinter.dialog (requis par simpledialog)
    
    # Modules lourds et inutiles
    'tcl.tzdata',
    'unittest',
    'distutils',
    'setuptools',
    'pip',
    'wheel',
    'email',
    'xml.etree',
    'xml.dom',
    'http',
    'urllib3',
    'requests',
    
    # Modules de développement
    'pydoc',
    'doctest',
    'pdb',
    'profile',
    'cProfile',
]

# ========================================================
# 2) HIDDEN IMPORTS : dépendances critiques
# ========================================================
hiddenimports = []

# CustomTkinter et dépendances
hiddenimports += [
    'customtkinter',
    'darkdetect',  # Utilisé par CustomTkinter pour détecter le mode sombre
]

# Tkinter : TOUS les modules utilisés par PassManager
# IMPORTANT : Ne pas exclure ces modules, sinon ImportError !
hiddenimports += [
    'tkinter',
    'tkinter.filedialog',      # Utilisé dans le script
    'tkinter.messagebox',      # Utilisé dans le script
    'tkinter.simpledialog',    # Utilisé dans le script
    'tkinter.commondialog',    # REQUIS par filedialog
    'tkinter.dialog',          # REQUIS par simpledialog
    'tkinter.font',            # REQUIS par messagebox et autres
    'tkinter.colorchooser',    # Peut être utilisé par widgets
    'tkinter.constants',       # REQUIS par tkinter
    '_tkinter',                # Backend C de tkinter
]

# Cryptography : collecter tous les sous-modules nécessaires
hiddenimports += collect_submodules("cryptography")
hiddenimports += collect_submodules("cryptography.hazmat")
hiddenimports += collect_submodules("cryptography.hazmat.primitives")
hiddenimports += collect_submodules("cryptography.hazmat.backends")

# Pillow (PIL) : modules essentiels pour les icônes PNG
hiddenimports += [
    'PIL._imagingtk',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.PngImagePlugin',  # Essentiel pour les icônes PNG
]

# Pyperclip : backends selon la plateforme
if sys.platform == 'win32':
    hiddenimports += ['pyperclip', 'ctypes', 'ctypes.wintypes']
elif sys.platform == 'darwin':
    hiddenimports += ['pyperclip', 'Foundation', 'AppKit']
else:  # Linux
    hiddenimports += ['pyperclip']

# SQLite est généralement inclus, mais on s'assure
hiddenimports += ['sqlite3']

# Modules standards nécessaires
hiddenimports += [
    'platform',
    'hashlib',
    'base64',
    'os',
    'time',
    'random',
    'string',
    'unicodedata',
]

# ========================================================
# 3) DONNÉES À INCLURE (thèmes, assets, configs)
# ========================================================
datas = []

# CustomTkinter : inclure les thèmes et assets
datas += collect_data_files("customtkinter", excludes=['__pycache__'])

# Tkinter : inclure toutes les données nécessaires
# IMPORTANT : Ne pas exclure les dialogs !
datas += collect_data_files("tkinter", excludes=['__pycache__', 'test'])

# Cryptography : certificats et données nécessaires
datas += collect_data_files("cryptography", excludes=['__pycache__'])

# PIL/Pillow : seulement les plugins PNG (pour les icônes)
# On exclut les autres formats d'image pour alléger
datas += collect_data_files("PIL", excludes=[
    "__pycache__",
    "PIL/Jpeg2KImagePlugin.py",
    "PIL/TiffImagePlugin.py",
    "PIL/WebPImagePlugin.py",
    "PIL/MpegImagePlugin.py",
    "PIL/FpxImagePlugin.py",
    "PIL/PsdImagePlugin.py",
    "PIL/IcoImagePlugin.py",
    "PIL/CurImagePlugin.py",
    "PIL/DdsImagePlugin.py",
    "PIL/EpsImagePlugin.py",
    "PIL/FitsImagePlugin.py",
    "PIL/FliImagePlugin.py",
    "PIL/FtexImagePlugin.py",
    "PIL/GbrImagePlugin.py",
    "PIL/GdImageFile.py",
    "PIL/GifImagePlugin.py",
    "PIL/GimpGradientFile.py",
    "PIL/GimpPaletteFile.py",
    "PIL/HdfImagePlugin.py",
    "PIL/IcnsImagePlugin.py",
    "PIL/ImImagePlugin.py",
    "PIL/ImtImagePlugin.py",
    "PIL/IptcImagePlugin.py",
    "PIL/JpegImagePlugin.py",
    "PIL/McIdasImagePlugin.py",
    "PIL/MicImagePlugin.py",
    "PIL/MpoImagePlugin.py",
    "PIL/MspImagePlugin.py",
    "PIL/PalmImagePlugin.py",
    "PIL/PcdImagePlugin.py",
    "PIL/PcxImagePlugin.py",
    "PIL/PixarImagePlugin.py",
    "PIL/PpmImagePlugin.py",
    "PIL/PsdImagePlugin.py",
    "PIL/SgiImagePlugin.py",
    "PIL/SpiderImagePlugin.py",
    "PIL/SunImagePlugin.py",
    "PIL/TgaImagePlugin.py",
    "PIL/WalImageFile.py",
    "PIL/WmfImagePlugin.py",
    "PIL/XbmImagePlugin.py",
    "PIL/XpmImagePlugin.py",
    "PIL/XVThumbImagePlugin.py",
    "PIL/ImageFilter.py",
    "PIL/ImageFont.py",
    "PIL/ImageOps.py",
    "PIL/ImageDraw.py",
    "PIL/ImageDraw2.py",
    "PIL/ImageChops.py",
    "PIL/ImageEnhance.py",
    "PIL/ImageMath.py",
    "PIL/ImageMode.py",
    "PIL/ImageMorph.py",
    "PIL/ImagePath.py",
    "PIL/ImageQt.py",
    "PIL/ImageSequence.py",
    "PIL/ImageShow.py",
    "PIL/ImageStat.py",
    "PIL/ImageTransform.py",
    "PIL/ImageWin.py",
    "PIL/BmpImagePlugin.py",
])

# ========================================================
# 4) BINAIRES : optimisation selon la plateforme
# ========================================================
binaries = []

# Sur Windows, on peut exclure certaines DLL inutiles
if sys.platform == 'win32':
    # Les DLL tkinter nécessaires seront incluses automatiquement
    pass

# ========================================================
# 5) ANALYSE DES DÉPENDANCES
# ========================================================
a = Analysis(
    ['PassManager.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ========================================================
# 6) OPTIMISATION : retirer les doublons et fichiers inutiles
# ========================================================
# Retirer les tests et __pycache__
a.datas = [x for x in a.datas if not (
    '__pycache__' in x[0] or 
    'test' in x[0].lower() or
    '.pyc' in x[0] or
    '.pyo' in x[0]
)]

# Retirer les fichiers de développement
a.datas = [x for x in a.datas if not any(
    keyword in x[0].lower() 
    for keyword in ['readme', 'license', 'changelog', 'contributing', '.md', '.txt']
)]

# ========================================================
# 7) CRÉATION DE L'ARCHIVE PYZ
# ========================================================
pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

# ========================================================
# 8) CONFIGURATION DE L'EXÉCUTABLE
# ========================================================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PassManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,           # Retire les symboles de débogage → plus léger
    upx=True,             # Compression UPX (si disponible) → encore plus léger
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # Pas de console (GUI uniquement)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='passmanager_icon.ico',
    version_file=None,    # Vous pouvez ajouter un fichier de version Windows
)

# ========================================================
# 9) INFORMATIONS DE BUILD
# ========================================================
print("\n" + "="*60)
print("PassManager - Configuration de build")
print("="*60)
print(f"Plateforme : {sys.platform}")
print(f"Mode : One-File (tout dans un seul .exe)")
print(f"Console : Desactivee (GUI)")
print(f"Optimisations : Strip + UPX")
print(f"Modules exclus : {len(excludes)}")
print(f"Hidden imports : {len(hiddenimports)}")
print("Modules tkinter requis : TOUS INCLUS")
print("="*60 + "\n")
