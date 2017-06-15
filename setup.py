from distutils.core import setup
import sys

import fitanalysis


requires = ['fitparse', 'numpy', 'pandas']
if sys.version_info < (2, 7):
  requires.append('argparse')

with open('LICENSE', 'r') as f:
  license_content = f.read()

setup(name='fitanalysis',
      version=fitanalysis.__version__,
      description='Python library for analysis of ANT/Garmin .fit files',
      author='Michael Traver',
      url='https://github.com/mtraver/python-fitanalysis',
      license=license_content,
      packages=['fitanalysis'],
      install_requires=requires)
