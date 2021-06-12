from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.conf import settings
from django.core.mail import send_mail

from datetime import datetime, timedelta

from .views import dictfetchall


def address_changes():
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

    message = """<str>Address changes for the last week</str> </br>
                <table>
                <tr>
                <td>Client Name</td>
                <td>Instructor Name</td>
                <td>Date Changed</td>
                <td>Change Type</td>
                <td>New Address</td>
                </tr>
              """
    for change in change_set:
        if change.historical_type == "+":
            ctype = "New Address"
        elif change.historical_type == "-":
            ctype = "Address Deleted"
        else:
            ctype = "Address Changed"

        new_line = "<tr><td>" + change.client_name + "</td><td>" + change.user_name + "</td><td>" + change.history_date + "</td><td>" + ctype + "</td><td>" + change.address_one + "</br>" + change.address_two + "</br>" + change.city + "</td></tr>"
        message = message + new_line

    message = message + "</table>"

    username = settings.EMAIL_HOST_USER

    send_mail("Address Changes",
              message,
              username,
              ['mjtolentino247@gmail.com'],
              # ['jhuynh@societyfortheblind.org '],
              fail_silently=False,
              html_message=True,
              )

    return HttpResponse('Mail successfully sent')
