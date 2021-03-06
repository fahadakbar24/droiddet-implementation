import pymongo

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mongoDb = mongoClient["droidDet"]
apksListCollection = mongoDb["apkList"]


def printException(ex):
    print("An error occurred: ")
    print(ex)


def apkExists(file_name):
    find_query = {"file_name": file_name}
    return True if(apksListCollection.find_one(find_query)) else False


def isDataExtracted(file_name):
    find_query = {"file_name": file_name}
    apk = apksListCollection.find_one(find_query)
    check_key = "permissions"

    return True if(apk and check_key in apk.keys()) else False


def createApkListCollection(apksList):
    apksListItems = []
    # try:
    for fileName in apksList:
        if not apkExists(fileName):
            apksListItems.append({
                "file_name": fileName,
                "apk_name": fileName,
                "category": "malicious" if "VirusShare" in fileName else "benign"
            })

    if apksListItems:
        apksListCollection.insert_many(apksListItems)

    # except Exception as ex:
    #     printException(ex)
    # finally:
    return apksListItems


def getApkListCollection():
    apksList = None
    # try:
    apksList = list(apksListCollection.find())
    # except Exception as ex:
    #     printException(ex)
    # finally:
    return apksList


def saveApkDocument(apkDoc):
    # try:
        apksListCollection.save(apkDoc)
    # except Exception as ex:
    #     printException(ex)
    # finally:
        return apkDoc

def removeApkDocuments(file_name = None):
    # try:
        criteria = {"file_name": file_name} if file_name else {}
        apksListCollection.remove(criteria)
    # except Exception as ex:
    #     printException(ex)
