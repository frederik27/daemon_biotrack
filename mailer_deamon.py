import os
import time
import globals
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import urllib.parse, urllib.request
from logs import LOG
from Base import DB

conBase = None  # base connection

#http post request
def getHTMLfromURL(url, timeout=30):
    uAgent = 'Mozilla/20.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/html",
                'User-Agent': uAgent
                }
    try:
        req = urllib.request.Request(url, None, headers)
        wTxt = urllib.request.urlopen(req, timeout=timeout).read()
    except Exception as e:
        LOG.log('~~ open error:  %s' % e)
        return ''
    return wTxt.decode('utf-8', 'replace').strip()

def send_mail(data, mutex):
    try:
        smtp = smtplib.SMTP(globals.SMTP_HOST, port=globals.SMTP_PORT, timeout=10)
        smtp.login(globals.SMTP_USER, globals.SMTP_PWD)
        html = getHTMLfromURL('http://new.maxtrack.uz')
        outer = MIMEMultipart()
        outer['Subject'] = data['subject']
        outer['To'] = data['emails']
        outer['From'] = globals.SMTP_USER
        #outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        part = MIMEText(html, 'html', _charset="UTF-8")
        outer.attach(part)

        # Now send or store the message
        composed = outer.as_string()
        smtp.sendmail(globals.SMTP_USER, data['emails'].split(), composed)
        LOG.log('email yuborildi. %s'%data['emails'])
        with mutex:
            global conBase
            sql = 'UPDATE %s SET updateDateTime = NOW() WHERE ID=%d'%(globals.mailer_sending, data['ID'])
            conBase.exec(sql)
    except Exception as e:
        LOG.log('send mail error %s'%str(e))

def mailer_deamon():
    while True:
        global conBase
        conBase = DB()
        if not conBase.connect():
            time.sleep(5)
            continue
        conBase.exec_query("SET @hozir = NOW();")
        sql = """
            SELECT
            ms.ID,
            ms.mailerListID,
            ms.updateDateTime,
            ms.sendDateTime,
            m.days,
            m.subject,
            GROUP_CONCAT(m.email)  emails
            FROM
            (SELECT
                ml.ID,
                ml.sendType,
                ml.days,
                ml.companyID,
                ml.alias  subject,
                mm.email
                FROM %s ml, %s mm
                WHERE ml.id = mm.mailerListID
                AND mm.isActive
                AND (
                        ml.sendType = 'weekly'  AND  LOCATE(WEEK(@hozir), CONCAT(',', ml.days, ',')) > 0
                        OR
                        ml.sendType = 'monthly' AND DAY(@hozir) = 15 AND LOCATE('16', CONCAT(',', ml.days, ',')) > 0
                        OR
                        ml.sendType = 'monthly' AND DAY(@hozir) = LAST_DAY(@hozir) AND LOCATE('32', CONCAT(',', ml.days, ',')) > 0
                    )

            ) m , %s ms
            WHERE
                ms.mailerListID = m.ID
                AND
                (
                    ms.updateDateTime is NULL OR  DATE(ms.updateDateTime) < CURDATE()
                )
                AND
                    ms.sendDateTime < CURTIME()
            GROUP BY ms.ID
            """%(globals.mailer_list, globals.mailer_mailer, globals.mailer_sending)
        ret = conBase.exec_query(sql)
        if len(ret) > 0:
            LOG.log('%d ta email yuborish kerak.'%len(ret))
        else:
            LOG.log('Hali email topilmadi.')


        mutex = threading.Lock()
        mail_threads = []
        for row in ret:
            LOG.log(str(row))
            mail_thread = threading.Thread(target=send_mail, args=(row, mutex))
            mail_thread.start()
            mail_threads.append(mail_thread)

        for thread in mail_threads:
            thread.join()

        time.sleep(60)


if __name__ == '__main__':
    mailer_deamon()

