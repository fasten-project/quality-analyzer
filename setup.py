from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='quality-analyzer',
    version='0.0.1',
    description='FASTEN RAPID Plugin',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='',
    author_email='',
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    keywords='',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'fasten',
        'lizard',
        'requests',
        'gitpython',
        'svn'
    ]
)
