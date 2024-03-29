# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{         nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"

,            project_dir ? builtins.toString ./..
,          nix_shell_dir ? "${project_dir}/_nix-shell"
,           gunicorn_dir ? "${nix_shell_dir}/gunicorn"
,             django_dir ? "${nix_shell_dir}/django"
,              nginx_dir ? "${nix_shell_dir}/nginx"

,                 deploy ? false
,                  debug ? false
,              sops_file ? "${project_dir}/secrets/lynx_settings.sops.json"
,                sp_kdbx ? "${project_dir}/secrets/sp.kdbx"

# NOTE Deployment environment: `dev` vs `prod` {{- {{-
#
#      It affects
#
#        1. which credentials are used
#
#        2. `dev` enables `DEBUG` in the Django configuration
# }}- }}-

# Possible values: top-level keys of `sops_file`.
, deployment_environment ? "dev"
}:

# HOW TO CALL
# ===========
#
# nix-shell nix/dev_shell.nix
# nix-shell nix/dev_shell.nix --arg "deploy" "true" --arg "debug" "true"
# nix-shell nix/dev_shell.nix --arg "debug"  "true" -v
# nix-shell nix/dev_shell.nix --argstr "deployment_environment"  "dev" -v

# THE `_nix-shell` TEMPORARY WORKING DIRECTORY {{-
# ============================================
#
# Used to save runtime  files (config, logs, pidfiles,
# etc.) during operation in one place instead of being
# scattered all over the system.
#
# Sub-directories    are   created    in   `shellHook`
# using    `mkdir`,    with     the    exception    of
# `_nix-shell/postgres`,   which   is  created   using
# `pg_ctl initdb`  (both the setup and  clean-up shell
# commands are fetched remotely in this case).
# }}-

# NOTE / TODO Incorporate NGINX or not? {{-
#
# Still deliberating whether full deployment should be
# available from this script  (i.e., setup -> gunicorn
# -> nginx).
#
# QUESTION Maybe just re-use the Nix shell expression
#          by  calling  it   from  here  using  `exec
#          nix-shell`?
#
#               exec nix-shell -p vim --run "sleep 7"
#
#          does exactly one would think it does so it
#          seems to be a viable option.
#
# assert start_nginx ->
# }}-

let

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

in
  pkgs.mkShell {

    # ENVIRONMENT VARIABLE DECLARATIONS
    DEPLOY_ENV = deployment_environment;

    # TODO pin to specific version (and migrate to flakes)
    buildInputs = with pkgs; [ # {{-
      postgresql_15
      just
      openssl # to generate SECRET_KEY on each serving

      # `sops` is  needed to  decrypt `secrets.json`  and to
      # export  its  contents as  environment variables; the
      # the rest is support (see README)
      sops
      jq
      keepassxc
      azure-cli

      # EXTERNAL DEPENDENCIES FOR PYTHON PACKAGES
      # TODO package Python packages and their deps with Nix
      systemd
      pkg-config
      cairo
      gobject-introspection
      icu
      python3

      # debug
      schemaspy
      tmux
      mtr  # modern traceroute
      # TODO Is there an alternative? busybox will also pull in `ps`, and it seems to be an inferior alterntive to the regular one.
      # busybox # sed, tr, ...
    ]; # }}-

    # TODO fail if not in the `slate-2` project directory
    shellHook =

      let
        # NOTE Same as  the snippets below, but  might be {{- {{-
        #      more readable in certain cases.
        #
        #      See also https://elixirforum.com/t/nix-the-package-manager/23231/3
        #
        #      shellHook =        shellHook =
        #        ''                 ''
        #          trap \             trap \
        #          "                  "
        #        ''                   echo lofa
        #      + ''                   sleep 2
        #          echo lofa          echo miez
        #          sleep 2            " \
        #          echo miez          EXIT
        #        ''                 ''
        #      + ''               ;
        #          " \
        #          EXIT
        #        ''
        #      ;

        # }}- }}-
        cleanUp = # {{-
          shell_commands:
            ''
              trap \
              "
              ${ builtins.concatStringsSep "" shell_commands }
              " \
              EXIT
            ''
        ;

        # }}-
      in
          # NOTE Why the `debug` flag? {{-
          #      ---------------------
          # Because it will output secrets stored in environment
          # variables as  well, thus it  feels safer to  make it
          # optional.

          # }}-
          ( if (debug)
            then ''
                   set -x
                 ''
            else ""
          )

          # TODO groups & (system) users
          #
          # The goal is to  have each participating service have
          # their eponymous system users, and an extra user with
          # `sudo` rights to kick things off:
          #
          #     group: lynx_app
          #     ├── user: (privileged user; e.g., lynx, toraritte)
          #     ├── user: gunicorn
          #     ├── user: nginx
          #     └── user: postgres
          #
          #     sudo usermod -a -G lynx_app <privileged-user>
          #     sudo usermod -a -G lynx_app gunicorn
          #     sudo usermod -a -G lynx_app nginx
          #     sudo usermod -a -G lynx_app postgres
          #
          # The  permissions will  be 750  (group: `lynx_app`;
          # user: privileged user) throughout the project dir.
          #
          #     sudo chown -R <privileged-user> <project_dir>
          #     sudo chgrp -R lynx_app <project_dir>
          #     sudo chmod -R 750 <project_dir>
          #
          #     # Otherwise system users won't be able to create files...
          #     sudo find <project_dir> -type d -exec chmod 770 {} +
          #
          # Use `tree -pug` to check the ownerships and permissions.

          # TODO 750 permissions: This might need some tweaking, as system users may have to write into files. (Although, the services started with their eponymous system users would create files using their own permissions, so this shouldn't be a problem, right? Also, static files should only need read permissions, given that they are, well, static.)

          # TODO There should be a deployment script (or `shell.nix`) to clone the repo, set up group and users, etc.
          # QUESTION: Will dir and file ownership be a problem? The plan is to have 750 applied recursively, where the owner system group will be `lynx_app` and the owner user will be the privileged user.
#
          # TODO (note from previous commit; couldn't decide if it can be tossed)
          # Create system users for nginx, gunicorn, postgresql, and login user (lynx), all of them with their own primary groupgs of the same name. There will be a secondary group (e.g., lynx-services) where these would also be included. The main directory for a lynx deployment will be "lynx-repo" with 750 permissions (owner: lynx, group: lynx-services - this means that service accounts (i.e., system users) will only have read permissions!). Specific service files will be owned the corresponding system user. (Once inside "lynx-repo", most dirs and files have 755/775 and 644, respectively, so this is not strictly necessary - especially in dev - but probably a good idea.)
#

        + ''
            # https://stackoverflow.com/a/14811915/1498178
            create_system_user_if_none() {

              # Only needed to set exit code.
              id "$1" &>/dev/null

              if [ $? -ne 0 ]
              then
                sudo adduser --system --no-create-home --disabled-login --disabled-password --group "$1"
              fi
            }

          ''

          # The privileged user will be created on VM / container creation
        + ''
            # create_system_user_if_none postgres
            # create_system_user_if_none gunicorn
            # create_system_user_if_none nginx

            create_system_group_if_none() {

              # Only needed to set exit code.
              getent group "$1" &>/dev/null

              if [ $? -ne 0 ]
              then
                sudo groupadd --system "$1"
              fi
            }

            # create_system_group_if_none lynx_app
          ''
        + ''
            # Already done in `postgres/shell-hook.sh`, but it doesn't hurt
            export NIX_SHELL_DIR="${nix_shell_dir}"
            export  GUNICORN_DIR="${gunicorn_dir}"
            export    DJANGO_DIR="${django_dir}"
            export     NGINX_DIR="${nginx_dir}"

            mkdir -p $GUNICORN_DIR
            mkdir -p $DJANGO_DIR
            mkdir -p $NGINX_DIR
          ''

          # NOTE Why not simply use a `just venv` recipe? {{-
          #      ----------------------------------------
          # Because the  first command creates a  virtual Python
          # environment, and the second one  enters into it in a
          # new  sub-shell. `just`  commands  run  in their  own
          # sub-shell so  any other recipe that  depends on this
          # `venv` will fail.
          #
          # Plus, as noted above:
          #
          # > Also, the whole point of  a `shell.nix` is to set up
          # > (and tear down) a shell environment after all.

          # }}-
        + ''
            VENV_DIR="''${DJANGO_DIR}/venv"
            python -m venv $VENV_DIR
            source "''${VENV_DIR}/bin/activate"
          ''

          # NOTE Why not make this a `just` recipe? {{-
          #      ----------------------------------
          # Because recipes  cannot be used in  global variables
          # and  couldn't  figure  out  how to  define  a  shell
          # function in  a `just` variable  that can be  used in
          # subsequent variable definitions.
          #
          # For the  record, there  was a  `just s`  recipe, but
          # these  would get  evaluated every  time, instead  of
          # simply  once  per  just invocation  (e.g.,  for  the
          # `add_schema` recipe this meant  that both 'USER' and
          # 'SCHEMA' would  have been extracted 4  times each in
          # one call.

          # }}-
        + ''
            get_db_settings () {
              sops --decrypt ${sops_file} \
              | jq -r ".[\"${deployment_environment}\"][\"DATABASE\"][\"$1\"]"
            }

            export -f get_db_settings
          ''

        + builtins.readFile ./postgres/shell-hook.sh

        + cleanUp
            [
              ( builtins.readFile ./postgres/clean-up.sh )
            ]

          # NOTE Why KeePassXC + SOPS? {{-
          #      ---------------------
          # The dance  with KeePassXC is needed  beforehand as I
          # was not able  to use a Azure  managed identity (MSI)
          # with SOPS (see
          # https://github.com/mozilla/sops/issues/1190
          # ),  so I  used a  dedicated Azure  service principal
          # instead -  but that SOPS authentication  method does
          # require secrets in environment variables...
          #
          # See also https://stackoverflow.com/a/75972492/1498178

            # NOTE Why didn't this get moved to Justfile?
            #      --------------------------------------
            # Because  the  `get_database_setting  <name>`  recipe
            # (more  specifically, SOPS)  in the  Justfile depends
            # on  the  environment  variables  exported  from  the
            # KeePassXC database. See note "Why KeePassXC + SOPS?"
            # above.
            #
            # `just`, just  as `make`, executes each  command in a
            # new shell,  therefore environment variables  have to
            # be set  before hand if  the recipes need  them. This
            # could  have been  set  in the  `Justfile`, but  then
            # running any recipe would probably nagged the user to
            # unlock the KeePassXC database.
            #
            # Also, the whole point of  a `shell.nix` is to set up
            # (and tear down) a shell environment after all.

          # }}-
        + ''
            source <(keepassxc-cli attachment-export ${sp_kdbx} az_sp_creds export.sh --stdout)
          ''

        + ( if (deploy)
            then ''
                   just
                 ''
            else ""
          )
    ;

    ######################################################################
    # Without  this, almost  everything  fails with  locale issues  when #
    # using `nix-shell --pure` (at least on NixOS).                      #
    # See                                                                #
    # + https://github.com/NixOS/nix/issues/318#issuecomment-52986702    #
    # + http://lists.linuxfromscratch.org/pipermail/lfs-support/2004-June#023900.html
    ######################################################################

    LOCALE_ARCHIVE =
      if pkgs.stdenv.isLinux
      then "${pkgs.glibcLocales}/lib/locale/locale-archive"
      else ""
    ;
  }

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
