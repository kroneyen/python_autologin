#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

def send_email(subject, body):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    FROM = 'from_user_maiil'
    TO = ['to_user_mail']
    # Prepare actual message
    msgText = MIMEText(body,'plain','utf-8')   ## mail body of chinese , setting harset utf8
    msg = MIMEMultipart()  ## merge mail  multiple part 
    msg['Subject'] = subject
    msg.attach(msgText)
     
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        #server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(from_user_mail,pwd)
        server.sendmail(FROM, TO, msg.as_string())  ## msg transfer  to string
        server.quit()
        if __name__ == '__main__':
         print ('successfully sent the mail')
    except:
        if __name__ == '__main__':
         print ('failed to send mail')
    
