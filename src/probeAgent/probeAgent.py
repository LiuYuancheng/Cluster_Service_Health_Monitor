#-----------------------------------------------------------------------------
# Name:        scheduler.py
#
# Purpose:     This module is a script use python <schedule> module to manage
#              the regular or random tasks (call the different actor modules to
#              simulate a normal user's daily action, generate random network
#              comm traffic or local operation event).
#              <schedule> reference link: https://schedule.readthedocs.io/en/stable/
#
# Author:      Yuancheng Liu
#
# Version:     v_0.2
# Created:     2022/12/09
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import time
from collections import OrderedDict

import probeGlobal as gv
import Log

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


class Prober(object):

    def __init__(self, id, timeInterval=5) -> None:
        self.probId = id
        self.functionCount = 0
        self.probActionDict = OrderedDict()
        self.crtResultDict = {}
        self.timeInterval = timeInterval
        self.terminate = False

    def addProbAction(self, probAction):
        self.functionCount += 1
        actId = '-'.join((self.probId, self.functionCount))
        self.probActionDict[actId] = probAction
        self.crtResultDict[actId] = {
            'time': time.time(),
            'result': None
        }

    def executeProbers(self):
        for probSet in self.probActionDict.items():
            actId, probAct = probSet
            self.crtResultDict[actId]['time'] = time.time()
            probAct.run()
            self.crtResultDict[actId]['result'] = probAct.getResult()

    def startRun(self):
        while not self.terminate:
            Log.gDebugPrint("Run prob functions one by one", gv.LOG_INFO)
            self.executeProbers()
            time.sleep(self.timeInterval)

