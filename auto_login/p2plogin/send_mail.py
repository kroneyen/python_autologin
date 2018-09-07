#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

def send_email(subject, body):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import configparser
    import ast

    config = configparser.ConfigParser()
    config.read('config.ini')
    ## get values from config mail section 
    m_from = config.get('mail','m_from')
    m_to = ast.literal_eval(config.get('mail','m_to'))
    m_pwd = config.get('mail','m_pwd')

    FROM = m_from 
    TO = m_to  
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
        server.login(FROM, m_pwd) 
        server.sendmail(FROM, TO, msg.as_string())  ## msg transfer  to string
        server.quit()
        if __name__ == '__main__':
         print ('successfully sent the mail')
    except:
        if __name__ == '__main__':
         print ('failed to send mail')
