import globals
import time
import threading
from datetime import datetime, timedelta

from logs import LOG
import utils


socket_thread = None

def create_mail(notificationType, companyID):

    LOG.log("Billing daemon -> companyID: %s" % companyID)
    companyRoots = utils.get_company_roots(companyID)

    for companyRoot in companyRoots:

        ret = utils.get_mail_template(notificationType, companyRoot['lang'])

        if ret and companyRoot['email']:
            msg = "%s" % ret['mess_body']

            #sent message to hr or manager
            msgTo = companyRoot['email']
            msg = msg.replace('{FullName}', companyRoot['fullname'])

            msg_title = ret['mess_title']
            fromEmail = ret['from']
            LOG.log("Billing daemon -> message send to %s" % msgTo)
            st = utils.save_mail(msgTo, msg, msg_title, fromEmail, companyID , datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            LOG.log("Billing daemon -> mail status: %s" % st)

###
# it si send mail 5 day after registrasion
###
def mail_after_five_day():

    ret = utils.get_billing_expiration_before_five_day()

    for row in ret:
        if row['day_interval'] == 14:
            create_mail(globals.notification_type_fiveDayAfterRegistration , row['companyID'])

    return 0

###
#   this function searchs upcoming billing expirations
#
#   function expected as params:
#   @DBConnection - connection to databse
#   @date - billing expirations date
#   @notificationType - notification type
###

def search_upcoming_expirations(date, notificationType):

	ret = utils.get_billing_expiration(date)

	for row in ret:
        # trial email one day before expiretions
		if row['day_interval'] == 14:
			if notificationType == globals.notification_type_oneDaybeforeBillingExpired:
				create_mail(globals.notification_type_oneDaybeforeBillingExpiredTrial, row['companyID'])
		    # trial email one day before expiretions
			else :
				create_mail(globals.notification_type_threeDaybeforeBillingExpiredTrial, row['companyID'])

	return 0


def billing_deamon():

    now = datetime.now()
    beforeThreeDay = (now + timedelta(days=3)).strftime('%Y-%m-%d')
    beforeDay = (now + timedelta(days=1)).strftime('%Y-%m-%d')

    dayNotification = globals.notification_type_oneDaybeforeBillingExpired
    threeDayNotification = globals.notification_type_threeDaybeforeBillingExpired

    # create mail three day ego expire account
    search_upcoming_expirations(beforeThreeDay, threeDayNotification);

    # create mail a day ego expire account
    search_upcoming_expirations(beforeDay, dayNotification);

    # create email 5 day after registration
    mail_after_five_day();

    # it is just a test
    # search_upcoming_expirations(conBase, '2013-05-04', dayNotification);

    LOG.log("Billing daemon -> sleep thread")


if __name__ == '__main__':

    ### DB ga connection qilib oladi
    while not utils.connectDB():
        time.sleep(5)

    billing_deamon()

