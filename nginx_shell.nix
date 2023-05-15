# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"
,  nix_shell_dir ? "" # --argstr
,      timestamp ? "" # --argstr
,           port ? "80"
}:

# HOW TO CALL?
# ====================================================
# The  most  common way  will  probably  be from  this
# repo  after  the  main  shell.nix  already  exported
# `NIX_SHELL_DIR` so:
#
#     nix-shell --argstr "nix_shell_dir" "${NIX_SHELL_DIR}" --argstr "timestamp" "$(date '+%Y-%m-%d_%H-%M-%S')" --argstr "port" "8000" nginx_shell.nix

# TODO look into `nginx` package in Nixpkgs
# NOTE ERRORS ON FIRST RUN {{-
#      ===================
# There will probably be a lot of errors along the lines of:
#
#     2023/05/05 15:55:03 [emerg] 3106282#3106282: mkdir() "/var/cache/nginx/proxy" failed (13: Permission denied)
#
# This is because (as far as I was able to figure it out) the NGINX Nix package has been compiled with these hard paths that HAVE TO exist, even though they won't be touched (and some of them could be over-ridden; e.g., error.log - see below).`
#
# These have done the trick thus far:
#
#     sudo mkdir -p /var/log/nginx/
#     sudo touch /var/log/nginx/error.log
#     sudo mkdir -p /var/cache/nginx/proxy
#     sudo mkdir -p /var/cache/nginx/uwsgi
#     sudo mkdir -p /var/cache/nginx/scgi
#     sudo mkdir -p /var/cache/nginx/fastcgi
#     sudo mkdir -p /var/cache/nginx/client_body
#
# As a one-liner:
#
#     sudo mkdir -p /var/log/nginx/ && sudo touch /var/log/nginx/error.log && sudo mkdir -p /var/cache/nginx/proxy && sudo mkdir -p /var/cache/nginx/uwsgi && sudo mkdir -p /var/cache/nginx/scgi && sudo mkdir -p /var/cache/nginx/fastcgi && sudo mkdir -p /var/cache/nginx/client_body
# }}-

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

let

  nixpkgs_url = "https://github.com/nixos/nixpkgs/tarball/${nixpkgs_commit}";
  pkgs =
    import
      # The downloaded archive will be (temporarily?) housed in the Nix store
      # e.g., "/nix/store/gk9x7syd0ic6hjrf0fs6y4bsd16zgscg-source"
      # (Try any of the `fetchTarball` commands  below  in `nix repl`, and it
      #  will print out the path.)
      ( builtins.fetchTarball nixpkgs_url) { config = {}; overlays = []; }
  ;

  # Realized in `shellHook`
  nginx_dir = nix_shell_dir + "/nginx";

  nginx_conf =
    pkgs.writeTextFile {

      name = "nginx.conf";

      text =

        # WARNING `error_log` here is a must {{-
        #         ==========================
        # This directive can be  over-ridden in lower levels /
        # contexts (e.g., see in `http`).
        #
        # An  `error_log`  directive  **must** stand  here  in
        # either   case,  otherwise   NGINX  will   check  for
        # `/var/log/nginx/error.log`, as  this value  has been
        # compiled into it. From the
        # [docs](http://nginx.org/en/docs/ngx_core_module.html#error_log):
        #
        # > If  on the  main configuration  level (i.e.,  `main`
        # > context) writing a  log to a file  is not explicitly
        # > defined, the default file will be used.
        #
        #
        # The file in the main `error_log` declaration doesn't
        # have  to  exist  (unlike  `/var/log/nginx/error.log`
        # when  no  main   level  `error_log`  declaration  is
        # present), but if there  is no new default specified,
        # then `nginx` will simply blow up for some reason. Go
        # figure.

        # }}-
        ''
          error_log ${nginx_dir}/nginx_main_error.log debug;
          pid ${nginx_dir}/nginx_${timestamp}.pid;
        ''

      + # `nginx` won't run without this block.
        ''
          events {}
        ''

      + ''
          http {
              access_log ${nginx_dir}/access_${timestamp}.log;
              error_log ${nginx_dir}/error_${timestamp}.log debug;

              # TODO r?syslog

              server {
                  listen ${port};
                  server_name localhost;

                  location / {
                      # your website configuration goes here
                      # for example:
                      root ${nix_shell_dir}/..;
                      index ${nix_shell_dir}/../README.md;
                  }
              }
          }
        ''
      ;
    };

    nginx_with_config =
      pkgs.writeShellScriptBin
        "nginx_lynx"
        ''
          exec ${pkgs.nginx}/bin/nginx -c ${nginx_conf} "$@"
        ''
    ;

in
  pkgs.mkShell {
    buildInputs = [
      # TODO for when a `just` recipe is created for NGINX: it runs as a daemon by default, same as PostgreSQL! Set trap / clean-up step to shut it down when exiting the shell.
      nginx_with_config
    ];


    shellHook =
      ''
        mkdir -p ${nginx_dir}

        nginx_lynx

        # NOTE It may take some time for NGINX to shut down; the line in `ps ax` is a good sign:
        # 2814526 ?        S      0:00 nginx: worker process is shutting down

        trap \
          "nginx_lynx -s quit" \
          EXIT

      ''
    ;
  }

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
