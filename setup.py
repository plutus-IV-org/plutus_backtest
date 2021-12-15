from setuptools import setup , find_packages

setup(
    name='backt',
    version='0.0.1',
    packages= find_packages(),
    install_requires=[
        'pandas',
        'yfinance',
        'numpy',
        'matplotlib.pyplot',
        'datetime'
    ],
)