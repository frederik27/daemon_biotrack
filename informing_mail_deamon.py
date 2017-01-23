from _ctypes_test import func
import os
import time
import globals
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
#import urllib.parse, urllib.request
from logs import LOG
from Base import DB

import utils
import threading
conBase = None  # base connection

socket_thread = None

###
#   get email address for send email
#
#   Description: email must change by server
#     - when company belong to UZ(local user) server than @email will biotrack.uz
#     - when company belong to RU server than @email will biotrackapp.ru
#     - when company belong to Amazong server than @email will biotrackapp.com
#
#   @companyId - company id
#   @email - ald email address
#
#   @return email
###
# def getFromEmail(companyId, email):
#     if email.find(globals.email_alias_for_uz) != -1:
#         return email
#     global conBase
#     company = utils.get_company_by_id(conBase, companyId)
#     #print(company)
#     if company and company[0]['lang'] == 'ru' :
#         email = email.replace(globals.email_alias_for_en, globals.email_alias_for_ru)
#         return email
#     return email

def send_mail(data):
    try:
        smtp = smtplib.SMTP(globals.SMTP_HOST, port=globals.SMTP_PORT, timeout=10)
        smtp.login(globals.SMTP_USER, globals.SMTP_PWD)
        outer = MIMEMultipart()
        outer['Subject'] = data['mess_title']
        outer['To'] = data['email']
        outer['From'] = data['from']

        s = data['mess_body']
        s = str.replace(s, "{logo_top}", globals.DB_HOSTNAME+"images/email/logo_top.png")
        s = str.replace(s, "{logo_bottom}", globals.DB_HOSTNAME+"images/email/logo_bottom.png")
        s = str.replace(s, "{hostName}", globals.DB_HOSTNAME)


        part = MIMEText(s, 'html', _charset="UTF-8")
        outer.attach(part)

        # Now send or store the message
        composed = outer.as_string()
        LOG.log('Informing email daemon -> email sent success. %s' % data['email'])
        utils.update_mail(data['id'])

    except Exception as e:
        LOG.log('Informing email daemon -> send mail error %s' % str(e))
        utils.fail_mail(data['id'])


def mailer_deamon():

    ret = utils.get_mails()
    if len(ret) > 0:
        LOG.log('Informing email daemon -> %d ta email yuborish kerak.' % len(ret))
    else:
        LOG.log('Informing email daemon -> yuboriladigan email yo`q.')


    mail_threads = []
    for row in ret:
        LOG.log('Informing email daemon -> from:%s to %s' % (str(row['from']), str(row['email'])))
        mail_thread = threading.Thread(target=send_mail, args=(row,))
        mail_thread.start()
        mail_threads.append(mail_thread)

    for thread in mail_threads:
        thread.join()



if __name__ == '__main__':

    ### DB ga connection qilib oladi
    while not utils.connectDB():
        time.sleep(5)

    socket_thread = threading.Thread(target=utils.listenPort, args=( globals.listenPort_informing_mail , ))
    socket_thread.start()
    mailer_deamon()

