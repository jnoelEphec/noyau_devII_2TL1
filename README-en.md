# Mephenger

This software has been developped for the EpheCom project by the
[EPHEC](ephec.be) college.

# Setting up the development environment

## Linux

```shell
python -m venv env
./env/bin/activate
python -m pip install setuptools
python setupy.py generate_requirements
python -m pip install -r requirements.txt
```

## Windows

> WIP

# Configuring the app

Kivy needs the project root's absolute path. The probably easiest way is to
define the `PRJ_ROOT` environment variable, e.g. in a `.env` file:

```shell
PRJ_ROOT=path/to/projet/root
```

---

# Build and install pypy package

> WIP

# Using [nix](https://nixos.org/explore.html)

> Note: Only supported on Unix platforms

This project is a [nix flake](https://nixos.wiki/wiki/Flakes) and provides a
[devshell](https://github.com/numtide/devshell), allowing developers to work
in a controlled environment.

Installing nix:

```shell
script="$(mktemp)"
curl -L https://nixos.org/nix/install -o "$script"
sh "$script" --daemon
rm "$script"
```

Entering the development shell:

```shell
nix develop
```

Running tests:

```shell
nix check
```

Running the app:

```shell
nix run
```

More in the [nix manual](https://nixos.org/manual/nix/stable/).
