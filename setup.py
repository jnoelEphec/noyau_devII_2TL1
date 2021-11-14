#!/usr/bin/env python
import distutils.cmd
import subprocess

from pkg_resources import parse_requirements
from setuptools import setup

REQUIREMENTS = [
    "alabaster==0.7.12",
    "Babel==2.9.1",
    "certifi==2021.5.30",
    "charset-normalizer==2.0.4",
    "colorama==0.4.4",
    "dnspython==2.1.0",
    "docutils==0.17.1",
    "idna==3.2",
    "imagesize==1.2.0",
    "Jinja2==3.0.1",
    "Kivy==2.0.0",
    "Kivy-Garden==0.1.4",
    "MarkupSafe==2.0.1",
    "packaging==21.0",
    "Pygments==2.10.0",
    "pymongo==3.12.0",
    "pyparsing==2.4.7",
    "python-dotenv==0.19.0",
    "pytz==2021.1",
    "requests==2.26.0",
    "snowballstemmer==2.1.0",
    "Sphinx==4.2.0",
    "sphinxcontrib-applehelp==1.0.2",
    "sphinxcontrib-devhelp==1.0.2",
    "sphinxcontrib-htmlhelp==2.0.0",
    "sphinxcontrib-jsmath==1.0.1",
    "sphinxcontrib-qthelp==1.0.3",
    "sphinxcontrib-serializinghtml==1.1.5",
    "urllib3==1.26.6",
]

NAME = "mephenger"

try:
    # Get version from the flake rather than git tags.
    # Uncommon but avoids git build dependency.
    VERSION = subprocess.check_output(
        ["grep", "-o", "-m", "1", "version = \"[a-zA-Z0-9.-]*\"", "flake.nix"],
    ).decode().replace("version =", "").replace("\"", "").strip()
except subprocess.CalledProcessError:
    VERSION = "0.dev0"


class GenRequirementsCmd(distutils.cmd.Command):
    """
    A custom command to generate requirements.txt
    """

    description = 'generate requirements.txt'
    user_options = []

    def run(self):
        """Run command."""
        with open("requirements.txt", "wt") as req_file:
            req_file.writelines([r + "\n" for r in REQUIREMENTS])

    # No options, the following methods do nothing
    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass


setup(
    name=NAME,
    version=VERSION,
    url="https://github.com/Austreelis/devII_2TL1-5",
    install_requires=REQUIREMENTS,
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
    cmdclass={
        'generate_requirements': GenRequirementsCmd,
    },
)
