import birthday_deamon
import billing_deamon
import holiday_deamon
import notification_deamon
import informing_mail_deamon
import task_daemon_with_login_request

from logs import LOG
import threading
import utils
import globals
import time

def start_billing_daemon():
    LOG.log("Billing daemon has started")
    billing_deamon.billing_deamon()

def start_notification_daemon():
    LOG.log("Notification daemon has started")
    notification_deamon.notification_deamon()


def start_infroming_daemon():
    LOG.log("Informing main daemon has started")
    informing_mail_deamon.mailer_deamon()


def start_task_daemon():
    LOG.log("Task daemon has started")
    task_daemon_with_login_request.task_deamon()


def listenPort():
    socket_thread = threading.Thread(target=utils.listenPort, args=( globals.listenPort_main , ))
    socket_thread.start()


if __name__ == '__main__':

    ### DB ga connection qilib oladi
    while not utils.connectDB():
        time.sleep(5)


    ## starting all daemons
    start_billing_daemon()
    start_infroming_daemon()
    start_notification_daemon()
    time.sleep(15)
    start_task_daemon()

    # listenPort()
