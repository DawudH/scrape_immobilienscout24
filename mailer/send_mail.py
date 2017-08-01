#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText

from mailer.construct_email import construct_html_email
from mailer.settings import email_from, email_password, email_to


def send_email(title, results, results_last_7_days):
    # allow less secure apps on google to use this feature:
    # https://myaccount.google.com/lesssecureapps
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_from, email_password)

    # Construct the html message
    html = construct_html_email(title, results, results_last_7_days)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEText(html, 'html')
    msg['Subject'] = title
    msg['From'] = email_from
    msg['To'] = ", ".join(email_to)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()
