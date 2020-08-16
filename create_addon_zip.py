files = ['__init__.py', 'background.py', 'dataio.py', 'equirectangular.py', 'progress.py', 'setup.py', 'xs360_addon.py', 'xstools.py']

from zipfile import ZipFile

z = ZipFile("tests/xs360.zip", "w")

for f in files:
    z.write(f, f'XSection360/{f}')

z.close()
