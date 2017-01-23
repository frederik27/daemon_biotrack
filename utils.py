from _socket import SOL_SOCKET, SO_REUSEADDR
import globals
from logs import LOG
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse, urllib.request
import datetime
import socket
from Base import DB
import threading

conBase = None  # base connection
mutex = threading.Lock()  # global mutex - semaphore controlling


def connectDB():
    global conBase
    conBase = DB()
    if not conBase.connect():
        return False
    return True


def send_mail(mail_to, msg, msg_title):
    try:
        smtp = smtplib.SMTP(globals.SMTP_HOST, port=globals.SMTP_PORT, timeout=10)
        smtp.login(globals.SMTP_USER, globals.SMTP_PWD)
        html = msg
        outer = MIMEMultipart()
        outer['Subject'] = msg_title
        outer['To'] = mail_to
        outer['From'] = globals.SMTP_USER
        # outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        part = MIMEText(html, 'html', _charset="UTF-8")
        outer.attach(part)
        # Now send or store the message
        composed = outer.as_string()
        smtp.sendmail(globals.SMTP_USER, mail_to, composed)
        smtp.quit()
        return 1
    except Exception as e:
        LOG.log('send email error:%s' % str(e))
        return -1


def save_mail(mail_to, msg, msg_title, fromEmail, companyID, send_time):
    print("save message")
    global conBase, mutex

    try:

        msg = msg.replace('\'', "\"")

        sql = """INSERT INTO %s
                (
                     `company_id`,  `email`,
                     `create_time`,  `send_time`,
                     `mess_title`,
                     `mess_body`,  `from`
                )
                VALUES ( %d, '%s', NOW(), '%s', '%s', '%s', '%s' );""" % \
              (globals.tbl_mail_send_message, companyID, mail_to, send_time, msg_title, msg, fromEmail)
        with mutex:
            insert = conBase.exec(sql)
        return insert
    except Exception as e:
        LOG.log('Error on creating new email:' + str(e), True)
        return False


###
#  this function must return company payment status
#  executed @companyID
#  company payment records was writen from `billing_status` table
#  status will checked by that way: todays date greater than  `billing_status`.`f_time` and smaller than `billing_status`.`l_time`
###
# def checkCompanyPaymentStatus(companyID):
# 	global conBase,mutex
# 	now = datetime.now()
# 	sql = """
# 		select * from %s billing_status
# 		where companyID = %d and
# 		billing_status.f_time < '%s' and billing_status.l_time > '%s'	""" %\
# 	(globals.tbl_billing_status, companyID, now, now)
#
# 	with mutex:
# 	    ret = conBase.exec_query(sql)
#
# 	if(len(ret)):
# 		return 1
# 	return 0


# this function must return companyID for this Employee

def get_company_id(employeeID):
    global conBase, mutex

    sql = """
        SELECT companyID from %s where id=%s limit 1  """ % \
          (globals.tbl_employee, employeeID)

    with mutex:
        ret = conBase.exec_query(sql)
    if ret:
        return ret[0]

    return


###
#   is using by @billing_deamon
#   get employee informations for create new email
#   function expected @employeeID
#
#   All informations we need for create an email are following:
#   @fullname - from person table `firstName` + `lastName`
#   @email   - from person table `email`
#   @lang   - from language table `code` if it is empty than company table language
#
#   returns employee object or null
#
###

def get_employee_info(employeeID):
    global conBase, mutex
    # billing_status li eski versiya uchun
    # sql = """
    #     SELECT CONCAT( p.firstName , ' ' , p.lastName) AS fullname, p.email,
    #         IF( `language`.code IS NULL, company.lang, `language`.code  ) AS lang FROM %s emp
    #             LEFT JOIN %s user ON user.employeeID = emp.ID
    #             LEFT JOIN %s u_s ON u_s.userID = user.ID
    #             LEFT JOIN %s `language` ON `language`.ID = u_s.langID
    #             LEFT JOIN %s company ON company.ID = emp.companyID
    #             LEFT JOIN %s p ON p.ID = emp.ID
    #             INNER JOIN %s bs ON bs.companyID = emp.companyID AND bs.f_time <= NOW() AND bs.l_time >= NOW()
    #         WHERE emp.ID = %d AND emp.state = 'active' AND emp.isActive = 1 AND p.email IS NOT NULL AND p.email != ''  """ % \
    #     (globals.tbl_employee, globals.tbl_user, globals.tbl_user_settings, globals.tbl_language , globals.tbl_company, globals.tbl_person, globals.tbl_billing_status,  employeeID )
    sql = """
        SELECT CONCAT( p.firstName , ' ' , p.lastName) AS fullname, uc.username as email,
            IF( `language`.code IS NULL, company.lang, `language`.code  ) AS lang FROM %s emp
                LEFT JOIN %s user ON user.employeeID = emp.ID
                LEFT JOIN user_credential uc ON uc.id = user.user_credential_id
                LEFT JOIN %s u_s ON u_s.userID = user.ID
                LEFT JOIN %s `language` ON `language`.ID = u_s.langID
                LEFT JOIN %s company ON company.ID = emp.companyID
                LEFT JOIN %s p ON p.ID = emp.ID
                INNER JOIN %s bs ON bs.company_id = emp.companyid AND (NOW() BETWEEN bs.start_dt and bs.end_dt) AND bs.`type` <> 'blocked'
            WHERE emp.ID = %d AND emp.state = 'active' AND emp.isActive = 1  """ % \
          (globals.tbl_employee, globals.tbl_user, globals.tbl_user_settings, globals.tbl_language, globals.tbl_company,
           globals.tbl_person, globals.tbl_billing_status, employeeID)

    with mutex:
        ret = conBase.exec_query(sql)
    if ret:
        return ret[0]

    return


###
#   is using by @holiday_deamon, @notification_deamon
#   get employees by company informations for create new email
#   function expected @companyID
#
#   All informations we need for create an email are following:
#   @fullname - from person table `firstName` + `lastName`
#   @email   - from person table `email`
#   @lang   - from language table `code` if it is empty than company table language
#
#   returns array of employee. array might be empty
###

def get_employees_info(companyID):
    global conBase, mutex

    # eski billing_statusli versiya
    # sql ="""
    #     SELECT CONCAT( p.firstName , ' ' , p.lastName) AS fullname, p.email, emp.companyID,
    #         IF( `language`.code IS NULL, c.lang, `language`.code  ) AS lang
    #     FROM %s bs
    #         LEFT JOIN %s c ON c.ID = bs.companyID
    #         RIGHT JOIN %s emp ON emp.companyID = c.ID and  emp.state = 'active' AND emp.isActive = 1
    #         LEFT JOIN %s `user` ON `user`.employeeID = emp.ID
    #         LEFT JOIN %s u_s ON u_s.userID = `user`.ID
    #         LEFT JOIN %s `language` ON `language`.ID = u_s.langID
    #         RIGHT JOIN %s p ON p.ID = emp.ID AND p.email IS NOT NULL AND p.email != ''
    #     WHERE bs.companyID = %d AND bs.f_time <= NOW() AND bs.l_time >= NOW()   """ % \
    #  ( globals.tbl_billing_status,  globals.tbl_company, globals.tbl_employee, globals.tbl_user, globals.tbl_user_settings, globals.tbl_language, globals.tbl_person, companyID )

    sql = """
        SELECT CONCAT( p.firstName , ' ' , p.lastName) AS fullname, uc.username as email, emp.companyID,
            IF( `language`.code IS NULL, c.lang, `language`.code  ) AS lang
        FROM %s bs
            LEFT JOIN %s c ON c.ID = bs.company_id
            RIGHT JOIN %s emp ON emp.companyID = c.ID and  emp.state = 'active' AND emp.isActive = 1
            LEFT JOIN %s `user` ON `user`.employeeID = emp.ID
            LEFT JOIN user_credential `uc` ON `user`.user_credential_id = uc.id
            LEFT JOIN %s u_s ON u_s.userID = `user`.ID
            LEFT JOIN %s `language` ON `language`.ID = u_s.langID
            RIGHT JOIN %s p ON p.ID = emp.ID
        WHERE bs.company_id = %d AND (NOW() BETWEEN bs.start_dt and bs.end_dt) AND bs.`type` <> 'blocked'   """ % \
          (globals.tbl_billing_status, globals.tbl_company, globals.tbl_employee, globals.tbl_user,
           globals.tbl_user_settings, globals.tbl_language, globals.tbl_person, companyID)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @holiday_deamon, @notification_deamon
#   get employees information by employees ids
#
#   @dbConnection - database connection
#   @mutex - flag for workin with threads
###

def get_employees_info_by_array_of_ids(ids):
    global conBase, mutex

    # billing_status li eski versiya
    # personSql = """
    # SELECT CONCAT( person.firstName , ' ' , person.lastName) AS fullname, person.email, department.title, employee.companyID,
    #     IF( `language`.code IS NULL, company.lang, `language`.code  ) AS lang
    # FROM %s person
    # left join %s as employee on employee.ID = person.ID
    # left join %s as department on department.ID = employee.departmentID
    #
    # LEFT JOIN %s user ON user.employeeID = employee.ID
    #     LEFT JOIN %s u_s ON u_s.userID = user.ID
    #     LEFT JOIN %s `language` ON `language`.ID = u_s.langID
    #     LEFT JOIN %s company ON company.ID = employee.companyID
    #     INNER JOIN %s bs ON bs.companyID = employee.companyID AND bs.f_time <= NOW() AND bs.l_time >= NOW()
    #
    # WHERE person.ID IN (%s) AND employee.state = 'active' AND employee.isActive = 1 AND person.email IS NOT NULL AND person.email != '' """ % \
    # (globals.tbl_person, globals.tbl_employee, globals.tbl_department, globals.tbl_user, globals.tbl_user_settings,
    #  globals.tbl_language, globals.tbl_company, globals.tbl_billing_status, ids)

    personSql = """
		SELECT CONCAT( person.firstName , ' ' , person.lastName) AS fullname, uc.username as email, department.title, employee.companyID,
		    IF( `language`.code IS NULL, company.lang, `language`.code  ) AS lang
		FROM %s person
		left join %s as employee on employee.ID = person.ID
		left join %s as department on department.ID = employee.departmentID

		LEFT JOIN %s user ON user.employeeID = employee.ID
		LEFT JOIN user_credential uc ON uc.id = user.user_credential_id
        LEFT JOIN %s u_s ON u_s.userID = user.ID
        LEFT JOIN %s `language` ON `language`.ID = u_s.langID
        LEFT JOIN %s company ON company.ID = employee.companyID
        INNER JOIN %s bs ON bs.company_id = employee.companyID AND (NOW() BETWEEN bs.start_dt AND bs.end_dt) AND bs.`type` <> 'blocked'

		WHERE person.ID IN (%s) AND employee.state = 'active' AND employee.isActive = 1  """ % \
                (globals.tbl_person, globals.tbl_employee, globals.tbl_department, globals.tbl_user,
                 globals.tbl_user_settings,
                 globals.tbl_language, globals.tbl_company, globals.tbl_billing_status, ids)


    # print(personSql)

    personCursor = []
    with mutex:
        personCursor = conBase.exec_query(personSql)

    return personCursor


###
#   is using by @birthday_deamon
#   get companies (only id of company ) by
#   function expected @birthdayDateStr like `%-m-d`
#
#   returns company ids. array might be empty
###

def get_companies_for_birthday(birthdayDateMonth, birthdayDateDay):
    global conBase, mutex

    sql = """
        SELECT employee.companyID FROM %s employee
            INNER JOIN %s person ON employee.ID = person.ID AND MONTH(person.birthDate) = %s AND DAY(person.birthDate) = %s
            INNER JOIN %s bs ON bs.company_id = employee.companyID AND (NOW() BETWEEN bs.start_dt AND bs.end_dt) AND bs.`type` <> 'blocked'
            WHERE employee.state = 'active' AND  employee.isActive = 1
            GROUP BY employee.companyID ; """ % \
          (globals.tbl_employee, globals.tbl_person, birthdayDateMonth, birthdayDateDay, globals.tbl_billing_status)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @billing_deamon, @birthday_deamon, @holiday_deamon, @notification_deamon
#   get mail template by language and mail type
#   function expected @type - mail type, @lang - language
#
#   returns mail template or Null
###

def get_mail_template(type, lang):
    global conBase, mutex

    sql = """
        SELECT m.type_id, m.`from`, m.mess_title, m.mess_body, m.params
        FROM %s m
        LEFT JOIN %s l ON m.type_id = l.id
        WHERE l.name = '%s' AND m.lang = '%s'""" % \
          (globals.tbl_mail_template_list, globals.tbl_mail_template_type, type, lang)

    with mutex:
        ret = conBase.exec_query(sql)

    if ret:
        return ret[0]
    return


###
#   is using by @notification_deamon
#   get notifications
#
#
###

def get_notifications():
    global conBase, mutex
    # billing_statusli eski versiyasi
    # sql = """
    # 	SELECT n.ID, n.notification_settingID, n.notification_typeID, n.employeeID, n.dateTime, n.eventTime, n.lang, n.type, nt.name
    # 	FROM %s n
    # 		 JOIN %s  nt ON n.notification_typeID = nt.ID
    # 		 INNER JOIN %s employee ON employee.ID = n.employeeID AND employee.state = 'active' AND employee.isActive = 1
    # 		 INNER JOIN %s p ON p.ID = n.employeeID AND p.email IS NOT NULL AND (p.email != '' OR n.`type` = 'company' OR n.`type` = 'my')
    # 		 INNER JOIN %s billing_status ON billing_status.companyID = employee.companyID AND billing_status.f_time <= NOW() AND billing_status.l_time >= NOW()
    # 	WHERE n.`status` = 0  AND n.`isBusy` = 0 AND n.dateTime >= NOW() - INTERVAL 1 DAY
    # 	LIMIT 5
    #         """ % (globals.tbl_notification, globals.tbl_notification_type, globals.tbl_employee, globals.tbl_person, globals.tbl_billing_status )
    sql = """
			SELECT n.ID, n.notification_settingID, n.notification_typeID, n.employeeID, n.dateTime, n.eventTime,
			n.lang, n.type, n.sendTo, nt.name
			FROM %s n
				 JOIN %s  nt ON n.notification_typeID = nt.ID
				 INNER JOIN %s employee ON employee.ID = n.employeeID AND employee.state = 'active' AND employee.isActive = 1
				 INNER JOIN %s p ON p.employeeID = n.employeeID AND (n.`type` = 'company' OR n.`type` = 'my')
				 INNER JOIN %s billing_status ON billing_status.company_id = employee.companyID AND (NOW() BETWEEN billing_status.start_dt and billing_status.end_dt) AND billing_status.`type` <> 'blocked'
			WHERE n.`status` = 0  AND n.`isBusy` = 0 AND n.dateTime >= NOW() - INTERVAL 1 DAY
			LIMIT 5
            """ % (
    globals.tbl_notification, globals.tbl_notification_type, globals.tbl_employee, 'user', globals.tbl_billing_status)
    # print('sql=',sql)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @holiday_deamon
###
def get_holidays():
    global conBase

    sql = """
        SELECT h.ID, h.companyID, h.holiday_date, h.holiday_name, h.IDs, h.type
        FROM %s h
        INNER JOIN %s bs ON bs.company_id = h.companyID AND (NOW() BETWEEN bs.start_dt AND bs.end_dt) AND bs.`type` <> 'blocked'
        WHERE h.holiday_date = CURDATE() + INTERVAL 1 day """ % \
          (globals.tbl_company_holidays, globals.tbl_billing_status)

    return conBase.exec_query(sql)


###
#   get company by ID
#
#
###

# def get_company_by_id(companiID):
#     global conBase,mutex
#
#     sql = """ SELECT * from %s where ID = %d """ %  (globals.tbl_company, companiID )
#
#     with mutex:
#         return conBase.exec_query(sql)

###
#   is using by @informing_mail_deamon
#  informing mail daemon
#  get not sending mails
###
def get_mails():
    global conBase, mutex
    sql = "commit;"
    with mutex:
        conBase.exec_query(sql)
    sql = "SELECT * FROM mail_send_message WHERE (send_time >=DATE_ADD(NOW(), INTERVAL -1 DAY) AND status = 1) OR (status = 0 AND create_time>=DATE_ADD(NOW(), INTERVAL -1 DAY)) LIMIT 5;"
    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @informing_mail_deamon
#   update mail as a fail
###
def fail_mail(id):
    global conBase, mutex
    sql = 'UPDATE mail_send_message SET status=-1 WHERE ID=%d' % id
    with mutex:
        conBase.exec(sql)

###
#   is using by @informing_mail_deamon
#   update mail as a send
###
def update_mail(id):
    global conBase, mutex
    sql = 'UPDATE mail_send_message SET status=10 WHERE ID=%d' % id
    with mutex:
        conBase.exec(sql)


###
#   is using by @billing_deamon
###


###
#   is using by @informing_mail_deamon
#   update mail as a send
###
def update_nofications(id, busy):
    global conBase, mutex
    sql = 'UPDATE notifications SET isBusy=%d WHERE ID=%d' % (busy, id)
    with mutex:
        conBase.exec(sql)


def get_billing_expiration(date):
    global conBase, mutex
    # old version
    # sql = """
    #     select *, DATEDIFF(l_time , f_time) as day_interval from (select * from %s order by l_time desc) t
    #     group by companyID
    #     having DATE(l_time) =  '%s' """ % (globals.tbl_billing_status, date)
    sql = """
        select *, DATEDIFF(start_dt , end_dt) as day_interval from (select * from %s order by end_dt desc) t
        group by company_id
        having DATE(end_dt) =  '%s' """ % (globals.tbl_billing_status, date)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @billing_deamon
###
def get_billing_expiration_before_five_day():
    global conBase, mutex
    # old version
    # sql = """
    #     select *, DATEDIFF(l_time , f_time) as day_interval from (select * from `%s` order by l_time desc) t
    #     group by companyID
    #     having DATE(f_time) =   DATE(NOW() - INTERVAL  5 DAY)  """ % (globals.tbl_billing_status )
    sql = """
        select *, DATEDIFF(end_dt , start_dt) as day_interval from (select * from `%s` order by end_dt desc) t
        group by company_id
        having DATE(start_dt) =   DATE(NOW() - INTERVAL  5 DAY)  """ % (globals.tbl_billing_status)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @billing_deamon
#   get company roots by company id
#   companiya boshliqlari yani roli ModuleCompanyRoot bo'lgan userlarni olish barilgan companiya idsi bilan
###

def get_company_roots(companyID):
    global conBase, mutex
    sql = """
        SELECT CONCAT( p.firstName , ' ' , p.lastName) AS fullname, uc.username as email,
            IF( `language`.code IS NULL, company.lang, `language`.code  ) AS lang FROM %s emp
                LEFT JOIN %s user ON user.employeeID = emp.ID
                LEFT JOIN user_credential uc ON uc.id = user.user_credential_id
                LEFT JOIN %s u_s ON u_s.userID = user.ID
                LEFT JOIN %s `language` ON `language`.ID = u_s.langID
                LEFT JOIN %s company ON company.ID = emp.companyID
                LEFT JOIN %s p ON p.ID = emp.ID
                INNER JOIN %s authassignment ON authassignment.userid=user.ID AND authassignment.itemname='ModuleCompanyRoot'
            WHERE emp.companyID = %d AND emp.state = 'active' AND emp.isActive = 1  """ % \
          (globals.tbl_employee, globals.tbl_user, globals.tbl_user_settings, globals.tbl_language, globals.tbl_company,
           globals.tbl_person, globals.tbl_authassignment, companyID)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @task_daemon_with_login_request
###
def get_planned_tasks():
    global conBase, mutex
    sql = '''SELECT * FROM %s
        WHERE status = '0' AND finishedDateTime IS NULL AND DATE(startDateTime) <= CURDATE();''' % globals.tbl_plannedchange
    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @task_daemon_with_login_request
###
def get_planned_tasks_old():
    global conBase, mutex
    sql = '''SELECT * FROM %s WHERE status = '-1'
        AND DATE(startDateTime) <= CURDATE()
        AND DATE(startDateTime) >= CURDATE() - INTERVAL 7 DAY ;''' % globals.tbl_plannedchange
    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @task_daemon_with_login_request
###
def update_planned_task_status(status, id):
    global conBase, mutex
    sql = "UPDATE %s SET status= '%s', finishedDateTime = NOW() WHERE ID=%s" % (globals.tbl_plannedchange, status, id)
    with mutex:
        conBase.exec(sql)


###
#   is using by @task_daemon_with_login_request
###
def call_procedure_init_employee_shift_report(employeeID, startDateTime):
    global conBase, mutex
    sql = "CALL `init_employee_shift_report`(%s, '%s')" % (employeeID, startDateTime)

    with mutex:
        conBase.exec(sql)


###
#   port listener
#   @return nothing
###
def listenPort(port):
    # global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    print("listening port: %s" % port)
    conn.bind(("", port))
    conn.listen(5)
    # now keep talking with the client
    while 1:
        # wait to accept a connection - blocking call
        c, addr = conn.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))


def get_persons_by_user_ids(usersID):
    global conBase, mutex
    sql = """
            SELECT DISTINCT p.lastName, p.firstName, p.email
            FROM %s p
            LEFT JOIN %s AS ns ON ns.userID = p.ID
            WHERE ns.userID IN (%s)""" % \
                 (globals.tbl_person, globals.tbl_notification_setting, usersID)

    with mutex:
        return conBase.exec_query(sql)



###
#   is using by @notification_deamon
#   select person by notification settings id
###
def get_person_by_notification_settings_id(usersID):
    global conBase, mutex
    sqlCompany = """
        SELECT  p.lastName, p.firstName, p.email
        FROM %s p
        LEFT JOIN %s AS ns ON ns.userID = p.ID
        WHERE ns.userID IN (%s)""" % \
                 (globals.tbl_person, globals.tbl_notification_setting, usersID)
    print("SQL ", sqlCompany)
    with mutex:
        return conBase.exec_query(sqlCompany)


###
#   is using by @notification_deamon
###
def update_notification_by_id(id):
    global conBase, mutex
    sql = 'UPDATE %s SET status = 1 WHERE ID=%d' % (globals.tbl_notification, id)
    with mutex:
        conBase.exec(sql)


###
#   is using by @notification_deamon
###
def get_notification_type(id):
    global conBase, mutex
    sql = """
        SELECT n.name
        FROM %s n
        WHERE n.ID = %d """ % (globals.tbl_notification_type, id)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @notification_deamon
###
def get_report(employeeID, date):
    global conBase, mutex

    sql = """
        SELECT r.lateIn, r.earlyOut
        FROM %s r
        WHERE r.employeeID = %d AND r.date LIKE '%s'""" % (globals.tbl_report, employeeID, date)

    with mutex:
        return conBase.exec_query(sql)


###
#   is using by @task_daemon_with_login_request
#   insert to daemon_users table
###
def insertDaemonUser(hashcode, salt):
    global conBase, mutex

    sql = """INSERT INTO %s (hashcode, salt) VALUES ( "%s", "%s")""" % (globals.tbl_daemon_user, hashcode, salt)
    with mutex:
        return conBase.exec(sql)


###
#   is using by @task_daemon_with_login_request
###
def clearOldTasDaemonUsers():
    global conBase, mutex

    sql = """DELETE FROM %s""" % (globals.tbl_daemon_user)
    with mutex:
        return conBase.exec_query(sql)
