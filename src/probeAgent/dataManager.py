#-----------------------------------------------------------------------------
# Name:        dataManage.py
#
# Purpose:     Data manager class used to provide specific data fetch and process 
#              functions and init the local data storage/DB. This manager is used 
#              by the scheduler(<actionScheduler>) obj.
#              
# Author:      Yuancheng Liu 
#
# Version:     v_0.2
# Created:     2023/01/11
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import threading
import time

from datetime import datetime

import probeGlobal as gv
import udpCom

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ The data manager is a module running parallel with the main thread to 
        handle the data-IO with dataBase and the monitor hub's data fetching/
        changing request.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        self.terminate = False
        self.server = udpCom.udpServer(None, gv.UDP_PORT)
        self.lastUpdate = datetime.now()

    def msgHandler(self, msg):
        """ Function to handle the data-fetch/control request from the monitor-hub.
            Args:
                msg (str/bytes): _description_
            Returns:
                bytes: message bytes reply to the monitor hub side.
        """
        gv.gDebugPrint("Incomming message: %s" % str(msg), logType=gv.LOG_INFO)
        return None

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function will be called by start(). """
        time.sleep(1)
        self.server.serverStart(handler=self.msgHandler)
        gv.gDebugPrint("DataManager running finished.", logType=gv.LOG_INFO)
    
    #-----------------------------------------------------------------------------
    def archiveResult(self, resultDict):
        pass
        return None