#-----------------------------------------------------------------------------
# Name:        monitorUtils.py
#
# Purpose:     The utility functions used in the monitor hub.
#              
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/04/19
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import os
import time
import cv2
import json
from collections import OrderedDict

import monitorGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camClient(object):
    """ Web video camera to fetch the video frame from a web-cam/live video source
        for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
        for local webcam use cv2.VideoCapture(0)
        reference: https://github.com/NakulLakhotia/Live-Streaming-using-OpenCV-Flask
        Args:
            object (_type_): _description_
    """
    def __init__(self, videoSrc, fps=18) -> None:
        # camera = cv2.VideoCapture('rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream')  
        # # use 0 for web camera
        self.camera = cv2.VideoCapture(videoSrc)
        self.fpsNum = fps
        
    def genFrames(self):
        """ generate frame by frame from camera
            Returns:
                _type_: Use yield to return byte video frame stream. None if video source 
                        is not avaliable.
                Yields:
                    byte: Video bytes wrapped by html iframe to plug in ajax. 
        """
        while True:
            # Capture frame-by-frame
            success, frame = self.camera.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                # concat frame one by one and show result
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            time.sleep(1.0/self.fpsNum)
        # default no video image place holder return None
        return None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class topologyGraph(object):
    """ The topology graph follows the grafana <Node Graph API>, to create the 
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
        """ Add a new node in the graph.
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
            id = int(id)
            onlinePct = round(float(online)/total, 3)
            offlinePct = round(float(total-online)/total, 3)
            self.nodes[id]['subTitle'] = str(online)+' / ' + str(total)
            self.nodes[id]['mainStat'] = str(onlinePct*100)+'%'
            self.nodes[id]['secondaryStat'] = str(offlinePct*100)+'%'
            self.nodes[id]['arc__passed'] = onlinePct
            self.nodes[id]['arc__failed'] = offlinePct
            return True
        else: 
            gv.gDebugPrint("The node [%s] is not exist, can not update" %str(id), logType=gv.LOG_INFO)
            return False

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class newsCarouselMgr(object):
    def __init__(self, newsDir, fileJsonPath) -> None:
        self.newsDir = newsDir
        self.fileJsonPath = fileJsonPath
        self.flaskImgPathList = []

    def getFlaskImgPaths(self):
        if os.path.exists(self.fileJsonPath):
            try:
                with open(self.fileJsonPath, 'r') as f:
                    self.flaskImgPathList = json.load(f)
            except Exception as err:
                gv.gDebugPrint("new carousel config json file open error")
        return [ os.path.join(self.newsDir, 'news', i) for i in self.flaskImgPathList ]
    

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