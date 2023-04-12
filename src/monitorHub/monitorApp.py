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
import json

from flask import Flask, request, render_template, jsonify
import monitorGlobal as gv
import dataManager

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
app = Flask(__name__)
PEOPLE_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

gv.iClusterGraph = dataManager.clusterGraph()
gv.iDataMgr = dataManager.DataManager(None, fetchMode=False)

targetInfo = ('172.18.178.6', gv.UDP_PORT)
#targetInfo = ('127.0.0.1', gv.UDP_PORT)
gv.iDataMgr.addTargetConnector(targetInfo[0], targetInfo[1])
gv.iDataMgr.addStateGroups()
gv.iDataMgr.createRandomHeatMapData()
gv.iDataMgr.buildTimeline()
gv.iDataMgr.start()

#-----------------------------------------------------------------------------
# graph request handling
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
# Ajax panel request handling
@app.route('/logo')
def show_logo():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'ncl_logo.png')
    return render_template("logo.html", logo_image = full_filename)

# Ajax panel request handling
@app.route('/heatmap')
def show_heatmap():
    heatmapJson = {
        'colNum': 15,
        'detail': [
            {'GroupName': 'Group1',
                'DMZ-Service': [1, 2, 3, 0, 0]+[0]*10,
                'Intranet-Service': [1, 2, 3, 3, 3]+[0]*10,
                'IT-SOC-Tools': [1, 1, 1, 1, 1]+[0]*10,
                'BUS-Clients': [1, 2, 3, 0, 0]+[0]*10,
                'IT-SOC-Clients': [1, 0, 0, 0, 0]+[0]*10,
             }
        ]
    }
    heatmapJson = gv.iDataMgr.getHeatMapJson()
    return render_template("heatmap.html", posts = heatmapJson)

@app.route('/newspanel')
def show_newspanel():
    picNameList = ['news_cidex.jpg', 'news_network.png', 'new_time.jpg','news_infra.png']
    newPicList = [ os.path.join(app.config['UPLOAD_FOLDER'], i) for i in picNameList ]
    return render_template("newspanel.html", posts = newPicList)

@app.route('/timeline')
def show_timeline():
    timeLineList = gv.iDataMgr.getTimelineJson()
    return render_template("timeline.html", posts = timeLineList)

#-----------------------------------------------------------------------------
# Data post request handling 
@app.route('/dataPost/<string:uuid>', methods=('POST',))
def add_message(uuid):
    content = request.json
    gv.gDebugPrint("Get raw data from %s "%str(uuid), logType=gv.LOG_INFO)
    gv.gDebugPrint("Raw Data: %s" %str(content['rawData']), prt=False, logType=gv.LOG_INFO)
    gv.iDataMgr.updateRawData(uuid, json.loads(content['rawData']))
    return jsonify({"ok":True})

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)

