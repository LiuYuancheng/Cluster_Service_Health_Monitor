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

import nmap
import time
import socket

import ntplib
from pythonping import ping
import probeGlobal as gv
import Log

#-----------------------------------------------------------------------------
class probeNetworkDriver(object):

    def __init__(self) -> None:
        self.tcpPortChecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ntpClient = ntplib.NTPClient()
        self.scanner = nmap.PortScanner()

#-----------------------------------------------------------------------------
    def checkPing(self, target, timeout=0.5):
        resultDict = {'target': target, 'result':None}
        try:
            data = ping(target, timeout=timeout, verbose=False)
            if data.rtt_max_ms < timeout*1000:
                resultDict['result'] = [data.rtt_min_ms, data.rtt_avg_ms, data.rtt_max_ms]
        except Exception as err:
            gv.gDebugPrint("Ping target [%s] not pingable" %str(target), gv.LOG_ERR)
            Log.exception(err)
        return resultDict
    
#-----------------------------------------------------------------------------
    def _parseNmapDict(self, nmapDict, protocalType='tcp'):
        resultDict = {}
        if protocalType in nmapDict.keys():
            nmapInfo = nmapDict[protocalType]
            for port, state in nmapInfo.items():
                serviceName = state['name'] if 'name' in state.keys() else 'None'
                isopen = state['state'] == 'open' if 'state' in state.keys() else False
                resultDict[str(port)] = (isopen, serviceName)
        return resultDict

#-----------------------------------------------------------------------------
    def fastScan(self, target):
        resultDict = {'target': target}
        self.scanner.scan(hosts=target, arguments='-F')
        nmapInfo = self.scanner[str(target)]
        resultDict.update(self._parseNmapDict(nmapInfo, 'tcp'))
        return resultDict
        
#-----------------------------------------------------------------------------
    def nmapPorts(self, target, portList):
        resultDict = {'target': target}
        for i in portList:
            resultDict[str(i)] = (False, 'None') 
        argStr = '-p ' + ','.join([str(i) for i in portList])
        self.scanner.scan(hosts=target, arguments=argStr)
        nmapInfo = self.scanner[str(target)]
        resultDict.update(self._parseNmapDict(nmapInfo, 'tcp'))
        return resultDict

#----------------------------------------------------------------------------- 
    def checkTcpPorts(self, target, portList, timeout=0.5):
       
        target = socket.gethostbyname(target) # translate hostname to IPv4 if it is a doman
        resultDict = {'target': target, 'result':False}
        socket.setdefaulttimeout(timeout)
        for port in portList:
            resultDict[str(port)] = False
            try:
                result = self.tcpPortChecker.connect_ex((str(target), int(port)))
                resultDict[str(port)] = result == 0
            except socket.gaierror:
                resultDict['target'] = None
                gv.gDebugPrint("Hostname [%s] Could Not Be Resolved" %str(target), gv.LOG_EXCEPT)
                break
            except socket.error:
                resultDict['target'] = None
                gv.gDebugPrint("\n Hostip [%s] is not reponse" %str(target), gv.LOG_EXCEPT)
                break
            except Exception as err:
                gv.gDebugPrint("Exception happens: %s" %str(err), gv.LOG_EXCEPT)
                continue
        
        return resultDict

#----------------------------------------------------------------------------- 
    def checkNTPService(self, target, pingFlg=False, portFlg=False, ntpPort=123):

        resultDict = {
            'target':target,
            'service': False,
        }

        # Check ping
        if pingFlg:
            resultDict['ping'] = False
            rstPing = self.checkPing(target)
            if rstPing['result']: resultDict['ping'] = True

        # Check port Open
        if portFlg:
            resultDict['port'] = False
            rstPort = self.checkTcpPorts(target, [ntpPort])
            if rstPort['target']: resultDict['port'] = rstPort['result']

        # Fetch data
        try:
            data = self.ntpClient.request(target, version=3)
            resultDict['service'] = data.offset
        except Exception as err: 
            gv.gDebugPrint("Time server [%s] not response" %str(target), gv.LOG_ERR)
            Log.exception(err)

        return resultDict










class probeFunc(object):

    def __init__(self) -> None:
        pass

    def run(self):
        print("this is time: %s" %str(time.time()))

    def getResult(self):
        return {'TimeStr': str(time.time())}
    
#-----------------------------------------------------------------------------
def testCase(mode):

    driver = probeNetworkDriver()
    if mode == 0:
        result = driver.checkPing('172.18.178.6')
    elif mode ==1:
        result = driver.checkTcpPorts('172.18.178.6', [22, 80, 443, 8080], timeout=3)
        # result = driver.checkTcpPorts('sg.pool.ntp.org', [123])
    elif mode ==2:
        result = driver.checkNTPService("www.google.com")
        result = driver.checkNTPService("sg.pool.ntp.org")

    elif mode ==3:
        result1 = driver.nmapPorts('172.18.178.6', [22, 80, 443, 8008])
        print(result1)
        result = driver.nmapPorts('172.18.178.7', [22, 80, 443, 8080])
    elif mode ==4:
        result = driver.fastScan('172.18.178.6')

    print(result)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(4)
