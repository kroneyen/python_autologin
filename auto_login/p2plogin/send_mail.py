#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

def send_email(subject, body):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    #import configparser
    #import ast
    import redis
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    ## get values from config mail section 
    m_from = config.get('mail','m_from')
    m_to = ast.literal_eval(config.get('mail','m_to'))
    m_pwd = config.get('mail','m_pwd')
    """
    ### redis data
    ### parameter redis.StrictRedis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, uni    x_socket_path=None)
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)

    m_from = r.hget('mail','m_from')
    m_to = r.hget('mail','m_to')
    m_pwd = r.hget('mail','m_pwd')

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
