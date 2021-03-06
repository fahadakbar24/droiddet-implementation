import os
import sys
import shutil
import concurrent.futures
from os.path import isfile, join
from pandas import DataFrame

from androguard.misc import AnalyzeAPK
from androguard.core import androconf
from androguard.decompiler import decompiler
from classifiers.helpers import normalize_dataset, Display

import dbModule

androconf.show_logging = True


class droidDet:
    dataset = {}
    permissions_list = {
        # # ORIGINAL PERMISSIONS : useful
        "perm_write": "android.permission.WRITE_EXTERNAL_STORAGE",
        "perm_send_sms": "android.permission.SEND_SMS",

        # ORIGINAL PERMISSIONS : useless
        # "perm_receive_sms": "android.permission.RECEIVE_SMS",
        # "perm_write_settings": "android.permission.WRITE_SECURE_SETTINGS",
        # "perm_install": "android.permission.INSTALL_PACKAGES",
        # "perm_update_device": "android.permission.UPDATE_DEVICE_STATS",
        # "perm_alarm": "android.permission.SET_ALARM",
        # "perm_write_history": "android.permission.WRITE_HISTORY_BOOKMARKS",
        # "perm_read_history": "android.permission.READ_HISTORY_BOOKMARKS",

        # New Permissions : useful
        "perm_read_phone_stats": "android.permission.READ_PHONE_STATE",

        # "perm_access_clocation": "android.permission.ACCESS_COARSE_LOCATION",
        # "perm_record_audio": "android.permission.RECORD_AUDIO",
        # "perm_camera": "android.permission.CAMERA",
        # "perm_access_flocation": "android.permission.ACCESS_FINE_LOCATION",


        # # New Permissions : LESS useless according to feature importance
        # "perm_read_storage": "android.permission.READ_EXTERNAL_STORAGE",
        # "perm_accounts":  "android.permission.GET_ACCOUNTS",
        # "perm_read_contacts": "android.permission.READ_CONTACTS",
        # "perm_read_sms": "android.permission.READ_SMS",
        # "perm_read_calendar": "android.permission.READ_CALENDAR",
        # "perm_write_contacts": "android.permission.WRITE_CONTACTS",
        # "perm_notification": "android.permission.ACCESS_NOTIFICATION_POLICY",
        # "perm_write_calendar": "android.permission.WRITE_CALENDAR",

        # # New Permissions : MORE useless according to feature importance
        # "perm_write_calls": "android.permission.WRITE_CALL_LOG",
        # "perm_read_calls": "android.permission.READ_CALL_LOG",
        # "perm_sensors": "android.permission.BODY_SENSORS",
    }

    @staticmethod
    def reset_dataset():
        droidDet.dataset = {}
        for perm_title in droidDet.permissions_list.keys():
            droidDet.dataset[perm_title] = []

        droidDet.dataset.update({
            "smali_size": [],
            "perm_rate": [],
            "class": []
        })

    @staticmethod
    def rename_files(path):
        try:
            def is_benign_apk():
                return "VirusShare" not in filename

            no_of_ben_files = 0
            no_of_mal_files = 0
            min_file_size = 1000000  # 1MB
            max_file_count = 1086

            for filename in os.listdir(path):
                file_source = join(path, filename)

                if not isfile(file_source):
                    continue
                elif os.stat(file_source).st_size < min_file_size:
                    os.remove(file_source)
                    continue
                elif ".apk" not in filename:
                    file_dest = join(path, filename + ".apk")
                    os.rename(file_source, file_dest)
                elif "PlayStore" not in filename and is_benign_apk():
                    file_dest = join(path, "PlayStore_" + filename)
                    os.rename(file_source, file_dest)

                if (is_benign_apk() and no_of_ben_files > max_file_count) or (
                        not is_benign_apk() and no_of_mal_files > max_file_count):
                    print("Moving excess file...")
                    file_dest = path + "excess/" + filename
                    shutil.move(file_source, file_dest)
                elif is_benign_apk():
                    no_of_ben_files += 1
                else:
                    no_of_mal_files += 1

            print(f"No. of Benign Files {no_of_ben_files}")
            print(f"No. of Malicious Files {no_of_mal_files}")
        except Exception as ex:
            Display.print_exception(ex)

    @staticmethod
    def print_apk_names(apksList):
        # printing apks list
        for loopCount, apk in enumerate(apksList):
            print(str(loopCount + 1) + ". " + str(apk["apk_name"]))

    @staticmethod
    def getApkList():
        apksList = list(dbModule.getApkListCollection())
        # droidDet.print_apk_names(apksList)

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
    def extract_apk_features(worker_args):
        print("Started Worker: ", worker_args["w_no"])
        totalApks = len(worker_args["apksList"])
        mb_byte_size = 1000000  # 1MB
        droidDet.reset_dataset()

        # getting apk permissions
        for loopCount, apk in enumerate(worker_args["apksList"]):
            try:
                if dbModule.isDataExtracted(apk['file_name']):
                    pass
                    # print("Skipping \"" + apk["apk_name"] + "\" : feature data already collected ...")
                else:
                    print(
                        f"\n(W#: {worker_args['w_no']}--{loopCount + 1}/{totalApks})"
                        f": getting permissions for: {apk['file_name']}"
                    )

                    apkObj, DalvikVMFormObj, dxAnalysisObj = AnalyzeAPK(
                        worker_args["apkDir"] + apk["file_name"],
                        session=None,
                        raw=False
                    )
                    apk["apk_name"] = apkObj.get_app_name()
                    apk["pkg_name"] = apkObj.get_package()
                    apk["permissions"] = apkObj.get_permissions()
                    apk["smali_size"] = sys.getsizeof(apkObj.get_raw()) / mb_byte_size
                    apk["perm_rate"] = len(apk["permissions"]) / apk["smali_size"]
                    apk["broad_recvrs"] = apkObj.get_receivers()
                    # apk["intent-filters"] = apkObj.get_intent_filters()

                    # saving apks permissions
                    droidDet.saveApk(apk)

                droidDet.extractCSVvalues(droidDet.dataset, apk)
            except Exception as ex:
                Display.print_exception(ex)
                # droidDet.remove_corrupted(worker_args["apkDir"], apk['file_name'])

    @staticmethod
    def extract_all_features(apkDir, apksList):
        apksList = normalize_dataset(apksList)
        allowed_workers = 1
        total_apks = len(apksList)
        group_size = total_apks // allowed_workers
        start = 0
        end = group_size

        args_for_worker = list()
        for n in range(allowed_workers):
            args_for_worker.append({
                "w_no": n,
                "apkDir": apkDir,
                "apksList": apksList[start: end],
            })

            start += group_size
            end = total_apks if (n == allowed_workers - 2) else end + group_size

        with concurrent.futures.ThreadPoolExecutor(max_workers=allowed_workers) as executor:
            print(f"starting {allowed_workers} Extraction threads ...")
            executor.map(droidDet.extract_apk_features, args_for_worker)

        droidDet.generateCsvDataset(droidDet.dataset)
        return droidDet.getApkList()

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
        for perm_title, permission in droidDet.permissions_list.items():
            dataset[perm_title].append(
                int(bool(permission in apk["permissions"]))
            )

        dataset["smali_size"].append(apk["smali_size"])
        dataset["perm_rate"].append(apk["perm_rate"])

        dataset["class"].append(apk["category"])

    csvPath = r'./datasets/droid-det.csv'

    @staticmethod
    def generateCsvDataset(dataset):
        df = DataFrame(dataset, columns=dataset.keys())
        df.to_csv(droidDet.csvPath, index=None, header=True)

        print(df)
        return droidDet.csvPath

    @staticmethod
    def improve():
        droidDet.reset_dataset()
        apks_list = droidDet.getApkList()

        for loopCount, apk in enumerate(apks_list):
            try:
                pass
            except Exception as ex:
                Display.print_exception(ex)
