## 1. Migrate from prod to dev

PROD:

```
pg_dump --exclude-table="account_*" $(get_db_settings 'NAME') > dump.sql
```
(Why the `--exclude` flag? See README's TODOs about `django-user-accounts`.)

DEV:

1. `scp` the `dump.sql` file from PROD to DEV
1. `just db`
1. `just c -f dump.sql`
1. `just c --command="ANALYZE"`
1. `just deps`
1. `just m migrate` (or `just m migrate --fake-initial`)
1. `just prep`
1. `just serve`

One-liner:

```
just db && just c  -f dump.sql && just c --command="ANALYZE" && just deps && just migrate && just prep && just serve
```

