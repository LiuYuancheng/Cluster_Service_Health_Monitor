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
import dataManager
from probeActions import probeFunc0
import Log

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class Prober(object):

    def __init__(self, id, target='localHost', timeInterval=1) -> None:
        self.probId = id
        self.target = target
        self.functionCount = 0
        self.probActionDict = OrderedDict()
        self.crtResultDict = {}
        self.timeInterval = timeInterval
        self.terminate = False

#-----------------------------------------------------------------------------
    def addProbAction(self, probAction):
        self.functionCount += 1
        actId = '-'.join((str(self.probId), str(self.functionCount)))
        self.probActionDict[actId] = probAction
        self.crtResultDict[actId] = {
            'time': time.time(),
            'result': {}
        }

#-----------------------------------------------------------------------------
    def executeProbeAction(self):
        if self.terminate: return 
        for probSet in self.probActionDict.items():
            actId, probAct = probSet
            self.crtResultDict[actId]['time'] = time.time()
            probAct.run()
            self.crtResultDict[actId]['result'] = probAct.getResult()
            time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
    def getResult(self):
        return self.crtResultDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ProbeAgent(object):

    def __init__(self, id, timeInterval=5) -> None:
        self.id = id
        self.timeInterval = timeInterval
        # start the datamanager to handler the monitor and database 
        gv.iDataMgr = dataManager.DataManager(self)
        gv.iDataMgr.start()
        #gv.gDebugPrint("Scheduler: %s init ready." %str(self.actorName), logType=gv.LOG_INFO)
        self.proberDict = OrderedDict()
        self.crtResultDict = {}
        self.terminate = False

#-----------------------------------------------------------------------------
    def addProber(self, prober):
        if str(prober.probId) in self.proberDict.keys():
            Log.gDebugPrint("Prober %s was exist, can not add" %str(prober.id), gv.LOG_WARN)
        else:
            proberID = str(prober.probId)
            self.proberDict[proberID] = prober
            self.crtResultDict[proberID] = prober.getResult()

#-----------------------------------------------------------------------------
    def executeProbers(self):
        if self.terminate: return 
        for proberSet in self.proberDict.items():
            pId, prober = proberSet
            prober.executeProbeAction()
            self.crtResultDict[pId] = prober.getResult()
            gv.iDataMgr.archiveResult(prober.getResult())

#-----------------------------------------------------------------------------     
    def startRun(self):
        while not self.terminate:
            self.executeProbers()
            time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
def main():
    agnet = ProbeAgent('127.0.0.1')
    prob1 = Prober('1')
    probFunc1 = probeFunc0()
    prob1.addProbAction(probFunc1)
    agnet.addProber(prob1)
    #agnet.executeProbers()
    agnet.startRun()
    print('Finish')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


