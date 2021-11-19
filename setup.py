#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
differential_gene_expression=differential_gene_expression:setup
"""

#with open('README.rst') as infile:
#    LONG_DESCRIPTION = infile.read()

#with open('myplugin/version.py') as infile:
#    exec(infile.read())

setup(name='differntial_gene_expression',
      version="0.1",
      description='Menubar plugin for differential gene expression',
      long_description="",
      url="",
      author='',
      author_email='',
      packages = find_packages(),
      package_data={},
      entry_points=entry_points
    )