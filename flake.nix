{
  description = "Flake for LoRaWAN IOT TH Sensors";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          python312
          rclone

          (pkgs.python312.withPackages (ps: with ps; [
            paho-mqtt
            requests
            python-dotenv
            ruff
            git-filter-repo
          ]))
        ];
      };
    };
}
