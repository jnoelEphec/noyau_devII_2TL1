# Mephenger

Ce logiciel a été développé dans le cadre du projet EpheCom de la haute-école
[EPHEC](ephec.be).

# Mise en place de l'environnement 

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

# Configurer l'aplication

Kivy a besoin de connaitre le chemin absolu du dossier du projet, pour cela le
plus simple est de définir la variable d'environnement `PRJ_ROOT`, par exemple
dans un ficher `.env`:

```shell
PRJ_ROOT=chemin/vers/le/dossier/du/projet
```

---

# Construire et installer le packet pypy

> WIP

# Utiliser ce projet avec [nix](https://nixos.org/explore.html)

> Note: ne fonctionne que sous Unix (Linux, BSD, MacOS...)

Ce projet est un [flake nix](https://nixos.wiki/wiki/Flakes) et met à
disposition une [devshell](https://github.com/numtide/devshell), permettant
aux développeur-se-s de travailler dans des environnement rigoureusement
controllés.

Les fichiers le configurant sont `flake.nix`, `flake.lock` (ne doit pas être
édité à la main) et `devshell.toml`.

Installer nix:

```shell
script="$(mktemp)"
curl -L https://nixos.org/nix/install -o "$script"
sh "$script" --daemon
rm "$script"
```

Entrer l'environnement de développement:

```shell
nix develop
```

Tester le projet:

```shell
nix check
```

Lancer l'app:

```shell
nix run
```

Plus d'informations dans le [manuel nix](https://nixos.org/manual/nix/stable/).
