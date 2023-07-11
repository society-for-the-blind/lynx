# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d" # --argstr
,    project_dir ? builtins.toString ./..
,         deploy ? false # --arg
,          debug ? false # --arg
,      sops_file ? "${project_dir}/secrets/lynx_settings.sops.json" # --argstr
,        sp_kdbx ? "${project_dir}/secrets/sp.kdbx"
# NOTE Possible values: top-level keys of `sops_file`
, deployment_environment ? "dev" # --argstr
}:

# USAGE EXAMPLES
# ==============
#
# nix-shell dev_shell.nix
# nix-shell dev_shell.nix --arg "deploy" "true" --arg "debug" "true"
# nix-shell dev_shell.nix --arg "debug"  "true" -v
# nix-shell dev_shell.nix --argstr "deployment_environment"  "dev" -v

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

in
  pkgs.mkShell {

    # ENVIRONMENT VARIABLE DECLARATIONS
    DEPLOY_ENV = deployment_environment;

    buildInputs = with pkgs; [ # {{-
      postgresql_15
      python3
      just
      openssl # to generate SECRET_KEY on each serving
      nginx

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
        # sn =:= shell.nixes
        sn_dir = "https://github.com/toraritte/shell.nixes/raw/main/";

        snFetchContents = # {{-
          rel_path:
          builtins.readFile
            ( builtins.fetchurl (sn_dir + rel_path) )
        ;

        # }}-
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

        + ''
            # Already done in `postgres/shell-hook.sh`, but it doesn't hurt
            export NIX_SHELL_DIR="${project_dir}/_nix-shell"
            export GUNICORN_DIR="''${NIX_SHELL_DIR}/gunicorn"
            export DJANGO_DIR="''${NIX_SHELL_DIR}/django"

            mkdir -p $GUNICORN_DIR
            mkdir -p $DJANGO_DIR
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

          # TODO This should probably in this repo and not fetched remotely
        + snFetchContents "postgres/shell-hook.sh"

        + cleanUp
            [
              # TODO This should probably in this repo and not fetched remotely
              ( snFetchContents "postgres/clean-up.sh" )
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
