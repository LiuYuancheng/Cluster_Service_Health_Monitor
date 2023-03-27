#-----------------------------------------------------------------------------
# Name:        commManage.py
#
# Purpose:     Communication manager.
#              
# Author:      Yuancheng Liu 
#
# Version:     v_0.2
# Created:     2023/01/11
# Copyright:   
# License:     
#-----------------------------------------------------------------------------

import probeGlobal as gv
import udpCom
import Log

class commManager(object):

    def __init__(self) -> None:
        self.udpServer = None
        self.udpClient = None
        self.httpClient = None
        