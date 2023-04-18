default: db deps migrate prep serve

db: create_db add_role

# TODO Add ICU? (postgres15)
create_db:
  createdb           \
    $(just s "NAME") \
    --host=$PGDATA   \
    --port=$(just s "PORT")

# NOTE
# Tried to  replace this with `just  c --command`, but
# it is  impossible to  figure out the  quoting scheme
# that  works through  all execution  layers (just  ->
# shell -> psql).  Not going to waste  to another hour
# to make it look good.

add_role:
  psql \
    --host=$PGDATA \
    --username=$(whoami) \
    --dbname=$(just s "NAME")  \
    --command="CREATE ROLE $(just s 'USER') WITH LOGIN PASSWORD '$(just s 'PASSWORD')'"

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

# WARNING sometimes works, other times it doesn't
reldoc host driver:
  schemaspy -t pgsql11 -host {{host}} -port $(just s 'PORT') -db $(just s 'NAME') -s public -u $(just s 'USER') -o . -dp {{driver}}

_django_manage +sub_commands:
  python lynx/manage.py {{sub_commands}}

_get_database_setting field:
  sops --decrypt secrets/lynx_settings.sops.json \
  | jq -r ".[\"DATABASES\"][\"default\"][\"{{field}}\"]"

_connect_lynx_db *flags:
  psql                        \
  --host=$PGDATA              \
  --port=$(just s "PORT")     \
  --username=$(whoami)        \
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
