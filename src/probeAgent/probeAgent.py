#-----------------------------------------------------------------------------
# Name:        probeAgent.py
#
# Purpose:     An agent program collects and schedules several different kinds 
#              of probers based on the customized config profile to check the 
#              entire service availably of a small cluster.
#
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/03/09
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os
import time
import json
from collections import OrderedDict

import probeGlobal as gv
# import own lib
import Log
import nmapUtils
import networkServiceProber
import localServiceProber

import dataManager

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class Prober(object):
    """ The prober is a package object contents a list of probe action (with target 
        config) and provide the api to run them under their add in sequence.
    """
    def __init__(self, id, target='localHost', timeInterval=0.5) -> None:
        """ Init the prober, each prober can only aim to one target (ip/doman/local).
        Args:
            id (_type_): prober's ID
            target (str, optional): ip/doman/or Local. Defaults to 'localHost'.
            timeInterval (int, optional): probe function execute interval. Defaults to 0.5 sec.
        """
        self.probId = id
        self.target = target
        self.functionCount = 0
        self.probActionDict = OrderedDict()
        self.crtResultDict = {'target': self.target}
        self.timeInterval = timeInterval
        self.terminate = False

#-----------------------------------------------------------------------------
    def addProbAction(self, probActionRef):
        """ Add a probAction functino in the prober.    
            Args:
                probActionRef (_type_): function reference.
        """
        self.functionCount += 1
        actId = '-'.join((str(self.probId), str(self.functionCount)))
        self.probActionDict[actId] = probActionRef
        self.crtResultDict[actId] = {
            'time': time.time(),
            'result': {} }

#-----------------------------------------------------------------------------
    def executeProbeAction(self):
        if self.terminate: return 
        for probSet in self.probActionDict.items():
            actId, probAct = probSet
            gv.gDebugPrint('Execute probe action: %s' %str(actId), logType=gv.LOG_INFO)
            self.crtResultDict[actId]['time'] = time.time()
            try:
                rst = probAct(self.target)
                if isinstance(rst, dict): self.crtResultDict[actId]['result'].update(rst)
            except Exception as err:
                Log.exception(err)
                self.crtResultDict[actId]['result'] = None
            if self.timeInterval > 0: time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
    def getResult(self):
        """ Return all the probeAction executed result. Example of result dict:
             { "target": <ip>,
                "<id>-1": {
                    "time": <time>,
                    "result": {
                        "target": <ip/doman>,
                        "<functionName>": [<result>, ]
                    }
                 }, ...}
        """
        return self.crtResultDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ProbeAgent(object):
    """ Agent collects and schedules several different kinds of probers """

    def __init__(self, id, fetchMode=False, timeInterval=5) -> None:
        self.id = id
        self.fetchMode = fetchMode
        self.timeInterval = timeInterval
        gv.iDataMgr = dataManager.DataManager(self, fetchMode=False)
        gv.iDataMgr.start()
        self.proberDict = OrderedDict()
        self.crtResultDict = {'id': self.id}
        self.terminate = False

#-----------------------------------------------------------------------------
    def addProber(self, prober):
        if str(prober.probId) in self.proberDict.keys():
            gv.gDebugPrint("Prober %s was exist, can not add" %str(prober.probId), logType=gv.LOG_WARN)
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
        gv.iDataMgr.archiveResult(self.crtResultDict)

#-----------------------------------------------------------------------------     
    def startRun(self):
        while not self.terminate:
            if not gv.gTestMode:
                self.executeProbers()
            time.sleep(1)
            if gv.iDataMgr:
                if gv.gTestMode:
                    print('load simulation data')
                    testFile = os.path.join(gv.DIR_PATH, 'test.json')
                    with open(testFile, 'r') as f:
                        data = json.load(f)
                        gv.iDataMgr.archiveResult(data)
                else:
                    gv.iDataMgr.archiveResult(self.crtResultDict)
                gv.iDataMgr.reportToHub()
            time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    
    # create the scanner.
    gv.iPortScanner = nmapUtils.nmapScanner()
    gv.iNetProbeDriver = networkServiceProber.networkServiceProber(debugLogger=Log)
    gv.iLocalProbeDriver = localServiceProber.localServiceProber('172.18.178.6', debugLogger=Log)
    agnet = ProbeAgent('172.18.178.6', timeInterval=60)
    
    # add a prober to check the Forni
    prober1 = Prober('FW', target='172.18.178.10')
    prober1.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_11(target):
        portList = [22, 113, 443, 8000, 8008, 8080, 8081]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober1.addProbAction(porbAction_11)
    agnet.addProber(prober1)

    # add a prober to control node2
    prober2 = Prober('CT02', target='10.0.6.4')
    prober2.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_21(target):
        portList = [22, 80, 3306, 5000, 8000]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober2.addProbAction(porbAction_21)
    agnet.addProber(prober2)

    # add a prober to compute node 01
    prober3 = Prober('CP01', target='10.0.6.11')
    prober3.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_31(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober3.addProbAction(porbAction_31)
    agnet.addProber(prober3)

    # add a prober to compute node 02
    prober4 = Prober('CP02', target='10.0.6.12')
    prober4.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_41(target):
        portList = [22]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober4.addProbAction(porbAction_31)
    agnet.addProber(prober4)

    # add a prober to compute node 03
    prober5 = Prober('CP03', target='10.0.6.13')
    prober5.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_51(target):
        portList = [22]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober5.addProbAction(porbAction_51)
    agnet.addProber(prober5)

    # add a prober to compute node 04
    prober6 = Prober('KP00', target='10.0.6.20')
    prober6.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_61(target):
        portList = [22, 5900, 6000, 6001]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober6.addProbAction(porbAction_61)
    agnet.addProber(prober6)

    # add a prober to compute node 04
    prober7 = Prober('KP01', target='10.0.6.21')
    prober7.addProbAction(gv.iNetProbeDriver.checkPing)
    prober7.addProbAction(porbAction_61)
    agnet.addProber(prober7)

    # add a prober to compute node 04
    prober8 = Prober('KP02', target='10.0.6.22')
    prober8.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_81(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober8.addProbAction(porbAction_81)
    agnet.addProber(prober8)

    # add a prober to compute node 04
    prober9 = Prober('CR00', target='10.0.6.23')
    prober9.addProbAction(gv.iNetProbeDriver.checkPing)
    prober9.addProbAction(porbAction_61)
    agnet.addProber(prober9)

    # add a prober to compute node 04
    prober10 = Prober('CR01', target='10.0.6.24')
    prober10.addProbAction(gv.iNetProbeDriver.checkPing)
    prober10.addProbAction(porbAction_61)
    agnet.addProber(prober10)


    # add a prober to compute node 04
    prober11 = Prober('GPU1', target='10.0.6.25')
    prober11.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_111(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober11.addProbAction(porbAction_111)
    agnet.addProber(prober11)

    # add a prober to compute node 04
    prober12 = Prober('GPU2', target='10.0.6.26')
    prober12.addProbAction(gv.iNetProbeDriver.checkPing)
    prober12.addProbAction(porbAction_111)
    agnet.addProber(prober12)

    # add a prober to compute node 04
    prober13 = Prober('GPU3', target='10.0.6.27')
    prober13.addProbAction(gv.iNetProbeDriver.checkPing)
    prober13.addProbAction(porbAction_111)
    agnet.addProber(prober13)

    prober14 = Prober('NTP0', target='0.sg.pool.ntp.org')
    def porbAction_141(target):
        if gv.iNetProbeDriver: return gv.iNetProbeDriver.checkNtpConn(target, pingFlg=False, portFlg=False)
    prober14.addProbAction(porbAction_141)
    agnet.addProber(prober14)

    prober15 = Prober('local', target='Local')
    def porbAction_151(target):
        configDict =  {
                'cpu': {'interval': 0.1, 'percpu': True},
                'ram': 0,
                'user': None,
                'disk': ['C:'],
                'network': {'connCount': 0},
                'process': {'count': 0, 'filter': ['python.exe', 'Fing.exe']},
                'dir': [r'C:\Works\NCL\Project\Openstack_Config\GPU', 'M:'],
            }
        if gv.iLocalProbeDriver: 
            gv.iLocalProbeDriver.updateResUsage(configDict=configDict)
            return gv.iLocalProbeDriver.getLastResult()
    prober15.addProbAction(porbAction_151)
    agnet.addProber(prober15)

    agnet.startRun()
    print('Finish')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
