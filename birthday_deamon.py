import os
import time
import globals
import conf
import pymysql
import time

import threading
import urllib.parse, urllib.request
from datetime import datetime, timedelta
from logs import LOG
from Base import DB

import utils
import string

conBase = None  # base connection
socket_thread = None

def send_sms(data, msg):
	pass

def create_mail(data, employeesNames):
	#print(data)
	global conBase


	employeeID = int(data['ids'])
	personCursor = utils.get_employee_info(employeeID)
	if personCursor is None :
		return

	mailTmp  = utils.get_mail_template(globals.tbl_notification_type_birthday, personCursor['lang'])

	st = 0
	#print(ret)
	#print(personCursor)
	if mailTmp and (personCursor['email']):
		fullName = personCursor['fullname']
		#print(personCursor)
		msg = "%s" % mailTmp['mess_body']

		#sent message to hr or manager
		msgTo = personCursor['email']
		msg = msg.replace('{FullName}', fullName)

		msg = msg.replace('{employeesNames}', employeesNames)

		msg_title = mailTmp['mess_title']
		fromEmail = mailTmp['from']
		LOG.log("Birthday daemon -> message send to %s" % msgTo)
		st = utils.save_mail(msgTo, msg, msg_title, fromEmail, data['companyID'] , datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		print("Birthday daemon ->email status: %s" % st)


def sync_with_notification_settings(companyID, employeesNames):
	sql = """
		SELECT ids, lang, companyID FROM %s ns
		LEFT JOIN %s company ON company.ID = ns.companyID
		WHERE ns.companyID = %d
		AND notificationTypeID = ( SELECT nt.ID FROM %s nt WHERE nt.name = '%s' ); """ % \
		  (globals.tbl_notification_setting, globals.tbl_company, companyID, globals.tbl_notification_type, globals.tbl_notification_type_birthday  )

	res = conBase.exec_query(sql)

	#print(res)

	for row in res:
		create_mail(row, employeesNames)



def get_birthdays_records(data, birthdayDateMonth, birthdayDateDay):
	sql = """
        SELECT lastName , firstName FROM %s employee
            INNER JOIN %s person ON employee.ID = person.ID AND  MONTH(person.birthDate) = %s AND DAY(person.birthDate) = %s
            WHERE employee.state = 'active' AND  employee.isActive = 1
            AND employee.companyID = %d ; """ % \
        (globals.tbl_employee, globals.tbl_person, birthdayDateMonth, birthdayDateDay, data['companyID'] )

	employeesCursor = conBase.exec_query(sql)

	#print(employeesCursor)

	personsFullname = ''

	for employee in employeesCursor:
		fullname = employee['firstName'] + ' ' + employee['lastName']
		if personsFullname:
			personsFullname = ', ' + fullname
		else:
			personsFullname = fullname

	sync_with_notification_settings(data['companyID'], personsFullname)



def birthday_deamon():

	while True:
		now = datetime.now()
		tomorrow = now + timedelta(days=1)
		# birthdayDate = tomorrow moth + tomorrow day
		dataMonth = tomorrow.strftime('%m')
		dataDay = tomorrow.strftime('%d')
		birthdayDateStr = '-%s-%s' % (dataMonth, dataDay)
		birthdayDateStr = '%'+birthdayDateStr
		print("Birthday daemon -> birthday date: %s" % birthdayDateStr)

		global conBase
		conBase = DB()
		if not conBase.connect():
			time.sleep(5)
			continue
		#conBase.exec_query("SET @hozir = NOW();")
		ret = utils.get_companies_for_birthday(dataMonth, dataDay)
		#print(ret)

		for row in ret:
			get_birthdays_records(row, dataMonth, dataDay)

		print("Birthday daemon -> sleep tread")
		time.sleep(3600*24)


if __name__ == '__main__':
	socket_thread = threading.Thread(target=utils.listenPort, args=( globals.listenPort_birthday , ))
	socket_thread.start()
	birthday_deamon()

