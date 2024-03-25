from setuptools import setup, find_packages
import os

datafiles = [(root, [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk('data')]

setup(
    name='cachebrowser',
    description='A proxy-less censorship resistance tool',
    version='0.1.1',
    author='Hadi Zolfaghari',
    author_email='hadi@cs.umass.edu',
    url='https://www.cachebrowser.net',
    license='MIT',
    packages=find_packages(include=['cachebrowser', 'cachebrowser.*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cachebrowser = cachebrowser.main:cachebrowser'
        ]
    },
    data_files=datafiles,
    install_requires=[
        'mitmproxy>=0.17',
        'click>=6.6',
        'PyYAML',
        'peewee',
        'tornado',
        'appdirs',
        'ipwhois',
    ],
)
