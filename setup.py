#!/usr/bin/env python
"""setup.py"""

import sys

from setuptools import setup
from subprocess import check_output
from os.path import isdir

if isdir("../.git") or isdir(".git"): # debian source tarballs don't contain .git
    version_cmd = "git describe --tags --always --long"
    version = check_output(version_cmd.split(" ")).decode().strip()
    print("Working on git version {}".format(version))
    # enforce https://www.python.org/dev/peps/pep-0440
    items = version[1:].split('-')
    if len(items) == 3:
        version = '{}+{}'.format(items[0], items[2][1:])
    print("--> PEP-0440 version will be {}".format(version))
    with open('runtests/version.py', 'w') as f:
        f.write('__version__ = "{}"\n'.format(version))
else:
    version = "undefined"

setup(name='runtests',
      version=version,
      description='Runtests.',
      long_description='''Runtests provides a runtest binary to run python unittest suites.''',
      author='Chris Blaise',
      author_email='cblaise@ariata.com',
      url='https://arista.com',
      scripts=['bin/runtests'],
      data_files=[('/usr/lib/runtests',['files/test_shell.key','files/test_shell.pub'])],
      packages=['runtests'],
      install_requires=[],
      license='GPL',
      #      test_suite='',
      #      cmdclass={'test': PyTest},
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: General Public License v2 (GPL-2)',
          'Environment :: Console',
          'Operating System :: POSIX',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.9'
      ))
