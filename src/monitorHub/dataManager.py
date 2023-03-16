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

from influxdb import InfluxDBClient
import threading
import time

import monitorGlobal as gv
from datetime import datetime

import Log
import udpCom
import random 

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
    def writeServiceInfo(self, serviceName, online, offline, total):
        """ Write the gateway data to the related gateway table based on gateway 
            name. 
        """
        dataJoson = [
            {
                "measurement": str(serviceName),
                "tags": {
                    "Name": "time",
                },
                "fields": {
                    "online": round(float(online),1),
                    "offline": round(float(offline),1),
                    "total": round(float(total),1),
                }
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
        self.timeInterval = 5
        self.server = udpCom.udpServer(None, gv.UDP_PORT)
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

    #-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            time.sleep(self.timeInterval)
            print("==========>")
            if self.dbhandler:
                onlineNum = 50+random.randint(10, 30)
                offlineNum = 100 - onlineNum
                self.dbhandler.writeServiceInfo('test0_allService', onlineNum, offlineNum, 100)

    #-----------------------------------------------------------------------------
    def updateCountResult(self, resultDict):
        for key in self.clusterResultDict.keys():
            if key in resultDict.keys():
                onlineCount = 0
                probDict = resultDict[key]
                for proberKey in rstDict.keys():
                    if key in proberKey:
                        rstDict = probDict[proberKey]['result']
                        for k in rstDict.keys():
                            if k == 'ping' and rstDict['ping']: onlineCount += 1
                            if isinstance(rstDict[k], list):
                                [state, serviceType] = rstDict[k]
                                if state == 'open': onlineCount += 1
                self.clusterResultDict[key]['online'] = onlineCount
