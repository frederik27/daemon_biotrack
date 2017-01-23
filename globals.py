
mailer_sending = 'mailersending'
mailer_list = 'mailerlist'
mailer_mailer = 'maileremail'
tbl_department = 'department'
tbl_employee = 'employee'
tbl_person = 'person'
tbl_notification = 'notifications'
tbl_notification_type = 'notification_type'
tbl_notification_setting = 'notification_setting'
tbl_report = 'report'
tbl_plannedchange = 'plannedchange'
tbl_mail_send_message = "mail_send_message"
tbl_mail_template_list = "mail_template_list"
tbl_mail_template_type = "mail_template_type"

tbl_temp_inout = "inout"
tbl_temp_inout = "temp_inout"



#holidays deamon settings
tbl_company_holidays = "company_holidays"
tbl_notification_type_holidays = "holidays"
tbl_company = "company"

#birthday deamon
tbl_notification_type_birthday = 'employeeBirthday'

#billing deamon
#tbl_billing_status = 'billing_status'
tbl_billing_status = 'billing_interval'
tbl_mail_send_message_test = 'mail_send_message_test'
tbl_user = 'user'
tbl_user_settings = 'user_settings'
tbl_language = 'language'
tbl_authassignment = 'authassignment'

notification_type_fiveDayAfterRegistration = 'fiveDayAfterRegistration'
notification_type_oneDaybeforeBillingExpired = 'oneDaybeforeBillingExpired'
notification_type_oneDaybeforeBillingExpiredTrial = 'oneDaybeforeBillingExpiredTrial'
notification_type_threeDaybeforeBillingExpired = 'threeDaybeforeBillingExpired'
notification_type_threeDaybeforeBillingExpiredTrial = 'threeDaybeforeBillingExpiredTrial'


#variables for periodic interval in second
retry_num = 1
delay = 10 #delay in second
task_deamon_period = 300

#load configuration file
import os
import conf
DIR = os.getcwd()
inipath = DIR + "/conf.ini"
config = conf.loadSettings(inipath)
DB_HOST = str(config['Database']['host'])
DB_HOSTNAME = str(config['Database']['hostName'])
DB_USER = str(config['Database']['user'])
DB_PWD = str(config['Database']['pwd'])
DB_NAME = str(config['Database']['db'])
SMTP_HOST = str(config['SMTP']['smtp_host'])
SMTP_USER = str(config['SMTP']['smtp_user'])
SMTP_PWD = str(config['SMTP']['smtp_pass'])
SMTP_PORT = int(config['SMTP']['smtp_port'])
PARAM = str(config['TaskDaemon']['param'])

### Ports for uptime root service
#   this ports are listening by daemons
#
###
listenPort_main = int(config['Ports']['listenPort_main'])
listenPort_informing_mail = int(config['Ports']['listenPort_informing_mail'])
listenPort_notification = int(config['Ports']['listenPort_notification'])
listenPort_holiday = int(config['Ports']['listenPort_holiday'])
listenPort_billing = int(config['Ports']['listenPort_billing'])
listenPort_birthday = int(config['Ports']['listenPort_birthday'])
listenPort_task = int(config['Ports']['listenPort_task'])
listenPort_inout_daemon = int(config['Ports']['listenPort_inout_daemon'])
### Ports for  uptime root service

#conf.saveSettings(inipath, config)

tbl_notification_type_lateInEmployee = "lateInEmployee"
tbl_notification_type_earlyOutEmployee = "earlyOutEmployee"
tbl_notification_type_lateInForMe = "lateInForMe"
tbl_notification_type_earlyOutForMe = "earlyOutForMe"

### email alias
email_alias_for_uz = 'biotrack.uz'
email_alias_for_ru = 'biotrack.ru'
email_alias_for_en = 'biotrack.com'


tbl_daemon_user = 'task_daemon'

moth_ru = ('', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
moth_en = ('', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')



