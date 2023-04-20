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
import sqlite3
from datetime import datetime, timedelta
from monitorGlobal import DB_PATH, SQL_PATH, dirpath

connection = sqlite3.connect(DB_PATH)

def resetDB():
    print("Clean and reset all the tables.")
    with open(SQL_PATH) as fh:
        connection.executescript(fh.read())

def testCase(mode):

    if mode == 0:
        resetDB()
    elif mode == 1:
        print("Reset DB and test insert data")
        resetDB()
        cur = connection.cursor()
        timelineExampleJson = os.path.join(dirpath, 'timeLineExample.json')
        with open(timelineExampleJson, 'r') as f:
            evtJsonList = json.load(f)
            for item in evtJsonList:
                evtTitle = item['evtTitle']
                dayNum = int(item['dayNum'])
                evtType = item['evtType']
                teamName = item['teamName']
                evtState = item['evtState']
                cur.execute('INSERT INTO evtTimeline \
                    (evtTitle, dayNum, evtType, teamName, evtState)\
                    VALUES (?, ?, ?, ?, ?)',
                    (evtTitle, dayNum, evtType, teamName, evtState))
    else:
        pass
        # Add your test code here and change the mode part to active it.
    connection.commit()
    connection.close()

if __name__ == '__main__':
    mode = 0
    testCase(mode)
