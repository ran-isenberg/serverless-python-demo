#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

setup(
    name='infrastructure',
    version='1.0',
    description='CDK code for deploying the serverless service',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.13',
    ],
    url='https://github.com/ran-isenberg/serverless-python-demo',
    author='Ran Isenberg, Heitor Lessa',
    author_email='ran.isenberg@ranthebuilder.cloud',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.json']},
    include_package_data=True,
    python_requires='>=3.13',
    install_requires=[],
)
