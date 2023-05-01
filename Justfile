# VARIABLES
# ---------

db_user   := `get_db_settings 'USER'`
db_port   := `get_db_settings 'PORT'`
db_schema := `get_db_settings 'SCHEMA'`
db_name   := `get_db_settings 'NAME'`

# NOTE `psql` username {{-
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

# }}-
psql_flags := (
  " --host=$PGDATA" +
  " --port="        + db_port  +
  " --username="    + `whoami` +
  " --dbname="      + db_name  +
  " "
)

# COMPOSITE RECIPES
# -----------------

serve_empty: db deps migrate prep add_django_superuser serve

serve_from dumpfile: db && deps migrate prep serve
  just c  -f {{dumpfile}}
  just c --command="ANALYZE"

db: create_db add_role grant_schema

# RECIPES
# -------

dump *extra:
  pg_dump \
  {{psql_flags}} \
  {{extra}}

# TODO Add ICU? (postgres15)
create_db:
  createdb         \
    {{db_name}}    \
    --host=$PGDATA \
    --port={{db_port}}

# NOTE Why doesn't this use `just c`? (or merged with `grant_schema`) {{-
#      ------------------------------
# This recipe is very resistant to refactoring, and my
# every attempt failed thus far. One of the reasons is
# that `PASSWORD`  changes often, and if  a particular
# instance has  dollar sign(s) in it,  then this seems
# to be the only way to do it.

# }}-
add_role:
  psql           \
  {{psql_flags}} \
  --command="CREATE ROLE {{db_user}} WITH LOGIN PASSWORD '$(get_db_settings 'PASSWORD')'"

# NOTE Why is this not a Django migration? {{-
#      -----------------------------------
# Because this is necessary for Django to even be able
# to touch  the database. From PostgreSQL  15, no user
# has access to the `public`  schema and it is treated
# just like any other.  Therefore, unless someone is a
# superuser, extra  privileges have  to be  granted to
# touch anything inside it.

# }}-
grant_schema:
  echo " \
    GRANT USAGE, CREATE ON SCHEMA {{db_schema}} TO {{db_user}};                   \
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {{db_schema}} TO {{db_user}};    \
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {{db_schema}} TO {{db_user}}; \
  " | just c

deps:
  pip install --upgrade pip
  pip install lynx/.

migrate *flag:
  just m showmigrations
  just m makemigrations
  just m migrate {{flag}}

# NOTE Apply Django migrations when database is **not** empty {{-
#      ------------------------------------------------------
# This may not be used much after getting the upgraded
# version  of  Lynx  into   production,  but  for  now
# it  is  needed  when the  production  database  gets
# `pg_dump`-ed, replayed  it to  a fresh  cluster, and
# this  recipe will  apply  only  the migrations  that
# are  necessery (e.g.,  production Lynx  only has  81
# migrations, but  development Lynx  has 82  after all
# the dependency upgrades).
#
# https://docs.djangoproject.com/en/4.2/topics/migrations/#adding-migrations-to-apps

# }}-
fake:
  just migrate --fake-initial

add_django_superuser:
  just m createsuperuser

prep:
  just m collectstatic
  just m check --deploy

serve:
  just m runserver 0:8000

# ALIASES
# -------

# NOTE Double quote `extra_flags` with special chars {{-
#      ---------------------------------------------
# For example,  to run  "backslash commands"  from the
# terminal, 2 quotes are needed:
#
#     just c -c "'\dt'"
#
# Sometimes it  is not possible  at all (or  not worth
# the effort); see note at `add_role` recipe.

# }}-
alias c := _connect_lynx_db
alias m := _django_manage
alias n := _shell_nixes

# HELPERS
# -------

# WARNING sometimes works, other times it doesn't

reldoc host driver:
  schemaspy -t pgsql11 -host {{host}} -port {{db_port}} -db {{db_name}} -s public -u {{db_user}} -o . -dp {{driver}}

_django_manage +sub_commands:
  python lynx/manage.py {{sub_commands}}

_shell_nixes:
  source <(curl https://raw.githubusercontent.com/toraritte/shell.nixes/main/run.sh) -n 22.11

# CAVEAT `extra_flags` variadic parameter {{-
#        ================================
# is  almost   useless,  unless  very   simple  `psql`
# `extra_flags`  are  provided  (e.g.,  `-U  postgres`
# to  override  the  hard-coded user).  Anything  that
# requires quoting  and/or has spaces in  it will turn
# the whole  thing into an unmanageable  mess, and one
# is better  off using workarounds (such  as the shell
# function `get_db_settings`in `dev_shell.nix`).

# }}-
_connect_lynx_db *extra_flags:
  psql           \
  {{psql_flags}} \
  {{extra_flags}}

# NOTES FOR FUTURE SELF
# ---------------------

# 1. SPACES IN VARIADIC ARGUMENTS {{-
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

# }}-

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
