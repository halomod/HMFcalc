'''
Created on May 20, 2013

@author: Steven
'''
from setuptools import setup, find_packages
import os

version = '1.0.2'
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
    long_description=read('README'),
    keywords="halo mass function",
    url="https://github.com/steven-murray/HMFcalc"
)
