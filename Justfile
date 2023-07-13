# TODOs {{-
#
# + **cut this file up into multiple justfiles**
#   reasons: no lazy loading (and those vars are only needed by a few recipes)
#            some recipes are just useful by themselves without any dependency (i.e., without in the nix-shell
#   A solution is using `just -f` and/or justfiles in different dirs (https://just.systems/man/en/chapter_51.html)
#
# + **Replace `just`?** (It's super slow...)
# }}-

# VARIABLES
# =========
# WARNING **Not lazy!**
#         https://github.com/casey/just/issues/953 (open@5/4/2023)

db_user   := `get_db_settings 'USER'`
db_port   := `get_db_settings 'PORT'`
db_schema := `get_db_settings 'SCHEMA'`
db_name   := `get_db_settings 'NAME'`

timestamp := `date "+%Y-%m-%d_%H-%M-%S"`

# NOTE override `psql` username {{-
#
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
# =================
serve_empty: db deps migrate prep add_django_superuser serve

# USAGE NOTES {{- {{-
#
# For example:
#
#     just serve_from backup/lynx_2023_07_04-exclude_account-fix_sipplan_17615.sql
#
# Once the a database has  been set up, simply use one
# of the `serve` recipes (e.g., `just serve`).
# }}- }}-
serve_from dumpfile: db && deps migrate prep serve
  just c  -f {{dumpfile}}
  just c --command="ANALYZE"

db: create_db add_role grant_schema

# RECIPES {{-
# =======

dump *extra:                           # {{-
  pg_dump \
  {{psql_flags}} \
  {{extra}}
# }}-

# TODO Add ICU? (postgres15)
create_db:                             # {{-
  createdb         \
    {{db_name}}    \
    --host=$PGDATA \
    --port={{db_port}}
# }}-

# NOTE Why doesn't this use `just c`? (or merged with `grant_schema`) {{- {{-
#      ------------------------------
# This recipe is very resistant to refactoring, and my
# every attempt failed thus far. One of the reasons is
# that `PASSWORD`  changes often, and if  a particular
# instance has  dollar sign(s) in it,  then this seems
# to be the only way to do it.

# }}- }}-
add_role:                              # {{-
  psql           \
  {{psql_flags}} \
  --command="CREATE ROLE {{db_user}} WITH LOGIN PASSWORD '$(get_db_settings 'PASSWORD')'"
# }}-

# NOTE Why is this not a Django migration? {{- {{-
#      -----------------------------------
# Because this is necessary for Django to even be able
# to touch  the database. From PostgreSQL  15, no user
# has access to the `public`  schema and it is treated
# just like any other.  Therefore, unless someone is a
# superuser, extra  privileges have  to be  granted to
# touch anything inside it.

# }}- }}-
grant_schema:                          # {{-
  echo " \
    GRANT USAGE, CREATE ON SCHEMA {{db_schema}} TO {{db_user}};                   \
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {{db_schema}} TO {{db_user}};    \
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {{db_schema}} TO {{db_user}}; \
  " | just c
# }}-

deps:                                  # {{-
  pip install --upgrade pip
  pip install lynx/.
# }}-

migrate *flag:                         # {{-
  just m showmigrations
  just m makemigrations
  just m migrate {{flag}}
# }}-

# NOTE Apply Django migrations when database is **not** empty {{- {{-
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

# }}- }}-
fake:                                  # {{-
  just migrate --fake-initial
# }}-

add_django_superuser:                  # {{-
  just m createsuperuser
# }}-

prep:                                  # {{-
  just m collectstatic
  just m check --deploy
# }}-

serve:                                 # {{-
  just m runserver 0:8000
# }}-

# NOTE Sockets (UDS vs TCP) {{- {{-
#      ====================
# Decided to use Unix  Domain Sockets (UDS) instead of
# internet (TCP) sockets when implementing the systemd
# unit files, because UDS is faster and also wanted to
# get  familiar with them. Leaving these Just  recipes
# here in case a quick test in dev is necessary.

# Good resources:
# + https://www.baeldung.com/linux/unix-vs-tcp-ip-sockets
# + https://serverfault.com/questions/124517/what-is-the-difference-between-unix-sockets-and-tcp-ip-sockets
# + https://stackoverflow.com/questions/14973942/tcp-loopback-connection-vs-unix-domain-socket-performance
# + https://lists.freebsd.org/pipermail/freebsd-performance/2005-February/001143.html

# }}- }}-
gunicorn ip_address port *extra_flags: # {{-
  cd {{justfile_directory()}}/lynx && \
  gunicorn                       \
  --bind {{ip_address}}:{{port}} \
  --workers 3                    \
  --log-level 'debug'            \
  --preload                      \
  --capture-output               \
  --pid "${GUNICORN_DIR}/gunicorn_{{timestamp}}.pid" \
  --access-logfile "${GUNICORN_DIR}/gunicorn_access_{{timestamp}}.log" \
  --error-logfile  "${GUNICORN_DIR}/gunicorn_error_{{timestamp}}.log"  \
    mysite.wsgi:application \
    {{extra_flags}}
# }}-

gunicorn_zeros port *extra_flags:
  just gunicorn 0.0.0.0 {{port}} {{extra_flags}}

gunicorn_local port *extra_flags:
  just gunicorn 127.0.0.1 {{port}} {{extra_flags}}

# }}-
# ALIASES {{-
# =======

# USAGE NOTE "Stack quote" `extra_flags` with special chars {{-
#      ---------------------------------------------
#
# For  example,  to  invoke  "backslash  commands"  in
# `psql` from  the terminal,  two distinct  quotes are
# needed:
#
#     just c -c "'\dt'"
#
# Sometimes it  is not possible  at all (or  not worth
# the effort); see note at `add_role` recipe.

# }}-
alias c := _connect_lynx_db
alias m := _django_manage
alias n := _shell_nixes
#     p := my_process_tree  (defined in DEBUG)

# }}-
# HELPERS {{-
# =======

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
# }}-
# DEBUG {{-
# =====

alias p := my_process_tree

# A better alternative to
#
#    watch -n 1 "ps xf"

my_process_tree:
  htop --user $(whoami) --tree

# }}-

# NOTES FOR FUTURE SELF
# =====================

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
