default: db deps migrate prep serve

alias s := _get_database_setting

_get_database_setting name:
  sops --decrypt secrets/lynx_settings.sops.json | jq -r ".[\"DATABASES\"][\"default\"][\"{{name}}\"]"

db:
  # ---
  createdb $(just s "NAME") --host=$PGDATA --port=$(just s "PORT")
  # ---
  psql \
  --host=$PGDATA \
  --username=$(whoami) \
  --dbname=$(just s "NAME")  \
  --command="CREATE ROLE $(just s 'USER') WITH LOGIN PASSWORD '$(just s 'PASSWORD')'"

deps:
  pip install --upgrade pip
  pip install lynx/.

migrate:
  python lynx/manage.py showmigrations
  python lynx/manage.py makemigrations
  python lynx/manage.py migrate

prep:
  python lynx/manage.py createsuperuser
  python lynx/manage.py collectstatic
  python lynx/manage.py check --deploy

serve:
  python lynx/manage.py runserver 0:8000

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
