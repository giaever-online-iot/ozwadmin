#!/usr/bin/env python3

import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name = "ozwadmin-splash",
    version = "0.0.1",
    author = "Joachim M. Giæver",
    description = "Simple splash screen",
    long_description = "Splash to help connect nessecary plugs to the snap package of ozwadmin",
    url = "https://git.giaever.org/home-assistant-snap/ozwadmin",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3"
    ],
    install_requires = requirements,
    python_requires = '>=3.8',
    entry_points = {
        'console_scripts': 'ozwadmin-splash=splash.main:run'
    }
)
