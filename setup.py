#!/usr/bin/env python
from setuptools import setup, find_packages

def setup_package():
  setup(
    name='elopackage',
    version='0.0.1',
    description='Player Rating',
    url='https://github.com/bf108/elo_package',
    author='Ben Farrell',
    author_email='ben.farrell08@gmail.com',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    include_package_data = True,
    install_requires=['numpy','pandas','scipy','matplotlib','pathlib']
  )

if __name__ == "__main__":
    setup_package()
