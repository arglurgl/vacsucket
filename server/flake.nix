{
  description = "Flake using pyproject.toml metadata";

  inputs = {
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixos-unstable";
    };

    nixos-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs = {
    nixpkgs,
    pyproject-nix,
    ...
  }: let
    inherit (nixpkgs) lib;
    forAllSystems = lib.genAttrs lib.systems.flakeExposed;

    project = pyproject-nix.lib.project.loadPyproject {
      projectRoot = ./.;
    };

    pythonAttr = "python3";
  in {
    devShells = forAllSystems (system: {
      default = let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.${pythonAttr};
        pythonEnv = python.withPackages (project.renderers.withPackages {inherit python;});
      in
        pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.ffmpeg
            pkgs.stdenv.cc.cc.lib
          ];

          shellHook = ''
            if [ -n "$LD_LIBRARY_PATH" ]; then
              export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:"$LD_LIBRARY_PATH"
            else
              export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib
            fi
          '';
        };
    });

    packages = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.${pythonAttr};
      in {
        default = python.pkgs.buildPythonPackage (project.renderers.buildPythonPackage {inherit python;});
      }
    );
  };
}
