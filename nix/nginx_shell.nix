# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"

,    project_dir ? builtins.toString ./..
,  nix_shell_dir ? "${project_dir}/_nix-shell"
,   gunicorn_dir ? "${nix_shell_dir}/gunicorn"
,     django_dir ? "${nix_shell_dir}/django"
,      nginx_dir ? "${nix_shell_dir}/nginx"

,           port
}:

# HOW TO CALL? {{- {{-
# ====================================================
# This Nix shell expression depends on `nix/dev_shell.nix`.
#
#     nix-shell --arg "port" "8001" nix/nginx_shell.nix
#
#  or, to replace the calling shell:
#
#     exec nix-shell --arg "port" "8001" nix/nginx_shell.nix
#
#  or, when serving from a privileged port (e.g., 80):
#
#     # TODO See issue #24
#     # NOTE Is it ok to run NGINX as root?
#     #      Yes: https://unix.stackexchange.com/questions/134301/
#
#     nix-shell --arg "port" "80" nix/nginx_shell.nix
#
#  For production, use:
#
#     nix-shell --arg "port" "443" nix/nginx_shell.nix
#
# > NOTE STATIC ASSETS NOT SERVED WHEN USING "sudo"
# >
# >      Permissions. The whole project is probably
# >      served from a  home directory, and NGINX's
# >      `nobody`  user  does  not have  access  to
# >      it.  For  example, files  and  directories
# >      in  the "slate-2"  repo have  644 and  755
# >      permissions,  respectively,  but the  home
# >      directory has 750,  meanning that `nobody`
# >      either  has to  be the  owner of  the home
# >      directory  or it  has to  be in  the group
# >      that has read rights on the home dir.
# >
# >      The following should help:
# >
# >          sudo -a -G <home-dir-allowed-group> nobody
#
#   TODO Perhaps moving out  the static assets from
#        the home directory would be more secure.`
#
# }}- }}-
# HOW TO MONITOR? {{- {{-
# ====================================================
#
#    watch -n 1 "{ ls -l _nix-shell/*/*pid ; echo ; sudo ps axf | egrep 'gunicorn|nginx' ; }"
#
# From this thread: https://unix.stackexchange.com/q/64736/85131
#
# }}- }}-

# TODO look into `nginx` package in Nixpkgs
# NOTE ERRORS ON FIRST RUN {{- {{-
#      ===================
# There will probably be a lot of errors along the lines of:
#
#     2023/05/05 15:55:03 [emerg] 3106282#3106282: mkdir() "/var/cache/nginx/proxy" failed (13: Permission denied)
#
# This is because  (as far as I was able  to figure it
# out) the  NGINX Nix  package has been  compiled with
# these  hard paths  that HAVE  TO exist,  even though
# they won't  be touched  (and some  of them  could be
# over-ridden; e.g., error.log - see below).`
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
#     # https://serverfault.com/questions/235154
#     # (The user should be whoever starts NGINX.)
#     sudo chown -R $(whoami):$(whoami) /var/{log,cache}/nginx
#
# As a one-liner:
#
#     sudo mkdir -p /var/log/nginx/ && sudo touch /var/log/nginx/error.log && sudo mkdir -p /var/cache/nginx/proxy && sudo mkdir -p /var/cache/nginx/uwsgi && sudo mkdir -p /var/cache/nginx/scgi && sudo mkdir -p /var/cache/nginx/fastcgi && sudo mkdir -p /var/cache/nginx/client_body & sudo chown -R $(whoami):$(whoami) /var/{log,cache}/nginx
# }}- }}-

# OUTDATED NOTE? (2023-07-08) {{- {{-
# NOTE https://discourse.nixos.org/t/how-to-add-local-files-into-nginx-derivation-for-nix-shell/6603
# Opted to keep `nginx.conf` out of the store, because
# 1. it is already in version control
# 2. if changes need to be made, one would have to create another config to override it
# -- Although, are there merits to keep it in the store?
#    + with NixOS, this would be a no brainer, but then the config would have to be rebuilt
#    + if a default config is kept in the store, it could still be over-ridden with another one using `-c`
#    Nonetheless, when this repo is deployed via a `shell.nix`, it may be more convenient to refer to a non-store config.
#
# let
#   nginx-with-config = pkgs.writeScriptBin "nginx-alt" ''
#     exec ${pkgs.nginx}/bin/nginx -c ${./nginx.conf} "$@"
#   '';
#
# in
# }}- }}-

let

  # NGINX doc's most valuable pages:
  # + [Alphabetical index of directives](http://nginx.org/en/docs/dirindex.html)
  # + [Alphabetical index of variables](http://nginx.org/en/docs/varindex.html)

  pkgs = # {{-
    import
      # The downloaded archive will be (temporarily?) housed in the Nix store
      # e.g., "/nix/store/gk9x7syd0ic6hjrf0fs6y4bsd16zgscg-source"
      # (Try any of the `fetchTarball` commands  below  in `nix repl`, and it
      #  will print out the path.)
      ( builtins.fetchTarball nixpkgs_url) { config = {}; overlays = []; }
  ;
  nixpkgs_url = "https://github.com/nixos/nixpkgs/tarball/${nixpkgs_commit}";

  # }}-
  timestamp = # {{-
    builtins.readFile (
      pkgs.runCommand
        "timestamp"
        { when = builtins.currentTime; }
        "echo -n `date -d @$when +%Y-%m-%d_%H-%M-%S` > $out"
    )
  ;
  # https://discourse.nixos.org/t/how-to-create-a-timestamp-in-a-nix-expression/30329

  # }}-
  nginx_conf = # {{-
    import
      ./nginx/nginx_conf.nix
      { inherit pkgs
                nix_shell_dir
                django_dir
                nginx_dir
                timestamp
                port
        ;
      }
  ;
  # }}-

  # NOTE See https://discourse.nixos.org/t/how-to-add-local-files-into-nginx-derivation-for-nix-shell/6603
  # QUESTION Why use the `*Bin` version?
  # ANSWER Because the NGINX  executable will then be
  #        added to PATH automatically.
  nginx_with_config =
    pkgs.writeShellScriptBin
      "nginx_lynx"
      ''
        exec ${pkgs.nginx}/bin/nginx -c ${nginx_conf} "$@"
      ''
  ;

in

  pkgs.mkShell {

    buildInputs =
      [ pkgs.inotify-tools
        nginx_with_config
      ];

    shellHook =

      let

        gunicorn_pidfile = "${gunicorn_dir}/${timestamp}.pid";
        sudo_string = "${ if ( port < 1024 ) then "sudo" else "" }";

      in

        ''
          set -x
        ''

        # TODO Convert to systemd service instead?
        #      See note above `inotifywait` below.
      + ''
          ( cd ${project_dir}/lynx && \
            gunicorn                  \
            --bind 127.0.0.1:8000     \
            --workers 3               \
            --log-level 'debug'       \
            --preload                 \
            --capture-output          \
            --pid ${gunicorn_pidfile}     \
            --access-logfile "${gunicorn_dir}/access_${timestamp}.log" \
            --error-logfile  "${gunicorn_dir}/error_${timestamp}.log"  \
              mysite.wsgi:application \
            --daemon
          )
        ''

        # NOTE Must   wait    for   Gunicorn's   pidfile,
        #      otherwise the clean-up section below won't
        #      register the  proper command to  shut down
        #      Gunicorn  (the  `cat` is  evaluated  right
        #      away,  not  lazily,   so  if  the  pidfile
        #      doesn't exist,  the command will fail with
        #      `kill -s SIGTERM`).
      + ''
          inotifywait --event create,moved_to,attrib --include '${timestamp}.pid$' ${gunicorn_dir}
        ''

        # NOTE `gunicorn_dir`      is     created      in
        #       `dev_shell.nix`  because  Gunicorn can  be
        #       tested with simple  Just recipe, and NGINX
        #       is  what depends  on Gunicorn  - not  vice
        #       versa.
      + ''
          mkdir -p ${nginx_dir}
          ${sudo_string} $(which nginx_lynx)
        ''

        # NOTE It may  take some  time for NGINX  to shut
        #      down (e.g., after  leaving the Nix shell);
        #      the line below in `ps ax` is a good sign:
        #
        #     2814526 ? S 0:00 nginx: worker process is shutting down
        #

      + ''
          trap \
            "
              ${sudo_string} $(which nginx_lynx) -s quit
              kill -s SIGTERM $( cat ${gunicorn_pidfile} )
            " \
            EXIT
        ''
      ;
    }

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
