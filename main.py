#!/bin/python3
import tkinter
from os import system, name
from droidDetModule import droidDet

# top = tkinter.Tk(screenName=None,  baseName=None,  className="DroidDet demo",  useTk=1)
# top.mainloop()

print("""
*************************
DROID-DET Implementation
*************************
""")

apkDir = "./datasets/apks/"

choice = 1
choiceRangeException = Exception("Please Enter a valid value between 0-3")

context_menu = """\nwhat do you want to do?
        1. Rename and get Files count
        2. Update List of Apks
        3. Generate Feature Set (Permissions data) 
            -- Extract APK Size & permissions
            -- Calculate permission rate
        4. Improve Classification results
        5. Apply rotation forest algorithm
        9. Clear Featureset data
        0. Exit
        """


def clear():
    if name == 'nt': 
        _ = system('cls') # for windows 
    else: 
        _ = system('clear') # for mac and linux(here, os.name is 'posix') 


# Getting list of apks
print("_____Getting Old Apk List ...")
apksList = droidDet.getApkList()

while choice != 0:
    # try:
        print(context_menu)
        choice = int(input("\n\nEnter your choice:\t"))
        clear()

        if choice == 1:
            print("_____Renaming Files ...")
            droidDet.rename_files(apkDir)

        elif choice == 2:
            # Getting list of apks
            print("_____Updating Apk List ...")
            apksList = droidDet.updateApkList(apkDir)

        elif choice == 3:
            print("_____Generating Feature Set")
            apksList = droidDet.extract_all_features(apkDir, apksList)

        elif choice == 4:
            print("_____ Improve classification results")
            droidDet.improve()
        
        elif choice == 9:
            print("______Clearing Featureset Data")
            apksList = droidDet.clearFeatureSet()
                
        elif choice == 0:
            print("______Exitting______")
            break
        # else:
        #     raise choiceRangeException
    # except:
    #     choice = -1
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #
    #     print("An error occurred(Main Menu): ")
    #     traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
