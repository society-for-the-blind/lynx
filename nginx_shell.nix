{ pkgs ? import <nixpkgs> {} }:

# NOTE https://discourse.nixos.org/t/how-to-add-local-files-into-nginx-derivation-for-nix-shell/6603
# Opted to keep `nginx.conf` out of the store, because
# 1. it is already in version control
# 2. if changes need to be made, one would have to create another config to override it
# -- Although, are there merits to keep it in the store?
#    + with NixOS, this would be a no brainer, but then the config would have to be rebuilt
#    + if a default config is kept in the store, it could still be over-ridden with another one using `-c`
#    Nonetheless, when this repo is deployed via a `shell.nix`, it may be more convenient to refer to a non-store config.

# let
#   nginx-with-config = pkgs.writeScriptBin "nginx-alt" ''
#     exec ${pkgs.nginx}/bin/nginx -c ${./nginx.conf} "$@"
#   '';
#
# in

pkgs.mkShell {
  buildInputs = [
    # TODO for when a `just` recipe is created for NGINX: it runs as a daemon by default, same as PostgreSQL! Set trap / clean-up step to shut it down when exiting the shell.
    pkgs.nginx
  ];


  shellHook =
  ''
    ${pkgs.nginx}/bin/nginx -p $(pwd) -c nginx.conf

    # NOTE It may take some time for NGINX to shut down; the line in `ps ax` is a good sign:
    # 2814526 ?        S      0:00 nginx: worker process is shutting down

    trap \
    "
    ${pkgs.nginx}/bin/nginx -p $(pwd) -c nginx.conf -s quit
    " \
    EXIT

  '';
}
