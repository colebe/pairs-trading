from setuptools import setup, find_packages

setup(
    name='pairs_trading',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'yfinance', 'scipy', 'matplotlib', 'scikit-learn', 'statsmodels'
    ],
    entry_points={
        'console_scripts': [
            'pairs-trader=main:main'
        ],
    },
)