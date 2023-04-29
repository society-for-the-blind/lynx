# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"
, deploy ? false
,  debug ? false
, deployment_environment ? "dev"
}:

# EXAMPLE CALLS
# -------------
#
# nix-shell dev_shell.nix
# nix-shell dev_shell.nix --arg "deploy" "true" --arg "debug" "true"
# nix-shell dev_shell.nix --arg "debug"  "true" -v

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

    # Environment variable declaration
    DEPLOY_ENV = deployment_environment;

    buildInputs = with pkgs; [
      postgresql_15
      python3
      just
      openssl # to generate SECRET_KEY on each serving

      # `sops` is  needed to  decrypt `secrets.json`  and to
      # export  its  contents as  environment variables; the
      # the rest is support (see README)
      sops
      jq
      keepassxc
      azure-cli

      # external dependencies for Python packages
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
      busybox # sed, tr, ...
    ];

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
          shell_scripts:
            ''
              trap \
              "
              ${ builtins.concatStringsSep "" shell_scripts }
              " \
              EXIT
            ''
        ;

        # }}-
      in

          # NOTE Why the `debug` flag?
          #      ---------------------
          # Because it will output secrets stored in environment
          # variables as  well, thus it  feels safer to  make it
          # optional.

          ( if (debug)
            then ''
                  set -x
                 ''
            else ""
          )

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
              sops --decrypt secrets/lynx_settings.sops.json \
              | jq -r ".[\"${deployment_environment}\"][\"DATABASE\"][\"$1\"]"
            }

            export -f get_db_settings
          ''

          # TODO This should probably in this repo and not fetched remotely
        + snFetchContents "postgres/shell-hook.sh"

      # + cleanUp {{-
        + cleanUp
            [
              ( snFetchContents "postgres/clean-up.sh" )

              ''
                echo -n 'deleting .venv/ static/ ... '
                rm -rf .venv
              ''

              # NOTE static assets
              #      -------------
              # `lynx/lynx/static`  has the  static assets  for this
              # project  that will  get copied  via `collectstatic`!
              # `settings.py` controls  the destination;  search for
              # `STATIC`.
              ''
                rm -rf lynx/static
                echo 'done'
              ''
            ]
          # }}-
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
            source <(keepassxc-cli attachment-export secrets/sp.kdbx az_sp_creds export.sh --stdout)
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
            python -m venv .venv
            source .venv/bin/activate
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
