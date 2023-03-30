#-----------------------------------------------------------------------------
# Name:        dataManager.py
#
# Purpose:     This module the manager module to process and archive all the 
#              incoming data. 
#              
# Author:      Yuancheng Liu
#
# Version:     v0.1
# Created:     2023/03/15
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import os
import time
import json
from random import randint
import threading
from datetime import datetime
from collections import OrderedDict

from influxdb import InfluxDBClient

import monitorGlobal as gv
import Log
import udpCom

# Define all the module local untility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income message to tuple with 3 element: request key, type and jsonString
        Args: msg (str): example: 'GET;dataType;{"user":"<username>"}'
    """
    req = msg.decode('UTF-8') if not isinstance(msg, str) else msg
    reqKey = reqType = reqJsonStr= None
    try:
        reqKey, reqType, reqJsonStr = req.split(';', 2)
    except Exception as err:
        Log.error('parseIncomeMsg(): The income message format is incorrect.')
        Log.exception(err)
    return (reqKey.strip(), reqType.strip(), reqJsonStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class topologyGraph(object):
    """ The topology graph follow the grafana <Node Graph API>, to create the 
        health state network map. 
        Doc link: https://grafana.com/grafana/plugins/hamedkarbasi93-nodegraphapi-datasource/
        github link: https://github.com/hoptical/nodegraph-api-plugin
    """
    def __init__(self) -> None:
        self.nodes = []
        self.edges = []
        self.nodeCount = 0
        self.edgeCount = 0
        self.nodes_fields = [{"field_name": "id", "type": "string"},
                    {"field_name": "title", "type": "string", "displayName": "ipAddr"},
                    {"field_name": "subTitle", "type": "string", "displayName": "health"},
                    {"field_name": "mainStat", "type": "string", "color": "green", "displayName": "onlineNum"},
                    {"field_name": "secondaryStat", "type": "string", "color": "red", "displayName": "offlineNum"},
                    {"field_name": "arc__failed", "type": "number", "color": "red", "displayName": "offline%"},
                    {"field_name": "arc__passed", "type": "number", "color": "green", "displayName": "online%"},
                    {"field_name": "detail__role","type": "string", "displayName": "NodeType"}]
        self.edges_fields = [{"field_name": "id", "type": "string"},
                    {"field_name": "source", "type": "string"},
                    {"field_name": "target", "type": "string"}] #,{"field_name": "mainStat", "type": "number"},
                    
#-----------------------------------------------------------------------------
    def addOneNode(self, ipAddr, role, online, total):
        """ Add a new node in the graph
            Args:
                ipAddr (str): _description_
                role (str): _description_
                online (int): the number of online service.
                total (int): total service.
            Returns: str: the new ID.
        """
        idStr = str(self.nodeCount)
        onlinePct = round(float(online)/total, 3)
        offlinePct = round(float(total-online)/total, 3)
        nodeInfo = {"id": idStr,
                    "title": ipAddr,
                    "subTitle": str(online)+' / ' + str(total),
                    "detail__role": role,
                    "mainStat": str(onlinePct*100)+'%',
                    "secondaryStat": str(offlinePct*100)+'%',
                    "arc__passed": onlinePct,
                    "arc__failed": offlinePct}
        self.nodes.append(nodeInfo)
        self.nodeCount += 1
        return idStr
    
#-----------------------------------------------------------------------------
    def addOneEdge(self, srcID, tgtID, Info=None):
        self.edgeCount += 1
        edgeInfo = {"id": str(self.edgeCount), "source": str(srcID), "target": str(tgtID)}
        self.edges.append(edgeInfo)

#-----------------------------------------------------------------------------
    def getNodes(self):
        return self.nodes
    
    def getEdges(self):
        return self.edges
    
    def getNodeFields(self):
        return self.nodes_fields
    
    def getEdgeFields(self):
        return self.edges_fields

#-----------------------------------------------------------------------------
    def updateNodeInfo(self, id, online, total):
        if 0 < id <  self.nodeCount:
            onlinePct = round(float(online)/total, 3)
            offlinePct = round(float(total-online)/total, 3)
            self.nodes[int(id)]['subTitle'] = str(online)+' / ' + str(total)
            self.nodes[int(id)]['mainStat'] = str(onlinePct*100)+'%'
            self.nodes[int(id)]['secondaryStat'] = str(offlinePct*100)+'%'
            self.nodes[int(id)]['arc__passed'] = onlinePct
            self.nodes[int(id)]['arc__failed'] = offlinePct
            return True
        else: 
            gv.gDebugPrint("The node [%s] is not exist, can not update" %str(id), logType=gv.LOG_INFO)
            return False

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class clusterGraph(topologyGraph):

    def __init__(self) -> None:
        super().__init__()
        self._idMapDict = {} # A map dict used map data manager's targets service count dict to the ids
        self._buildStateGraph()

#-----------------------------------------------------------------------------
    def _buildStateGraph(self):
        n1 = self.addOneNode('172.25.123.220', 'dashboard', 2, 2)
        n2 = self.addOneNode('172.18.172.6 [JP]', 'jumphost', 4, 4)
        n3 = self.addOneNode('172.18.172.10 [FW]', 'firewall', 5, 6)
        self._idMapDict['FW'] = int(n3)
        self.addOneEdge(n1, n2)
        self.addOneEdge(n1, n3)
        n4 = self.addOneNode('0.sg.pool.ntp.org [NTP]', 'NTP', 1, 2)
        self._idMapDict['SUP'] = int(n4)
        self.addOneEdge(n3, n4)
        n5 = self.addOneNode('10.0.6.4 [CT02]', 'Openstack_CT', 5, 5)
        self._idMapDict['CT02'] = int(n5)
        self.addOneEdge(n2, n5)
        self.addOneEdge(n3, n5)
        n6 = self.addOneNode('10.0.6.11 [CP01]', 'Openstack_CP', 2, 2)
        self._idMapDict['CP01'] = int(n6)
        self.addOneEdge(n5, n6)
        n7 = self.addOneNode('10.0.6.12 [CP02]', 'Openstack_CP', 1, 2)
        self._idMapDict['CP02'] = int(n7)
        self.addOneEdge(n5, n7)
        n8 = self.addOneNode('10.0.6.13 [CP03]', 'Openstack_CP', 1, 2)
        self._idMapDict['CP03'] = int(n8)
        self.addOneEdge(n5, n8)
        n9 = self.addOneNode('10.0.6.20 [KP00]', 'Kypo_CP', 4, 4)
        self._idMapDict['KP00'] = int(n9)
        self.addOneEdge(n5, n9)
        n10 = self.addOneNode('10.0.6.21 [KP01]', 'Kypo_CP', 4, 4)
        self._idMapDict['KP01'] = int(n10)
        self.addOneEdge(n5, n10)
        n11 = self.addOneNode('10.0.6.22 [KP02]', 'Kypo_CP', 3, 4)
        self._idMapDict['KP02'] = int(n11)
        self.addOneEdge(n5, n11)
        # Add the CISS red nodes
        n12 = self.addOneNode('10.0.6.23 [CTF01]', 'CTF-D_VB', 4, 4)
        self._idMapDict['CR00'] = int(n12)
        self.addOneEdge(n2, n12)
        n13 = self.addOneNode('10.0.6.24 [CTF02]', 'CTF-D_VB', 3, 4)
        self._idMapDict['CR01'] = int(n13)
        self.addOneEdge(n2, n13)
        # Add the GPU
        n14 = self.addOneNode('10.0.6.25 [GPU01]', 'GPU', 1, 2)
        self._idMapDict['GPU1'] = int(n14)
        self.addOneEdge(n2, n14)
        n15 = self.addOneNode('10.0.6.26 [GPU02]', 'GPU', 2, 2)
        self._idMapDict['GPU2'] = int(n15)
        self.addOneEdge(n2, n15)
        n16 = self.addOneNode('10.0.6.27 [GPU03]', 'GPU', 2, 2)
        self._idMapDict['GPU3'] = int(n16)
        self.addOneEdge(n2, n16)

#-----------------------------------------------------------------------------
    def updateNodesState(self, serveiceCountDict):
        for key in serveiceCountDict.keys():
            if key in self._idMapDict.keys():
                nodeId = self._idMapDict[key]
                online = serveiceCountDict[key]['online']
                total = serveiceCountDict[key]['total']
                self.updateNodeInfo(nodeId, online, total)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class heatMapManager(object):

    def __init__(self, columNum=10) -> None:
        self.colNum = columNum
        self.stateGroups = OrderedDict()

    def getColNum(self):
        return self.colNum
    
#-----------------------------------------------------------------------------
    def addGroup(self, groupName, groupTagList):
        stateDict = {}
        for tag in groupTagList:
            stateDict[tag] = [0]*self.colNum
        self.stateGroups[groupName] = stateDict

#-----------------------------------------------------------------------------
    def updateGroupState(self, groupName, stateDict):
        if groupName in self.stateGroups.keys():
            for key in stateDict.keys():
                if len(stateDict[key]) < self.colNum:
                    stateDict[key] = stateDict[key] + [0]*(self.colNum - len(stateDict[key]))
                self.stateGroups[groupName].update(stateDict)
        else:
            gv.gDebugPrint("The group [%s] is not added in the group dict" %str(groupName), logType=gv.LOG_WARN)

#-----------------------------------------------------------------------------
    def getHeatMapJson(self):
        heatMapJson = {
            'colNum': self.colNum,
            'detail':[]
        }
        for key, val in self.stateGroups.items():
            groupState = {'GroupName': key}
            groupState.update(val)
            heatMapJson['detail'].append(groupState)
        return heatMapJson

#-----------------------------------------------------------------------------
    def getDetailCounts(self):
        resultJson = {}
        for key, val in self.stateGroups.items():
            onlineCount = 0
            warningCount = 0
            offlineCount = 0
            for states in val.values():
                onlineCount += states.count(1)
                warningCount += states.count(2)
                offlineCount += states.count(3)
            resultJson[key] = [onlineCount, warningCount, offlineCount]
        return resultJson
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class InfluxCli(object):
    """ Client to connect to the influx db and insert data."""
    def __init__(self, ipAddr=None, dbInfo=None):
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
            gv.gDebugPrint("Can not connect to the data base, please check whether the influxDB service is running. \n" 
                + "- Windows:   go to D:\\Tools\\InfluxDB\\influxdb-1.8.1-1 and run influxd.exe \n"
                + "- Ubuntu:    sudo systemctl start influxdb", logType=gv.LOG_ERR )
            exit()
        # state the UDP server:
        gv.gDebugPrint("InfluxDB client inited", logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def writeServiceInfo(self, serviceName, fieldDict):
        """ Write the score data to the related gateway table."""
        dataJoson = [
            {   "measurement": str(serviceName),
                "tags": { "Name": "time",},
                "fields": fieldDict
            }]
        self.dbClient.write_points(dataJoson)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class scoreCalculator(object):
    """ A Customized score calculator. """
    def __init__(self) -> None:
        # service percentage result dictionary
        self.serviceInfoDict = {
            'total_num': 0.0,
            'firewall_on': 0.0,
            'firewall_off': 100.0,
            'openstack_on': 0.0,
            'openstack_off': 100.0,
            'kypo_on': 0.0,
            'kypo_off': 100.0,
            'ctf_on': 0.0,
            'ctf_off': 100.0,
            'gpu_on': 0.0,
            'gpu_off': 100.0,
            'sup_on': 0.0,
            'sup_off': 100.0
        }
        # cluster service online count 
        self.serveiceCountDict = {
            'FW':   { "online": 0,"total": 8},
            'CT02': { "online": 0,"total": 6},
            'CP01': { "online": 0,"total": 3},
            'CP02': { "online": 0,"total": 3},
            'CP03': { "online": 0,"total": 3},
            'KP00': { "online": 0,"total": 5},
            'KP01': { "online": 0,"total": 5},
            'KP02': { "online": 0,"total": 5},
            'CR00': { "online": 0,"total": 5},
            'CR01': { "online": 0,"total": 5},
            'GPU1': { "online": 0,"total": 3},
            'GPU2': { "online": 0,"total": 3},
            'GPU3': { "online": 0,"total": 3},
            'SUP':  { "online": 0,"total": 3},
        }

#-----------------------------------------------------------------------------
    def _getStatePct(self, countList):
        online, total = countList[0], countList[1]
        onPct = round(float(online)*100/total,1)
        offPct = round(100.0 - onPct, 1)
        return (onPct, offPct)

    def getSericeCounts(self):
        return self.serveiceCountDict
    
    def getSericeInfo(self):
        return self.serviceInfoDict

    def getScoreInfo(self, key):
        ScoreDict ={
            'online': round(self.serviceInfoDict['total_num']/60, 1),
            'offline': 0.0,
            'total': 0.0
        }
        return ScoreDict

#-----------------------------------------------------------------------------
    def updateSericeCount(self, rawDataDict):
        """ Update the internal data count based on the raw data dict.
            Args:
                rawDataDict (_type_): _description_
        """
        for key in self.serveiceCountDict.keys():
            if key in rawDataDict.keys():
                onlineCount = 0
                probDict = rawDataDict[key]
                for proberKey in probDict.keys():
                    if key in proberKey:
                        rstDict = probDict[proberKey]['result']
                        for k in rstDict.keys():
                            if k == 'ping' and rstDict['ping']: onlineCount += 1
                            if isinstance(rstDict[k], list):
                                state = rstDict[k]
                                if state[0] == 'open': onlineCount += 1
                self.serveiceCountDict[key]['online'] = onlineCount

#-----------------------------------------------------------------------------
    def updateServiceInfo(self):
        totalcount = [0, 0]
        fwCounts = [0, 0]
        opCounts = [0, 0]
        kpCounts = [0, 0]
        ctfCounts = [0, 0]
        gpuCounts = [0, 0]
        supCounts = [0, 0]

        for item in self.serveiceCountDict.items():
            key, val = item
            totalcount[0] += val['online']
            totalcount[1] += val['total']

            if 'FW' in key:
                fwCounts[0] += val['online']
                fwCounts[1] += val['total']

            if 'CT' in key or 'CP' in key:
                opCounts[0] += val['online']
                opCounts[1] += val['total']

            if 'KP' in key:
                kpCounts[0] += val['online']
                kpCounts[1] += val['total']

            if 'CR' in key:
                ctfCounts[0] += val['online']
                ctfCounts[1] += val['total']

            if 'GPU' in key:
                gpuCounts[0] += val['online']
                gpuCounts[1] += val['total']

            if 'SUP' in key:
                supCounts[0] += val['online']
                supCounts[1] += val['total']

        # calculate the percentage;
        self.serviceInfoDict['total_num'] =  round(float(totalcount[0]), 1)

        rst = self._getStatePct(fwCounts)
        self.serviceInfoDict['firewall_on'] = rst[0]
        self.serviceInfoDict['firewall_off'] = rst[1]

        rst = self._getStatePct(opCounts)
        self.serviceInfoDict['openstack_on'] = rst[0]
        self.serviceInfoDict['openstack_off'] = rst[1]

        rst = self._getStatePct(kpCounts)
        self.serviceInfoDict['kypo_on'] = rst[0]
        self.serviceInfoDict['kypo_off'] = rst[1]

        rst = self._getStatePct(ctfCounts)
        self.serviceInfoDict['ctf_on'] = rst[0]
        self.serviceInfoDict['ctf_off'] = rst[1]

        rst = self._getStatePct(gpuCounts)
        self.serviceInfoDict['gpu_on'] = rst[0]
        self.serviceInfoDict['gpu_off'] = rst[1]

        rst = self._getStatePct(supCounts)
        self.serviceInfoDict['sup_on'] = rst[0]
        self.serviceInfoDict['sup_off'] = rst[1]

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ The data manager is a module running parallel with the main thread to 
        handle the data-IO with dataBase and the monitor hub's data fetching/
        changing request.
    """
    def __init__(self, parent, fetchMode=True) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        self.fetchMode = fetchMode
        self.connectorsDict = dict() if self.fetchMode else None
        self.rawDataDict = dict()   # The dictionary used to save the raw data.
        # set the score database client
        self.dbhandler = InfluxCli(ipAddr=('localhost', 8086), dbInfo=('root', 'root', gv.gDataTale))

        self.timeInterval = 30
        # the percentage will be shown on dashboard.
        self.scoreCal = scoreCalculator()
        
        # create the heatmap manager
        self.heatMapMgr = heatMapManager(columNum=25)
        self.terminate = False

    def setFetchInterval(self, timeInterval):
        self.timeInterval = timeInterval

#-----------------------------------------------------------------------------
    def addStateGroups(self):
        groupTags = ['Group1', 'Group2', 'Group3', 'Group4', 'Group5']
        serviceTags = ['DMZ-Service', 'Intranet-Service', 'IT-SOC-Tools', 'BUS-Clients', 'IT-SOC-Clients' ]
        for tag in groupTags:
            self.heatMapMgr.addGroup(tag, serviceTags)

    def getHeatMapJson(self, testMode=True):            
        return self.heatMapMgr.getHeatMapJson() if self.heatMapMgr else {}

    def createRandomHeatMapData(self):
        groupTags = ['Group1', 'Group2', 'Group3', 'Group4', 'Group5']
        serviceTags = ['DMZ-Service', 'Intranet-Service', 'IT-SOC-Tools', 'BUS-Clients', 'IT-SOC-Clients' ]
        maxColNum = self.heatMapMgr.getColNum()
        for tag in groupTags:
            randStateDict = {}
            for serviceT in serviceTags:
                randStateDict[serviceT] = [max(1, randint(0,3)) for _ in range(randint(5, maxColNum))]
            self.heatMapMgr.updateGroupState(tag, randStateDict)

#-----------------------------------------------------------------------------
    def addTargetConnector(self, ipaddress, port):
        if ipaddress in self.rawDataDict.keys():
            gv.gDebugPrint('The target [%s] is exist' % str(ipaddress))
        else:
            if self.fetchMode:
                self.connectorsDict[str(ipaddress)] = udpCom.udpClient((ipaddress, port))
            self.rawDataDict[str(ipaddress)] = {}

#-----------------------------------------------------------------------------
    def fetchData(self, cmd=None):
        """ fetch data from the agents if under fetch mode."""
        if self.fetchMode:
            for ipaddr in self.connectorsDict.keys():
                gv.gDebugPrint('Fetch data from agent[%s]...' %str(ipaddr), logType=gv.LOG_INFO)
                if not cmd or not isinstance(cmd, str): cmd = 'GET;data;fetch' 
                resp = self.connectorsDict[ipaddr].sendMsg(cmd, resp=True)
                if resp is None:
                    gv.gDebugPrint('Agent [%s] is not responsed.' %str(ipaddr), logType=gv.LOG_WARN)
                else:
                    _, _, data = parseIncomeMsg(resp)
                    inputDict = json.loads(data)
                    self.updateRawData(ipaddr, inputDict)
                    #self.rawDataDict[ipaddr] = inputDict
                    self.scoreCal.updateSericeCount(inputDict)
        else:
            gv.gDebugPrint('Fetch mode is disabled.', logType=gv.LOG_WARN)

#-----------------------------------------------------------------------------
    def updateRawData(self, ipaddr, dataDict):
        if ipaddr in self.rawDataDict.keys():
            gv.gDebugPrint('Add raw data')
            self.rawDataDict[ipaddr] = dataDict
            self.scoreCal.updateSericeCount(dataDict)
        else:
            gv.gDebugPrint('The agent [%s] is not registered, please add the agent first.' %str(ipaddr), logType=gv.LOG_WARN)

#-----------------------------------------------------------------------------

    def _convertToInfluxField(self, countsJson):
        countField = {}
        for key in countsJson.keys():
            data = countsJson[key]
            countField[key+'_ok'] = float(data[0])
            countField[key+'_warn'] = float(data[1])
            countField[key+'_critical'] = float(data[2])
        return countField


#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            # fetch data from the agents
            if self.fetchMode and self.scoreCal: self.fetchData(cmd='GET;data;fetch')
            if self.dbhandler:
                self.scoreCal.updateServiceInfo()
                print("Update the database")
                try:
                    self.dbhandler.writeServiceInfo(gv.gMeasurement, self.scoreCal.getSericeInfo())
                    time.sleep(0.1)     
                    self.dbhandler.writeServiceInfo('test0_allService', self.scoreCal.getScoreInfo(None))
                except Exception as err:
                    gv.gDebugPrint("Error when update the dataBase: %s" %str(err), logType=gv.LOG_EXCEPT)
                    self.dbhandler = None
                if gv.iClusterGraph:
                    gv.iClusterGraph.updateNodesState(self.scoreCal.getSericeCounts())
            if self.heatMapMgr:
                self.createRandomHeatMapData()
                fielddata = self._convertToInfluxField(self.heatMapMgr.getDetailCounts())
                self.dbhandler.writeServiceInfo('test0_allCounts', fielddata)
            time.sleep(self.timeInterval)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase(mode):

# Opening JSON file
    mgr = DataManager(None)
    dirpath = os.path.dirname(__file__)
    f = open(os.path.join(dirpath, 'test.json'))
    data = json.load(f)
    inputDict = data
    #print(inputDict)
    mgr.updateCountResult(inputDict)
    mgr.updateServiceInfo()

    print(mgr.getResultDict())
    print(mgr.getSericeDict())

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(0)
