> !NOTE!
> Commit 7035ee86 is what is currently running in production, but it is outdated (e.g., Django is at 2.2.17), but needed these steps to get a sense of how replicate the production server (and it is still missing a lot of stuff, such as HTTPS and email setup).

### B.0. Set up development environment

1. Install Nix (see [download page](https://nixos.org/download.html) for more):

        sh <(curl -L https://nixos.org/nix/install) --daemon

2. (OPTIONAL) Enter shell with most common tools

        source <(curl https://raw.githubusercontent.com/toraritte/shell.nixes/main/baseline/baseline.sh)

   <sup>Read more [here](https://github.com/toraritte/shell.nixes/blob/main/baseline/baseline_config.nix).</sup>

3. Clone this repo & enter the clone

        git clone https://gitlab.com/society-for-the-blind/slate-2.git
        cd slate-2

4. Make Python3 available (deliberately avoiding the word "install"):

        nix-shell -v -p python3

### B.1 Install dependencies

> QUESTION
> This is only a setup step, right? If `.venv` is present, only `activate` below seems to be needed.

    python -m venv .venv
    source .venv/bin/activate

> required (runtime?) dependency for psycopg2-binary

    sudo apt install libpq-dev

> TODO
> [`libpq-dev`](https://packages.debian.org/sid/libpq-dev) exposes the "_Header files and static library for compiling C programs to link with the libpq library in order to communicate with a PostgreSQL database backend._" How to do this with Nix?

> When going through the steps on a brand new ubuntu server VM, the `netifaces` package would not install and error out with `Getting requirements to build wheel ... error`. This is a faily obscure message, and there is no solution anywhere. Tried running `pip install` without the `--use-pep517` flag, and it worked, but blew up at the `cryptography` package (see notes below), hence the command repeated again **with** the flag so that the dependencies all get installed.

    pip install -r lynx/requirements.txt

    # (Wait for it to crash when building `cryptography`, and then:)

    pip install -r lynx/requirements.txt --use-pep517

> TODO
> The `cryptography` package failed to build without adding `--use-pep517` to `pip`, and the errors were preceded by a warning:
>
>     DEPRECATION: cryptography is being installed using the legacy 'setup.py install' method, because it does not have a 'pyproject.toml' and the 'wheel' package is not installed. pip 23.1 will enforce this behaviour change. A possible replacement is to enable the '--use-p ep517'
>
> `requirements.txt` should therefore be migrated to the new format, `pyproject.toml`. This is used by Poetry by default, so maybe switch to that too?

> ULTIMATE TODO
> Clean up the reproducibility nightmare above.

### B.2 Start the Django app

`settings.py` has a `DATABASES` section, such as

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'database_name',
            'USER': 'database_role_name',
            'PASSWORD': 'password',
            'HOST': 'ip_address',
            'PORT': 'port_number',
        }
    }

and these settings will be used to set up the PostgreSQL instance and the Lynx database. `<settings.py_DATABASES_(key)>` instances will point to the specific settings needed.


1. Copy `settings.py` into `<repo_root>/lynx/mysite` directory

        scp -i <private_key> <path_to>/settings.py <user>@<vm_ip_address>:<path>

   (`-i` can be omitted if using `ssh-agent` or similar tool that has the private key added to it.)

   > TODO Best way to manage secrets?
   >
   > `settings.py` contains all the secrets, and as there are other apps with this same need (TR2 for one), so find a way to do this in a way that no one has to worry about losing crucial files.

2. Apply differences in `dummy_settings.py` to `settings.py`.

   As far as I can tell, the only differences (that are not comments and redacted secrets) are in `INSTALLED_APPS`; namely, the additions of the following lines:

   + `'accounts'`
   + `'django.contrib.sites'`

3. Start PostgreSQL instance

        nix-shell  -v -E 'import (builtins.fetchurl "https://raw.githubusercontent.com/toraritte/shell.nixes/main/_composables/postgres_shell.nix")' --argstr "nixpkgs_commit" "3ad7b8a7e8c2da367d661df6c3742168c53913fa"

   > NOTES
   > + The `nixpkgs_commit` part may need to be updated.
   > + `PGDATA` is set by the Nix expression! See `postgres_shell.nix`.

   > WARNING
   > `pg_hba.conf` is set up with the least security possible for development!

4. Create database

        createdb <settings.py_DATABASES_NAME> --host=$PGDATA --port=<settings.py_DATABASES_PORT>

5. Create user (i.e., login role)

        # Connect to the PostgreSQL instance
        # ( `--username` is probably superfluous: the
        #   active system user  will be the superuser,
        #   and `psql` uses it to log in.
        # )

        psql --host=$PGDATA --username=$(whoami) --port=<settings.py_DATABASES_PORT> --dbname=<settings.py_DATABASES_NAME>

        # On the `psql` prompt:

        CREATE ROLE <settings.py_DATABASES_USER> WITH LOGIN PASSWORD <settings.py_DATABASES_PASSWORD;

   > WARNING / TODO
   > This is related to the `pg_hba.conf` WARNING above: the current settings won't ask for a password when logging in (see [Postgresql does not prompt for password](https://stackoverflow.com/questions/1335503/postgresql-does-not-prompt-for-password)), but it is probably prudent to set it up.
   >
   > Especially because production settings will be tightened up anyway.

   > NOTE
   > Decided against using `createuser`, because the password could be save in the shell history. Otherwise it would have looked like this:
   >
   >      createuser --host=$PGDATA --port=<settings.py_DATABASES_PORT> <settings.py_DATABASES_USER>

5. Apply database migrations

   First, test with

        python lynx/manage.py showmigrations

   > NOTE
   > This may fail with
   >
   >      django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 module: libpq.so.5: cannot open shared object file: No such file or directory
   >
   > or
   >
   >      ImportError: libpq.so.5: cannot open shared object file: No such file or directory
   >
   > Don't want to burn through another VM so the solution will probably be the combinations of these commands. The order that I executed them in this iteration:
   >
   >      sudo find / -name libpq.so.5
   >      sudo ln -s /usr/lib/x86_64-linux-gnu/libpq.so.5 /usr/lib/libpq.so.5
   >      sudo ln -s /usr/lib/x86_64-linux-gnu/libpq.so.5 /usr/lib64/libpq.so.5
   >      pip uninstall psycopg2-binary
   >      pip uninstall psycopg2
   >      pip install -r lynx/requirements.txt --use-pep517

   If that went through, go ahead with applying the migrations:

        python lynx/manage.py migrate

6. Start the app with

        python lynx/manage.py runserver 0:8000

   > NOTE
   > `manage.py` may be moved around in the future so the path may need to be adjusted.

   > NOTE **0.0.0.0 and 127.0.0.1 are not the same**
   > + https://www.reddit.com/r/django/comments/knznxb/difference_between_hosting_on_1270018000_and/
   > + https://serverfault.com/questions/78048/whats-the-difference-between-ip-address-0-0-0-0-and-127-0-0-1
   >
   > Also, **`localhost` vs 127.0.0.1**:
   > + https://stackoverflow.com/questions/20778771/what-is-the-difference-between-0-0-0-0-127-0-0-1-and-localhost
   > + https://www.baeldung.com/cs/127-0-0-1-vs-localhost#:~:text=The%20term%20localhost%20is%20usually,connect%20with%20the%20device%20itself.
   >
   > See the network troubleshooting steps in this gist: [Configure PostgreSQL to allow remote connections](https://gist.github.com/toraritte/f8c7fe001365c50294adfe8509080201).


---

vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
