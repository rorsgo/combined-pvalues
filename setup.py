#!/usr/bin/env python

from setuptools import setup
import cpv
version = cpv.__version__

setup(name='cpv',
      version=version,
      description='combine p-values',
      author='Brent Pedersen',
      author_email='bpederse@gmail.com',
      maintainer='Rodrigo Santos',
      maintainer_email='rorvts@gmail.com',
      license='MIT',
      url='https://github.com/rorsgo/combined-pvalues',
      packages=['cpv', 'cpv.tests'],
      install_requires=['scipy', 'numpy', 'toolshed', 'interlap'],
      scripts=['cpv/comb-p'],
      long_description=open('README.md').read(),
      classifiers=["Topic :: Scientific/Engineering :: Bio-Informatics"],
 )