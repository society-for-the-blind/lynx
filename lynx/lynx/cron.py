import django
from django.db import connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from datetime import datetime, timedelta
import os
import sys
from . import cron_scripts

day_of_week = datetime.today().weekday()
# now = datetime.datetime.now()
# hour = now.hour

if 0 <= day_of_week <= 4: #this is running whenever I restart the server, this will mean it can only run on weekdays

    sys.path.append("/var/www/lynx/slate-2/lynx/")
    sys.path.append("/var/www/lynx/slate-2/lynx/mysite")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

    django.setup()
    cron_scripts.address()
