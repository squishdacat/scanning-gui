with import <nixpkgs> { };
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "rpi-scanner-frontend";
  src = ../main.py;
  propagatedBuildInputs = [
    saneyaml
    pillow
    pyqt6
  ];
}
