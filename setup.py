#!/usr/bin/env python

from setuptools import setup

long_description = """Python wrapper for the R pscl package.
"""

appname = "pscl"
version = "0.01"

setup(**{
    "name": appname,
    "version": version,
    "packages": [
        'pscl',
        ],
    "author": "Thom Neale",
    "author_email": "twneale@gmail.com",
    "long_description": long_description,
    "description": 'Python wrapper for the R pscl package.',
    "license": "MIT",
    "url": "http://twneale.github.com/pypscl/",
    "platforms": ['any'],
    "scripts": [
    ]
})
