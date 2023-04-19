#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        databaseHandler.py
#
# Purpose:     This module will provide several database clients to connect to 
#              different kind of data base to implement query execution, table 
#              create, data insert, update and delete. 
#              
#
# Author:      Yuancheng Liu
#
# Created:     2023/03/19
# Version:     v_0.1
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

# incluxdb Doc: https://influxdb-python.readthedocs.io/en/latest/examples.html
from influxdb import InfluxDBClient

class dbHandler(object):
    def __init__(self, databaseName=None) -> None:
        self.dbConnected = False
        self._testConnect()
        if self.dbConnected: 
            print("Database [%s] handler inited." %str(databaseName))
        else:
            print("Database [%s] handler init fail: DB connection error." %str(databaseName))

    def _testConnect(self):
        if self.getTablsList():
            self.dbConnected = True

    def createTable(self, tableName):
        return None 

    def getTablsList(self):
        return None 

    def dropTable(self, tableName):
        return None 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class InfluxCli(dbHandler):
    """ Client to connect to the influx db and insert data."""

    def __init__(self, ipAddr=None, dbInfo=None) -> None:
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
                + "- Ubuntu:    sudo systemctl start influxdb")
            exit()
        super().__init__(databaseName='InfluxDB1.8.1')
        
    #-----------------------------------------------------------------------------
    def getTablsList(self):
        try:
            if self.dbClient.ping():
                return self.dbClient.get_list_measurements()
            print("InfluxDB server does not response ping() ")
            return None
        except:
            print("InfluxDB server connection error ")
            return None

    #-----------------------------------------------------------------------------
    def dropTable(self, tableName):
        if self.dbConnected:
            self.dbClient.drop_measurement(tableName)
        return self.dbConnected

    #-----------------------------------------------------------------------------
    def insertToFields(self, measurement, fieldDict):
        """ Write the score data to the related gateway table."""
        dataJoson = [
            {   "measurement": str(measurement),
                "tags": { "Name": "time",},
                "fields": fieldDict
            }]
        self.dbClient.write_points(dataJoson)



