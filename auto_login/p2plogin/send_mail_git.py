#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

def send_email(subject, body):
    import smtplib

    FROM = 'from_user_maiil'
    TO = 'to_user_mail'
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(from_user_mail,pwd)
        server.sendmail(FROM, TO, message)
        server.quit()
        if __name__ == '__main__':
         print ('successfully sent the mail')
    except:
        if __name__ == '__main__':
         print ('failed to send mail')
	
