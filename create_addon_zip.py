files = ['__init__.py', 'background.py', 'dataio.py', 'equirectangular.py', 'progress.py', 'setup.py', 'blender_gui.py', 'xstools.py']

from zipfile import ZipFile

z = ZipFile("XSection360_Addon.zip", "w")

for f in files:
    path = 'XSection360/' + f
    z.write(path, f'XSection360/{f}')

z.close()
