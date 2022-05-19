#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
$ python setup.py register sdist upload

First Time register project on pypi
https://pypi.org/manage/projects/


Pypi Release
$ pip3 install twine

$ python3 setup.py sdist
$ twine upload dist/keri-0.0.1.tar.gz

Create release git:
$ git tag -a v0.4.2 -m "bump version"
$ git push --tags
$ git checkout -b release_0.4.2
$ git push --set-upstream origin release_0.4.2
$ git checkout master

Best practices for setup.py and requirements.txt
https://caremad.io/posts/2013/07/setup-vs-requirement/
"""

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages, setup

setup(
    name='caxe',
    version='0.0.1',  # also change in src/caxe/__init__.py
    license='Apache Software License 2.0',
    description='Credential Attribute XBRL Extraction Tool',
    long_description="Tool for extracting credential attributes from xBRL documents",
    author='Philip S. Feairheller',
    author_email='pfeairheller@gmail.com',
    url='https://github.com/WebOfTrust/caxe',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://caxe.readthedocs.io/',
        'Changelog': 'https://caxe.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/WebOfTrust/caxe/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.10.3',
    install_requires=[
        'keri>=0.6.6',
        'multicommand>=1.0.0',
        'Arelle>=1.0.0',
        'lxml>=4.6.3',
        'blake3>=0.3.1',
        'pycountry>=20.7.3,<21.0.0',
        'falcon>=3.1.0',
    ],
    extras_require={
    },
    tests_require=[
        'coverage>=5.5',
        'pytest>=6.2.5',
    ],
    setup_requires=[
    ],
    entry_points={
        'console_scripts': [
            'cake = caxe.app.cli.cake:main',
        ]
    },
)
