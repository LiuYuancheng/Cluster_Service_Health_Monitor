

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

    #-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            time.sleep(self.timeInterval)
            print("==========>")
            if self.dbhandler:
                onlineNum = 50+random.randint(10, 30)
                offlineNum = 100 - onlineNum
                self.dbhandler.writeServiceInfo('test0_allService', onlineNum, offlineNum, 100  )

