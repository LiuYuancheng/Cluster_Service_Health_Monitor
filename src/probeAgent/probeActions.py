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
import socket
import http.client

import ntplib
from pythonping import ping
import probeGlobal as gv

import nmapUtils
import Log

#-----------------------------------------------------------------------------
class probeNetworkDriver(object):

    def __init__(self) -> None:
        self.tcpPortChecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ntpClient = ntplib.NTPClient()
        self.scanner = nmapUtils.nmapScanner()

    def _parseTarget(self, target):
        target = str(target).replace(' ', '')
        return '127.0.0.1' if target.lower() == 'localhost' else target
    
#-----------------------------------------------------------------------------
    def checkPing(self, target, timeout=0.5):
        """ Check the target is pingable (ICMP service avaliable).
            Args:
                target (_type_): _description_
                timeout (float, optional): _description_. Defaults to 0.5.

            Returns:
            _type_: _description_
        """
        target = self._parseTarget(target)
        resultDict = {'target': target, 'ping': None}
        try:
            data = ping(target, timeout=timeout, verbose=False)
            if data.rtt_max_ms < timeout*1000:
                resultDict['ping'] = [data.rtt_min_ms, data.rtt_avg_ms, data.rtt_max_ms]
        except Exception as err:
            gv.gDebugPrint("Ping target [%s] not pingable" %str(target), gv.LOG_ERR)
            Log.exception(err)
        return resultDict

#----------------------------------------------------------------------------- 
    def checkTcpConn(self, target, portList, timeout=0.5):
        """ Check a TCP service ports are connectable.

        Args:
            target (_type_): _description_
            portList (_type_): _description_
            timeout (float, optional): _description_. Defaults to 0.5.

        Returns:
            _type_: _description_
        """
        target = socket.gethostbyname(self._parseTarget(target)) # translate hostname to IPv4 if it is a doman
        resultDict = {'target': target}
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
    def checkNtpConn(self, target, pingFlg=False, portFlg=False, ntpPort=123):
        """ Check whether a NTP(Network Time Protocol) service is avaliable. As we use the nmap
            to scan the port, most of the public ntp server will ban the client who did the ports
            scan for their server, so the port state may show 'down' 

        Args:
            target (_type_): _description_
            pingFlg (bool, optional): _description_. Defaults to False.
            portFlg (bool, optional): _description_. Defaults to False.
            ntpPort (int, optional): _description_. Defaults to 123.

        Returns:
            _type_: _description_
        """
        target = self._parseTarget(target)
        resultDict = {'target': target, 'ping': None, 'ntp': None}
        # Check ping
        if pingFlg:resultDict.update(self.checkPing(target))
        # Check port Open
        if portFlg:
            result = self.scanner.scanTcpPorts(target, [
                                               ntpPort]) if portFlg == 'nmap' else self.checkTcpConn(target, [ntpPort])
            resultDict.update(result)
        # Fetch time offset data
        try:
            data = self.ntpClient.request(target, version=3)
            resultDict['ntp'] = data.offset
        except Exception as err:
            gv.gDebugPrint(
                "Time server [%s] not response" % str(target), gv.LOG_ERR)
            Log.exception(err)
        return resultDict

#----------------------------------------------------------------------------- 
    def checkHttpConn(self, target, requestConfig, timeout=3):
        target = self._parseTarget(target)
        #target = target.replace('http', 'https') if 'http://' in target else 'https://' + target
        resultDict = {  'target': target, 
                        'conn': 'http',
                        'port': 80 }
        if 'conn' in requestConfig.keys(): resultDict['conn'] = str(requestConfig['conn']).lower()
        if 'port' in requestConfig.keys(): resultDict['port'] = requestConfig['port']
        conn = http.client.HTTPSConnection(target, resultDict['port'], timeout) if resultDict['conn'] == 'https' else http.client.HTTPConnection(
            target, resultDict['port'], timeout)
        req = requestConfig['req'] if 'req' in requestConfig.keys() else 'HEAD'
        par = requestConfig['par'] if 'par' in requestConfig.keys() else '/'
        resultDict[':'.join((req, par))] = None
        try:
            conn.request(req, par)
            rst = conn.getresponse()
            resultDict[':'.join((req, par))] = (rst.status, rst.reason)
        except Exception as error:
            gv.gDebugPrint("Error when connect to the target: %s " %str(error), logType=gv.LOG_EXCEPT)
        if conn: conn.close()
        return resultDict
        
#-----------------------------------------------------------------------------
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

    if mode == 1:
        result = driver.checkTcpConn('172.18.178.6', [22, 23])

    elif mode ==2:
        result = driver.checkNtpConn('0.sg.pool.ntp.org', pingFlg=True, portFlg=True)
    
    elif mode ==3:
        testhttpCofig = {
            'target': '127.0.0.1',
            'port': 8080,
            'conn': 'http',
            'req': 'HEAD',
            'par': '/'
            }
        result = driver.checkHttpConn('127.0.0.1',testhttpCofig)
        print(result)
        testhttpCofig = {
            'target': '127.0.0.1',
            'port': 8080,
            'conn': 'http',
            'req': 'GET',
            'par': '/horizon'
            }
        result = driver.checkHttpConn('127.0.0.1',testhttpCofig)
    # elif mode ==1:
    #     result = driver.checkTcpPorts('172.18.178.6', [22, 80, 443, 8080], timeout=3)
    #     # result = driver.checkTcpPorts('sg.pool.ntp.org', [123])
    # elif mode ==2:
    #     result = driver.checkNTPService("www.google.com")
    #     result = driver.checkNTPService("sg.pool.ntp.org")

    # elif mode ==3:
    #     result1 = driver.nmapPorts('172.18.178.6', ['22-23', 80, 443, 8008])
    #     print(result1)
    #     result = driver.nmapPorts('172.18.178.7', [22, 80, 443, 8080])
    # elif mode ==4:
    #     result = driver.fastScan('172.18.178.6')

    print(result)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(3)
