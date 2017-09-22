from setuptools import setup

with open('README.rst') as f:
    long_description=f.read()

setup(
    name='log_parser',
    version='0.1',
    description='Parse log and filter results',
    long_description=long_description,
    author='Peter Denmead',
    author_email='log_parser@example.com',
    url='https://example.com',
    packages=['log_parser',
              'profiler'],
    install_requires=[
        'pytest == 3.2.2',
        'statistics == 1.0.3.5',
        'tox == 2.8.2'],
    entry_points={
        'console_scripts': [
            'log_parser=log_parser.log_parser:main',
        ],
    },
)
