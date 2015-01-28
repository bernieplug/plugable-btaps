from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plugable-btaps',
    version='0.8.3',

    description='Open Source Library for Controlling the Plugable PS-BTAPS1 Bluetooth AC Outlet Switch',
    long_description=long_description,
    url='https://github.com/bernieplug/plugable-btaps',

    # Author details
    author='Plugable Technologies',
    author_email='ivan@plugable.com',

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Home Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],

    keywords='bluetooth home-automation',

    packages=['btaps'],
    install_requires=['pybluez'],

    entry_points={
        'console_scripts': [
            'btaps=btaps:main',
        ],
    },
)