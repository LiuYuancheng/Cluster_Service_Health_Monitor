#-----------------------------------------------------------------------------
# Name:        dbBaseHandler.py
#
# Purpose:     This program is used to reset the dataBase and test the querys.
#              
# Author:      Yuancheng Liu 
#
# Version:     v_0.2
# Created:     2023/04/20
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import os
import json
import time
import sqlite3
from random import randint
from datetime import datetime, timedelta
from monitorGlobal import DB_PATH, SQL_PATH, dirpath
from databaseHandler import Sqlite3Cli

connection = Sqlite3Cli(DB_PATH, databaseName = "Raw_DataBase")

def testCase(mode):

    if mode == 0:
        connection.executeScript(SQL_PATH)
    elif mode == 1:
        print("Reset DB and test insert data")
        connection.executeScript(SQL_PATH)
        timelineExampleJson = os.path.join(dirpath, 'timeLineExample.json')
        with open(timelineExampleJson, 'r') as f:
            evtJsonList = json.load(f)
            for item in evtJsonList:
                print("Insert test data.")
                evtTitle = item['evtTitle']
                dayNum = int(item['dayNum'])
                evtType = item['evtType']
                teamName = item['teamName']
                evtState = item['evtState']
                querStr = 'INSERT INTO evtTimeline (evtTitle, dayNum, evtType, teamName, evtState) VALUES (?, ?, ?, ?, ?)'
                paramters = (evtTitle, dayNum, evtType, teamName, evtState)
                connection.executeQuery(querStr, paramList=paramters)
                time.sleep(randint(5, 10))
    else:
        pass
        # Add your test code here and change the mode part to active it.
    connection.close()

if __name__ == '__main__':
    mode = 1
    testCase(mode)
