import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpm",
    version="0.1",
    scripts=['scripts/cpm'],
    author="Jordi Sánchez",
    description="Chromos Package Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jorsanpe/cpm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
