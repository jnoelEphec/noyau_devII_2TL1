# If you don't know what this file is, you can safely ignore it
{
  inputs = {
    devshell.url = "github:numtide/devshell";
    nixpkgs.url = "nixpkgs";
  };

  outputs = { devshell, nixpkgs, self, ... } @ inputs: let
    systems = [ "x86_64-linux" ];
    mkOutputs = system: let

      pkgs = nixpkgs.lib.recursiveUpdate nixpkgs (import nixpkgs {
        inherit system;
        overlays = [ devshell.overlay ];
      });

      pname = "chat";

      pythonPkg = with pkgs.python39.pkgs; buildPythonPackage rec {
        inherit pname;
        version = "0.1.0";

        src = ./.;

        buildInputs = [ kivy ];
        propagateBuildInputs = [ kivy ];

        doCheck = false;

        meta.homepage = "https://github.com/Austreelis/prejet-dev2-2tl1-5";
      };

      pythonEnv = pkgs.python39.withPackages (pkgs: with pkgs; [
        kivy
        pythonPkg
      ]);

    in {
      devShell.${system} = pkgs.devshell.fromTOML ./devshell.toml;

      packages.${system}.${pname} = pythonPkg;

      defaultPackage.${system} = self.packages.${system}.${pname};

      apps.${system}.${pname} = {
        type = "app";
        program = "${pythonEnv}/bin/python -m ${pname}";
      };

      defaultApp = {
        type = "app";
        program = self.apps.${system}.${pname};
      };
    };
  in with builtins; foldl'
    nixpkgs.lib.recursiveUpdate
    { }
    (map mkOutputs systems);
}
