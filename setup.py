#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'serverlessPythonScheduled',
    packages = ['serverless_pyScheduled'],
    version = "0.0.2",
    license='Apache2',
    description = "Serverless Python Metadata example",
    author = 'OCLC Platform Team',
    author_email = "devnet@oclc.org",
    url = 'http://oclc.org/developer/home.en.html',
    download_url = 'git@github.com:OCLC-Developer-Network/pyMetadataStuff.git',
    install_requires = ['boto3 >=1.9']
)
