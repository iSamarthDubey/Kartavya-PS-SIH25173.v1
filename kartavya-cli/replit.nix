{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.virtualenv
    pkgs.git
    pkgs.curl
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.bash
    pkgs.which
    pkgs.vim
    pkgs.less
    pkgs.man
    pkgs.tree
    pkgs.htop
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      # Needed for pandas / numpy
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      # Needed for pygame
      pkgs.glib
    ];
    
    PYTHONPATH = "${placeholder "out"}/src";
    PIP_DISABLE_PIP_VERSION_CHECK = "1";
    PYTHONUNBUFFERED = "1";
    
    # Rich terminal support
    FORCE_COLOR = "1";
    TERM = "xterm-256color";
  };
}
