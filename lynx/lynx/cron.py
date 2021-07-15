import django
from django.db import connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from datetime import datetime, timedelta
import os
import sys
from .cron_scripts import address

sys.path.append("/var/www/lynx/slate-2/lynx/")
sys.path.append("/var/www/lynx/slate-2/lynx/mysite")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

django.setup()
address()
