'''File to house global variables and helper methods'''

# Data and partition variables, Static
import pandas as pd

df_Dnum = 0
df_cat = 0
df_inst = 0
df_coup = 0
df_sing = 0
df_pro = 0
max_dance_couples = 0
max_heats = 0
eventName = 0

# TODO DEBUG
debug = False
count = False
inst = False
check = False
singles_only = False
couples_only = False

# Dynamic Event variables and Structures
logString = ""
eventdiv = []
age_brackets = []
dance_dfs = 0
inst_tree = 0
inst2sing_tree = 0
test_dict = {}
SingleBaseCols = ["Dancer #", "First Name", "Last Name", "Age", "Lead/Follow", "Level", "Instructor Dancer #'s", "School"]
CoupleBaseCols = ["Lead Dancer #", "Lead First Name", "Lead Last Name", "Lead Age",
                  "Follow Dancer #", "Follow First Name", "Follow Last Name", "Follow Age",
                  "Level", "School"]
age_bnames = ["A", "A1", "B", "B1", "C", "C1", "D"]
lvls = ["AB", "FB", "AS", "FS", 'AG', "FG"]
lvl_conversion = [0, 1, 2, 3, 4, 5]
eventlvlnames_s = []
eventlvlnames_c = []
eventages_s = []
eventages_c = []
ev = "None"
debug_floors = []

# Conflict variables, Static
# solved = 0  # counts how many resolveConflict() calls for this pair search
# nsolved = 0  # counts how many resolveNConflict() calls for this pair search
# solutioncount = 0  # holds which solution in the chain I am on
max_conflicts = 1000
maxsolves = 3
maxorder = 3
maxsolutions = [7, 5, 5]  # Termination clauses for solving conflicts n times
solved = [0] * maxorder
presolved = [0] * maxorder
solution = [0] * (maxorder + 1)
starting_instructors_for_heat = []

# Participant sheets
participantsheetcols = {"Day": [], "Heat #": [], "Floor": [], "Partner #": [], "Partner Name": [], "Event": [],
                        "Syllabus": [], "Division": []}
participantsheets = {}
participantsheet_excelcols = ["A", "B", "C", "D", "E", "F", "G", "H"]
participantsheet_exceldimensions = [9, 35, 9, 15, 22, 24, 9, 18]
participantsheet_excelalignments = ["right", "center", 'right', "right", 'center', 'center', 'center', 'center']
# Heat sheets
excelcols = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
excelalignments = ["center", "right", 'left', "left", 'right', 'left', 'left', 'center', 'left']
exceldimensions = [9, 15, 15, 15, 15, 18, 18, 7, 15]
df_cols = ['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Follow Dancer #', 'Follow First Name',
           'Follow Last Name', 'Level', 'School']


def getNode(dance_dfs, div):
    try:
        for i, key in enumerate(div):
            if i == 0:
                tmp = dance_dfs[key]
            elif type(tmp) is dict:
                tmp = tmp[key]
        return tmp
    except Exception:
        print("Node does not exist", div)
        return {}


def deleteEmpty(dance_dfs):
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            deleteEmpty(dance_dfs[each])
            if len(dance_dfs[each]) == 0:  # If dict is now empty, delete it
                del dance_dfs[each]
        elif (dance_dfs[each]).empty:
            del dance_dfs[each]
    return dance_dfs


def updateDanceDfs(dance_dfs, df_for_heat, floor_info, full_key):
    try:
        if type(dance_dfs[floor_info[0]]) is dict:
            updateDanceDfs(dance_dfs[floor_info[0]], df_for_heat, floor_info[1:], full_key)
        else:
            dance_dfs[floor_info[0]] = df_for_heat
        return dance_dfs
    except:
        print("Df pool is already deleted for", full_key)


def buildInstTree(dance_dfs, inst_tree, ev):
    """Builds the dictionary tree of all instructors and thier count in that division

           Parameters
           ----------
           dance_df : Pandas DataFrame
               Current pool of single contestants
           inst_tree : Python Dictionary
               Tree of dictionaries key'd by the division metrics

           Returns
           -------
           dict
              tree of all instructor counts key'd by thier division
           """
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            inst_tree[each] = {}
            buildInstTree(dance_dfs[each], inst_tree[each], ev)
        else:
            singles_only = dance_dfs[each][(dance_dfs[each]['type id'] == 'L') | (dance_dfs[each]['type id'] == 'F')]
            if not singles_only.empty:
                inst_tree[each] = {}
                # Find unique instructors for this division
                for row, data in singles_only.iterrows():  # Iterate down all rows of Single df
                    if data["type id"] == "L":
                        contestant_col = "Lead Dancer #"
                        inst_col = "Follow Dancer #"
                        inst_fname = "Follow First Name"
                        inst_lname = "Follow Last Name"
                    elif data["type id"] == "F":
                        contestant_col = "Follow Dancer #"
                        inst_col = "Lead Dancer #"
                        inst_fname = "Lead First Name"
                        inst_lname = "Lead Last Name"
                    # if type(data["Instructor Dancer #'s"]) == int:
                    #     tmp = [data["Instructor Dancer #'s"]]
                    #     data["Instructor Dancer #'s"] = tmp
                    #     del tmp
                    # elif type(data["Instructor Dancer #'s"]) != list:
                    #     tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
                    #     data["Instructor Dancer #'s"] = tmp
                    #     del tmp
                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                        if num in inst_tree[each].keys():
                            inst_tree[each][num] += data[
                                ev]  # Need to add this contestant's entry number for this event
                        else:
                            inst_tree[each][num] = data[ev]  # Need to add this contestant's entry number for this event
    return inst_tree


def buildInst2SingTree(dance_dfs, inst2sing_tree, ev):
    """Builds the dictionary tree of all instructors and thier count in that division

           Parameters
           ----------
           dance_df : Pandas DataFrame
               Current pool of single contestants
           inst_tree : Python Dictionary
               Tree of dictionaries key'd by the division metrics

           Returns
           -------
           dict
              tree of all instructor counts key'd by thier division
           """
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            inst2sing_tree[each] = {}
            buildInst2SingTree(dance_dfs[each], inst2sing_tree[each], ev)
        else:
            singles_only = dance_dfs[each][(dance_dfs[each]['type id'] == 'L') | (dance_dfs[each]['type id'] == 'F')]
            if not singles_only.empty:
                inst2sing_tree[each] = {}
                # Find unique instructors for this division
                for row, data in singles_only.iterrows():  # Iterate down all rows of Single df
                    if data["type id"] == "L":
                        contestant_col = "Lead Dancer #"
                        inst_col = "Follow Dancer #"
                        inst_fname = "Follow First Name"
                        inst_lname = "Follow Last Name"
                    elif data["type id"] == "F":
                        contestant_col = "Follow Dancer #"
                        inst_col = "Lead Dancer #"
                        inst_fname = "Lead First Name"
                        inst_lname = "Lead Last Name"
                    # if type(data["Instructor Dancer #'s"]) == int:
                    #     tmp = [data["Instructor Dancer #'s"]]
                    # else:
                    #     tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
                    # data["Instructor Dancer #'s"] = tmp
                    # del tmp
                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                        # singles for that instructor tree
                        if inst2sing_tree[each].get(num) is None:
                            inst2sing_tree[each][num] = [data[contestant_col]]
                        if data[contestant_col] not in inst2sing_tree[each][num]:
                            inst2sing_tree[each][num].append(data[contestant_col])

    return inst2sing_tree


def instructorOperation(row):
    if type(row["Instructor Dancer #'s"]) == int:
        return [row["Instructor Dancer #'s"]]
    else:
        return [int(x) for x in row["Instructor Dancer #'s"].split(";")]
