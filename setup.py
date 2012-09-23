#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='blueblazer',
      version='1.0',
      description='A random alcoholic cocktail generator.',
      author='Charles Nelson',
      author_email='cnelsonsic@gmail.com',
      url='https://github.com/cnelsonsic/blueblazer',
      packages=find_packages(),
      scripts=['bin/blueblazer-http',],
      license='LICENSE',
      install_requires=['PyYAML>=3.10', 'pyxdg>=0.19', 'flask>=0.9'],
     )
