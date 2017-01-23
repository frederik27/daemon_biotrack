import logging
import os
from datetime import datetime
class LOG:
    def log(msg):
        fname = os.getcwd() + '/logs/' + datetime.now().strftime('%Y%m%d') + ".txt"
        with open(fname, "a") as f:
            f.write("[" + datetime.now().strftime('%H:%M:%S') +"] " + msg + "\n")
        #logging.basicConfig(format = '%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = fname)
        #logging.debug(msg)
        #if p:
        print(msg)


