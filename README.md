> NOTE
> Legacy build steps can be found in [`build-steps-Django-2.2.md`](./build-steps-Django-2.2.md)

1. Install Nix (see [download page](https://nixos.org/download.html) for more):

        sh <(curl -L https://nixos.org/nix/install) --daemon

   > NOTE
   > The [Determinate Systems' Nix installer](https://determinate.systems/posts/determinate-nix-installer) works like a charm, and should switch to that:
   >
   > ```text
   > curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
   > source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' # or restart the shell
   > ```

2. (OPTIONAL) Enter a Nix shell with the most common tools

        source <(curl https://raw.githubusercontent.com/toraritte/shell.nixes/main/run.sh) -n "22.11"

   <sup>Read more [here](https://github.com/toraritte/shell.nixes/blob/main/baseline/baseline_config.nix).</sup>

3. Clone this repo & enter the clone

        git clone https://github.com/society-for-the-blind/slate-2.git
        cd slate-2

   If the `dev` branch is needed, then use:

        git clone -b dev https://github.com/society-for-the-blind/slate-2.git
        cd slate-2

4. Enter [`./nix/dev_shell.nix`](./nix/dev_shell.nix). (See comments there or use the command below.)

        nix-shell nix/dev_shell.nix --argstr "deployment_environment"  "dev"

   > NOTE Which deployment environment? See note at the top of `dev_shell.nix`.

5. See [`Justfile`](./Justfile) on how to build (and toy-serve) the project.

   The needed command will probably be one of the following:

       just # short for `just serve_empty`
       just serve_from <path-to-postgresql-dumpfile>

    Or build (and toy-serve) right away with:

       nix-shell nix/dev_shell.nix --arg "deploy" "true"

6. To serve with NGINX, enter [`./nix/nginx_shell.nix`](./nix/nginx_shell.nix).

   > NOTE: **HTTPS only, both for testing and in production.**

   From the project root:

       nix-shell                                                       \
         --argstr "ssl_cert"    "$( readlink -f lynx-dev-server.crt )" \
         --argstr "private_key" "$( readlink -f lynx-dev-server.key )" \
         --argstr "domain"      "lynx.dev"                             \
         nix/nginx_shell.nix

   (See [HTTPS notes](./https-notes.md) on how to create the keys and SSL certificates for testing.)

## Notes <!-- {{- -->

### Logs

Logs are saved in `_nix-shell/`.

### Python / Django errors

The very first error I got with this app:

      `ImportError: bad magic number in 'mysite.settings': b'\x03\xf3\r\n'`

 The solution provided in the [Stackoverflow thread](https://stackoverflow.com/questions/52477683/importerror-bad-magic-number-in-time-b-x03-xf3-r-n-in-django) (i.e., deleting `*.pyc` files) worked.

<!-- }}- -->
## SchemaSpy  <!-- {{- -->

Get the latest [SchemaSpy release](https://github.com/schemaspy/schemaspy/releases) and [PostgreSQL JDBC driver](https://jdbc.postgresql.org/).

```text
schemaspy -t pgsql11 -host 1.2.3.4 -port $(just s "PORT") -db $(just s "NAME") -s public -u $(just s "USER") -o output/directory/ -dp postgresql-42.6.0.jar

schemaspy -t pgsql11 -host localhost -port 5432 -db lynx -s public -u postgres -hq -dp postgresql-42.6.0.jar -imageformat svg  -I "(django|auth)_.*" -o 07
                                                                                                                               ^^^^^^^^^^^^^^^^^^^^^
                                                                                                                               this part may be necessary
                                                                                                                               for debugging
```

Use SSH tunneling to connect to a remote database:

1. `ssh -i <cert> -L 5432:localhost:5432 user@1.2.3.4`
2. Change `-host` in the `schemaspy` conmmand above to `localhost`.

<!-- }}- -->
## QUESTIONS <!-- {{- -->

1. Do migration  files need to be  checked into version
   control or should they be generated from scratch via
   `makemigration`? <!-- {{- -->

   ANSWER: See the relevant docs below, but the concensus is that they should be checked in. There are alternatives to it, but that is not a version control problem, but a management / methodology one. See [this SO thread and links in the comments](https://stackoverflow.com/questions/30195699/should-django-migrations-live-in-source-control).

   + https://docs.djangoproject.com/en/4.1/topics/migrations/
   + https://docs.djangoproject.com/en/4.1/topics/db/models/
   + https://realpython.com/django-migrations-a-primer/
   + https://docs.djangoproject.com/en/4.1/intro/overview/
<!-- }}- -->

1. How   does    the   `django-user-accounts`   package
   integrate with `django-auth`? <!-- {{- -->

   Decided to remove `django-user-accounts` because it was not used (the corresponding `account_*` tables were virtually empty; see backup) and it caused extra work after updating everything (see this [Django forum thread](https://forum.djangoproject.com/t/upgrading-from-2-2-to-4-2-yields-relatedobjectdoesnotexist-user-has-no-account-error/20437)).

   Nonetheless, I wonder how this package was shown on the admin page, in its own section?

   Also, a couple of notes regarding removed `django-user-accounts` settings:

   + `ACCOUNT_PASSWORD_EXPIRY = 60*60*24*14  # seconds until pw expires, this example shows 14 days`

     Found [this thread](https://stackoverflow.com/questions/15571046/django-force-password-expiration) while doing research on how to implement this, and, as it turns out, this practice is recommended against (see articles by the [NCSC](https://www.ncsc.gov.uk/blog-post/problems-forcing-regular-password-expiry) and the [FTC](https://www.ftc.gov/news-events/blogs/techftc/2016/03/time-rethink-mandatory-password-changes)).

     See more at the next item.

   + `ACCOUNT_PASSWORD_USE_HISTORY = True`

     This sounds like a good idea on the surface, but this will be abused the same way as the previous option, if it is used to disallow previous passwords (or what else is this used for?).

   Will have to do more reading on thi, but instead of using these options, a better strategy would be to

   1. (periodically) scan existing password hashes in known compromised password databases, and report it to user and supervisor

   1. immediately compare the credentials of new users and report it (this is an internal website, so users will be added by administrators) => better yet, suggest non-compromised passwords automatically

     **Potentional issues**: It is a challenge to educate everyday users, even people in higher positions, to adopt common sense security practices (as it affects convenience, comfort zone, etc.), but the majority of Lynx users are legally blind, and some commonly used tools may be completely inaccessible (e.g., password managers).

  <!-- }}- -->
<!-- }}- -->
## TODOs <!-- {{- -->

### Done (or considered done, at least) <!-- {{- -->

1. Avoid stacking subshells -> Package properly with Nix (or, at least, do it in a single `shell.nix`)

   (case in point: https://stackoverflow.com/questions/21976606/why-avoid-subshells)

   > **RESOLUTION**: see `dev_shell.nix`.

1. Figure out how to add `settings.py` to version control in a safe manner.

   Just spent ca. 3 hours solving runtime errors that were resolved by (1) adjusting version numbers in `requirements.txt` and (2) adding missing entries to `INSTALLED_APPS` in `settings.py`. Adding `dummy_settings.py` as a workaround for now.

   > **RESOLUTION**: Use KeePassXC and SOPS. See commands in `dev_shell.nix` and [this Stackoverlow answer](https://stackoverflow.com/a/75972492/1498178).

<!-- }}- -->
### Active <!-- {{- -->

1. Audit `pg_hba.conf`

   ... as it is quite rudimentary (and may even be insecure) at the moment. For example, the current settings won't ask for a password when logging in (see [Postgresql does not prompt for password](https://stackoverflow.com/questions/1335503/postgresql-does-not-prompt-for-password)), but it is probably prudent to set it up.

1. !!! https://docs.djangoproject.com/en/4.1/intro/tutorial01/

1. Rename the current production PostgreSQL user. (Just do `\du` in the `psql` shell and you'll see why.)

   On that note, it would be prudent to implement security best practices. For example:
   + [should a postgresql cluster in production have superusers](https://www.google.com/search?q=should+a+postgresql+cluster+in+production+have+superusers&oq=should+a+postgresql+cluster+in+production+have+superusers&aqs=chrome..69i57j33i160l3.17593j0j7&sourceid=chrome&ie=UTF-8)
   + see tab group on phone

1. [Django: How to manage development and production settings? (SO)](https://stackoverflow.com/questions/10664244/django-how-to-manage-development-and-production-settings)

   Related: [(loading secrets into `settings.py` from textfiles)](https://serverfault.com/questions/1022877/do-i-have-to-restart-my-server-after-changing-settings-py)

1. Save documents in database?

1. (Related to 2.) Set up database backup and/or replication.

1. Adopt decision records (DR)

   + https://github.com/joelparkerhenderson/decision-record
   + https://adr.github.io/
   + https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html

1. Cull dependencies

   There are a lot of packages that may not even be needed, so audit `requirements.txt`.

1. Make dev environment more flexible.

   That is, don't make `dev_shell.nix` run until the web server is running (this would be a good candidate task for `prod_shell.nix` or something similar), but just add the tools needed (plus maybe add clean up commands to `shellHook`), but the rest (setting up the database, set up virtualenv, run migrations etc) should be done by job runners (e.g., with `just`).

   > UPDATE (2023-04-15)
   > This has largely been achieved with the latest set of commits (adding [`Justfile`](./Justfile) and parameters to [`dev_shell.nix`](./dev_shell.nix)), but still unsure what the ideal producion environment would look like (and how it should be deployed). See also the LXD/LXC-related TODO somewhere on this list.

1. Explore containerization

   The [`DRAFT-lxc-deploy.sh`](./DRAFT-lxc-deploy.sh) script is an attempt at using LXD/LXC containers, but it also adds extra complexity (see file). The current approach with Nix seems highly reproducible already, but could be wrong and there may be other benefits.

1. Fetch Python packages from Nixpkgs (or create a new package collection)
  <!-- }}- -->
<!-- }}- -->

vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:
