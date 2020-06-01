import os
import sys
import shutil
from pandas import DataFrame

from androguard.misc import AnalyzeAPK
from androguard.core import androconf 
from androguard.decompiler import decompiler
# from rotation_forest import RotationForestClassifier

import dbModule
# from svmModule import svm

androconf.show_logging = True


class Display:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print_exception(ex):
        print(f"{Display.FAIL}An error occurred: {ex} {Display.ENDC}")


class droidDet:
    @staticmethod
    def print_apk_names(apksList):
        # printing apks list
        for loopCount, apk in enumerate(apksList):
            print(str(loopCount + 1) + ". " + str(apk["apk_name"]))

    @staticmethod
    def getApkList():
        apksList = list(dbModule.getApkListCollection())

        droidDet.print_apk_names(apksList)

        return apksList

    @staticmethod
    def updateApkList(dirPath):
        apksList = list(filter(lambda obj: obj.endswith('.apk'), os.listdir(dirPath)))

        # saving apks list
        apksList = droidDet.saveApksList(apksList)

        return apksList

    @staticmethod
    def saveApksList(apksList):
        new_apks = dbModule.createApkListCollection(apksList)
        apksList = dbModule.getApkListCollection()

        droidDet.print_apk_names(new_apks) if new_apks else print("No New apks to add ...")

        return apksList

    @staticmethod
    def remove_corrupted(apk_dir, file_name):
        try:
            print("Removing \"" + file_name + "\" : apk seems corrupted/unable to decode ...")
            dbModule.removeApkDocuments(file_name)
            shutil.move(apk_dir + file_name, apk_dir + '/corrupted/' + file_name)
        except Exception as ex:
            Display.print_exception(ex)

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
            "smali_size": [],
            "perm_rate": [],
            "class": []
        }

        # getting apk permissions
        for loopCount, apk in enumerate(apksList):
            try:
                if dbModule.isDataExtracted(apk['file_name']):
                    print("Skipping \"" + apk["apk_name"] + "\" : feature data already collected ...")
                else:
                    print(
                        "\n({}/{})getting permissions for: {}".format(
                            loopCount+1, totalApks, apk['file_name']
                        )
                    )

                    apkObj, DalvikVMFormObj, dxAnalysisObj = AnalyzeAPK(
                        apkDir + apk["file_name"],
                        session=None,
                        raw=False
                    )
                    apk["apk_name"] = apkObj.get_app_name()
                    apk["pkg_name"] = apkObj.get_package()
                    apk["permissions"] = apkObj.get_permissions()
                    apk["smali_size"] = sys.getsizeof(apkObj.get_raw())
                    apk["broad_recvrs"] = apkObj.get_receivers()
                    # apk["intent-filters"] = apkObj.get_intent_filters()
                    perm_rate = len(apk["permissions"])/apk["smali_size"]
                    apk["perm_rate"] = perm_rate

                    # saving apks permissions
                    droidDet.saveApk(apk)

                droidDet.extractCSVvalues(dataset, apk)
            except Exception as ex:
                Display.print_exception(ex)
                droidDet.remove_corrupted(apkDir, apk['file_name'])

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
        dataset["perm_write"].append(bool("android.permission.WRITE" in apk["permissions"]))
        dataset["perm_update_device"].append(bool("android.permission.UPDATE_DEVICE_STATS" in apk["permissions"]))
        dataset["perm_alarm"].append(bool("android.permission.SET_ALARM" in apk["permissions"]))
        dataset["perm_install"].append(bool("android.permission.INSTALL_PACKAGES" in apk["permissions"]))
        dataset["perm_write_history"].append(bool("android.permission.WRITE_HISTORY_BOOKMARKS" in apk["permissions"]))
        dataset["perm_read_history"].append(bool("android.permission.READ_HISTORY_BOOKMARKS" in apk["permissions"]))
        dataset["perm_write_settings"].append(bool("android.permission.WRITE_SECURE_SETTINGS" in apk["permissions"]))
        dataset["perm_send_sms"].append(bool("android.permission.SEND_SMS" in apk["permissions"]))
        dataset["perm_recieve_sms"].append(bool("android.permission.RECEIVE_SMS" in apk["permissions"]))

        dataset["smali_size"].append(apk["smali_size"])
        dataset["perm_rate"].append(apk["perm_rate"])

        dataset["class"].append(apk["category"])

    csvPath = r'./datasets/droid-det.csv'
    @staticmethod
    def generateCsvDataset(dataset):
        df = DataFrame(dataset, columns = dataset.keys())
        df.to_csv(droidDet.csvPath, index = None, header = True)

        print(df)
        return droidDet.csvPath

    @staticmethod
    def svmClassify(apksList):
        # svm.classify(droidDet.csvFile)
        pass