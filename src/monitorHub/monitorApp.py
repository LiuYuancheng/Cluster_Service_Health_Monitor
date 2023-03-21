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
app = Flask(__name__)
PEOPLE_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

gv.iClusterGraph = dataManager.clusterGraph()
gv.iDataMgr = dataManager.DataManager(None, fetchMode=True)

#targetInfo = ('172.18.178.6', gv.UDP_PORT)
targetInfo = ('127.0.0.1', gv.UDP_PORT)
gv.iDataMgr.addTargetConnector(targetInfo[0], targetInfo[1])
gv.iDataMgr.start()

#-----------------------------------------------------------------------------
@app.route('/api/graph/fields')
def fetch_graph_fields():
    result = {"nodes_fields": gv.iClusterGraph.getNodeFields(),
              "edges_fields": gv.iClusterGraph.getEdgeFields()}
    return jsonify(result)

@app.route('/api/graph/data')
def fetch_graph_data():
    result = {"nodes": gv.iClusterGraph.getNodes(), 
              "edges": gv.iClusterGraph.getEdges()}
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

