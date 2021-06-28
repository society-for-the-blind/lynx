from django.http import HttpResponse
from django.db import connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from datetime import datetime, timedelta

import sys, os, django
# append root folder of django project
# could be solved with a relative path like os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..') which corresponds to the parent folder of the actual file.
sys.path.append('/var/www/lynx/slate-2/lynx/lynx')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lynx.settings")
django.setup()


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def address_changes(self):
    date = datetime.today() - timedelta(days=7)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT CONCAT(client.first_name, ' ', client.last_name) as client_name,
                       CONCAT(au.first_name, ' ', au.last_name) as user_name,
                       CONCAT(his.address_one, ' ', his.suite) as address_one,
                       address_two,
                       CONCAT(his.city, ' ', his.state, ', ', his.zip_code) as city,
                       history_type, history_date, his.id
                FROM lynx_historicaladdress his
                JOIN lynx_contact client on his.contact_id = client.id
                JOIN auth_user au on his.history_user_id = au.id
                WHERE history_date > '%s' 
                  and (his.id,history_date) in (select hist.id, max(hist.history_date) 
                  from lynx_historicaladdress hist group by hist.id);""" % (date))
        change_set = dictfetchall(cursor)

    username = settings.EMAIL_HOST_USER

    plaintext = get_template('lynx/email_change_address.txt')
    htmly = get_template('lynx/email_change_address.html')

    d = {'change_set': change_set}

    subject = 'Address Changes'
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, username, ['mjtolentino247@gmail.com']) #', 'jhuynh@societyfortheblind.org'])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print("mail sent")

    return HttpResponse('Mail successfully sent')
