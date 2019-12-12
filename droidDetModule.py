import os
import sys
from androguard.misc import AnalyzeAPK
from androguard.core import androconf 
from androguard.decompiler import decompiler

import dbModule

androconf.show_logging = True

class droidDet:
    @staticmethod
    def getApkList():
        apksList = list(dbModule.getApkListCollection())
    
        # printing apks list
        for apk in apksList:
            print(str(apk))

        return apksList

    @staticmethod
    def updateApkList(dirPath):
        apksList = list(filter(lambda obj: obj.endswith('.apk'), os.listdir(dirPath)))

        # printing apks list
        for loopCount, apk in enumerate(apksList):
            print(str(loopCount + 1) + ". " + apk)

        # saving apks list
        print("_____Saving Apk List ...")
        apksList = droidDet.saveApksList(apksList)

        return apksList

    @staticmethod
    def saveApksList(apksList):
        dbModule.createApkListCollection(apksList)
        apksList = dbModule.getApkListCollection()

        # printing apks apksList
        for apk in apksList:
            print(str(apk))

        return apksList

    @staticmethod
    def extractFeatureSet(apkDir, apksList):
        totalApks = len(apksList)

        # getting apk permissions
        for loopCount, apk in enumerate(apksList):
            if(dbModule.isDataExtracted(apk['apk_name'])):
                print("Skipping \"" + apk["apk_name"] + "\" : feature data already collected ...")
            else:
                print(
                    ("\n({}/{})getting permissions for: {}").format(
                        loopCount+1, totalApks, apk['apk_name']
                    )
                )

                apkObj, DalvikVMFormObj, dxAnalysisObj = AnalyzeAPK(apkDir + apk["apk_name"], session=None, raw=False)
                apk["permissions"] = apkObj.get_permissions()
                apk["smali_size"] = sys.getsizeof(apkObj.get_raw())
                apk["broad_recvrs"] = apkObj.get_receivers()
                # apk["intent-filters"] = apkObj.get_intent_filters()
                perm_rate = len(apk["permissions"])/apk["smali_size"]
                apk["perm_rate"] = perm_rate

                # saving apks permissions
                droidDet.saveApk(apk)

        return apksList

    @staticmethod
    def saveApk(apkDoc):
        apkDoc = dbModule.saveApkDocument(apkDoc)
        print(str(apkDoc))

        return apkDoc

    @staticmethod
    def clearFeatureSet():
        dbModule.removeApkDocuments()
        return []