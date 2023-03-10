#-----------------------------------------------------------------------------
# Name:        nmapUtils.py
#
# Purpose:     This module is a extend module of the lib <python-nmap> and the 
#              nmap software. The module need Nmap to be installed:
#              https://nmap.org/download
#
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/03/10
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import nmap

OPEN_TAG = 'open'
CLOSE_TAG = 'closed'
FILTER_TAG = 'filtered'
UNKNOWN_TAG = 'unknown'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class nmapScanner(object):

    def __init__(self) -> None:
        self.scanner = nmap.PortScanner()
        self.resultDict = None

#-----------------------------------------------------------------------------
    def _parseNmapDict(self, nmapDict, protocalType='tcp', showFiltered=False):
        """ Convert the Nmap scan result dict to {'<portnum>':(<state>, serverType), ...}
            format.
            Args:
                nmapDict (dict): nampScanDict[<ip>]
                protocalType (str, optional): protocalType. Defaults to 'tcp'.
                showFiltered (bool, optional): whether show 'filtered' port. Defaults to False.
            Returns:
                _type_: _description_
        """
        resultDict = {}
        if protocalType in nmapDict.keys():
            nmapInfo = nmapDict[protocalType]
            for port, state in nmapInfo.items():
                if state['state'] == FILTER_TAG and not showFiltered: continue
                serviceName = state['name'] if 'name' in state.keys() else UNKNOWN_TAG
                isopen = state['state'] if 'state' in state.keys() else CLOSE_TAG
                resultDict[str(port)] = (isopen, serviceName)
        return resultDict

#-----------------------------------------------------------------------------
    def scanPortDecorator(scanFunction):
        def innerFunc(self, target, portInfo, showFiltered=False):
            self.resultDict = {}
            if str(target).lower() == 'localhost': target = '127.0.0.1' 
            self.resultDict = {'target': target, 'state': 'down'}
            scanFunction(self, target, portInfo, showFiltered=showFiltered)
            if target in self.scanner.all_hosts():
                nmapInfo = self.scanner[str(target)]
                self.resultDict['state'] = nmapInfo.state()
                if self.resultDict['state'] == 'up':
                    self.resultDict.update(self._parseNmapDict(nmapInfo, protocalType='tcp',showFiltered=showFiltered))
            return self.resultDict.copy()
        return innerFunc
    
#-----------------------------------------------------------------------------
    @scanPortDecorator
    def scanTcpPorts(self, target, portList, showFiltered=False):
        """ Check a list TCP port state and service 
            Args:
                target (_type_): target IP address
                portList (_type_): list of int port.
                showFiltered (bool, optional): whether show 'filtered' port. Defaults to False.
            Returns:
                _type_: _description_
        """
        for i in portList:
            self.resultDict[str(i)] = (CLOSE_TAG, UNKNOWN_TAG) 
        argStr = '-p ' + ','.join([str(i) for i in portList])
        self.scanner.scan(hosts=target, arguments=argStr)

    #-----------------------------------------------------------------------------
    def scanTcpPortsOld(self, target, portList, showFiltered=False):
        """ Same as function function scanTcpPorts(), current not used."""
        if str(target).lower() == 'localhost': target = '127.0.0.1' 
        resultDict = {'target': target, 'state': 'down'}
        for i in portList:
            resultDict[str(i)] = (CLOSE_TAG, UNKNOWN_TAG) 
        argStr = '-p ' + ','.join([str(i) for i in portList])
        self.scanner.scan(hosts=target, arguments=argStr)
        if target in self.scanner.all_hosts():
            nmapInfo = self.scanner[str(target)]
            resultDict['state'] = nmapInfo.state()
            if resultDict['state'] == 'up':
                resultDict.update(self._parseNmapDict(nmapInfo, protocalType='tcp',showFiltered=showFiltered))
        return resultDict
    
#-----------------------------------------------------------------------------
    @scanPortDecorator
    def scanPortRange(self, target, portRange, showFiltered=False):
        """_summary_

        Args:
            target (_type_): _description_
            portList (_type_): _description_
            showFiltered (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        argStr = str(portRange[0])+'-'+str(portRange[1])
        self.scanner.scan(target, argStr)


    #-----------------------------------------------------------------------------
    def scanPortRange_old(self, target, portRange, showFiltered=False):
        """ Same as function function scanTcpPorts(), current not used."""
        if str(target).lower() == 'localhost': target = '127.0.0.1' 
        resultDict = {'target': target, 'state': 'down'}
        argStr = str(portRange[0])+'-'+str(portRange[1])
        self.scanner.scan(target, argStr)
        if target in self.scanner.all_hosts():
            nmapInfo = self.scanner[str(target)]
            resultDict['state'] = nmapInfo.state()
            if resultDict['state'] == 'up':
                resultDict.update(self._parseNmapDict(nmapInfo, protocalType='tcp',showFiltered=showFiltered))
        return resultDict
    
#-----------------------------------------------------------------------------
def testCase(mode):

    scanner = nmapScanner()
    if mode == 0:
        print("Test function: scanTcpPorts() ")
        print(' - 1.Scan reachable ip:')
        rst = scanner.scanTcpPorts('172.18.178.6', [22, 443,8008])
        print('\t', rst)
        print(' - 2.Scan reachable ip, show filtered port:')
        rst = scanner.scanTcpPorts('172.18.178.6', [80], showFiltered=True)
        print('\t', rst)
        print(' - 3.Scan un-reachable ip:')
        rst = scanner.scanTcpPorts('172.18.178.11', [80], showFiltered=True)
        print('\t', rst)
    elif mode == 1:
        print(' - 4.Scan localhhost:')
        rst = scanner.scanTcpPorts('localhost', [134, 443, 3000])
        print('\t', rst)
    elif mode == 2:
        print(' - 5.Scan port range 22 - 30')
        rst = scanner.scanPortRange('172.18.178.6', (22,30), showFiltered=True )
        print('\t', rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(2)
