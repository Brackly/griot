from setuptools import setup, find_packages

import sys

sys.path.append("./src")

import datetime
import griot

local_version = datetime.datetime.utcnow().strftime("%Y%m%d.%H%M%S")

setup(
    name="griot",

    version=griot.__version__ + "+" + local_version,
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
