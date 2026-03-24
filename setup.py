from setuptools import find_packages, setup

setup(
    name="loqedAPI",
    version="2.1.11",
    description="Python package to use the Loqed Smart Door Lock APIs in a local network. To be used by Home Assistant.",
    url="https://github.com/cpolhout/loqedAPI",
    author="Casper Polhout",
    author_email="cpolhout@gmail.com",
    license="BSD 2-clause",
    packages=find_packages(exclude=["tests", "generator"]),
    install_requires=[
        "aiohttp",
        "async-timeout",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "aioresponses",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
)
