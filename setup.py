from setuptools import find_packages, setup

setup(
    name="loqedAPI",
    version="2.1.8",
    description="Python package to use the Loqed Smart Door Lock APIs in a local network. To be used by Home Assistant.",
    url="https://github.com/cpolhout/loqedAPI",
    author="Casper Polhout",
    author_email="cpolhout@gmail.com",
    license="BSD 2-clause",
    packages=find_packages(exclude=["tests", "generator"]),
    install_requires=["aiohttp", "async-timeout"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
