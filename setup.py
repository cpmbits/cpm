# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpm-cli",
    version="0.3",
    scripts=['scripts/cpm'],
    author="Jordi Sánchez",
    description="Chromos Package Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jorsanpe/cpm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
