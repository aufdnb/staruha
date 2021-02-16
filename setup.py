#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "Click>=6.0",
    "boto3==1.17.7",
    "botocore==1.20.7",
    "click==7.1.2",
    "nltk==3.5",
    "pandas==1.2.2",
    "slack-sdk==3.3.2",
    "wordcloud==1.8.1",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest",
]

setup(
    author="bobrinik",
    author_email="",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="staruha checks for rumors and tells it to the world.",
    entry_points={
        "console_scripts": [
            "staruha=staruha.cli:main",
        ],
    },
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords="staruha",
    name="staruha",
    packages=find_packages(include=["staruha"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/bobrinik/staruha",
    version="0.1.0",
    zip_safe=False,
)
