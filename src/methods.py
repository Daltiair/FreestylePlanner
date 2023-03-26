import math

import pandas as pd
import os
import random
import init
import socket
from conflict import resolveConflictSingles, resolveConflictCouples, resetSolutionLogic
from init import updateDanceDfs, getNode, buildInstTree, instructorOperation
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ConflictItemCouple
from uuid import getnode as gma
from output import buildEvent, makeHeatDict, buildEventfast

'''
FIle with all methods used to create the Freestyle itenerary
'''

IP = ""
port = 8989

def run():
    # Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO encrypt the file with the ip addr, add read and decryption here
    client.connect((IP, port))

    # Import all input Sheets independently
    file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'

    # get file and size
    bytestr = open(file, "rb")
    # fileSize = os.path.getsize(file)

    # Make file name the Event name in the server
    df_set = pd.read_excel(file, sheet_name='Settings', index_col=0)
    eventName = df_set['Data']['Event Name']

    # Get mac address, if not faked send all the data
    mac1 = gma()
    if mac1 == gma():
        # Send all info
        client.send((eventName + ".xlsm").encode())
        client.send(gma())
        # client.send(str(fileSize).encode())

        data = bytestr.read()
        client.sendall(data)
        client.send(b"<Terminate>")

    # TODO continually run until a message comes from the server, depending on the message execute differently
'''



'''
def partitionData():
    # Define base column lengths
    baseSingleCols = 8
    baseCoupleCols = 10
    baseInstructorCols = 4
    baseSettingsRows = 8
    """
    # DF's to make debugging faster
    data_set = {'Event Days'
                'Freestyle Time for Day 1 (in Hrs)':
                'Freestyle Time for Day 2 (in Hrs)':
                'Freestyle Time for Day 3 (in Hrs)':
                'Number of Judges':
                'Couples per Judge':
                'Number of Ballrooms':
                'Judges per Ballroom':
                'Heat Duration (Min)':
                'Heat Intermission (Min)':
                'Number of Age Brackets':
                'Age Bracket 1':
                'Age Bracket 2':
                'Age Bracket 3':
                'Event Name':
                'Data': 3,
                        4,
                        8,
                        10,
                        8,
                        4,
                        2,
                        4,
                        1.5,
                        1,
                        3,
                        35,
                        55,
                        56,
                        Hello World
                }
    
    df_set = pd.DataFrame(data=data_set)
    
    data_cat = {'Dance': ['Foxtrot',
                          'ChaCha',
                          'Bachata',
                          'Showdown'],
                'Genre': ['Smooth',
                          'Rhythm',
                          'Specialty',
                          'Event'],
                'Price': [35,
                          35,
                          35,
                          75]
                }
    df_cat = pd.DataFrame.from_dict(data_cat)
    data_inst = {'Dancer #': [205,
                              206],
                'First Name': ['Ashley',
                               'Jennifer'],
                'Last Name': ['Kipps',
                              'Howard'],
                'School': ['Richmond',
                           'Richmond']
                 }
    init.df_inst = pd.DataFrame.from_dict(data_inst)
    data_sing = {'Dancer #': [101,
                              102,
                              103,
                              104],
                 'First Name': ['Dalton',
                                "Marin",
                                "Kevin",
                                "Kayla"],
                 'Last Name': ['Dabney',
                               "Walters",
                               "Donahue",
                               "Dabney"],
                 'Age': [25,
                         24,
                         32,
                         23],
                 'Lead/Follow': ['Lead',
                                 "Follow",
                                 'Lead',
                                 "Follow"],
                 'Level': ["B1", "B1", "B3", "B4"],
                 "Instructor Dancer #'s": [[205,206],
                                        [206,205],
                                           [205, 206],
                                           [206]],
                 'School': ['Richmond',
                            'Richmond',
                            'Richmond',
                            'Richmond'],
                 'Open Foxtrot': [1,
                                  1,
                                  2,
                                  2],
                 'Closed ChaCha': [2,
                                   4,
                                   0,
                                   0],
                 'Showdown': [1,
                              3,
                              0,
                              0]
                 }
    df_sing = pd.DataFrame.from_dict(data_sing)
    data_coup = {'Lead Dancer #': [425],
                 'Lead First Name': ['Bill'],
                 'Lead Last Name': ['Richardson'],
                 'Lead Age': [54],
                 'Follow Dancer #': [426],
                 'Follow First Name': ['Suzi'],
                 'Follow Last Name': ['Richardson'],
                 'Follow Age': [52],
                 'Level': ["S4"],
                 'School': ['Richmond'],
                 'Open Foxtrot': [3],
                 'Closed ChaCha': [1],
                 'Closed Bachata': [2],
                 'Showdown': [1]
                 }
    df_coup = pd.DataFrame.from_dict(data_coup)
    """
    # Import all input Sheets independently
    file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
    df_set = pd.read_excel(file, sheet_name='Settings', index_col=0, engine="openpyxl")
    init.df_cat = pd.read_excel(file, sheet_name='Event Categories')

    # Make list of Genres
    genrelist = list(init.df_cat['Genre'].unique())
    # Make list of Dances/Events
    dancelist = list(init.df_cat['Dance'].unique())

    heats = makeHeatDict(genrelist, init.df_cat)

    # Stops pandas from reading useless blank columns
    cols = []
    for i in range(len(dancelist)+baseSingleCols):
        cols.append(i)

    init.df_sing = pd.read_excel(file, sheet_name='Singles', usecols=cols)
    init.df_sing['type id'] = ''
    init.df_sing["Dancer #"] = init.df_sing['Dancer #'].astype(int)
    init.df_sing["Age"] = init.df_sing['Age'].astype(int)
    init.df_sing["Instructor Dancer #'s"] = init.df_sing.apply(instructorOperation, axis=1)
        # # Retrofit the instructor list data
        # if type(entry["Instructor Dancer #'s"]) == int:
        #     tmp = [entry["Instructor Dancer #'s"]]
        # else:
        #     tmp = [int(x) for x in entry["Instructor Dancer #'s"].split(";")]
        # entry["Instructor Dancer #'s"] = tmp
        # del tmp

    # Stops pandas from reading useless blank columns
    cols = []
    for i in range(len(dancelist) + baseCoupleCols):
        cols.append(i)
    # df = pd.DataFrame
    # hello = {"Hello": df}
    # deleteEmpty(hello)
    # print(len(hello))
    init.df_coup = pd.read_excel(file, sheet_name='Couples', usecols=cols)
    init.df_coup["Lead Dancer #"] = init.df_coup['Lead Dancer #'].astype(int)
    init.df_coup["Follow Dancer #"] = init.df_coup['Follow Dancer #'].astype(int)
    init.df_coup["Lead Age"] = init.df_coup['Lead Age'].astype(int)
    init.df_coup["Follow Age"] = init.df_coup['Follow Age'].astype(int)
    init.df_coup["type id"] = "C"

    init.df_inst = pd.read_excel(file, sheet_name='Instructors')
    init.df_inst["Dancer #"] = init.df_inst['Dancer #'].astype(int)

    # Get all settings data partitioned and saved
    days = int(df_set['Data']['Event Days'])
    hours_p_day = []
    # create list holding hours of heat time per day
    for each in range(days):
        hours_p_day.append(int(df_set['Data'][each + 1]))

    # make df_Dnum
    cols = ['Lead Dancer #', "Lead First Name", "Lead Last Name"]
    coupl = init.df_coup[cols]
    coupl = coupl.rename(columns={'Lead First Name': 'First Name', 'Lead Last Name': 'Last Name',
                                  'Lead Dancer #': 'Dancer #'})
    cols = ['Follow Dancer #', "Follow First Name", "Follow Last Name"]
    coupf = init.df_coup[cols]
    coupf = coupf.rename(columns={'Follow First Name': 'First Name', 'Follow Last Name': 'Last Name',
                            'Follow Dancer #': 'Dancer #'})
    cols = ['Dancer #', "First Name", "Last Name"]
    sing = init.df_sing[cols]

    cols = ['Dancer #', "First Name", "Last Name"]
    inst = init.df_inst[cols]

    init.df_Dnum = pd.concat([coupl, coupf, sing, inst])

    judges = int(df_set['Data']['Number of Judges'])
    judge_ratio = int(df_set['Data']['Couples per Judge'])
    ballrooms = int(df_set['Data']["Number of Ballrooms"])
    ballroom_judges = int(df_set['Data']['Judges per Ballroom'])
    heat_duration = df_set['Data']['Heat Duration (Min)']
    heat_intermission = df_set['Data']['Heat Intermission (Min)']
    bracket_count = int(df_set['Data']['Age Brackets'])
    init.eventName = df_set['Data']['Event Name']

    init.age_brackets = []
    for each in range(bracket_count-1):
        init.age_brackets.append(int(df_set['Data'][each + days + 2]))
    init.age_brackets.append(1000)  # Append to make sure to get the last age bracket

    # Max number of couples on the floor for a dance assume even # of judges per ballroom
    init.max_dance_couples = judges * judge_ratio
    # couples_per_ballroom = int(max_dance_couples / ballrooms)  # Number of Couples on a singular ballroom
    # couples_per_ballroom = 7  # Number of Couples on a singular ballroom

    heats_p_day = []  # Holds # of heats per day
    # Calculations based on Settings data
    for count, each in enumerate(hours_p_day):
        heat_time = heat_duration + heat_intermission
        heats_p_day.append((60 / heat_time) * each)

    init.max_heats = sum(heats_p_day)  # Max number of heats for entire event due to time settings
    heats_p_hour = init.max_heats / sum(hours_p_day)
    return heats


def sliceDfs(df_sing, df_coup):
    # Slice Contestant dfs based on levels
    df_sing_AB = df_sing[(df_sing.Level == 'NC') | (df_sing.Level == 'B1') | (df_sing.Level == 'B2')]
    df_sing_FB = df_sing[(df_sing.Level == 'B3') | (df_sing.Level == 'B4')]
    df_sing_AS = df_sing[(df_sing.Level == 'S1') | (df_sing.Level == 'S2')]
    df_sing_FS = df_sing[(df_sing.Level == 'S3') | (df_sing.Level == 'S4')]
    df_sing_AG = df_sing[(df_sing.Level == 'G1') | (df_sing.Level == 'G2')]
    df_sing_FG = df_sing[(df_sing.Level == 'G3') | (df_sing.Level == 'G4') | (df_sing.Level == 'GB')]

    df_coup_AB = df_coup[(df_coup.Level == 'NC') | (df_coup.Level == 'B1') | (df_coup.Level == 'B2')]
    df_coup_FB = df_coup[(df_coup.Level == 'B3') | (df_coup.Level == 'B4')]
    df_coup_AS = df_coup[(df_coup.Level == 'S1') | (df_coup.Level == 'S2')]
    df_coup_FS = df_coup[(df_coup.Level == 'S3') | (df_coup.Level == 'S4')]
    df_coup_AG = df_coup[(df_coup.Level == 'G1') | (df_coup.Level == 'G2')]
    df_coup_FG = df_coup[(df_coup.Level == 'G3') | (df_coup.Level == 'G4') | (df_coup.Level == 'GB')]

    df_contestants = {'Single': [df_sing_AB, df_sing_FB, df_sing_AS, df_sing_FS, df_sing_AG, df_sing_FG],
                      'Couple': [df_coup_AB, df_coup_FB, df_coup_AS, df_coup_FS, df_coup_AG, df_coup_FG]
                     }

    return df_contestants
''' If I go back to saving singles and couples dances in list format each index is a different level

                    while init.dance_dfs_dict[iterator].empty:
                        init.dance_dfs_dict.remove(0)
                        df_list = dance_couples_list
                        query_df = df_list[iterator] # new df to be selecting from 
                    while dance_couples_list[couples_iterator].empty:
                        dance_couples_list.remove(0)
                        df_list = init.dance_dfs_dict
                        query_df = df_list[iterator] # new df to be selecting from
                        level_bp.append(dance_heat_count)
'''


def getContestantConflictList(dance_df, inst, contestants):
    """Finds the all contestants that will conflict for the current heat roster given the instructor inst

       Parameters
       ----------
       dance_df : Pandas DataFrame
           Current pool of single contestants
       inst : int
           Instructor Randomly picked from list of instructors possible for the level
       contestants : list[[int]]
           List of 6 lists holding all contestants that are placed in current heat
           List of 6 lists holding all contestants that are placed in current heat

       Returns
       -------
       list[int]
           a list of Dancer #'s that will conflict with the current heat roster
       """
    dupe_con = []
    for row, singles in dance_df.iterrows():
        # Set column variables based on single type
        if singles["type id"] == "L":
            contestant_col = "Lead Dancer #"
            inst_col = "Follow Dancer #"
            inst_fname = "Follow First Name"
            inst_lname = "Follow Last Name"
        elif singles["type id"] == "F":
            contestant_col = "Follow Dancer #"
            inst_col = "Lead Dancer #"
            inst_fname = "Lead First Name"
            inst_lname = "Lead Last Name"
        else:
            raise Exception("Type id for " + singles + " is invalid")
        # Retrofit the instructor list data
        # if type(singles["Instructor Dancer #'s"]) == int:
        #     tmp = [singles["Instructor Dancer #'s"]]
        # else:
        #     tmp = [int(x) for x in singles["Instructor Dancer #'s"].split(";")]
        # singles["Instructor Dancer #'s"] = tmp
        # del tmp
        for num in singles["Instructor Dancer #'s"]:
            if num == inst:
                for each in contestants:
                    if each.count(singles[contestant_col]) > 0:
                        dupe_con.append(each)
    return dupe_con


def getContestantFreeList(dance_df, inst, contestants):
    """Finds the all contestants that are free for the current heat roster given the instructor inst

       Parameters
       ----------
       dance_df : Pandas DataFrame
           Current pool of single contestants
       inst : int
           Instructor Randomly picked from list of instructors possible for the level
       contestants : list[[int]]
           List of 6 lists holding all contestants that are placed in current heat
           List of 6 lists holding all contestants that are placed in current heat

       Returns
       -------
       list[int]
           a list of Dancer #'s that are free with the current heat roster
       """
    free_con = []
    for row, singles in dance_df.iterrows():
        # Set column variables based on single type
        if singles["type id"] == "L":
            contestant_col = "Lead Dancer #"
            inst_col = "Follow Dancer #"
            inst_fname = "Follow First Name"
            inst_lname = "Follow Last Name"
        elif singles["type id"] == "F":
            contestant_col = "Follow Dancer #"
            inst_col = "Lead Dancer #"
            inst_fname = "Lead First Name"
            inst_lname = "Lead Last Name"
        else:
            raise Exception("Type id for " + singles + " is invalid")
        for num in singles["Instructor Dancer #'s"]:
            if num == inst:
                for each in contestants:
                    if each.count(singles[contestant_col]) == 0:
                        free_con.append(each)
    return free_con

def deleteEmpty(dance_dfs):
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            deleteEmpty(dance_dfs[each])
            if len(dance_dfs[each]) == 0:  # If dict is now empty, delete it
                del dance_dfs[each]
        elif dance_dfs[each].empty:
            del dance_dfs[each]
    return dance_dfs


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


def pickDfs(ev, dance_dfs, inst_tree, floors, div, eventages_s, eventages_c, couples_per_floor):
    print()
    l_keys = [0, 1, 2, 3, 4, 5]

    if div.count('T') == 0 and div.count('t') == 0:
        start = "A"
    elif "S" in dance_dfs:
        start = "S"
    else:
        start = "C"

    shell = dance_dfs[start]
    picked_keys = []
    picked_keys.append(start)
    # TODO how to handel lead and follow 3 or 4 split with singles
    while type(shell) is dict:
        # pick = random.choice(list(shell.keys()))  # random choice
        pick = list(shell.keys())[0]
        picked_keys.append(pick)
        shell = shell[pick]

    # If only one floor return the key
    if len([picked_keys]) == floors:
        return [picked_keys]
    unideal = []  # keys that do not meet initial conditions but if no other options will choose one of these
    # If picked df is a single
    if picked_keys[0] == "S":
        iter = 1  # Iterator to track key index
        # if divided by L and F, set labels
        if ("S" in div) or ("s" in div):
            same_s = "same_s"
            opp_s = "opp_s"
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_s = "Follow"
            opp_s = "Lead"

        # If divided by level set the same level
        if ("L" in div) or ("l" in div):
            same_l = picked_keys[iter]
            diff_l = "diff_l"
            lev_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_l = 0
            diff_l = 0

        # If divided by age set the same age bracket
        if ("A" in div) or ("a" in div):
            same_a = picked_keys[iter]
            diff_a = "diff_a"
            age_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_a = 0
            diff_a = 0

        #        Opposite Gender
        prio_s = [["S", opp_s, same_l, same_a], ["S", opp_s, same_l, diff_a], ["S", opp_s, diff_l, same_a],
                  ["S", opp_s, diff_l, diff_a],
        #         Same Gender
                  ["S", same_s, same_l, diff_a], ["S", same_s, diff_l, same_a], ["S", same_s, diff_l, diff_a],
        #         Couples
                  ["C", same_l, same_a], ["C", same_l, diff_a], ["C", diff_l, same_a], ["C", diff_l, diff_a]]
        all_poss = []  # holds all possible keys to be selected, used in the case of different level or age
        picked_keys = [picked_keys]
        prio = 0
        while prio < len(prio_s):
            if dance_dfs.get(prio_s[prio][0]) is None:
                prio += 1
                continue
            poss_key = []
            iter = 1
            # Take out unused key slots
            if div.count('T') != 0 or div.count('t') != 0:
                poss_key.append(prio_s[prio][0])
            else:
                poss_key.append("A")
            if (div.count('s') != 0 or div.count('S') != 0) and poss_key[0] == "S":
                if prio_s[prio][1] == "opp_s":
                    if picked_keys[-1][iter] == "Lead":
                        poss_key.append("Follow")
                    else:
                        poss_key.append("Lead")
                else:
                    if picked_keys[-1][iter] == "Follow":
                        poss_key.append("Follow")
                    else:
                        poss_key.append("Lead")
                iter += 1
            if div.count('L') != 0 or div.count('l') != 0:
                if prio_s[prio][2] != "diff_l":
                    poss_key.append(prio_s[prio][2])
                    all_poss.append(poss_key)
                else:  # If different level make a key with all possible levels
                    for lev in l_keys:  # For all level keys
                        if lev != picked_keys[0][lev_index]:  # if not the same level, create a new possible key
                            poss_key.append(lev)
                            all_poss.append(poss_key)
                            poss_key = poss_key[:-1]
                iter += 1
            if div.count('A') != 0 or div.count('a') != 0:
                if len(all_poss) == 0:  # in case 'l' split is not part of this Event
                    all_poss.append(poss_key)
                try:
                    if prio_s[prio][3] != "diff_a":
                        for key in all_poss:
                            key.append(prio_s[prio][3])
                    else:  # If different age make a key with all possible ages
                        curr_all_poss = len(all_poss)
                        if prio_s[prio][0] == "S":  # Make sure to give the correct age brackets based on the current possible key(s)
                            ages_to_use = eventages_s
                        else:
                            ages_to_use = eventages_c
                        agelist = ages_to_use.copy()
                        agelist.remove(picked_keys[0][age_index])
                        # iter = 0
                        for age in agelist:
                            for j in range(curr_all_poss):
                                poss_key = all_poss[j][:]
                                poss_key.append(age)
                                all_poss.append(poss_key)
                        # Remove the all_poss with no age
                        all_poss = all_poss[curr_all_poss:]
                except:
                    print(prio_s, prio)
            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            for every in all_poss:
                for i, key in enumerate(every):
                    if i == 0:
                        tmp = dance_dfs[key]
                        continue
                    if key not in tmp:
                        break
                    if type(tmp[key]) is dict:
                        tmp = tmp[key]
                    elif every not in picked_keys:  # add to picked list only if that key combo is not in already
                        # if added is a single
                        if every[0] == "S":
                            cop = []
                            for key in picked_keys:
                                cop.append(key[:])
                            # Sanity check the levels in question
                            unique = findUnique(inst_tree, cop, every)
                            count = findInstCount(inst_tree, every)
                            # find # of 'singles' rooms
                            sfloors = 0
                            for room in picked_keys:
                                if room[0] == "S":
                                    sfloors += 1
                            if every[0] == "S":
                                sfloors += 1
                            # if (unique >= (len(picked_keys) * couples_per_floor)-3) and (count > (couples_per_floor-2)):
                            if unique >= (sfloors * couples_per_floor)-2:
                                picked_keys.append(every)
                                picked = True
                                break
                            else:
                                unideal.append([every, count])
                        else:  # if not a single
                            count = findContestantCount(dance_dfs, every, ev)
                            if count[0] >= couples_per_floor-2:
                                picked_keys.append(every)
                                picked = True
                            else:
                                unideal.append([every, count[1]])
                if picked:  # If picked break
                    picked = False
                    prio = 1  # So I don't skip other gender prio options
                    break
                if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                    prio += 1
            all_poss.clear()  # Once all possible keys in priority slot are not picked, clear the list
            if len(picked_keys) == floors:
                break
                
    # If picked df is a couple
    elif picked_keys[0] == "C" or picked_keys[0] == "A":
        iter = 1  # Iterator to track key index
        # If divided by level set the same level
        if ("L" in div) or ("l" in div):
            same_l = picked_keys[iter]
            diff_l = "diff_l"
            lev_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_l = 0
            diff_l = 0

        # If divided by age set the same age bracket
        if ("A" in div) or ("a" in div):
            same_a = picked_keys[iter]
            diff_a = "diff_a"
            age_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_a = 0
            diff_a = 0

        # Pick priority list depending on starting key
        if picked_keys[0] == "C":
            #         Couples
            prio_c = [["C", same_l, diff_a], ["C", diff_l, same_a], ["C", diff_l, diff_a],
            #         Singles
            #           ["S", "single", same_l, same_a], ["S", "single", same_l, diff_a], ["S", "single", diff_l, same_a],
            #           ["S", "single", diff_l, diff_a]
                      ]
        elif picked_keys[0] == "A":
            prio_c = [["A", same_l, diff_a], ["A", diff_l, same_a], ["A", diff_l, diff_a]]

        all_poss = []  # holds all possible keys to be selected, used in the case of different level or age
        picked_keys = [picked_keys]
        prio = 0
        while prio < len(prio_c):

            poss_key = []
            iter = 1
            if dance_dfs.get(prio_c[prio][0]) is None:
                prio += 1
                continue
            # Take out unused key slots
            if div.count('T') != 0 or div.count('t') != 0:
                poss_key.append(prio_c[prio][0])
            else:
                poss_key.append("A")
            if (div.count('s') != 0 or div.count('S') != 0) and poss_key[0] == "S":
                poss_key.append("Lead")
                all_poss.append(poss_key)
                poss_key = poss_key[:-1]
                poss_key.append("Follow")
                all_poss.append(poss_key)
                iter += 1
            if div.count('L') != 0 or div.count('l') != 0:
                if len(all_poss) == 0:  # in case 's' split is not part of this event
                    all_poss.append(poss_key)
                if prio_c[prio][1] != "diff_l":
                    for key in all_poss:
                        key.append(prio_c[prio][1])
                else:  # If different level make a key with all possible levels
                    curr_all_poss = len(all_poss)
                    for lev in l_keys:  # duplicate current all_poss per different level
                        if lev != picked_keys[0][lev_index]:
                            for j in range(curr_all_poss):
                                poss_key = all_poss[j][:]
                                poss_key.append(lev)
                                all_poss.append(poss_key)
                    # remove first 2 keys that have no age
                    all_poss = all_poss[curr_all_poss:]
                iter += 1
            if div.count('A') != 0 or div.count('a') != 0:
                if len(all_poss) == 0:  # In case 's' split is not part of this
                    all_poss.append(poss_key)
                if prio_c[prio][2] != "diff_a":
                    for key in all_poss:
                        key.append(prio_c[prio][2])
                else:  # If different age make a key with all existing key with all ages
                    curr_all_poss = len(all_poss)
                    if prio_c[prio][0] == "S":  # Make sure to give the correct age brackets for selection, based on the possible keys
                        ages_to_use = eventages_s
                    else:
                        ages_to_use = eventages_c
                    agelist = ages_to_use.copy()
                    agelist.remove(picked_keys[0][age_index])
                    for age in agelist:
                        for j in range(curr_all_poss):
                            poss_key = all_poss[j][:]
                            poss_key.append(age)
                            all_poss.append(poss_key)
                    # Remove the all_poss with no age
                    all_poss = all_poss[curr_all_poss:]

            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            print("Checking all possible keys", all_poss)
            for every in all_poss:
                for i, key in enumerate(every):
                    if i == 0:
                        tmp = dance_dfs[key]
                        continue
                    if key not in tmp:
                        break
                    if type(tmp[key]) is dict:
                        tmp = tmp[key]
                    elif every not in picked_keys:  # add to picked list only if that key combo is not in already
                        # if added is a single
                        if every[0] == "S":
                            cop = []
                            for key in picked_keys:
                                cop.append(key[:])
                            # Sanity check the levels in question
                            unique = findUnique(inst_tree, cop, every)
                            count = findInstCount(inst_tree, every)
                            # find # of 'singles' rooms
                            sfloors = 0
                            for room in picked_keys:
                                if room[0] == "S":
                                    sfloors += 1
                            if every[0] == "S":
                                sfloors += 1
                            # if (unique >= (len(picked_keys) * couples_per_floor)-3) and (count > (couples_per_floor-2)):
                            if unique >= (sfloors * couples_per_floor) - 2:
                                picked_keys.append(every)
                                picked = True
                                break
                            else:
                                unideal.append([every, count])
                        else:  # if not a single
                            print("Checking if", every, "can be added")
                            count = findContestantCount(dance_dfs, every, ev)
                            if count[0] >= (couples_per_floor - 2):
                                picked_keys.append(every)
                                picked = True
                            else:
                                print("added an unideal heat", every)
                                unideal.append([every, count[1]])
                if picked:  # If picked break
                    picked = False
                    prio = 0  # So I don't skip other gender prio options
                    break
                if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                    prio += 1
            all_poss.clear()  # Once all possible keys in priority slot are not picked, clear the list
            if len(picked_keys) == floors:
                break

        # If all possible keys are tried and not filled the floors try the unideal heats
        while len(picked_keys) != floors:
            if len(unideal) == 0:
                break
            largest = 0
            largest_index = 0
            for i, each in enumerate(unideal):
                if each[1] > largest:
                    largest = each[1]
                    largest_index = i
            print("Using Unideal heat", unideal[largest_index][0])
            picked_keys.append(unideal[largest_index][0])
            del unideal[largest_index]
    if len(picked_keys) < floors:
        pass
    return picked_keys


def findUnique(inst_tree, picked_keys, newkey):

    instructors = []

    picked_keys.append(newkey)
    for each in picked_keys:
        if each[0] != "C":
            tmp = inst_tree[each[0]]
            i = 1
            while type(tmp) is dict and i < len(each):
                tmp = tmp[each[i]]
                i += 1
            instructors = list(tmp.keys()) + instructors

    return len(set(instructors))


def findInstCount(inst_tree, newkey):
    for i, each in enumerate(newkey):
        if i == 0:
            tmp = inst_tree[each]
            continue
        tmp = tmp[each]

    return len(tmp.keys())


def findContestantCount(dance_dfs, newkey, ev):
    try:
        for i, each in enumerate(newkey):
            if i == 0:
                tmp = dance_dfs[each]
                continue
            tmp = tmp[each]
        return [tmp.shape[0], tmp[ev].sum()]
    except:
        print(newkey, "No longer in pool")


def PoachPrevHeatsSingles(roomid, div, dance_df, heat, heatlist, acceptablecouples):
    if heatlist.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this events Division settings")
        return
    heatlen = len(heat.getRoster()[roomid])
    couples_per_floor = heatlist.getCouplesPerFloor()

    poachlist = []
    heatnums = []
    potentials = 0
    poachsingles = []
    poachinst = []
    runcounter = 0
    # While current heat's selection room is less than half the size of a full room
    while heatlen < acceptablecouples:
        if runcounter > 5:  # If poacher runs for 15 iterations and no fill then break out
            print("forcing out poaching", div)
            break
        print("Gather entries to Poach", div)
        for heat_index, each in enumerate(heatlist.getRostersList()):
            # Check if heat has division
            if div not in each.getDiv():
                continue
            # # Find an entry in the previous heat room that has no conflicts with current heat
            # if each.getDiv().count(div) > 1:
            #     past_heat_iter = each.getDiv().count(div)
            # else:
            #     past_heat_iter = 1
            # start_at = 0
            # for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
            swapping_room = each.getDiv().index(div, 0)
            if not len(each.getRoster()[swapping_room]) > acceptablecouples:
                continue
            start_at = swapping_room
            index_iter = 0
            index_2_swap = -1
            dup = False
            for contestant, inst in zip(each.getSingles()[swapping_room], each.getInstructors()[swapping_room]):
                for i, singles in enumerate(heat.getSingles()):
                    if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                        dup = True
                        break
                for i, instructors in enumerate(heat.getInstructors()):
                    if contestant in instructors:  # make sure the conflict is not because it has some inst trying to be freed
                        raise Exception(contestant, "in Singles Instructor list")
                        # conflict to check the previous heat entry nth conflict
                        # resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index,swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee])
                        # resolverLog.addConflict(resolverconflict, con_num)
                        # print("Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), 'inst', inst)
                    if inst in instructors:
                        dup = True
                        break
                for i, couples in enumerate(heat.getCouples()):
                    if contestant in couples:
                        dup = True
                        break
                if not dup:
                    index_2_swap = index_iter
                    # if (contestant in poachsingles) or (inst in poachinstructors):
                    if contestant not in poachsingles and inst not in poachinst and heat_index not in heatnums:
                        # Check this single/inst is not in the list already
                        poachlist.append([heat_index, swapping_room, index_2_swap])
                        heatnums.append(heat_index)
                        poachsingles.append(contestant)
                        poachinst.append(inst)
                    else:
                        potentials += 1
                dup = False
                index_iter += 1
        # Determine if it is better to backfill
        # if (len(poachlist) + len(heat.getSingles()[roomid])) < acceptablecouples or heatlist.getDivisionHoleCount(div) >= heatlen:
        #     print("Poach will not reach acceptable roster size")
            # backfill_df = pd.DataFrame()
            # for i, contestant in enumerate(reversed(heat.getSingles()[roomid])):
            #     index = len(heat.getSingles()[roomid]) - 1
            #     tmp = heat.stealEntry(roomid, index)
            #     backfill_df = pd.concat([backfill_df, tmp])
            #     # if singles["type id"] == "L":
            #     #     contestant_col = "Lead Dancer #"
            #     #     inst_col = "Follow Dancer #"
            #     #     inst_fname = "Follow First Name"
            #     #     inst_lname = "Follow Last Name"
            #     # elif singles["type id"] == "F":
            #     #     contestant_col = "Follow Dancer #"
            #     #     inst_col = "Lead Dancer #"
            #     #     inst_fname = "Lead First Name"
            #     #     inst_lname = "Lead Last Name"
            #     # else:
            #     #     raise Exception("Type id for " + singles + " is invalid")
            #     # if dance_df[dance_df[contestant_col] == contestant].shape[0] > 0:
            #     #     dance_df.loc[dance_df.loc[:, contestant_col] == tmp.loc[0, contestant_col], init.ev] = dance_df.loc[dance_df.loc[:, contestant_col] == tmp.loc[0, contestant_col], init.ev] + 1
            #     # dance_df = pd.concat([dance_df, tmp])
            # print("Backfilling", div)
            # result = backfill(backfill_df, div, heatlist, couples_per_floor, init.ev)
            # if result == -1:  # If backfill failed put entries back into the room
            #     for row, data in backfill_df.iterrows():
            #         data = data.to_frame().T
            #         heat.addEntry(data, roomid)
            # return
        instructors_list = []
        for i, each in enumerate(heat.getInstructors()):
            for every in each:
                instructors_list.append(every)
        singles_list = []
        for i, each in enumerate(heat.getSingles()):
            for every in each:
                singles_list.append(every)
        print("Poaching from heats", div, poachlist)
        counter = 0
        while counter < 2:
            for poach in reversed(poachlist):
                if heatlen == acceptablecouples:
                    return
                # poach = random.choice(poachlist)
                heat2poach = heatlist.getRostersList()[poach[0]]
                # Check if either are in Heat already
                if heat2poach.getSingles()[poach[1]][poach[2]] in singles_list:
                    continue
                if heat2poach.getInstructors()[poach[1]][poach[2]] in instructors_list:
                    continue
                if len(heat2poach.getRoster()[poach[1]]) >= couples_per_floor and counter == 0:
                    print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                elif counter >= 1 and len(heat2poach.getRoster()[poach[1]]) >= acceptablecouples:
                    print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                # Add new entry to the check list to stop multiple person problem
                singles_list.append(heat.getSingles()[roomid][-1])
                instructors_list.append(heat.getInstructors()[roomid][-1])
            counter += 1
        poachlist.clear()
        runcounter += 1


def PoachPrevHeatsCouples(roomid, div, dance_df, heat, heatlist, acceptablecouples):
    if heatlist.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this event's Division settings")
        return
    couples_per_floor = heatlist.getCouplesPerFloor()
    heatlen = len(heat.getRoster()[roomid])
    poachlist = []
    # poachcouples = []
    # While current heat's selection room is less than half the size of a full room
    for heat_index, each in enumerate(heatlist.getRostersList()):
        # Check if heat has division
        if div not in each.getDiv():
            continue
        # Find an entry in the previous heat room that has no conflicts with current heat
        if each.getDiv().count(div) > 1:
            past_heat_iter = each.getDiv().count(div)
        else:
            past_heat_iter = 1
        start_at = 0

        swapping_room = each.getDiv().index(div, start_at)
        start_at = swapping_room
        index_iter = 0
        index_2_swap = -1
        lookin = each.getCouples()[swapping_room]
        dup = False
        for contestant in lookin:
            for i, singles in enumerate(heat.getSingles()):
                if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                    dup = True
                    break
            for i, instructors in enumerate(heat.getInstructors()):
                if contestant in instructors:  # make sure the conflict is not because it has some inst trying to be freed
                    raise Exception("Couples Conflict Contestant", contestant, "in Singles Instructor list")
                    # conflict to check the previous heat entry nth conflict
                    # resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index,swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee])
                    # resolverLog.addConflict(resolverconflict, con_num)
                    # print("Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), 'inst', inst)
            for i, couples in enumerate(heat.getCouples()):
                if contestant in couples:
                    dup = True
                    break
            # if no conflicts with both lead and follow, make the swap with entry index i
            if math.fmod(index_iter, 2) == 1:
                if not dup:
                    index_2_swap = int((index_iter-1) / 2)
                    f = contestant
                    if [heat_index, swapping_room, index_2_swap] not in poachlist: # and (l not in poachcouples) and (f not in poachcouples): # Check this couple is not in the list already
                        poachlist.append([heat_index, swapping_room, index_2_swap])
                        # poachcouples.append(l)
                        # poachcouples.append(f)
                dup = False
            else:
                if not dup:
                    l = contestant
            index_iter += 1

    if (len(poachlist) + len(heat.getCouples()[roomid])) < acceptablecouples or heatlist.getDivisionHoleCount(div) >= heatlen:
        backfill_df = pd.DataFrame()
        for contestant in reversed(heat.getCouples()[roomid]):
            index = len(heat.getCouples()[roomid])-1
            tmp = heat.stealEntry(roomid, index)
            backfill_df = pd.concat([backfill_df, tmp])
            # dance_df = pd.concat([dance_df, tmp])
        print("Backfilling", div)
        result = backfill(backfill_df, div, heatlist, couples_per_floor, init.ev)
        if result == -1:  # If backfill failed put entries back into the room
            for row, data in backfill_df.iterrows():
                heat.addEntry(data, roomid)
    else:
        couples_list = []
        for i, each in enumerate(heat.getCouples()):
            for every in each:
                couples_list.append(every)
        print("Poaching from heats", div, poachlist)
        counter = 0
        while counter < 2:
            for poach in poachlist:
                if heatlen == acceptablecouples:
                    return
                # poach = random.choice(poachlist)
                heat2poach = heatlist.getRostersList()[poach[0]]
                # Check if either are in Heat already
                if heat2poach.getCouples()[poach[1]][poach[2]] in couples_list:
                    continue
                if heat2poach.getCouples()[poach[1]][poach[2] + 1] in couples_list:
                    continue
                if len(heat2poach.getRoster()[poach[1]]) >= couples_per_floor and counter == 0:
                    print("Contestant", heat2poach.getCouples()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                elif counter >= 1 and len(heat2poach.getRoster()[poach[1]]) >= acceptablecouples:
                    # Check if either are in Heat already
                    print("Contestant", heat2poach.getCouples()[poach[1]][poach[2]], "stolen from heat, room",poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
            counter += 1


def backfill(dance_df, div, heat_list, couples_per_floor, ev):
    # Todo: while df has entries
    #  loop over the heat list and find a heat that is < max
    #  if found check the meta data,
    #  check if contestant(s) is alreay in the heat
    #  loop over the inst of single and strike it if it is there, if there are no inst left move on
    print("Backfilling", div)
    if heat_list.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this events Division settings")
        return
    if heat_list.getDivisionHoleCount(div) == 0:
        print("No holes to fill exiting backfill, next heat will poach", div)
        return
    if heat_list.getDivisionHoleCount(div) < dance_df[ev].sum():
        print("Not enough holes to deplete list")

    backfill_df = dance_df.copy(True)
    list_index = 0
    heats = heat_list.getRostersList()
    heats_count = len(heats)
    backfill_list = []
    nobackfill = False
    while heat_list.getDivisionHoleCount(div) > 0 and not nobackfill:
        nobackfill = True
        for row, data in backfill_df.iterrows():
            # Set columns to check
            if data["type id"] == "L":
                con_col = ["Lead Dancer #", "Lead Dancer #"]
            elif data["type id"] == "F":
                con_col = ["Follow Dancer #", "Follow Dancer #"]
            else:
                con_col = ["Lead Dancer #", "Follow Dancer #"]
            # Search the list
            placed = False
            list_index = 0
            while (list_index < heats_count):

                # Check if heat has this division
                if div not in heats[list_index].getDiv():
                    list_index += 1
                    continue
                # Check if Dancer is already in heat
                found = False
                inst_found = False
                for each in heats[list_index].getSingles():
                    if data[con_col[0]] in each or data[con_col[1]] in each:
                        found = True
                        break
                for each in heats[list_index].getInstructors():
                    if data[con_col[0]] in each or data[con_col[1]] in each:
                        raise Exception("While in backfill() Instructor # matches with " + data)
                        break
                for each in heats[list_index].getCouples():
                    if data[con_col[0]] in each or data[con_col[1]] in each:
                        found = True
                        break
                if found:
                    list_index += 1
                    break
                roomid = heats[list_index].getDiv().index(div)  # Note will only return
                # if couple place it
                if data["type id"] == "C":
                    heats[list_index].addEntry(data, roomid)
                    list_index += 1
                    break

                # If single need to check the instructors
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
                else:
                    raise Exception("While running backfill() for", div, "Type id for", data, "is invalid")

                # Check all instructor options
                if data["type id"] != "C":
                    for inst in data["Instructor Dancer #'s"]:
                        inst_found = False
                        for each in heats[list_index].getInstructors():
                            if inst in each:
                                inst_found = True
                                break
                        for each in heats[list_index].getCouples():
                            if inst in each:
                                inst_found = True
                                break
                        for each in heats[list_index].getSingles():
                            if inst in each:
                                inst_found = True
                                break
                        if not inst_found:
                            break

                    if inst_found:
                        found = True

                if (not found) and len(heats[list_index].getRoster()[roomid]) <= couples_per_floor:
                    nobackfill = False
                    # Set candidate to this single/inst match
                    candidate = data.to_frame().T
                    candidate = candidate.reset_index(drop=True)
                    if data["type id"] != "C":
                        instructor_data = init.df_inst[init.df_inst["Dancer #"] == inst].reset_index(drop=True)
                        candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                        candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                        candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                    print("Candidate", candidate.loc[0,contestant_col], "Backfilled to", list_index, div,)
                    heats[list_index].addEntry(candidate, roomid)
                    # Remove the placed candidate from the df, or -1 if multi-entry
                    dance_df.loc[dance_df.loc[:, contestant_col] == candidate.loc[0, contestant_col], ev] = candidate.loc[0, ev] - 1
                    break
                list_index += 1
                if not found:
                    break
        backfill_df = backfill_df[backfill_df.loc[:, ev] != 0]

    dance_df = backfill_df
    return

        # if len(backfill_list) < dance_df[init.ev].sum():
        #     print("Backfill not possible recommend changing Division settings for", div, "in", init.ev)
        #     return -1
        # else:
        #     for each in backfill_list:
        #         # Set candidate to this single/inst match
        #         candidate = each[0]
        #         candidate = candidate.reset_index(drop=True)
        #         data = data.to_frame().T
        #         if data["type id"] != "C":
        #             instructor_data = init.df_inst[init.df_inst["Dancer #"] == each[1]].reset_index(drop=True)
        #             candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
        #             candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
        #             candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
        #         heats[each[1]].addEntry(candidate, each[2])
        #         # Remove the placed candidate from the df, or -1 if multi-entry
        #         dance_df.loc[dance_df.loc[:, contestant_col] == candidate.loc[0, contestant_col], ev] = candidate.loc[0, ev] - 1



