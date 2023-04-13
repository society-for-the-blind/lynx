# nixos-22.11 channel
# Apr 9, 2023, 9:59 PM EDT
{ nixpkgs_commit ? "ea96b4af6148114421fda90df33cf236ff5ecf1d"
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
        # sn = shell.nixes
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

      # NOTE
      # The dance  with KeePassXC is needed  beforehand as I
      # was not able  to use a Azure  managed identity (MSI)
      # with SOPS (see
      # https://github.com/mozilla/sops/issues/1190
      # ),  so I  used a  dedicated Azure  service principal
      # instead -  but that SOPS authentication  method does
      # require secrets in environment variables...
        snFetchContents "postgres/shell-hook.sh"
      + cleanUp
          [
            ( snFetchContents "postgres/clean-up.sh" )
            ''
              echo -n 'deleting .venv ... '
              rm -rf .venv
              rm -rf lynx/static
              echo 'done'
            ''
          ]
      +
        ''
          source <(keepassxc-cli attachment-export secrets/sp.kdbx az_sp_creds export.sh --stdout)
          d () { sops --decrypt secrets/lynx_settings.sops.json | jq -r ".[\"DATABASES\"][\"default\"][\"$1\"]"; }

          createdb $(d "NAME") --host=$PGDATA --port=$(d "PORT")

          psql \
            --host=$PGDATA \
            --username=$(whoami) \
            --dbname=$(d "NAME")  \
            --command="CREATE ROLE $(d 'USER') WITH LOGIN PASSWORD '$(d 'PASSWORD')'"

          python -m venv .venv
          source .venv/bin/activate
          pip install --upgrade pip
          pip install lynx/.

          python lynx/manage.py showmigrations

          python lynx/manage.py makemigrations
          python lynx/manage.py migrate
          python lynx/manage.py check --deploy

          python lynx/manage.py createsuperuser
          # python lynx/manage.py collectstatic
          # python lynx/manage.py runserver 0:8000
      ''
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