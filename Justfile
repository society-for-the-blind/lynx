default: db deps migrate prep serve

db:
  # >>>
  # TODO Add ICU? (postgres15)
  createdb           \
    $(just s "NAME") \
    --host=$PGDATA   \
    --port=$(just s "PORT")
  # >>>
  # >>> The  argument  to  `just c`  needs  to  be
  # >>> surrounded by  quotes because  it contains
  # >>> spaces  and  `just`  will  parse  them  as
  # >>> individual  tokens  to executed.  See  the
  # >>> `aaa` recipe at the bottom.
  # >>>
  just c "--command=\"CREATE ROLE $(just s 'USER') WITH LOGIN PASSWORD '$(just s 'PASSWORD')'\""

deps:
  pip install --upgrade pip
  pip install lynx/.

migrate:
  just m showmigrations
  just m makemigrations
  just m migrate

prep:
  just m createsuperuser
  just m collectstatic
  just m check --deploy

serve:
  just m runserver 0:8000

# ALIASES
# -------

alias s := _get_database_setting
alias m := _django_manage
alias c := _connect_lynx_db

# HELPERS
# -------

_django_manage +sub_commands:
  python lynx/manage.py {{sub_commands}}

_get_database_setting field:
  sops --decrypt secrets/lynx_settings.sops.json \
  | jq -r ".[\"DATABASES\"][\"default\"][\"{{field}}\"]"

_connect_lynx_db *flags:
  psql                        \
  --host=$PGDATA              \
  --port=$(just s "PORT")     \
  --username=$(just s "USER") \
  --dbname=$(just s "NAME")   \
  {{flags}}

# NOTES FOR FUTURE SELF
# ---------------------

# 1. SPACES IN VARIADIC ARGUMENTS
# ===============================
#
# WRONG: just aaa 'not simply' dev_shell.nix
#
#        Will be called as
#
#        grep not simply dev_shell.nix
#
# RIGHT: just aaa "'not simply'  dev_shell.nix"
# RIGHT: just aaa "'not simply'" dev_shell.nix
#
#        Both will be called as intended:
#
#        grep 'not simply' dev_shell.nix

aaa *params:
  grep {{params}}

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
