#-----------------------------------------------------------------------------
# Name:        AgentRun.py
#
# Purpose:     The executable file.
#              
# Author:      Yuancheng Liu 
#
# Version:     v_0.2
# Created:     2023/01/11
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import probeGlobal as gv
import Log
import nmapUtils
import networkServiceProber
import localServiceProber

import commManager
import dataManager
import probeAgent

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def initGlobalVal():
    gv.iPortScanner = nmapUtils.nmapScanner()
    gv.iNetProbeDriver = networkServiceProber.networkServiceProber(debugLogger=Log)
    gv.iLocalProbeDriver = localServiceProber.localServiceProber('172.18.178.6', debugLogger=Log)

    gv.iCommMgr = commManager.commManager()
    #gv.iCommMgr.initUDPServer(3001)
    #gv.iCommMgr.initUDPClient('127.0.0.1', 3002)
    gv.iCommMgr.start()

#-----------------------------------------------------------------------------
def initProbers(agent):
    gv.gDebugPrint('Start to init the probers', logType=gv.LOG_INFO)
     # add a prober to check the Forni
    prober1 = probeAgent.Prober('FW', target='172.18.178.10')
    prober1.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_11(target):
        portList = [22, 113, 443, 8000, 8008, 8080, 8081]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober1.addProbAction(porbAction_11)
    agent.addProber(prober1)

    # add a prober to control node2
    prober2 = probeAgent.Prober('CT02', target='10.0.6.4')
    prober2.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_21(target):
        portList = [22, 80, 3306, 5000, 8000]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober2.addProbAction(porbAction_21)
    agent.addProber(prober2)

    # add a prober to compute node 01
    prober3 = probeAgent.Prober('CP01', target='10.0.6.11')
    prober3.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_31(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober3.addProbAction(porbAction_31)
    agent.addProber(prober3)

    # add a prober to compute node 02
    prober4 = probeAgent.Prober('CP02', target='10.0.6.12')
    prober4.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_41(target):
        portList = [22]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober4.addProbAction(porbAction_31)
    agent.addProber(prober4)

    # add a prober to compute node 03
    prober5 = probeAgent.Prober('CP03', target='10.0.6.13')
    prober5.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_51(target):
        portList = [22]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober5.addProbAction(porbAction_51)
    agent.addProber(prober5)

    # add a prober to compute node 04
    prober6 = probeAgent.Prober('KP00', target='10.0.6.20')
    prober6.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_61(target):
        portList = [22, 5900, 6000, 6001]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober6.addProbAction(porbAction_61)
    agent.addProber(prober6)

    # add a prober to compute node 04
    prober7 = probeAgent.Prober('KP01', target='10.0.6.21')
    prober7.addProbAction(gv.iNetProbeDriver.checkPing)
    prober7.addProbAction(porbAction_61)
    agent.addProber(prober7)

    # add a prober to compute node 04
    prober8 = probeAgent.Prober('KP02', target='10.0.6.22')
    prober8.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_81(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober8.addProbAction(porbAction_81)
    agent.addProber(prober8)

    # add a prober to compute node 04
    prober9 = probeAgent.Prober('CR00', target='10.0.6.23')
    prober9.addProbAction(gv.iNetProbeDriver.checkPing)
    prober9.addProbAction(porbAction_61)
    agent.addProber(prober9)

    # add a prober to compute node 04
    prober10 = probeAgent.Prober('CR01', target='10.0.6.24')
    prober10.addProbAction(gv.iNetProbeDriver.checkPing)
    prober10.addProbAction(porbAction_61)
    agent.addProber(prober10)


    # add a prober to compute node 04
    prober11 = probeAgent.Prober('GPU1', target='10.0.6.25')
    prober11.addProbAction(gv.iNetProbeDriver.checkPing)
    def porbAction_111(target):
        portList = [22, 5900]
        if gv.iPortScanner: return gv.iPortScanner.scanTcpPorts(target, portList)
    prober11.addProbAction(porbAction_111)
    agent.addProber(prober11)

    # add a prober to compute node 04
    prober12 = probeAgent.Prober('GPU2', target='10.0.6.26')
    prober12.addProbAction(gv.iNetProbeDriver.checkPing)
    prober12.addProbAction(porbAction_111)
    agent.addProber(prober12)

    # add a prober to compute node 04
    prober13 = probeAgent.Prober('GPU3', target='10.0.6.27')
    prober13.addProbAction(gv.iNetProbeDriver.checkPing)
    prober13.addProbAction(porbAction_111)
    agent.addProber(prober13)

    prober14 = probeAgent.Prober('NTP0', target='0.sg.pool.ntp.org')
    def porbAction_141(target):
        if gv.iNetProbeDriver: return gv.iNetProbeDriver.checkNtpConn(target, pingFlg=False, portFlg=False)
    prober14.addProbAction(porbAction_141)
    agent.addProber(prober14)

    prober15 = probeAgent.Prober('local', target='Local')
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
    agent.addProber(prober15)

#-----------------------------------------------------------------------------
def main():
    initGlobalVal()
    agent = probeAgent.ProbeAgent('172.18.178.6', timeInterval=60)
    initProbers(agent)
    print("startRun")
    agent.startRun()
    print('Finish')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
