#-----------------------------------------------------------------------------
# Name:        monitorApp.py
#
# Purpose:     The main monitor application to start other module, insert data 
#              to the score database and update the topology panel in Grafana. 
#              
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/03/15
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import os

from flask import Flask, render_template, jsonify
import monitorGlobal as gv
import dataManager

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

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
app = Flask(__name__)
PEOPLE_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

gv.iDataMgr = dataManager.DataManager(None, fetchMode=True)
graph = dataManager.topologyGraph()
buildGraph()
#targetInfo = ('172.18.178.6', gv.UDP_PORT)
targetInfo = ('127.0.0.1', gv.UDP_PORT)
gv.iDataMgr.addTargetConnector(targetInfo[0], targetInfo[1])
gv.iDataMgr.start()

#-----------------------------------------------------------------------------
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
@app.route('/logo')
def show_logo():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'ncl_logo.png')
    return render_template("logo.html", user_image = full_filename)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)

