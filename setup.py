'''
Created on May 20, 2013

@author: Steven
'''
from setuptools import setup, find_packages
version = '1.0.0'

setup(
    name="HMFcalc",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    requires=['numpy', 'pandas'],
    author="Steven Murray",
    author_email="steven.jeanette.m@gmail.com",
    description="A halo mass function calculator web-app in django",
    keywords="halo mass function",
    url="https://github.com/steven-murray/HMFcalc",
    # could also include long_description, download_url, classifiers, etc.
)
