{
  lib,
  buildPythonApplication,
  buildPythonPackage,
  fetchPypi,
  setuptools,
  pyqt6,
  pillow,
  saneyaml,
  qt6,
  utsushi,
}:

buildPythonApplication {
  pname = "scanning-gui";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  build-system = [ setuptools ];

  dependencies = [
    pyqt6
    pillow
    saneyaml
  ];

  nativeBuildInputs = [
    qt6.wrapQtAppsHook
    qt6.qtbase
  ];

  # buildPythonApplication does its own wrapping; let it, and merge Qt's
  # env (plugin paths etc.) plus utsushi onto PATH into that single wrapper.
  dontWrapQtApps = true;
  preFixup = ''
    makeWrapperArgs+=("''${qtWrapperArgs[@]}")
    makeWrapperArgs+=(--prefix PATH : ${lib.makeBinPath [ utsushi ]})
  '';

  meta = {
    description = "Fullscreen scanning kiosk GUI";
    mainProgram = "scanning-gui";
    license = lib.licenses.mit; # set to your actual license
  };
}
