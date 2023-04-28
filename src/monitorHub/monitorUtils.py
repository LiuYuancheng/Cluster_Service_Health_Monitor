#-----------------------------------------------------------------------------
# Name:        monitorUtils.py
#
# Purpose:     This module will provide the utility functions used in the monitor hub.
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
        
    def getFrames(self):
        """ Get frame one by one from camera based on the fps rate.
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


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
eventJson = {
    "title": {
        "text": {
            "headline": " CIDeX 2022",
            "text": " <b> The inaugural Critical Infrastructure Defence Exercise (CIDeX) 2022 \
                    is the largest OT hands-on-keyboard Critical Infrastructure defence exercise. \
                    It provides a platform for Singapore’s cyber defenders to train together the \
                    defence of Critical Information Infrastructure (CII). </b> <br>\
                    With a better insight into how the CII – comprising IT and OT networks – \
                    can suffer from cyberattacks and their adverse consequences, the blue teams \
                    can distil these lessons and tailor them to augment their respective organisations’ \
                    cyber defence and protection strategies.<br><br>\
                    Relaite link: https://itrust.sutd.edu.sg/cidex-2022/"
        },
        "media": {
            "url": "static/img/news/news_cidex.jpg"
        },

    },
    "events": [
        {
            "start_date": {
                "year":	"2022",
				"month":"11",
                "day": "6"
            },
            "end_date": {
                "year": "2022",
				"month":"11",
                "day": "10"
            },
            "media": {
                "url": "https://www.google.com/maps/place/COM3/@1.2930687,103.7708788,16.5z/data=!4m14!1m7!3m6!1s0x31da1b7c11a9a70d:0x21b81bbe73813191!2sCOM3!8m2!3d1.294872!4d103.7745683!16s%2Fg%2F11rnd20sk8!3m5!1s0x31da1b7c11a9a70d:0x21b81bbe73813191!8m2!3d1.294872!4d103.7745683!16s%2Fg%2F11rnd20sk8"
            },
            "text": {
                "headline": "Cyber Execise Setup",
                "text": "\
                    <h4> Event location: </h4> <br>\
                    <b>NUS School of Computing (COM 3) </b><br>\
                    Address: 11 Research Link, Singapore 119391 <br><br>\
                    Over 50 cyber defenders from 17 organisations representing five critical \
                    sectors — power, water, telecommunication, land transport and maritime — will \
                    form five combined blue teams to monitor and defend the CII systems over two days. \
                    A composite red team will launch a series of live simulated cyber attacks on these \
                    systems over two days, while the five blue teams will work in concert to detect and \
                    respond against the attacks."
            },
            "background": {
				"opacity": "60",
                "url": "static/img/information/venue_bg.png"
            }
        },

        {   "start_date": {
                "year":	"2022",
				"month":"11",
                "day": "12"
            },
            "media": {
                "url": "static/img/information/prerunImg.png"
            },
            "text": {
                "headline": "Execise Pre-Run",
                "text": "\
                    <h4> Familiarisation & Training </h4> <br>\
                    A comprehensive familiarisation and training session will be organised in Oct 2022 to equip the CII blue teams with the capability and confidence to navigate through the CI platform and utilise tools to monitor the platform and respond to cyber attacks. More details will follow."
            },
            "background": {
				"opacity": "60",
                "url": "static/img/information/prerunBg.png"
            }
        },

        {   
            "start_date": {
                "year":	"2022",
				"month":"11",
                "day": "14"
            },
            "media": {
                "url": "static/img/information/day0img.png"
            },
            "text": {
                "headline": "Day0 : Cyber Exercise Start ",
                "text": "A comprehensive 3-day pre-exercise training programme will be conducted in SAF’s Cyber Test and Evaluation Centre (CyTEC), so as to equip the blue teams with the capability and confidence to navigate through the CII platform and utilize appropriate cyber tools to monitor the platform and respond to the cyber attacks."
            },
            "background": {
				"opacity": "60",
                "url": "static/img/information/prerunBg.png"
            }

        },

        {   
            "start_date": {
                "year":	"2022",
				"month":"11",
                "day": "15"
            },
            "media": {
                "url": "static/img/news/new_time.jpg"
            },
            "text": {
                "headline": "Day1 : National agencies defend simulated attack",
                "text": "<b> Attack on water and power plants in cyber drill </b><br><br>\
                    A comprehensive 3-day pre-exercise training programme \
                    CIDeX 2022’s platform has three OT testbeds contributed by iTrust — the Secure Water Treatment (SWaT), Water Distribution (WaDi) and Electric Power and Intelligent Control (EPIC) OT testbeds, integrated with an Enterprise IT network of VMs hosted within NCL."
            },
            "background": {
				"opacity": "60",
                "url": "static/img/news/news_cidex.jpg"
            }
        },

        {   
            "start_date": {
                "year":	"2022",
				"month":"11",
                "day": "16"
            },
            "media": {
                "url": "https://www.youtube.com/watch?v=1ErztYQRJe0"
            },
            "text": {
                "headline": "Day2 : VVIP session",
                "text": "<b> Preventing Power Supply Outages and water cuts</b><br><br>\
                    > Blue Team, comprising participants from the national agencies, played\
                    the role of cyber defenders. The Blue Team defended the digital infrastructure, \
                    which include an enterprise IT network and three OT testbeds – replicating a water \
                    treatment plant, a water distribution plant and a power grid system – against live simulated \
                    cyber-attacks launched by a composite Red Team made up of DIS and CSA personnel.<br><br>\
                    <b>DIS and CSA sign Joint Operations Agreement (JOA)</b><br><br>\
                    > The CSA-DIS JOA establishes a framework for cooperation and collaboration in the areas of \
                    joint operations and capability development that will contribute towards a secure national cyberspace.<br><br>\
                    Relaite link: https://www.comp.nus.edu.sg/news/2022-inaugural-cidex-2022/\
                    "
            }
        },

    ]
}
