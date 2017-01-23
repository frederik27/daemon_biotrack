#!/usr/bin/python
# -*- coding: utf-8 -*-

import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket, time, os, sys
from logs import LOG

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "Task Deamon"
    _svc_display_name_ = "Task Deamon service"
    svcStop = False

    def __init__(self, args):
        self.svcStop = False
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def setupSvc(self):
        sys.argv.append('install')
        win32serviceutil.InstallService(None, self._svc_name_, self._svc_display_name_)


    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.svcStop = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while True:
            LOG.log('service running.')
            time.sleep(10)
        #task_deamon.task_deamon()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)