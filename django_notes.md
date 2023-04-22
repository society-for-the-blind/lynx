## 1. Migrations

The topic is still fuzzy for me, but I think it is that:

1. models are created / altered
2. migrations are calculated from step 1.

At the moment, there are 82 migrations in [`lynx/lynx/migrations`](./lynx/lynx/migrations), but then I

1. deleted that directory
2. `python lynx/manage.py makemigrations lynx` (or `just m makemigrations`)

and there was a new initial Lynx migration (check with `just m showmigrations`), that seemed to be identical to the end result of applying the previous 82 migrations.

> QUESTION Is there a way to compare whether the end results are really identical? My current method was to scan the second initial migration and comparing its size (i.e., number of lines) to the previous batch, and it looked ok.

### 1.1 How to consolidate PostgreSQL backup methods with existing migrations?

#### 1.1.2 Logical backups (i.e., `pg_dump` and `pg_dumpall`)

Dumps produce SQL commands that will get replayed on the target database.

select * from account_account as a join auth_user as u on a.user_id = u.id;

