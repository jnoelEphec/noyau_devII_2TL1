#!/usr/bin/env python
import subprocess

from pkg_resources import parse_requirements
from setuptools import setup


NAME = "mephenger"

try:
    # Get version from flake rather than git tags
    # Uncommon but avoids git build dependency
    VERSION = subprocess.check_output(
        ["grep", "-o", "-m", "1", "version = \"[a-zA-Z0-9.-]*\"", "flake.nix"],
    ).decode().replace("version =", "").replace("\"", "").strip()
except subprocess.CalledProcessError:
    VERSION = "0.dev0"

with open("requirements.txt") as requirements:
    setup(
        name=NAME,
        version=VERSION,
        url="https://github.com/Austreelis/devII_2TL1-5",
        install_requires=[str(req) for req in
                          parse_requirements(requirements)],
        packages=[NAME],
        package_dir={NAME: NAME},
        entry_points={
            "console_scripts": [
                NAME + "=" + NAME,
            ],
        },
        classifiers=[
            "Topic :: Communications :: Chat",
            "Development Status :: 1 - Planning",
        ],
    )
