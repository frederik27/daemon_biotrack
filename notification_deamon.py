import globals
import utils
import time
import threading
import urllib.request

from datetime import datetime
from logs import LOG

socket_thread = None

def file_exists(location):
    request = urllib.request.Request(location)
    request.get_method = lambda : 'HEAD'
    try:
        response = urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def get_diff_time(notificationTypeID, employeeID, date):
    diffTime = ''

    try:

        notificationType = utils.get_notification_type(notificationTypeID)

        report = utils.get_report(employeeID, date)

        #print('Notification daemon -> report record');
        #print(report);
        if report:
            if notificationType and notificationType[0]['name'] == globals.tbl_notification_type_lateInForMe or  notificationType[0]['name'] == globals.tbl_notification_type_lateInEmployee :
                diffTime = report[0]['lateIn']

            elif notificationType and notificationType[0]['name'] == globals.tbl_notification_type_earlyOutEmployee or  notificationType[0]['name'] == globals.tbl_notification_type_earlyOutForMe :
                diffTime = report[0]['earlyOut']

    except Exception as e:
        LOG.log('Notification daemon -> ~~ open error:  %s' % e)

    return "%s" % diffTime

def send_notification(data):
    print("Я ЗАШЕЛ СЮДА")
    utils.update_nofications(data['ID'], 1)
    print("Notification daemon -> Busy: 1" )


    ret = utils.get_mail_template(data['name'], data['lang'])
    curDt = data['eventTime']
    if data['lang'] == 'ru':
        #DD.MM.YYYY HH:MI:SS
        #9 Март 2008
        dayformat = '%d %s %4d' % (curDt.day, globals.moth_ru[curDt.month], curDt.year)
    if data['lang'] == 'en':
        #MM-DD-YYYY HH:MI:SS
        #March 9, 2008
        dayformat = '%s %2d, %4d' % (globals.moth_en[curDt.month], curDt.day, curDt.year)
    s = ret['mess_body']
    s = str.replace(s, "{logo_top}", globals.DB_HOSTNAME+"images/email/logo_top.png")
    s = str.replace(s, "{logo_bottom}", globals.DB_HOSTNAME+"images/email/logo_bottom.png")
    s = str.replace(s, "{hostName}", globals.DB_HOSTNAME)
    s = str.replace(s, "{date}", dayformat)
    # print("emp", data['employeeID'])
    compID = utils.get_company_id(data['employeeID'])
    # print("comp", compID['companyID'])
    imgUrl=("images/employee/40/%s/%s.png" % (compID['companyID'], data['employeeID']))
    # print("img url", imgUrl)
    imgUrl = globals.DB_HOSTNAME + imgUrl
    if file_exists(imgUrl):
        s = str.replace(s, "{image_data}", imgUrl)
    else:
        s = str.replace(s, "{image_data}", globals.DB_HOSTNAME + 'images/avatar-empty.png')
    #print(s)
    ret['mess_body'] = s
    #print(ret['mess_body'])
    # print(globals.DB_HOSTNAME)
    # print(data['employeeID'])

    personCursor = utils.get_employees_info_by_array_of_ids(data['employeeID'])
    #print("PerCUr", personCursor)

    st = 0

    if ret and personCursor:
        fullName = personCursor[0]['fullname']
        departmentName = "%s" % personCursor[0]['title']

        fromEmail = ret['from']
        msg_title = ret['mess_title']

        time = "%s" % data['eventTime']
        time = time.split(' ')
        msg = "%s" % ret['mess_body']

        #getting different time. it depends on notification type
        diffTime = get_diff_time(data['notification_typeID'], data['employeeID'], time[0])

        msg = msg.replace('{time}', time[1])
        msg = msg.replace('{diffTime}', diffTime)
        msg = msg.replace('{department}', departmentName)
        msg = msg.replace('{employeeFullname}', fullName)

        msgTo = personCursor[0]['email']
        if data['type'] == 'company':
            print("COMPANY")
            saveMsg = msg
            personsData = utils.get_persons_by_user_ids(data['sendTo'])
            for personData in personsData:
                fullNameCompany = ''
                if personData and personData['email']:
                    fullNameCompany = personData['firstName'] + ' ' + personData['lastName']
                    msgTo = personData['email']

                msg = saveMsg.replace('{FullName}', fullNameCompany)

                print('Notification daemon -> message send to %s' % msgTo)
                st = utils.save_mail(msgTo, msg, msg_title, fromEmail, personCursor[0]['companyID'],
                                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print("MY")
            msg = msg.replace('{FullName}', fullName)
            print('Notification daemon -> message send to %s' % msgTo)
            st = utils.save_mail(msgTo, msg, msg_title, fromEmail, personCursor[0]['companyID'] , datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        print("Notification daemon -> email status: %s" % st)

    utils.update_notification_by_id(data['ID'])
    # utils.update_nofications(data['ID'], 0)
	# print("Notification daemon -> Busy: 0" )


def timetostr(t):
    res = ''
    stime = str(t).split(':')
    hour = int(stime[0])
    min = int(stime[1])
    if hour > 0:
        res += str(hour) + ' ч '
    if min > 0:
        res += str(min) + ' мин.'
    return res


def notification_deamon():
    ret = utils.get_notifications()
    print("ret=", ret)

    for row in ret:
        utils.update_nofications(row['ID'], 1)
    num_ret = len(ret)
    LOG.log('Notification daemon -> %s notification find:%s'%(num_ret, datetime.now()))

    mail_threads = []
    for row in ret:
        print('row=', row,)
        mail_thread = threading.Thread(target=send_notification, args=(row,))
        mail_thread.start()
        mail_threads.append(mail_thread)

    for thread in mail_threads:
        thread.join()
        exit()



if __name__ == '__main__':

    while not utils.connectDB():
        time.sleep(5)

    # socket_thread = threading.Thread(target=utils.listenPort, args=( globals.listenPort_notification , ))
    # socket_thread.start()
    notification_deamon()

