###
#   Author is Ulug'bek Ro'zimboyev <ulugbekrozimboyev@gmail.com>
#   version 2.0.0
#
#   This daemon based on task_deamon.
#   Differences between task_deamon and this one:
#       - before call dissmiss employee or another action, do login to biotrack system
#       - crypt class. it is used to increaze security of login
#
###
import json
import urllib.request, urllib.parse, urllib.error, http.cookiejar
import time
from datetime import datetime
import globals
from logs import LOG
import utils

socket_thread = None
loginCookie = None
cryptObj = None

def _syncTaskDaemonUser():
    utils.clearOldTasDaemonUsers()
    utils.insertDaemonUser(cryptObj.key, cryptObj.salt)

def http_request(url, data):
    """
    HTTP send function
    param url: type string
    param data: type dictionary
    """


    global loginCookie

    try:
        json_data = json.loads(data)
        param = ''
        for k in json_data.keys():
            if param == '':
                param += '%s=%s' % (k, json_data[k])
            else:
                param += '&%s=%s' % (k, json_data[k])
        param +=  '&TaskDaemon=1'


        print("Task daemon -> url: %s" % url)
        #print(param)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Cookie' : '%s=%s' % (loginCookie.name , loginCookie.value)
        }

        proxy_support = urllib.request.ProxyHandler({"http":globals.DB_HOSTNAME})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

        req = urllib.request.Request(url, param.encode(), headers)

        f = urllib.request.urlopen(req)

        response = f.read()

        f.close()
        LOG.log("Task daemon -> %s" % (str(response)) )
        if (b'"status":true' in response) or (b'"success":"success"' in response):
            return True
        return False
    except Exception as e:
        LOG.log("Task daemon -> http send error: %s, url:%s, params:%s" %(e,url, param))
        return False


def task_deamon():

    global loginCookie

    first_start = True

    #checking for time
    if not (datetime.now().hour in [0, 1, 9]) and not first_start:
        #time.sleep(12 * globals.task_deamon_period)
        print('Task daemon -> sleep here')

    ret = None

    if not (datetime.now().hour in [9]):
        ret = utils.get_planned_tasks()
    if (first_start or (datetime.now().hour in [9])) and not ret:
        ret = utils.get_planned_tasks_old()

    first_start = False

    if not ret:
        LOG.log('Task daemon -> task yoq:%s'%datetime.now())
        #time.sleep(globals.task_deamon_period)

    num_ret = len(ret)
    err_num = 0
    i = 0
    LOG.log('Task daemon -> %s task topildi:%s' % (num_ret, datetime.now()))
    while num_ret > i:
        status = '1'
        row = ret[i]

        if not row['actionURL']:
            i += 1
            continue
        # if globals.SSL_MODE == 'False':
        #     row['actionURL'] = row['actionURL'].replace("https://", "http://")

        if not http_request(row['actionURL'], row['postParams']):
            err_num += 1 #error count
            if err_num < globals.retry_num: #check for error count
                time.sleep(globals.delay)
                #loginCookie = None
                continue
            else:
                LOG.log('Task daemon -> task bajarilmadi,  %s marta takroran bajarilib korildi task-ID:%s'%(globals.retry_num, row['ID']))
                status = '-1'
        else:
            status = '1'

        if row['typeChangeID'] == 3:
            utils.call_procedure_init_employee_shift_report(row['employeeID'], row['startDateTime'])

        utils.update_planned_task_status(status, row['ID'])

        i += 1
        err_num = 0


if __name__ == '__main__':

    ### DB ga connection qilib oladi
    while not utils.connectDB():
        time.sleep(5)

    task_deamon()