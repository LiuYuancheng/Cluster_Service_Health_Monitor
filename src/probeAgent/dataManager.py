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

import time
import json
import threading
import requests

from datetime import datetime

import probeGlobal as gv
import udpCom
import Log


# Define all the local untility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income message to tuple with 3 elements: request key, type and jsonString
        Args: msg (str): example: 'GET;dataType;{"user":"<username>"}'
    """
    req = msg.decode('UTF-8') if not isinstance(msg, str) else msg
    try:
        reqKey, reqType, reqJsonStr = req.split(';', 2)
        return (reqKey.strip(), reqType.strip(), reqJsonStr)
    except Exception as err:
        Log.error('parseIncomeMsg(): The income message format is incorrect.')
        Log.exception(err)
        return('','',json.dumps({}))

#-----------------------------------------------------------------------------
def postData(jsonDict):
    reportUrl = "http://%s:%s/dataPost/" % (gv.gMonitorHubAddr['ipaddr'], str(gv.gMonitorHubAddr['port']))
    reportUrl += str(jsonDict['id'])
    try:
        gv.gDebugPrint("Start to report monitorHub[%s]" %str(gv.gMonitorHubAddr['ipaddr']), logType=gv.LOG_INFO)
        res = requests.post(reportUrl, json={"rawData":json.dumps(jsonDict)})
        if res.ok:
            gv.gDebugPrint(" monitorHub reply: %s" %str(res.json()), logType=gv.LOG_INFO)
    except Exception as err:
        gv.gDebugPrint("Service side not reachable, error: %s" %str(err), logType=gv.LOG_ERR)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ The data manager is a module running parallel with the main thread to 
        handle the data-IO with dataBase and the monitor hub's data fetching/
        changing request.
    """
    def __init__(self, parent, fetchMode=True) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        self.terminate = False
        self.fetchMode = fetchMode
        self.reportInterval = 0
        self.server = udpCom.udpServer(None, gv.UDP_PORT)
        self.lastUpdate = datetime.now()
        self.resultDict = {}

    #-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ Function to handle the data-fetch/control request from the monitor-hub.
            Args:
                msg (str/bytes): _description_
            Returns:
                bytes: message bytes reply to the monitor hub side.
        """
        gv.gDebugPrint("Incomming message: %s" % str(msg), logType=gv.LOG_INFO)
        resp = b'REP;deny;{}'
        (reqKey, reqType, reqJsonStr) = parseIncomeMsg(msg)
        if reqKey=='GET':
            if reqType == 'data':
                resp = ';'.join(('REP', 'data', json.dumps(self.resultDict)))
        return resp

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function will be called by start(). """
        time.sleep(1)
        if self.fetchMode:
            self.server.serverStart(handler=self.msgHandler)
        elif self.reportInterval > 0:
            while not self.terminate:
                time.sleep(self.reportInterval)
                self.reportToHub()
        gv.gDebugPrint("DataManager running finished.", logType=gv.LOG_INFO)
    
    #-----------------------------------------------------------------------------
    def archiveResult(self, resultDict):
        self.resultDict = resultDict
        gv.gDebugPrint(json.dumps(resultDict), prt=False, logType=gv.LOG_INFO)
        return None
    
    #-----------------------------------------------------------------------------
    def reportToHub(self):
        if not self.fetchMode:
            postData(self.resultDict)