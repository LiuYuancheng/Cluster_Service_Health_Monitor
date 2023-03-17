#-----------------------------------------------------------------------------
# Name:        probGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2023/03/15
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import os
import time
import json
import random 
import threading
from influxdb import InfluxDBClient

import monitorGlobal as gv
from datetime import datetime

import Log
import udpCom

# Define all the module local untility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income message to tuple with 3 element: request key, type and jsonString
        Args: msg (str): example: 'GET;dataType;{"user":"<username>"}'
    """
    req = msg.decode('UTF-8') if not isinstance(msg, str) else msg
    reqKey = reqType = reqJsonStr= None
    try:
        reqKey, reqType, reqJsonStr = req.split(';', 2)
    except Exception as err:
        Log.error('parseIncomeMsg(): The income message format is incorrect.')
        Log.exception(err)
    return (reqKey.strip(), reqType.strip(), reqJsonStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class InfluxCli(object):
    """ Client to connect to the influx db and insert data."""
    def __init__(self, ipAddr=None, dbInfo=None):
        """ Init the influx DB client to login to the data base. dbInfo: name, 
            password, databaseName. init example: 
            client = InfluxCli(ipAddr=('127.0.0.1', 8086), dbinfo=('root', 'root', 'gatewayDB'))
        """
        (ip, port) = ipAddr if ipAddr else ('localhost', 8086)
        (user, pwd, dbName) = dbInfo if dbInfo and len(
            dbInfo) == 3 else ('root', 'root', 'gatewayDB')
        #self.dbClient = InfluxDBClient('localhost', 8086, 'root', 'root', 'quantumGWDB')
        # link to data base:
        try:
            self.dbClient = InfluxDBClient(ip, port, user, pwd, dbName)
        except Exception as e:
            print("Can not connect to the data base, please check whether the influxDB service is running. \n" 
                + "- Windows:   go to D:\\Tools\\InfluxDB\\influxdb-1.8.1-1 and run influxd.exe \n"
                + "- Ubuntu:    sudo systemctl start influxdb" )
            exit()
        # state the UDP server:
        print("inited")

    #-----------------------------------------------------------------------------
    def writeServiceInfo(self, serviceName, fieldDict):
        """ Write the gateway data to the related gateway table based on gateway 
            name. 
        """
        dataJoson = [
            {
                "measurement": str(serviceName),
                "tags": { "Name": "time",},
                "fields": fieldDict
            }]
        self.dbClient.write_points(dataJoson)

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
        self.dbhandler = InfluxCli(ipAddr=('localhost', 8086), dbInfo=('root', 'root', gv.TB_NAME))
        self.terminate = False
        self.timeInterval = 20
        self.ipaddress = '172.18.178.6'
        self.udpPort = 3001
        self.connector = udpCom.udpClient((self.ipaddress, self.udpPort))
        self.lastUpdate = datetime.now()
        self.resultDict = {}
        # the percentage will be shown on dashboard.
        self.serviceInfoDict = {
            'total_num': 0.0,
            'firewall_on': 0.0,
            'firewall_off':100.0,
            'openstack_on':0.0,
            'openstack_off':100.0,
            'kypo_on':0.0,
            'kypo_off':100.0,
            'ctf_on':0.0,
            'ctf_off':100.0,
            'gpu_on': 0.0,
            'gpu_off': 100.0,
            'sup_on': 0.0,
            'sup_off': 100.0
        }

        self.clusterResultDict = {
            'FW': { "online": 0,"total": 8},
            'CT02': { "online": 0,"total": 6},
            'CP01': { "online": 0,"total": 3},
            'CP02': { "online": 0,"total": 3},
            'CP03': { "online": 0,"total": 3},
            'KP00': { "online": 0,"total": 5},
            'KP01': { "online": 0,"total": 5},
            'KP02': { "online": 0,"total": 5},
            'CR00': { "online": 0,"total": 5},
            'CR01': { "online": 0,"total": 5},
            'GPU1': { "online": 0,"total": 3},
            'GPU2': { "online": 0,"total": 3},
            'GPU3': { "online": 0,"total": 3},
            'SUP': { "online": 0,"total": 3},
        }

        self.testMode = True

#-----------------------------------------------------------------------------
    def _getStatePct(self, countList):
        online, total = countList[0], countList[1]
        if self.testMode: online = random.randint(0, min(online+1, total))
        onPct = round(float(online)*100/total,1)
        offPct = round(100.0 - onPct, 1)

        return (onPct, offPct)

#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            if self.dbhandler:
                if self.testMode:
                    dirpath = os.path.dirname(__file__)
                    f = open(os.path.join(dirpath, 'test.json'))
                    data = json.load(f)
                    inputDict = data
                    self.updateCountResult(inputDict)
                    self.updateServiceInfo()
                    print(self.getSericeDict())
                else:
                    resp = self.connector.sendMsg('GET;data;fetch', resp=True)
                    if resp:
                        k, t, data = parseIncomeMsg(resp)
                        inputDict = json.loads(data)
                        self.updateCountResult(inputDict)
                        self.updateServiceInfo()
                        print(self.getSericeDict())
                self.dbhandler.writeServiceInfo(gv.gMeasurement, self.getSericeDict())
                # update the score
                ScoreDict ={
                    'online': round(self.serviceInfoDict['total_num']/60, 1),
                    'offline': 0.0,
                    'total': 0.0
                }
                self.dbhandler.writeServiceInfo('test0_allService', ScoreDict)
            time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
    def updateServiceInfo(self):
        totalcount = [0, 0]
        fwCounts = [0, 0]
        opCounts = [0, 0]
        kpCounts = [0, 0]
        ctfCounts = [0, 0]
        gpuCounts = [0, 0]
        supCounts = [0, 0]
        for item in self.clusterResultDict.items():
            key, val = item
            totalcount[0] += val['online']
            totalcount[1] += val['total']

            if 'FW' in key:
                fwCounts[0] += val['online']
                fwCounts[1] += val['total']

            if 'CT' in key or 'CP' in key:
                opCounts[0] += val['online']
                opCounts[1] += val['total']

            if 'KP' in key:
                kpCounts[0] += val['online']
                kpCounts[1] += val['total']

            if 'CR' in key:
                ctfCounts[0] += val['online']
                ctfCounts[1] += val['total']

            if 'GPU' in key:
                gpuCounts[0] += val['online']
                gpuCounts[1] += val['total']

            if 'SUP' in key:
                supCounts[0] += val['online']
                supCounts[1] += val['total']

        # calculate the percentage;
        self.serviceInfoDict['total_num'] =  round(float(totalcount[0]), 1)
        if self.testMode: self.serviceInfoDict['total_num'] += random.randint(0, 12)

        rst = self._getStatePct(fwCounts)
        self.serviceInfoDict['firewall_on'] = rst[0]
        self.serviceInfoDict['firewall_off'] = rst[1]

        rst = self._getStatePct(opCounts)
        self.serviceInfoDict['openstack_on'] = rst[0]
        self.serviceInfoDict['openstack_off'] = rst[1]

        rst = self._getStatePct(kpCounts)
        self.serviceInfoDict['kypo_on'] = rst[0]
        self.serviceInfoDict['kypo_off'] = rst[1]

        rst = self._getStatePct(ctfCounts)
        self.serviceInfoDict['ctf_on'] = rst[0]
        self.serviceInfoDict['ctf_off'] = rst[1]

        rst = self._getStatePct(gpuCounts)
        self.serviceInfoDict['gpu_on'] = rst[0]
        self.serviceInfoDict['gpu_off'] = rst[1]

        rst = self._getStatePct(supCounts)
        self.serviceInfoDict['sup_on'] = rst[0]
        self.serviceInfoDict['sup_off'] = rst[1]

#-----------------------------------------------------------------------------
    def updateCountResult(self, resultDict):
        for key in self.clusterResultDict.keys():
            if key in resultDict.keys():
                onlineCount = 0
                probDict = resultDict[key]

                for proberKey in probDict.keys():
                    if key in proberKey:
                        rstDict = probDict[proberKey]['result']
                        for k in rstDict.keys():
                            if k == 'ping' and rstDict['ping']: onlineCount += 1
                            if isinstance(rstDict[k], list):
                                state = rstDict[k]
                                if state[0] == 'open': onlineCount += 1
                self.clusterResultDict[key]['online'] = onlineCount

    def getResultDict(self):
        return self.clusterResultDict
    
    def getSericeDict(self):
        return self.serviceInfoDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase(mode):
    
  
# Opening JSON file
    mgr = DataManager(None)
    dirpath = os.path.dirname(__file__)
    f = open(os.path.join(dirpath, 'test.json'))
    data = json.load(f)
    inputDict = data
    #print(inputDict)
    mgr.updateCountResult(inputDict)
    mgr.updateServiceInfo()

    print(mgr.getResultDict())
    print(mgr.getSericeDict())

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(0)
