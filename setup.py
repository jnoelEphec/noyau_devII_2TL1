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
    "kivy-deps.angle==0.3.0",
    "kivy-deps.glew==0.3.0",
    "kivy-deps.sdl2==0.3.1",
    "Kivy-Garden==0.1.4",
    "MarkupSafe==2.0.1",
    "packaging==21.0",
    "Pygments==2.10.0",
    "pymongo==3.12.0",
    "pyparsing==2.4.7",
    "pypiwin32==223",
    "python-dotenv==0.19.0",
    "pytz==2021.1",
    "pywin32==301",
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
    PKG_NAME_RE = re.compile("(?:[a-zA-Z][a-zA-Z0-9._-]*)?[a-zA-Z0-9]")
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
                f"Invalid version spec for package {package}: "
                f"{'.'.join(version)}"
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
    def major_version(self):
        """
        All but the last element of the version if it is has more than one part.
        The whole version otherwise.
        """
        return self.version if self.version is None or len(self.version) == 1 \
            else self.version[:-1]

    @property
    def patch(self):
        """
        The last element of the version if it is has more than one part.
        None otherwise.
        """
        return None if self.version is None or len(self.version) == 1 \
            else self.version[-1]

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
        # Check package names are the same
        if self.package != o.package:
            return None
        # Check if version info is available for both packages
        # (1)
        if self.version is None or o.version is None:
            return None, None
        # Check if version info structure is the same
        if self.patch is None and o.patch is not None or \
                self.patch is not None and o.patch is None \
                or (self.version is not None
                    and len(self.version) != len(o.version)):
            return None, None
        # Check if o's version is compatible
        version_compatible = self.version == o.version
        if self.criterion == 1:
            version_compatible = self.major_version == o.major_version
        elif self.criterion == 0:
            # We know v1 and v2 are both lists thanks to (1), thus the <=
            # operation is defined
            # noinspection PyTypeChecker
            version_compatible = version_compatible or self.version <= o.version

        # Check if version compatibility requirement (a.k.a. criteria) are
        # looser than o's, stricter, or the same
        if o.criterion > self.criterion:
            return version_compatible, None
        if self.criterion > o.criterion:
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
        is_compatible = self.compatible_with(o)

        if is_compatible is None:
            raise ValueError(
                f"Cannot upgrade package '{self.package}' to different package "
                f"'{o.package}'"
            )
        is_version_compatible, is_criterion_compatible = is_compatible
        if not ignore_looser_criterion and is_criterion_compatible is None:
            raise ValueError(
                f"Cannot upgrade package {self.package} with a looser version "
                f"compatibility requirement ({self.criteria(o.criterion)}) than "
                f"its current ({self.criteria(self.criterion)})"
            )
        if force_keep_criterion and not is_criterion_compatible:
            raise ValueError(
                f"Cannot upgrade package {self.package} with a stricter "
                f"version compatibility requirement "
                f"({self.criteria(o.criterion)}) than its current "
                f"({self.criteria(self.criterion)})"
            )
        if force_compatible_version and not is_version_compatible:
            raise ValueError(
                f"Cannot upgrade package {self.package} at version "
                f"{'.'.join(self.version)} to non-compatible version "
                f"{o.version}"
            )
        return Requirement(
            f"{o.package}{self.criteria(o.criterion)}{'.'.join(o.version)}"
        )


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
        """
        Compare two sets of requirements, one being the reference.
        """
        self._ref = ref
        self._to = to
        self._from_to = {}

        # Incrementally add in packages to catch incompatible ones
        for r in self._get_requirements(to):
            try:
                self._from_to[r.package] = \
                    self._from_to.get(r.package, r).upgrade(
                        r,
                        force_compatible_version=force_compatible_version,
                        force_keep_criterion=force_keep_criterion,
                        ignore_looser_criterion=ignore_looser_criterion
                    )
            except ValueError:
                raise ValueError(
                    "Got two incompatible requirements of the same package:"
                    f" {self._from_to[r.package]} and {r}"
                )

        # This one will be emptied as we add requirements from the reference
        self._extra = self._from_to.copy()
        # This one will be filled further more as we add requirements from the
        # reference
        self._merged = self._from_to.copy()
        # These one will be filled up with requirements from the reference
        self._from_ref = {}
        self._missing = {}
        self._stricter = {}
        self._looser = {}
        self._conflicts = {}
        self._behind = {}
        self._ahead = {}

        # Add the reference's requirements
        for r in self._get_requirements(ref):
            if r.package in self._from_ref:
                # If requirement's package is already known from the reference,
                # just check if it is compatible with the already merged in
                # requirement and replace it in the reference's requirements
                try:
                    self._merged[r.package] = \
                        self._merged[r.package].upgrade(
                            r,
                            force_compatible_version=force_compatible_version,
                            force_keep_criterion=force_keep_criterion,
                            ignore_looser_criterion=ignore_looser_criterion
                        )
                    self._from_ref[r.package] = self._merged[r.package]
                except ValueError:
                    raise ValueError(
                        "Got two incompatible requirements of the same package:"
                        f" {self._from_ref[r.package]} and {r}"
                    )
                continue

            # If requirements is not already known from the reference, we
            # should first check if it is compatible with the same package from
            # the already merged in set (if there is one, hence why `.get`)
            try:
                self._merged[r.package] = \
                    self._merged.get(r.package, r).upgrade(
                        r,
                        force_compatible_version=force_compatible_version,
                        force_keep_criterion=force_keep_criterion,
                        ignore_looser_criterion=ignore_looser_criterion
                    )
                if r.package in self._conflicts:
                    del self._conflicts[r.package]
            except ValueError:
                # Requirement isn't compatible, add it to conflicting packages
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
        """
        A sequence of requirements whose version is newer than the reference.
        """
        return self._ahead.values()

    @property
    def behind(self):
        """
        A sequence of requirements whose version is older than the reference.
        """
        return self._behind.values()

    @property
    def compared_requirements(self):
        """
        The sequence of requirements compared to the reference set.
        """
        return self._from_to.values()

    @property
    def conflicts(self):
        """
        A sequence of packages from the reference set that conflict with the
        compared set.
        """
        return self._conflicts.values()

    @property
    def extra(self):
        """
        A sequence of packages that are not in the reference set.
        """
        return self._extra.values()

    @property
    def looser(self):
        """
        A sequence of packages whose version compatibility requirement (a.k.a
        the criterion of Requirements objects) is looser than the reference.
        """
        return self._looser.values()

    @property
    def merged(self):
        return self._merged.values()

    @property
    def missing(self):
        """
        A sequence of packages that are in the reference set but missing from
        the compared set.
        """
        return self._missing.values()

    @property
    def ref_requirements(self):
        """
        The sequence of requirements from the reference set.
        """
        return self._from_ref.values()

    @property
    def stricter(self):
        """
        A sequence of packages whose version compatibility requirement (a.k.a
        the criterion of Requirements objects) is stricter than the reference.
        """
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
