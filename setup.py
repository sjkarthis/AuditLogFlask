from setuptools import setup, find_packages

setup(
    name='project1',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'shared-utils @ file://../shared_utils',
    ],
)
