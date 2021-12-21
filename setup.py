from setuptools import setup , find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='showel-responsibility',

    version='0.0.6',

    description="backt is a python library \
    for backtesting your investment decisions using Python 3.9 and above.",

    long_description_content_type='text/markdown',

    license="MIT",

    keywords="backtest",

    author="IlliaBoloto",

    author_email="ils.boloto96@gmail.com",

    long_description=long_description,

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',
# Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',

        # Indicate which Topics are covered by the package
        'Topic :: Software Development',
        'Topic :: Office/Business :: Financial',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.9',
    ],

    packages=find_packages(include=['backt', 'backt.*']),

    url="https://github.com/witmul/backt/tree/main",

    python_requires=">=3.9.0",

    install_requires=[
        "numpy>=1.21.2",
        "pandas>=1.3.3",
        "plotly>=5.4.0",
        "yfinance>=0.1.63"
    ],
)