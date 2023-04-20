# VARIABLES
# ---------

db_user     := `get_db_settings 'USER'`
db_port     := `get_db_settings 'PORT'`
db_schema   := `get_db_settings 'SCHEMA'`
db_name     := `get_db_settings 'NAME'`

# NOTE `psql` username
#      ===============
# The  username is  hard-coded, but  it can  be easily
# overridden  by adding  `-U` or  `--username` again.
#
# For example:
#
#      $ just c -U postgres
#
#      lynx=> \conninfo
#      ...as user "postgres"...

psql_flags := (
  " --host=$PGDATA" +
  " --port="        + db_port  +
  " --username="    + `whoami` +
  " --dbname="      + db_name  +
  " "
)

# COMPOSITE RECIPES
# -----------------

default: db deps migrate prep serve

db: create_db add_role add_schema

# RECIPES
# -------

# TODO Add ICU? (postgres15)
create_db:
  createdb         \
    {{db_name}}    \
    --host=$PGDATA \
    --port={{db_port}}

# NOTE
# This recipe is very resistant to refactoring, and my
# every attempt failed thus far. One of the reasons is
# that `PASSWORD`  changes often, and if  a particular
# instance has  dollar sign(s) in it,  then this seems
# to be the only way to do it.

add_role:
  psql           \
  {{psql_flags}} \
  --command="CREATE ROLE {{db_user}} WITH LOGIN PASSWORD '$(get_db_settings 'PASSWORD')'"

add_schema:
  echo " \
    CREATE SCHEMA {{db_schema}};                                                  \
    GRANT USAGE, CREATE ON SCHEMA {{db_schema}} TO {{db_user}};                   \
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {{db_schema}} TO {{db_user}};    \
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {{db_schema}} TO {{db_user}}; \
  " | just c

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

alias m := _django_manage
alias c := _connect_lynx_db

# HELPERS
# -------

# WARNING sometimes works, other times it doesn't

reldoc host driver:
  schemaspy -t pgsql11 -host {{host}} -port {{db_port}} -db {{db_name}} -s public -u {{db_user}} -o . -dp {{driver}}

_django_manage +sub_commands:
  python lynx/manage.py {{sub_commands}}

# CAVEAT `extra_flags` variadic parameter
#        ================================
# is  almost   useless,  unless  very   simple  `psql`
# `extra_flags`  are  provided  (e.g.,  `-U  postgres`
# to  override  the  hard-coded user).  Anything  that
# requires quoting  and/or has spaces in  it will turn
# the whole  thing into an unmanageable  mess, and one
# is better  off using workarounds (such  as the shell
# function `get_db_settings`in `dev_shell.nix`).

_connect_lynx_db *extra_flags:
  psql           \
  {{psql_flags}} \
  {{extra_flags}}

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
