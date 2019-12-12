import pymongo

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mongoDb = mongoClient["droidDet"]
apksListCollection = mongoDb["apkList"]

# mongoDocument = {
#     "app_name": "",
#     "file": "",
#     "perm_recieve_boot_completed": False,
#     "perm_internet": False,
#     "perm_read_external_storage": False,
#     "perm_write_external_storage": False,
# }

def printException(ex):
    print("An error occurred: " +str(ex))

def apkExists(apkName):
    findQuery = {"apk_name": apkName}
    return True if(apksListCollection.find_one(findQuery)) else False

def isDataExtracted(apkName):
    findQuery = {"apk_name": apkName}
    apk = apksListCollection.find_one(findQuery)
    check_key = "permissions"

    print(apk)
    return True if(apk and check_key in apk.keys()) else False

def createApkListCollection(apksList):
    apksListItems = []
    try:
        for apkName in apksList:
            if(not apkExists(apkName)):
                apksListItems.append({"apk_name": apkName})

        apksListCollection.insert_many(apksListItems)
    except Exception as ex:
        printException(ex)
    finally:
        return apksListItems

def getApkListCollection():
    apksList = None
    try:
        apksList = list(apksListCollection.find())
    except Exception as ex:
        printException(ex)
    finally:
        return apksList

def saveApkDocument(apkDoc):
    try:
        apksListCollection.save(apkDoc)
    except Exception as ex:
        printException(ex)
    finally:
        return apkDoc

def removeApkDocuments():
    try:
        apksListCollection.remove({})
    except Exception as ex:
        printException(ex)