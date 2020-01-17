import os
import sys
from pandas import DataFrame

from androguard.misc import AnalyzeAPK
from androguard.core import androconf 
from androguard.decompiler import decompiler
# from rotation_forest import RotationForestClassifier

import dbModule
from svmModule import svm

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
    def updateApkList(dirPath, category):
        apksList = list(filter(lambda obj: obj.endswith('.apk'), os.listdir(dirPath)))

        # printing apks list
        for loopCount, apk in enumerate(apksList):
            print(str(loopCount + 1) + ". " + apk)

        # saving apks list
        print("_____Saving Apk List ...")
        apksList = droidDet.saveApksList(apksList, category)

        return apksList

    @staticmethod
    def saveApksList(apksList, category):
        dbModule.createApkListCollection(apksList, category)
        apksList = dbModule.getApkListCollection()

        # printing apks apksList
        for apk in apksList:
            print(str(apk))

        return apksList

    @staticmethod
    def extractFeatureSet(apkDir, apksList):
        totalApks = len(apksList)
        dataset = {
            "perm_write": [],
            "perm_update_device": [],
            "perm_alarm": [],
            "perm_install": [],
            "perm_write_history": [],
            "perm_read_history": [],
            "perm_write_settings": [],
            "perm_send_sms": [],
            "perm_recieve_sms": [],
            "class":[]
        }

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
                
            droidDet.extractCSVvalues(dataset, apk)

        droidDet.generateCsvDataset(dataset)
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

    @staticmethod
    def extractCSVvalues(dataset, apk):
        dataset["perm_write"].append(int("android.permission.WRITE" in apk["permissions"]))
        dataset["perm_update_device"].append(int("android.permission.UPDATE_DEVICE_STATS" in apk["permissions"]))
        dataset["perm_alarm"].append(int("android.permission.SET_ALARM" in apk["permissions"]))
        dataset["perm_install"].append(int("android.permission.INSTALL_PACKAGES" in apk["permissions"]))
        dataset["perm_write_history"].append(int("android.permission.WRITE_HISTORY_BOOKMARKS" in apk["permissions"]))
        dataset["perm_read_history"].append(int("android.permission.READ_HISTORY_BOOKMARKS" in apk["permissions"]))
        dataset["perm_write_settings"].append(int("android.permission.WRITE_SECURE_SETTINGS" in apk["permissions"]))
        dataset["perm_send_sms"].append(int("android.permission.SEND_SMS" in apk["permissions"]))
        dataset["perm_recieve_sms"].append(int("android.permission.RECEIVE_SMS" in apk["permissions"]))
        dataset["class"].append("benign")

    csvPath = r'./examples/dataset/droid-det.csv'
    @staticmethod
    def generateCsvDataset(dataset):
        df = DataFrame(dataset, columns = dataset.keys())
        df.to_csv(droidDet.csvPath, index = None, header = True)

        print(df)
        return droidDet.csvPath

    @staticmethod
    def svmClassify(apksList):
        svm.classify(droidDet.csvFile)