## 1. Migrate from prod to dev

PROD:

```
pg_dump $(get_db_settings 'NAME') > dump.sql
```

DEV:

0. `scp` the `dump.sql` file from PROD to DEV
1. `just db`
2. `just c -f dump.sql`
3. `just deps`
4. `just m migrate` (or `just m migrate --fake-initial`)
5. `just c --command="analyze"`

6. TODO: https://forum.djangoproject.com/t/upgrading-from-2-2-to-4-2-yields-relatedobjectdoesnotexist-user-has-no-account-error/20437

   ```sql
   select * from account_account as a join auth_user as u on a.user_id = u.id;
   ```
