from PyInstaller import __main__ as pyi

params = [
    '-F',#single file
    'cv2capture.py'
]

#pyinstaller -F main.py

pyi.run(params)