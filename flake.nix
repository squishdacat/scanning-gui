{
  description = "Scanning kiosk GUI";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems f;
    in
    {
      # This is what makes it feel native: applying the overlay adds
      # `scanning-gui` to pkgs, so pkgs.scanning-gui works everywhere.
      overlays.default = final: prev: {
        scanning-gui = final.python3Packages.callPackage ./package.nix { };
      };

      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in
        {
          default = pkgs.scanning-gui;
        }
      );
    };
}
