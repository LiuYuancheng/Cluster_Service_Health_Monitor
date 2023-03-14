#-----------------------------------------------------------------------------
# Name:        localServiceProber.py
#
# Purpose:     This module is a untility module of the lib <python- psutil> to provide
#              some extend function. 
#              psutil doc link: https://psutil.readthedocs.io/en/latest/#system-related-functions
#
# Author:      Yuancheng Liu
#
# Version:     v_0.1.1
# Created:     2023/03/14
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os 
import time
import psutil

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class Prober(object):
    """ A simple object with a private debugPrint function. the probe lib function 
        will be inheritance of it.
    """
    def __init__(self, debugLogger=None) -> None:
        self._debugLogger = debugLogger
        self._logInfo = 0
        self._logWarning = 1
        self._logError = 2
        self._logException =3 

    def _debugPrint(self, msg, prt=True, logType=None):
        if prt: print(msg)
        if not self._debugLogger: return 
        if logType == self._logWarning:
            self._debugLogger.warning(msg)
        elif logType == self._logError:
            self._debugLogger.error(msg)
        elif logType == self._logException:
            self._debugLogger.exception(msg)
        elif logType == self._logInfo:
            self._debugLogger.info(msg)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class localServiceProber(Prober):

    def __init__(self, id, debugLogger=None) -> None:
        """ Init the obj, example: driver = networkServiceProber()"""
        super().__init__(debugLogger=debugLogger)
        self.id = id
        self.resultDict = {}
        self._initResultDict()
        
    
    def _initResultDict(self):
        self.resultDict = { 'target': ':'.join(('local', str(self.id))),
                            'time': time.time()
                           }

#-----------------------------------------------------------------------------
    def resetResult(self):
        for key in self.resultDict.keys():
            if key == 'target' or key == 'time': continue
            self.resultDict[key] = None

#-----------------------------------------------------------------------------
    def getLastResult(self):
        return self.resultDict

#-----------------------------------------------------------------------------
    def getResUsage(self, configDict=None):
        resultDict ={}
        if configDict is None: 
            configDict = {
                'cpu': {'interval': None, 'percpu': False},
                'ram': 0,
                'user': None,
                'disk': [],
                'network': {'connCount': 0}
            }
        # Check CPU:
        if 'cpu' in configDict.keys():
            interval = configDict['cpu']['interval'] if 'interval' in configDict['cpu'].keys() else None
            percpuFlg = configDict['cpu']['percpu'] if 'percpu' in configDict['cpu'].keys() else False
            resultDict['cpu'] = psutil.cpu_percent(interval=interval, percpu=percpuFlg)
        
        # Check Mem usage percent
        if 'ram' in configDict.keys():
            data = psutil.virtual_memory()
            resultDict['ram'] = data.percent

        # Check current user
        if 'user' in configDict.keys():
            resultDict['user'] = [str(user.name) for user in psutil.users()]

        # Check disk
        if 'disk' in configDict.keys():
            resultDict['disk'] = {} 
            for diskTag in configDict['disk']:
                resultDict['disk'][diskTag] = psutil.disk_usage(diskTag).percent
        
        # Check network conntion
        if 'network' in configDict.keys():
            resultDict['network'] = {} 
            resultDict['network']['connCount'] = len(psutil.net_connections())

        return resultDict

#-----------------------------------------------------------------------------
    def getProcessState(self, configDict=None):
        resultDict ={'process':{}}
        if configDict is None: 
            configDict = {
                'process': {
                    'count': 0,
                    'filter': []
                }
            }
        if 'process' in configDict.keys():
            # Check total process 
            if 'count' in configDict['process'].keys():
                resultDict['process']['count'] = len(psutil.pids())
            # Check the filtered process we want to check
            
            if 'filter' in configDict['process'].keys():
                
                filterDict = {}
                for key in configDict['process']['filter']:
                    filterDict[str(key).lower()] = []
            
                for proc in psutil.process_iter(['pid', 'name', 'username']):
                    infoName = proc.info['name']
                    if str(infoName).lower() in filterDict.keys():
                         filterDict[str(infoName).lower()].append(proc.info)
                
                resultDict['process']['filter'] = filterDict

        return resultDict
    
#-----------------------------------------------------------------------------
    def getDirFiles(self, configDict=None):    
        resultDict ={'dir':{}}
        if configDict is None: 
            configDict = {
                'dir': []
            }
        if 'dir' in configDict.keys():
            for dirPath in configDict['dir']:
                dirPath = r'{}'.format(dirPath)
                resultDict['dir'][dirPath] = os.listdir(dirPath)

        return resultDict

#-----------------------------------------------------------------------------
    def updateResUsage(self, configDict=None):
        self.resultDict['time'] = time.time()
        self.resultDict.update(self.getResUsage(configDict=configDict))
        self.resultDict.update(self.getProcessState(configDict=configDict))

#----------------------------------------------------------------------------- 
#-----------------------------------------------------------------------------
def testCase(mode):
    # Init the logger;
    # import os, sys
    # import Log
    # DIR_PATH = dirpath = os.path.dirname(__file__)
    # TOPDIR = 'src'
    # LIBDIR = 'lib'
    # idx = dirpath.find(TOPDIR)
    # gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
    # # Config the lib folder 
    # gLibDir = os.path.join(gTopDir, LIBDIR)
    # if os.path.exists(gLibDir):
    #     sys.path.insert(0, gLibDir)
    # APP_NAME = ('TestCaseLog', 'networkServiceProber')
    # import Log
    # Log.initLogger(gTopDir, 'Logs', APP_NAME[0], APP_NAME[1], historyCnt=100, fPutLogsUnderDate=True)
    driver = localServiceProber('127.0.0.1')
    if mode == 0:
        configDict =  {
                'cpu': {'interval': 0.1, 'percpu': False},
                'ram': 0,
                'user': None,
                'disk': ['C:'],
                'network': {'connCount': 0}
            }
        driver.updateResUsage(configDict=configDict)
        result = driver.getLastResult()
    elif mode == 1:
        configDict =  {
                'process': {'count': 0, 'filter': ['python.exe', 'Fing.exe']},
            }
        result = driver.getProcessState(configDict=configDict)
    elif mode ==2:
        configDict =  {
            'dir': [r'C:\Works\NCL\Project\Openstack_Config\GPU'],
        }
        result = driver.getDirFiles(configDict=configDict)
    print(result)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(2)
