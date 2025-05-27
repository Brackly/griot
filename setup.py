from setuptools import setup, find_packages

import sys

sys.path.append("./src")

import datetime
import griot


setup(
    name="griot",

    version=griot.__version__ ,
    author="khanbrackly@gmail.com",
    description="wheel file based on griot/src",
    packages=find_packages(where="./src"),
    package_dir={"": "src"},
    entry_points={
        "packages": [
            "main=griot.main:main",
        ],
    },
    install_requires=[

        "setuptools"
    ],
)
