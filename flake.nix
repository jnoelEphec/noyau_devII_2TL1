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

      pythonEnv = pkgs.python39.withPackages (pkgs: with pkgs; [
        kivy
      ]);

    in {
      devShell.${system} = pkgs.devshell.fromTOML ./devshell.toml;

      apps.${system}.mephenger = {
        type = "app";
        program = "${pythonEnv}/bin/python -m ${self}/mephenger";
      };

      defaultApp.${system} = {
        type = "app";
        program = self.apps.${system}.mephenger.program;
      };
    };
  in with builtins; foldl'
    nixpkgs.lib.recursiveUpdate
    { }
    (map mkOutputs systems);
}
