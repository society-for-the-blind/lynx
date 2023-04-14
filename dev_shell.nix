# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"
, deploy ? false
}:

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
    buildInputs = with pkgs; [
      postgresql
      python3
      just

      # `sops` is  needed to  decrypt `secrets.json`  and to
      # export  its  contents as  environment variables; the
      # the rest is support (see README)
      sops
      jq
      keepassxc
      azure-cli

      # external dependencies for Python packages
      systemd
      pkg-config
      cairo
      gobject-introspection
      icu
    ];

    shellHook =

      let
        # sn =:= shell.nixes
        sn_dir = "https://github.com/toraritte/shell.nixes/raw/main/";

        snFetchContents =
          rel_path:
          builtins.readFile
            ( builtins.fetchurl (sn_dir + rel_path) )
        ;

        cleanUp =
          shell_scripts:
            ''
              trap \
              "
              ${ builtins.concatStringsSep "" shell_scripts }
              " \
              EXIT
            ''
        ;

      in

      # TODO this may not be correct anymore
      # Export environment variables
      # Step 1. Env vars for SOPS to work (see NOTE below)
      # Step 2. Env vars for Django to run Lynx itself

        snFetchContents "postgres/shell-hook.sh"

        # CLEAN UP AFTER EXITING NIX-SHELL
        # --------------------------------

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
      +
        # SETUP
        # -----
        # `just` is used to organize  commands and to only run
        # them when needed.

        # NOTE Why KeePassXC + SOPS?
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
        ''
          source <(keepassxc-cli attachment-export secrets/sp.kdbx az_sp_creds export.sh --stdout)
        ''

          # NOTE Why not simple use a `just venv` recipe?
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
