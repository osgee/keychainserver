import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendemail(sender, pwd, to, msg, server, port=587):
    s = smtplib.SMTP(server, port)
    s.set_debuglevel(0)
    s.starttls()
    s.login(sender, pwd)
    s.sendmail(sender, to, msg.as_string())
    s.quit()


def send(touser, username):
    sender = 'feedback.keychain@gmail.com'
    # sender='simstudy5@163.com'
    pwd = 'superkeychain'
    msg = MIMEMultipart()
    server = 'smtp.gmail.com'
    localtime = time.asctime()
    msg['From'] = sender
    msg['To'] = touser
    msg['Subject'] = "you have successfully signed up in Keychain! " + localtime
    text = """
    
    Hi ,""" + touser + """

Thank you for being a Keychain member.
We’re writing to inform you that you have 
signed up successfully. 

I was hoping you wouldn't mind giving a bit
of feedback about your Keychain experience. 

    feedback@superkeychain.com

Thanks in advance, and if you have any questions 
or comments directly for me then just let me know.

Tao Feng
Customer Happiness Engineer, Keychain 
    
    """
    content = MIMEText(text, 'plain')
    msg.attach(content)
    sendemail(sender, pwd, touser, msg, server)
