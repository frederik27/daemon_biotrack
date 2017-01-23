import os
import time
import globals
import conf
import pymysql
import time

import threading
import urllib.parse, urllib.request
from datetime import datetime
from logs import LOG
from Base import DB

import utils

import string
import  socket

conBase = None  # base connection
socket_thread = None

def send_notification(data):
	#print(data)
	global conBase

	personCursor = utils.get_employees_info_by_array_of_ids(data['IDs'])

	st = 0
	#print(ret)
	#print(personCursor)
	if personCursor :
		ret = utils.get_mail_template(data['name'], personCursor[0]['lang'])

		msg = "%s" % ret['mess_body']

		#sent message to hr or manager
		msgTo = personCursor[0]['email']
		msg = msg.replace('{FullName}', personCursor[0]['fullname'])

		msg = msg.replace('{holidayName}', data['holidayName'])

		msg_title = ret['mess_title']
		fromEmail = ret['from']
		print('Holiday daemon -> message send to %s' % msgTo)
		st = utils.save_mail(msgTo, msg, msg_title, fromEmail, data['companyID'] , datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		print("Holiday daemon -> email status: %s " % st)


def send_holiday_notification(data):
	sql = """
        SELECT n.ID, n.notificationTypeID, n.IDs, n.companyID, nt.name, company.lang
        FROM %s n
            LEFT JOIN %s  nt ON n.notificationTypeID = nt.ID
            LEFT JOIN %s company ON company.ID = n.companyID
        WHERE n.email = 1 AND nt.name = '%s' AND n.companyID = %d """ % \
    (globals.tbl_notification_setting, globals.tbl_notification_type, globals.tbl_company,
                   globals.tbl_notification_type_holidays, data['companyID'])

	notificationSettings = conBase.exec_query(sql)

	for row in notificationSettings:
		row['holidayName'] = data['holiday_name']
		row['companyID'] = data['companyID']
		send_notification(row)


def holiday_deamon():

	while True:
		global conBase
		conBase = DB()
		if not conBase.connect():
			time.sleep(5)
			continue
		#conBase.exec_query("SET @hozir = NOW();")

		ret = utils.get_holidays()
		#print(ret)
		for row in ret:
			send_holiday_notification(row)


		time.sleep(3600*24)


if __name__ == '__main__':
	socket_thread = threading.Thread(target=utils.listenPort, args=( globals.listenPort_holiday , ))
	socket_thread.start()
	holiday_deamon()

