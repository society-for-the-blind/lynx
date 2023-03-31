> NOTE
> Legacy build steps can be found in [`build-steps-Django-2.2.md`](./build-steps-Django-2.2.md)

> QUESTIONS
>
> 1. Where are the logs save right now?
>
> 2. Do migration files need to be checked into version control or should they be generated from scratch via `makemigration`?
>
>    ANSWER: See the relevant docs below, but the concensus is that they should be checked in. There are alternatives to it, but that is not a version control problem, but a management / methodology one. See [this SO thread and links in the comments](https://stackoverflow.com/questions/30195699/should-django-migrations-live-in-source-control).
>
>    + https://docs.djangoproject.com/en/4.1/topics/migrations/
>    + https://docs.djangoproject.com/en/4.1/topics/db/models/
>    + https://realpython.com/django-migrations-a-primer/
>    + https://docs.djangoproject.com/en/4.1/intro/overview/

## TOP PRIORITY TODOS

0. !!! https://docs.djangoproject.com/en/4.1/intro/tutorial01/

1. Figure out how to add `settings.py` to version control in a safe manner.

   Just spent ca. 3 hours solving runtime errors that were resolved by (1) adjusting version numbers in `requirements.txt` and (2) adding missing entries to `INSTALLED_APPS` in `settings.py`. Adding `dummy_settings.py` as a workaround for now.

   Places to start:

   + [(loading secrets into `settings.py` from textfiles)](https://serverfault.com/questions/1022877/do-i-have-to-restart-my-server-after-changing-settings-py)

   + [Django: How to manage development and production settings? (SO)](https://stackoverflow.com/questions/10664244/django-how-to-manage-development-and-production-settings]

2. Save documents in database?

3. (Related to 2.) Set up database backup and/or replication.

4. Avoid stacking subshells -> Package properly with Nix (or, at least, do it in a single `shell.nix`)

   (case in point: https://stackoverflow.com/questions/21976606/why-avoid-subshells)

5. Adopt decision records (DR)

   + https://github.com/joelparkerhenderson/decision-record
   + https://adr.github.io/
   + https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html

6. Cull dependencies

   There are a lot of packages that may not even be needed, so audit `requirements.txt`.

## Reproducible build steps after upgrading Django to 4.1

> WARNING Only for development!
>
> See TODO item 4. above.

1. Install Nix (see [download page](https://nixos.org/download.html) for more):

        sh <(curl -L https://nixos.org/nix/install) --daemon

   (... and then issue `source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'` if you don't want to restart your shell.)

2. (OPTIONAL) Enter shell with most common tools

        source <(curl https://raw.githubusercontent.com/toraritte/shell.nixes/main/run.sh) -n "22.11"

   <sup>Read more [here](https://github.com/toraritte/shell.nixes/blob/main/baseline/baseline_config.nix).</sup>

3. Clone this repo & enter the clone

        git clone https://github.com/society-for-the-blind/slate-2.git
        cd slate-2

   > NOTE - The rest of the steps are / will be part of [`dev_shell.nix`](./dev_shell.nix) so run that instead (e.g., via `nix-shell -v --argstr "nixpkgs_commit" "22.11" dev_shell.nix` or simply `nix-shell -v dev_shell.nix`)

4. Make Python3 available (deliberately avoiding the word "install"), and add external dependencies for packages in [`lynx/requirements.txt`](./lynx/requirements.txt):

        nix-shell -p systemd pkg-config cairo gobject-introspection icu python3

   > **NOTE** `.venv`
   > Setting  up a Python virtual environment is deferred until step 11. as some of the PostgreSQL header files are needed during `pip install`, and didn't want to take any chances.

5. Copy `settings.py` into `<repo_root>/lynx/mysite` directory

        scp -i <private_key> <path_to>/settings.py <user>@<vm_ip_address>:<path>

   <sup>`-i` can be omitted if using `ssh-agent` or similar tool that has the private key added to it.</sup>

6. Apply updates in `dummy_settings.py` to `settings.py`.

7. Start PostgreSQL instance

        source <(curl https://raw.githubusercontent.com/toraritte/shell.nixes/main/postgres/postgres.sh)

   > NOTES
   > + The `nixpkgs_commit` part may need to be updated.
   > + WARNING `pg_hba.conf` is set up with the least security possible for development!

8. (NOT NEEDED) Make `libpq.so.5` available for the `psycopg2` Python package

        sudo find / -name libpq.so.5
        sudo ln -s <the-found-path> /usr/lib/libpq.so.5
        sudo ln -s <the-found-path> /usr/lib64/libpq.so.5

9. Create database

        createdb <settings.py_DATABASES_NAME> --host=$PGDATA --port=<settings.py_DATABASES_PORT>

10. Create user (i.e., login role)

    Connect to the PostgreSQL instance via `psql` ( `--username` is probably superfluous: when PostgreSQL is started via the `shell.nix` in **step 7.**, then the active system user  will be the superuser, and `psql` uses it to log in.)

          psql --host=$PGDATA --username=$(whoami) --port=<settings.py_DATABASES_PORT> --dbname=<settings.py_DATABASES_NAME>

    On the `psql` prompt:

          CREATE ROLE <settings.py_DATABASES_USER> WITH LOGIN PASSWORD <settings.py_DATABASES_PASSWORD>;

    > WARNING / TODO
    > This is related to the `pg_hba.conf` WARNING above: the current settings won't ask for a password when logging in (see [Postgresql does not prompt for password](https://stackoverflow.com/questions/1335503/postgresql-does-not-prompt-for-password)), but it is probably prudent to set it up.
    >
    > Especially because production settings will be tightened up anyway.

    > NOTE
    > Decided against using `createuser`, because the password will probably be saved in the shell's history. Otherwise it would have looked like this:
    >
    >      createuser --host=$PGDATA --port=<settings.py_DATABASES_PORT> <settings.py_DATABASES_USER>

    > MORE TODO
    > Set the password using its hash when it comes to deploying in production.
    > + [PostgreSQL: Documentation: 15: CREATE ROLE](https://www.postgresql.org/docs/current/sql-createrole.html)
    > + [PostgreSQL: Documentation: 15: 21.5. Password Authentication](https://www.postgresql.org/docs/current/auth-password.html)
    > + [c# - How to Generate SCRAM-SHA-256 to Create Postgres 13 User - Stack Overflow](https://stackoverflow.com/questions/68400120/how-to-generate-scram-sha-256-to-create-postgres-13-user)
    > + [Generating an SHA-256 Hash From the Command Line | Baeldung on Linux](https://www.baeldung.com/linux/sha-256-from-command-line)
    > + [Creating user with encrypted password in PostgreSQL - Stack Overflow](https://stackoverflow.com/questions/17429040/creating-user-with-encrypted-password-in-postgresql)
    > + [PostgreSQL: Documentation: 15: 20.3. Connections and Authentication](https://www.postgresql.org/docs/current/runtime-config-connection.html#GUC-PASSWORD-ENCRYPTION)


11. Set up virtual Python environment

          python -m venv .venv

    > NOTE
    > If there is already a `.venv` directory, then this step is not necessary. (I think.)

12. Activate virtual Python environment

          source .venv/bin/activate

          pip install --upgrade pip

13. Install packages

          pip install lynx/.

    > NOTE
    > The install target is the directory where `pyproject.toml` is (and right now it is in the `lynx/` directory).

14. Apply database migrations

    First, test with

          python lynx/manage.py showmigrations

    Second, to accomodate included applications (and to apply existing migrations):

          python lynx/manage.py makemigrations

    Finally, go ahead with applying the migrations:

          python lynx/manage.py migrate

15. Check for issues

          python lynx/manage.py check --deploy

16. Start the app with

          python lynx/manage.py runserver 0:8000

## Notes

+ The very first error I got with this app:

        `ImportError: bad magic number in 'mysite.settings': b'\x03\xf3\r\n'`

   The solution provided in the [Stackoverflow thread](https://stackoverflow.com/questions/52477683/importerror-bad-magic-number-in-time-b-x03-xf3-r-n-in-django) (i.e., deleting `*.pyc` files) worked.

   > TODO
   > `*.pyc` files are "_byte cache files_" generated when a Django project is "built", so these should be in `.gitignore`.
   >
   > UPDATE Hm, `.pyc` files are specified in `.gitignore`, so these have probably been commited by accident.

   The next error when running `python manage.py runserver`:

+ `ModuleNotFoundError: No module named 'mysite.settings'`

   `mysite/settings.py` file was missing. Given that it contains all of the project's secrets, it is understandable that it is not in version control.

   > TODO
   > Read up about this, especially about how to switch between environrments (e.g., prod, dev).
   > + https://docs.djangoproject.com/en/2.1/topics/settings/#envvar-DJANGO_SETTINGS_MODULE
   > + https://stackoverflow.com/questions/10664244/django-how-to-manage-development-and-production-settings
   > + https://www.digitalocean.com/community/tutorials/how-to-harden-your-production-django-project

3. The next exception is database-related, so figure out how to configure a PostgreSQL instance with a Django project.

vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
