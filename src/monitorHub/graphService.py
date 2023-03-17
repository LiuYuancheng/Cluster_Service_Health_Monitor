#-----------------------------------------------------------------------------
# Name:        probGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2023/03/15
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

from flask import Flask, jsonify
import monitorGlobal as gv
import dataManager

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class topologyGraph(object):

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
        self.edges_fields = [ {"field_name": "id", "type": "string"},
                    {"field_name": "source", "type": "string"},
                    {"field_name": "target", "type": "string"},
                    #{"field_name": "mainStat", "type": "number"},
                    ]

#-----------------------------------------------------------------------------
    def addOneNode(self, ipAddr, role, online, total):
        self.nodeCount += 1
        idStr = str(self.nodeCount)
        onlinePct = round(float(online)/total, 3)
        offlinePct = round(float(total-online)/total, 3)
        nodeInfo = { "id": idStr, 
                    "title": ipAddr, 
                    "subTitle": str(online)+' / ' +str(total), 
                    "detail__role": role,
                    "mainStat": str(onlinePct*100)+'%',
                    "secondaryStat": str(offlinePct*100)+'%',
                    "arc__passed": onlinePct, 
                    "arc__failed": offlinePct, 
                    }
        self.nodes.append(nodeInfo)
        return idStr
    

#-----------------------------------------------------------------------------
    def updateNodeInfo(self, id, online, total):
        if id <  self.nodeCount:
            onlinePct = round(float(online)/total, 3)
            offlinePct = round(float(total-online)/total, 3)
            self.nodes[int(id)]['subTitle'] =  str(online)+' / ' +str(total)
            self.nodes[int(id)]['mainStat'] = str(onlinePct*100)+'%'
            self.nodes[int(id)]['secondaryStat'] = str(offlinePct*100)+'%'
            self.nodes[int(id)]['arc__passed'] = onlinePct
            self.nodes[int(id)]['arc__failed'] = offlinePct

#-----------------------------------------------------------------------------
    def addOneEdge(self, srcID, tgtID, Info=None):
        self.edgeCount += 1
        edgeInfo = {"id": str(self.edgeCount), "source": str(srcID), "target": str(tgtID)}
        self.edges.append(edgeInfo)

    def getNodes(self):
        return self.nodes
    
    def getEdges(self):
        return self.edges
    
    def getNodeFields(self):
        return self.nodes_fields
    
    def getEdgeFields(self):
        return self.edges_fields

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def buildGraph():
    n1 = graph.addOneNode('172.25.123.220', 'dashboard', 2, 2)
    n2 = graph.addOneNode('172.18.172.6 [JP]', 'jumphost', 4, 4)
    n3 = graph.addOneNode('172.18.172.10 [FW]', 'firewall', 5, 6)
    graph.addOneEdge(n1, n2)
    graph.addOneEdge(n1, n3)
    n4 = graph.addOneNode('0.sg.pool.ntp.org [NTP]', 'NTP', 1, 2)
    graph.addOneEdge(n3, n4)
    n5 = graph.addOneNode('10.0.6.4 [CT02]', 'Openstack_CT', 5, 5)
    graph.addOneEdge(n2, n5)
    graph.addOneEdge(n3, n5)
    n6 = graph.addOneNode('10.0.6.11 [CP01]', 'Openstack_CP', 2, 2)
    graph.addOneEdge(n5, n6)
    n7 = graph.addOneNode('10.0.6.12 [CP02]', 'Openstack_CP', 1, 2)
    graph.addOneEdge(n5, n7)
    n8 = graph.addOneNode('10.0.6.13 [CP03]', 'Openstack_CP', 1, 2)
    graph.addOneEdge(n5, n8)
    n9 = graph.addOneNode('10.0.6.20 [KP00]', 'Kypo_CP', 4, 4)
    graph.addOneEdge(n5, n9)
    n10 = graph.addOneNode('10.0.6.21 [KP01]', 'Kypo_CP', 4, 4)
    graph.addOneEdge(n5, n10)
    n11 = graph.addOneNode('10.0.6.22 [KP02]', 'Kypo_CP', 3, 4)
    graph.addOneEdge(n5, n11)
    # Add the CISS red nodes
    n12 = graph.addOneNode('10.0.6.23 [CTF01]', 'CTF-D_VB', 4, 4)
    graph.addOneEdge(n2, n12)
    n13 = graph.addOneNode('10.0.6.24 [CTF02]', 'CTF-D_VB', 3, 4)
    graph.addOneEdge(n2, n13)
    
    # Add the GPU
    n14 = graph.addOneNode('10.0.6.25 [GPU01]', 'GPU', 1, 2)
    graph.addOneEdge(n2, n14)
    n15 = graph.addOneNode('10.0.6.26 [GPU02]', 'GPU', 2, 2)
    graph.addOneEdge(n2, n15)
    n16 = graph.addOneNode('10.0.6.27 [GPU03]', 'GPU', 2, 2)
    graph.addOneEdge(n2, n16)


app = Flask(__name__)
graph = topologyGraph()
buildGraph()
gv.iDataMgr = dataManager.DataManager(None)
gv.iDataMgr.start()


@app.route('/api/graph/fields')
def fetch_graph_fields():
    result = {"nodes_fields": graph.getNodeFields(),
              "edges_fields": graph.getEdgeFields()}
    return jsonify(result)


@app.route('/api/graph/data')
def fetch_graph_data():

    result = {"nodes": graph.getNodes(), "edges": graph.getEdges()}
    return jsonify(result)

@app.route('/api/health')
def check_health():
    return "API is working well!"

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)

