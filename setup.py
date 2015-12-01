#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

version = ''
with open('introspy/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

author = ''
with open('introspy/__init__.py', 'r') as fd:
    author = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version or not author:
    raise RuntimeError('Cannot find version or author information')

original_dir = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
try:
    setup(
        name="Introspy-Analyzer",
        version=version,
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,

        # metadata for upload to PyPI
        author=author,
        author_email="nabla.c0d3@gmail.com",
        description="Introspy-Analyzer",
        license="GPL",
        keywords="ios android",
        url="https://isecpartners.github.io/Introspy-iOS/",
        long_description=open("README.md").read(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GPL License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
        install_requires=[
            'six'
        ],
        platforms='All',
    )

finally:
    os.chdir(original_dir)
