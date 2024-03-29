## 1. Debug template from `views.py`

```python
import web_pdb;

class SipNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = SipNote
    fields = ['note', 'note_date', 'at_devices',  'independent_living', 'orientation', 'communications', 'dls',
              'support', 'advocacy', 'counseling', 'information', 'services', 'retreat', 'in_home', 'seminar',
              'modesto', 'group', 'community', 'class_hours', 'sip_plan', 'instructor']
    template_name_suffix = '_edit'

    def dispatch(self, request, *args, **kwargs):
        # web_pdb.set_trace()  # Add this line to trigger the debugger
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # web_pdb.set_trace()  # Add this line to trigger the debugger
        return super().get(request, *args, **kwargs)
```

## 2. Migrate from prod to dev

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

Serving with gunicorn:
```
just gunicorn 8000
```

Use `--reload` when developing:
```
just gunicorn 8000 --reload
```

```
# /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

# /etc/systemd/system/gunicorn.service 

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lynx/slate-2/lynx
ExecStart=/home/mjtolentino/.local/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
	  --log-level debug \
          mysite.wsgi:application

[Install]
WantedBy=multi-user.target
```
