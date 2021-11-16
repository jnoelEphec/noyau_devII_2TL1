#!/usr/bin/env python
import distutils.cmd
import re
import subprocess
from typing import List, Literal, Optional, Tuple, Union

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


class Requirement:
    PKG_NAME_RE = re.compile("(?:[a-zA-Z][a-zA-Z0-9_-]*)?[a-zA-Z0-9]")
    VERSION_RE = re.compile("[a-zA-Z0-9]+")
    CRITERIA = {">=": 0, "=~": 1, "==": 2}

    def criteria(self, c: int) -> str:
        return {v: k for k, v in self.CRITERIA.items()}[c]

    def __init__(self, r: str):
        package = r
        version = criterion = None
        for c, i in self.CRITERIA.items():
            if c in r:
                package, version = r.split(c, 1)
                version = version.split(".")
                criterion = i
        if not self.PKG_NAME_RE.fullmatch(package):
            raise ValueError(f"Invalid package name: {package}")
        if not all([self.VERSION_RE.fullmatch(v) for v in version]):
            raise ValueError(
                f"Invalid version spec for package {package}: {'.'.join(version)}"
            )

        self._package = package
        self._version = version
        self._criterion = criterion
        self._str = r

    def __str__(self):
        return self._str

    def __hash__(self):
        return hash(self.package) ^ hash(self.version) ^ hash(self.criterion)

    def __gt__(self, o):
        if isinstance(o, str):
            try:
                o = Requirement(o)
                return self > o
            except ValueError:
                return False
        if not isinstance(o, Requirement):
            return False
        return self._as_tuple() > o._as_tuple()

    def __eq__(self, o):
        if isinstance(o, str):
            try:
                o = Requirement(o)
                return self == o
            except ValueError:
                return False
        if not isinstance(o, Requirement):
            return False
        return self._as_tuple() == o._as_tuple()

    def __lt__(self, o):
        return o > self

    def _as_tuple(self) -> (
            str,
            Optional[List[str]],
            Optional[Literal[0, 1, 2]]
    ):
        return self.package, self.version, self.criterion

    @property
    def criterion(self) -> Optional[Literal[0, 1, 2]]:
        return self._criterion

    @property
    def package(self) -> str:
        return self._package

    @property
    def version(self) -> Optional[List[str]]:
        return self._version

    def compatible_with(self, o: Union[str, 'Requirement']) -> Optional[Tuple[
            Optional[bool],
            Optional[bool]
    ]]:
        """
        Check if a requirement is a compatible version of a given package of
        this requirement.

        :return:
            - if `o` is not for the same package: `None`
            - otherwise if the version representation are not compatible
                (e.g. `"1.2.3" and `"0.alpha0"`, or if no version information
                is available): `(None, None)`
            - otherwise a tuple where:
                - the first value is `True` if the requirements' versions are
                    compatible according to this requirement's version
                    compatibility requirement, `False` otherwise
                - the second value is:
                    - `None` if this requirement has a looser version
                        compatibility requirement than `o`'s
                    - `True ` if this requirement's and `o`'s compatibility
                        requirements are the same.
                    - `False` if this requirement has a stricter version
                        compatibility requirement than `o`'s
        """
        if isinstance(o, str):
            return self.compatible_with(Requirement(o))
        p1, v1, c1 = self._as_tuple()
        p2, v2, c2 = o._as_tuple()
        # Check package names are the same
        if p1 != p2:
            return None
        # Check if version info is available for both packages
        # (1)
        if v1 is None or v2 is None:
            return None, None
        # Split major, minor, etc. version info from the last segment
        # (supposedly patch number), if version follows such structure
        major_minor1 = v1
        major_minor2 = v2
        patch1 = patch2 = None
        if v1 is not None and len(v1) > 1:
            major_minor1 = v1[:-1]
            patch1 = v1[-1]
        if v2 is not None and len(v2) > 1:
            major_minor2 = v2[:-1]
            patch2 = v2[-1]
        # Check if version info structure is the same
        if patch1 is None and patch2 is not None or \
                patch1 is not None and patch2 is None \
                or v1 is not None and len(v1) != len(v2):
            return None, None
        # Check if o's version is compatible
        version_compatible = v1 == v2
        if c1 == 1:
            version_compatible = major_minor1 == major_minor2
        elif c1 == 0:
            # We know v1 and v2 are both lists thanks to (1), thus the <=
            # operation is defined
            # noinspection PyTypeChecker
            version_compatible = version_compatible or v1 <= v2

        # Check if version compatibility requirement (a.k.a. criteria) are
        # looser than o's, stricter, or the same
        if c2 > c1:
            return version_compatible, None
        if c1 > c2:
            return version_compatible, False
        return version_compatible, True

    def upgrade(
        self,
        o: Union[str, 'Requirement'],
        *,
        force_compatible_version: bool = False,
        force_keep_criterion: bool = False,
        ignore_looser_criterion: bool = False,
    ) -> 'Requirement':
        """
        Update a requirement from another with a newer version or stricter
        version compatibility requirement.
        """
        if isinstance(o, str):
            return self.upgrade(Requirement(o))
        p1, v1, c1 = self._as_tuple()
        p2, v2, c2 = o._as_tuple()
        is_compatible = self.compatible_with(o)

        if is_compatible is None:
            raise ValueError(
                f"Cannot upgrade package '{p1}' to different package '{p2}'"
            )
        is_version_compatible, is_criterion_compatible = is_compatible
        if not ignore_looser_criterion and is_criterion_compatible is None:
            raise ValueError(
                f"Cannot upgrade package {p1} with a looser version "
                f"compatibility requirement ({self.criteria(c2)}) than its "
                f"current ({self.criteria(c1)})"
            )
        if force_keep_criterion and not is_criterion_compatible:
            raise ValueError(
                f"Cannot upgrade package {p1} with a stricter version "
                f"compatibility requirement ({self.criteria(c2)}) than its "
                f"current ({self.criteria(c1)})"
            )
        if force_compatible_version and not is_version_compatible:
            raise ValueError(
                f"Cannot upgrade package {p1} at version {'.'.join(v1)} to "
                f"non-compatible version {v2}"
            )
        return Requirement(f"{p2}{self.criteria(c2)}{'.'.join(v2)}")


class RequirementsComparison:

    def __init__(
        self,
        ref: Optional[str] = None,
        to: str = "requirements.txt",
        *,
        force_compatible_version: bool = False,
        force_keep_criterion: bool = False,
        ignore_looser_criterion: bool = False,
    ):
        self._ref = ref
        self._to = to
        self._from_to = {r.package: r for r in self._get_requirements(to)}
        self._extra = self._from_to.copy()
        self._merged = self._from_to.copy()
        self._from_ref = {}
        self._missing = {}
        self._stricter = {}
        self._looser = {}
        self._conflicts = {}
        self._behind = {}
        self._ahead = {}

        for r in self._get_requirements(ref):
            if r.package in self._from_ref:
                try:
                    self._from_ref[r.package] = \
                        self._from_ref[r.package].upgrade(
                            r,
                            force_compatible_version=force_compatible_version,
                            force_keep_criterion=force_keep_criterion,
                            ignore_looser_criterion=ignore_looser_criterion
                        )
                except ValueError:
                    raise ValueError(
                        "Got two incompatible requirements of the same package:"
                        f" {self._from_ref[r.package]} and {r}"
                    )
                continue

            try:
                self._merged[r.package] = \
                    self._from_to.get(r.package, r).upgrade(
                        r,
                        force_compatible_version=force_compatible_version,
                        force_keep_criterion=force_keep_criterion,
                        ignore_looser_criterion=ignore_looser_criterion
                    )
                if r.package in self._conflicts:
                    del self._conflicts[r.package]
            except ValueError:
                self._conflicts[r.package] = r

            if r.package in self._extra:
                del self._extra[r.package]

            if r.package not in self._from_to:
                self._from_ref[r.package] = r
                self._missing[r.package] = r
                continue

            self._from_ref[r.package] = r
            to = self._from_to[r.package]

            if r.criterion > to.criterion:
                self._looser[r.package] = r
                if r.package in self._stricter:
                    del self._stricter[r.package]
            elif to.criterion > r.criterion:
                self._stricter[r.package] = r
                if r.package in self._looser:
                    del self._looser[r.package]
            elif r.package in self._stricter:
                del self._stricter[r.package]
            elif r.package in self._looser:
                del self._looser[r.package]

            if r.version > to.version:
                self._behind[r.package] = r
                if r.package in self._ahead:
                    del self._ahead[r.package]
            elif to.version > r.version:
                self._ahead[r.package] = r
                if r.package in self._behind:
                    del self._behind[r.package]
            elif r.package in self._ahead:
                del self._ahead[r.package]
            elif r.package in self._ahead:
                del self._ahead[r.package]

    @staticmethod
    def _get_requirements(source: Optional[str]) -> List[Requirement]:
        if source is None:
            return [Requirement(r) for r in REQUIREMENTS]
        try:
            with open(source) as f:
                return [Requirement(r.strip(" \t\n\r")) for r in f.readlines()]
        except FileNotFoundError:
            return []

    @property
    def ahead(self):
        return self._ahead.values()

    @property
    def behind(self):
        return self._behind.values()

    @property
    def compared_requirements(self):
        return self._from_to.values()

    @property
    def conflicts(self):
        return self._conflicts.values()

    @property
    def extra(self):
        return self._extra.values()

    @property
    def looser(self):
        return self._looser.values()

    @property
    def merged(self):
        return self._merged.values()

    @property
    def missing(self):
        return self._missing.values()

    @property
    def ref_requirements(self):
        return self._from_ref.values()

    @property
    def stricter(self):
        return self._stricter.values()


class GenRequirementsCmd(distutils.cmd.Command):
    """
    A custom command to generate requirements.txt
    """

    description = 'generate requirements.txt'
    user_options = []

    def run(self):
        """Run command."""
        try:
            comparison = RequirementsComparison()
        except ValueError as e:
            self.announce(f"Error: {e}")
            self.announce(f"Could not generate requirements.txt", 1)
            return

        max_len = max([len(r.package) for r in comparison.merged])

        for r in list(comparison.merged) + list(comparison.conflicts):
            presence = " "
            criterion_status = " "
            version_status = "  "
            lvl = 3
            if r in comparison.missing:
                presence = "+"
                lvl = min(2, lvl)
            elif r in comparison.extra:
                presence = "-"
            elif r in comparison.conflicts:
                presence = "!"
                lvl = min(1, lvl)

            if r in comparison.looser:
                criterion_status = "^"
                lvl = min(2, lvl)
            elif r in comparison.stricter:
                criterion_status = "v"

            if r in comparison.ahead:
                version_status = "<-"
            elif r in comparison.behind:
                version_status = "->"
                lvl = min(2, lvl)
            filling = " " * (max_len - len(r.package))
            self.announce(
                f"{presence} {filling}{r.package} {criterion_status} "
                f"{r.criteria(r.criterion)} {version_status} "
                f"{'.'.join(r.version)}", lvl
            )

        from_txt = list(comparison.compared_requirements)
        from_ref = list(comparison.ref_requirements)
        for r in comparison.conflicts:
            txt_r = None
            for t_r in from_txt:
                if t_r.package == r.package:
                    txt_r = t_r
            ref_r = None
            for r_r in from_ref:
                if r_r.package == r.package:
                    ref_r = r_r
            self.warn(
                f"Package {r.package} has conflicting version specification:\n"
                f"  - requirements.txt: {txt_r}\n"
                f"  - setupt script:    {ref_r}"
            )

        if len(comparison.conflicts) > 0:
            self.announce("Error: Unresolved conflicts", 1)
            return

        merged_requirements = RequirementsComparison().merged

        def generate():
            lines = [f"{req}\n" for req in merged_requirements]
            lines.sort()
            with open("requirements.txt", "wt") as f:
                f.writelines(lines)

        self.execute(generate, [], "generating requirements.txt")

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
