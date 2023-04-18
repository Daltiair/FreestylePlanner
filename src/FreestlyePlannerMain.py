''' Driver file for the FreeStyle Planner Application
runs all the methods and outputs an excel sheet with a Freestyle itenerary for a dacne event 

Written by Dalton Dabney 7/9/22
'''
import sys

from methods import *
from output import *
from selection import *
# from gui import *
import getpass
import hashlib


def startProcess(instance):
    # try:
    heats = partitionData()
    createParticipantSheets()
    Selection(heats)
    # except Exception as e:
    #     print(e)

if __name__ == '__main__':
    # freestylePlannerGuiApp().run()
    startProcess([])
    # hash = hashlib.sha512()
    # while True:
    #     if "PlannerBypass" in os.environ:
    #         partitionData()
    #     else:
    #         try:
    #             pword = getpass.getpass(stream=sys.stderr)
    #         except Exception as error:
    #             print("Error", error)
    #         else:
    #             filepath = os.getcwd().replace('\src', "") + "/"
    #             with open(filepath+'password.txt') as f:
    #                 password = f.readlines()
    #             hash.update(pword.encode())
    #             if hash.hexdigest() == password[0]:
    #                 freestylePlannerGuiApp().run()
    #             else:
    #                 print("Wrong Password")
    # ran = False


