import math

import pandas as pd
import os
import init
import socket
from init import updateDanceDfs, getNode, buildInstTree, instructorOperation
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
    for i in range(len(dancelist)+len(init.SingleBaseCols)):
        cols.append(i)
    # cols = init.SingleBaseCols.copy()
    # cols.extend(dancelist)

    init.df_sing = pd.read_excel(file, sheet_name='Singles', usecols=cols)
    # init.df_sing = pd.read_excel(file, sheet_name='Singles')
    init.df_sing['type id'] = ''
    init.df_sing["Dancer #"] = init.df_sing['Dancer #'].astype(int)
    init.df_sing["Age"] = init.df_sing['Age'].astype(int)
    init.df_sing["Instructor Dancer #'s"] = init.df_sing.apply(instructorOperation, axis=1)

    # Stops pandas from reading useless blank columns
    cols = []
    for i in range(len(dancelist) + len(init.CoupleBaseCols)):
        cols.append(i)
    # cols = init.CoupleBaseCols.copy()
    # cols.extend(dancelist)

    init.df_coup = pd.read_excel(file, sheet_name='Couples', usecols=cols)
    init.df_coup["Lead Dancer #"] = init.df_coup['Lead Dancer #'].astype(int)
    init.df_coup["Follow Dancer #"] = init.df_coup['Follow Dancer #'].astype(int)
    init.df_coup["Lead Age"] = init.df_coup['Lead Age'].astype(int)
    init.df_coup["Follow Age"] = init.df_coup['Follow Age'].astype(int)
    init.df_coup["type id"] = "C"

    # Make event columns as int
    for each in dancelist:
        if each in init.df_coup.columns:
            init.df_coup[each] = init.df_coup[each].astype(int)

        if each in init.df_sing.columns:
            init.df_sing[each] = init.df_sing[each].astype(int)

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
                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                        # singles for that instructor tree
                        if inst2sing_tree[each].get(num) is None:
                            inst2sing_tree[each][num] = [data[contestant_col]]
                        if data[contestant_col] not in inst2sing_tree[each][num]:
                            inst2sing_tree[each][num].append(data[contestant_col])

    return inst2sing_tree


def pickDfs(ev, dance_dfs, inst_tree, floors, div, eventages_s, eventages_c, couples_per_floor):
    print()
    # l_keys = [0, 1, 2, 3, 4, 5]

    if div.count('T') == 0 and div.count('t') == 0:
        start = "A"
    elif dance_dfs.get("S") is not None:
        start = "S"
    elif dance_dfs.get("C") is not None:
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
                # Since Couples has a different possible key
                if poss_key[0] == "S":
                    prio_lvl_index = 2
                    lvlnames = init.eventlvlnames_s
                else:
                    prio_lvl_index = 1
                    lvlnames = init.eventlvlnames_c
                if prio_s[prio][prio_lvl_index] != "diff_l":
                    poss_key.append(prio_s[prio][prio_lvl_index])
                    all_poss.append(poss_key)
                else:  # If different level make a key with all possible levels
                    for lev in lvlnames:  # For all level keys
                        if lev != picked_keys[0][lev_index]:  # if not the same level, create a new possible key
                            poss_key.append(lev)
                            all_poss.append(poss_key)
                            poss_key = poss_key[:-1]
                iter += 1
            if div.count('A') != 0 or div.count('a') != 0:
                # Since Couples has a different possible key
                if poss_key[0] == "S":
                    prio_age_index = 3
                else:
                    prio_age_index = 2
                if len(all_poss) == 0:  # in case 'l' split is not part of this Event
                    all_poss.append(poss_key)
                if prio_s[prio][prio_age_index] != "diff_a":
                    for key in all_poss:
                        key.append(prio_s[prio][prio_age_index])
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
            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            for every in all_poss:
                if every not in picked_keys:  # add to picked list only if that key combo is not in already
                    print("Checking if", every, "can be added")
                    if getNode(inst_tree, every) == {}:  # Check if node is there
                        if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                            prio += 1
                        continue
                    # if added is a single
                    if every[0] == "S":
                        # Sanity check the levels in question
                        unique = findUnique(inst_tree, copyList(picked_keys), every)
                        count = findInstCount(inst_tree, every)
                        # find # of 'singles' rooms
                        sfloors = 0
                        for room in picked_keys:
                            if room[0] == "S":
                                sfloors += 1
                        sfloors += 1
                        # if (unique >= (len(picked_keys) * couples_per_floor)-3) and (count > (couples_per_floor-2)):
                        if unique >= (sfloors * couples_per_floor) - 2:
                            picked_keys.append(every)
                            picked = True
                        else:
                            unideal.append([every, count])
                    else:  # if not a single
                        count = findContestantCount(dance_dfs, every, ev)
                        if count[0] >= couples_per_floor - 2:
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
                    for lev in init.eventlvlnames_c:  # duplicate current all_poss per different level
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
            if 'n' in div or "N" in div:
                all_poss.append(poss_key)
            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            print("Checking all possible keys", all_poss)
            for every in all_poss:
                if every not in picked_keys:  # add to picked list only if that key combo is not in already
                    print("Checking if", every, "can be added")
                    if getNode(inst_tree, every) == {}:  # Check if node is there
                        if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                            prio += 1
                        continue
                    # if added is a single
                    if every[0] == "S":
                        # Sanity check the levels in question
                        unique = findUnique(inst_tree, copyList(picked_keys), every)
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


def copyList(copy):

    cop = []
    for key in copy:
        cop.append(key[:])
    return cop


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
            while list_index < heats_count:

                # Check if heat has this division
                if div not in heats[list_index].getDiv():
                    list_index += 1
                    continue
                # Check if heat has holes
                if sum(heats[list_index].getHoles()) == 0:
                    list_index += 1
                    continue
                # Find room with holes, and see if it matches
                roomids = []
                for i, room_info in enumerate(heats[list_index].getDiv()):
                    if room_info == div:
                        roomids.append(i)  # Note will only return
                if roomids == []:
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
                    continue

                # If couple place it
                for roomid in roomids:
                    if data["type id"] == "C" and len(heats[list_index].getRoster()[roomid]) < couples_per_floor:
                        candidate = data.to_frame().T
                        candidate = candidate.reset_index(drop=True)
                        heats[list_index].addEntry(candidate, roomid)
                        nobackfill = False
                        print("Candidate", candidate.loc[0, "Lead Dancer #"], candidate.loc[0, "Follow Dancer #"], "Backfilled to", list_index, div, "Room", roomid)
                        backfill_df.loc[(backfill_df.loc[:, "Lead Dancer #"] == candidate.loc[0, "Lead Dancer #"]) &
                                        (backfill_df.loc[:, "Follow Dancer #"] == candidate.loc[0, "Follow Dancer #"]), ev] = candidate.loc[0, ev] - 1
                        break
                # If backfilled a hole, break the loop for this backfill entyr
                if not nobackfill:
                    break
                else:  # if not backfilled look in another heat
                    list_index += 1
                    continue

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
                for roomid in roomids:
                    if (not found) and len(heats[list_index].getRoster()[roomid]) < couples_per_floor:
                        nobackfill = False
                        # Set candidate to this single/inst match
                        candidate = data.to_frame().T
                        candidate = candidate.reset_index(drop=True)
                        if data["type id"] != "C":
                            instructor_data = init.df_inst[init.df_inst["Dancer #"] == inst].reset_index(drop=True)
                            candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                            candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                            candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                        print("Candidate", candidate.loc[0, contestant_col], "Backfilled to", list_index, div)
                        heats[list_index].addEntry(candidate, roomid)
                        # Remove the placed candidate from the df, or -1 if multi-entry
                        backfill_df.loc[(backfill_df.loc[:, contestant_col] == candidate.loc[0, contestant_col]) &
                                        (dance_df["type id"] != "C"), ev] = candidate.loc[0, ev] - 1
                        break
                list_index += 1
                if not found:
                    break
        backfill_df = backfill_df[backfill_df.loc[:, ev] != 0]

    if not backfill_df[backfill_df.loc[:, ev] < 0].empty:
        raise Exception("Negatyive values in df", div)

    updateDanceDfs(init.dance_dfs, backfill_df, div, div)
    return


def setupSinglesEvent(eventrow, contestant_data):
    div = eventrow.loc[:, 'Event Divisions'][0]

    # Use Combine Age Brackets field to set up dance dfs tree
    combineage_s = eventrow.loc[:, 'Combine Age Brackets'][0]
    if type(combineage_s) == float:  # if blank
        init.eventages_s = init.age_brackets.copy()
    else:
        combineage = eventrow.loc[:, 'Combine Age Brackets'][0].split(";")
        eventage = []
        for age in init.age_brackets:
            eventage.append([age])
        for combo in combineage:
            first = int(combo[0])
            last = int(combo[2])
            if first > last:  # Swap them if entered incorrectly
                first = last
                last = first
            if first > len(init.age_brackets) or last > len(init.age_brackets):
                raise Exception("Combine Age Brackets for", init.ev, "has a number outside", "1-" + str(len(init.age_brackets)))
            for j in range(last - first):
                eventage[first + j - 1].clear()
        for entry in eventage:
            if entry != []:
                init.eventages_s.append(entry[0])

    # Use Combine Levels field to set up dance dfs tree for Singles
    eventlvls_s = []
    combinelvls_s = eventrow.loc[:, 'Combine Levels'][0]
    if type(combinelvls_s) == float:  # if blank
        init.eventlvlnames_s = init.lvls.copy()
    else:
        combinelvl = eventrow.loc[:, 'Combine Levels'][0].split(";")
        lvlnames_s = []
        lvlcombos_s = []
        firsts = []
        lasts = []
        for lvl in init.lvls:
            lvlnames_s.append([lvl])
        for dfs in contestant_data["Single"]:
            lvlcombos_s.append([dfs])
        for combo in combinelvl:
            concat_data_s = []
            first = combo[0:2]
            firsts.append(first)
            first = init.lvl_conversion[init.lvls.index(first)]
            last = combo[3:]
            lasts.append(last)
            last = init.lvl_conversion[init.lvls.index(last)]
            if first > last:  # Swap them if entered incorrectly
                first = last
                firsts[-1] = lasts[-1]
                last = first
                lasts[-1] = firsts[-1]
            if last - 1 >= len(init.lvls) or first < 0:
                raise Exception("Combine Levels for", init.ev, "has a number outside 1-6")
            for j in range(last - first):
                lvlnames_s[first + j].clear()
                concat_data_s.append(contestant_data['Single'][first + j])
                lvlcombos_s[first + j].clear()
            concat_data_s.append(contestant_data['Single'][last])
            lvlcombos_s[last] = [pd.concat(concat_data_s)]
        for i, entry in enumerate(lvlnames_s):
            if entry != []:
                if entry[0] in lasts:
                    tmp = entry[0]
                    entry[0] = firsts[lasts.index(entry[0])] + "-" + entry[0]
                    # del firsts[lasts.index(tmp)]
                init.eventlvlnames_s.append(entry[0])
        for i, entry in enumerate(lvlcombos_s):
            if entry != []:
                eventlvls_s.append(entry[0])
        contestant_data["Single"] = eventlvls_s

    shell_s = {"Lead": {}, "Follow": {}}
    for Single, lvl in zip(contestant_data['Single'], init.eventlvlnames_s):
        Single = Single[Single[init.ev] > 0]
        # Need this to get around Lead/Follow key being deleted when combining tree branches
        # if (div.count('S') == 0 and div.count('s') == 0) or (div.count('T') == 0 and div.count('t') == 0):
        #     init.dance_dfs["S"]["Lead"] = {}
        #     init.dance_dfs["S"]["Follow"] = {}
        #     shell_s["Lead"] = {}
        #     shell_s["Follow"] = {}
        init.dance_dfs["S"]["Lead"][lvl] = {}
        init.dance_dfs["S"]["Follow"][lvl] = {}
        shell_s["Lead"][lvl] = {}
        shell_s["Follow"][lvl] = {}
        if not Single.empty:
            if not Single[Single['Lead/Follow'] == 'Lead'].empty:
                df = Single[(Single['Lead/Follow'] == 'Lead') | (Single['Lead/Follow'] == 'L')]
                df.loc[:, 'type id'] = 'L'
                df = df.rename(columns={'First Name': 'Lead First Name', 'Last Name': 'Lead Last Name',
                                        'Dancer #': 'Lead Dancer #', "Age": "Lead Age"})
                df['Follow First Name'] = ''
                df['Follow Last Name'] = ''
                df['Follow Age'] = ''
                df['Follow Dancer #'] = ''
                df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age", "Follow Age",
                         "Instructor Dancer #'s",
                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School', init.ev]]
                for i, age in enumerate(init.eventages_s):
                    # SLice so that it is inside age bracket
                    if i == 0:  # Set bounds of age bracket
                        lower = 1
                        upper = age
                    else:
                        lower = init.eventages_s[i - 1] + 1
                        upper = age
                    # Split the df based on which age is lower and then add them together at the end
                    sliced_l = df[(lower <= df["Lead Age"]) & (df["Lead Age"] <= upper)]
                    shell_s["Lead"][lvl][age] = sliced_l
            else:
                for i, age in enumerate(init.eventages_s):
                    init.dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                    shell_s["Lead"][lvl][age] = pd.DataFrame()
                    # shell_i["Lead"][lvl][age] = pd.DataFrame()

            if not Single[Single['Lead/Follow'] == 'Follow'].empty:

                df2 = Single[Single['Lead/Follow'] == 'Follow']
                df2.loc[:, 'type id'] = 'F'
                df2 = df2.rename(columns={'First Name': 'Follow First Name', 'Last Name': 'Follow Last Name',
                                          'Dancer #': 'Follow Dancer #', "Age": "Follow Age"})
                df2['Lead First Name'] = ''
                df2['Lead Last Name'] = ''
                df2['Lead Age'] = ''
                df2['Lead Dancer #'] = ''
                df2 = df2[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age",
                           "Instructor Dancer #'s",
                           'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age', 'Level', 'School',
                           init.ev]]
                for i, age in enumerate(init.eventages_s):
                    # SLice Couple so that it is inside age bracket
                    if i == 0:  # Set bounds of age bracket
                        lower = 1
                        upper = age
                    else:
                        lower = init.eventages_s[i - 1] + 1
                        upper = age
                    # Split the df based on which age is lower and then add them together at the end
                    sliced_f = df2[(lower <= df2["Follow Age"]) & (df2["Follow Age"] <= upper)]
                    shell_s["Follow"][lvl][age] = sliced_f
            else:
                for i, age in enumerate(init.eventages_s):
                    init.dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                    shell_s["Follow"][lvl][age] = pd.DataFrame()
        else:
            for i, age in enumerate(init.eventages_s):
                init.dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                init.dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                shell_s["Follow"][lvl][age] = pd.DataFrame()
                shell_s["Lead"][lvl][age] = pd.DataFrame()

        # Add together dfs based on the division metrics of this event
        if div.count('A') == 0 and div.count('a') == 0:
            # Lead concat
            for i, key in enumerate(shell_s["Lead"][lvl].keys()):
                if i == 0:
                    tmp = shell_s["Lead"][lvl][key]
                    continue
                tmp = pd.concat([tmp, shell_s["Lead"][lvl][key]])
            shell_s["Lead"][lvl] = tmp

            # Follow Concat
            for i, key in enumerate(shell_s["Follow"][lvl].keys()):
                if i == 0:
                    tmp = shell_s["Follow"][lvl][key]
                    continue
                tmp = pd.concat([tmp, shell_s["Follow"][lvl][key]])
            shell_s["Follow"][lvl] = tmp

    # Combine all levels if needed
    if div.count('L') == 0 and div.count('l') == 0:
        # Lead Concat
        for i, lvl in enumerate(shell_s["Lead"].keys()):
            if i == 0:
                tmp = shell_s["Lead"][lvl]
                continue
            if type(tmp) is dict:
                for subkey in tmp.keys():
                    tmp[subkey] = pd.concat([tmp[subkey], shell_s["Lead"][lvl][subkey]])
            else:
                tmp = pd.concat([tmp, shell_s["Lead"][lvl]])
        shell_s["Lead"] = tmp

        # Follow Concat
        for i, lvl in enumerate(shell_s["Follow"].keys()):
            if i == 0:
                tmp = shell_s["Follow"][lvl]
                continue
            if type(tmp) is dict:
                for subkey in tmp.keys():
                    tmp[subkey] = pd.concat([tmp[subkey], shell_s["Follow"][lvl][subkey]])
            else:
                tmp = pd.concat([tmp, shell_s["Follow"][lvl]])
        shell_s["Follow"] = tmp

    # if event Singles should be combined
    if (div.count('S') == 0 and div.count('s') == 0) or (div.count('T') == 0 and div.count('t') == 0):
        # Singles Lead/Follow Concat
        for i, key in enumerate(shell_s.keys()):
            if i == 0:
                tmp = shell_s[key]
                continue
            if type(tmp) is dict:  # Go down the tree and combine the corresponding N nodes
                for subkey in tmp.keys():
                    if type(tmp[subkey]) is dict:
                        for subkey2 in tmp[subkey].keys():
                            tmp[subkey][subkey2] = pd.concat(
                                [tmp[subkey][subkey2], shell_s[key][subkey][subkey2]])
                    else:
                        tmp[subkey] = pd.concat([tmp[subkey], shell_s[key][subkey]])
            else:
                tmp = pd.concat([tmp, shell_s[key]])
            shell_s = tmp
    init.dance_dfs["S"] = shell_s


def setupCouplesEvent(eventrow, contestant_data):
    div = eventrow.loc[:, 'Event Divisions'][0]
    
    # Use Combine Age Brackets field to set up dance dfs tree
    combineage_c = eventrow.loc[:, 'Combine Age Brackets'][0]
    if type(combineage_c) == float:  # if blank
        init.eventages_c = init.age_brackets.copy()
    else:
        combineage = eventrow.loc[:, 'Combine Age Brackets'][0].split(";")
        eventage = []
        for age in init.age_brackets:
            eventage.append([age])
        for combo in combineage:
            first = int(combo[0])
            last = int(combo[2])
            if first > last:  # Swap them if entered incorrectly
                first = last
                last = first
            if first > len(init.age_brackets) or last > len(init.age_brackets):
                raise Exception("Combine Age Brackets for", init.ev, "has a number outside", "1-" + str(len(init.age_brackets)))
            for j in range(last - first):
                eventage[first + j - 1].clear()
        for entry in eventage:
            if entry != []:
                init.eventages_c.append(entry[0])

    # Use Combine Levels field to set up dance dfs tree for Couples
    eventlvls_c = []
    combinelvls_c = eventrow.loc[:, 'Combine Levels'][0]
    if type(combinelvls_c) == float:  # if blank
        init.eventlvlnames_c = init.lvls.copy()
    else:
        combinelvl = eventrow.loc[:, 'Combine Levels'][0].split(";")
        lvlnames_c = []
        lvlcombos_c = []
        firsts = []
        lasts = []
        for lvl in init.lvls:
            lvlnames_c.append([lvl])
        for dfs in contestant_data["Couple"]:
            lvlcombos_c.append([dfs])
        for combo in combinelvl:
            concat_data_c = []
            first = combo[0:2]
            firsts.append(first)
            first = init.lvl_conversion[init.lvls.index(first)]
            last = combo[3:]
            lasts.append(last)
            last = init.lvl_conversion[init.lvls.index(last)]
            if first > last:  # Swap them if entered incorrectly
                first = last
                firsts[-1] = lasts[-1]
                last = first
                lasts[-1] = firsts[-1]
            if last - 1 >= len(init.lvls) or first < 0:
                raise Exception("Combine Levels for", init.ev, "has a number outside 1-6")
            for j in range(last - first):
                lvlnames_c[first + j].clear()
                concat_data_c.append(contestant_data['Couple'][first + j])
                lvlcombos_c[first + j].clear()
            print(last)
            concat_data_c.append(contestant_data['Couple'][last])
            lvlcombos_c[last] = [pd.concat(concat_data_c)]
        for i, entry in enumerate(lvlnames_c):
            if entry != []:
                if entry[0] in lasts:
                    tmp = entry[0]
                    entry[0] = firsts[lasts.index(entry[0])] + "-" + entry[0]
                    # del firsts[lasts.index(tmp)]
                init.eventlvlnames_c.append(entry[0])
        for i, entry in enumerate(lvlcombos_c):
            if entry != []:
                eventlvls_c.append(entry[0])
        contestant_data["Couple"] = eventlvls_c
    shell_c = {}

    for Couple, lvl in zip(contestant_data['Couple'], init.eventlvlnames_c):
        Couple = Couple[Couple[init.ev] > 0]
        init.dance_dfs["C"][lvl] = {}
        shell_c[lvl] = {}
        if not Couple.empty:  # Couple df operations
            Couple['type id'] = 'C'
            Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Lead Age',
                             'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age',
                             'Level', 'School', init.ev]]
            if div.count('t') == 0 or div.count("T") == 0:
                Couple["Instructor Dancer #'s"] = ''
            for i, age in enumerate(init.eventages_c):
                # Slice Couple so that it is inside age bracket
                if i == 0:  # Set bounds of age bracket
                    lower = 1
                    upper = age
                else:
                    lower = init.eventages_c[i - 1] + 1
                    upper = age
                # Split the df based on which age is lower and then add them together at the end
                sliced_f = Couple[Couple["Lead Age"] >= Couple["Follow Age"]]
                sliced_f = sliced_f[(lower <= sliced_f["Follow Age"]) & (sliced_f["Follow Age"] <= upper)]
                sliced_l = Couple[Couple["Lead Age"] < Couple["Follow Age"]]
                sliced_l = sliced_l[(lower <= sliced_l["Lead Age"]) & (sliced_l["Lead Age"] <= upper)]
                shell_c[lvl][age] = pd.concat([sliced_l, sliced_f])
        else:
            for i, age in enumerate(init.eventages_c):
                init.dance_dfs["C"][lvl][age] = pd.DataFrame()
                shell_c[lvl][age] = pd.DataFrame()

    # Add together dfs based on the division metrics of this event
    if div.count('A') == 0 and div.count('a') == 0:
        # Couple Concat
        for lvl in shell_c.keys():
            for i, key in enumerate(shell_c[lvl].keys()):
                if i == 0:
                    tmp = shell_c[lvl][key]
                    continue
                tmp = pd.concat([tmp, shell_c[lvl][key]])
            shell_c[lvl] = tmp

    # Combine all levels if needed
    if div.count('L') == 0 and div.count('l') == 0:
        for i, key in enumerate(shell_c.keys()):
            if i == 0:
                tmp = shell_c[key]
                continue
            if type(tmp) is dict:
                for subkey in tmp.keys():
                    tmp[subkey] = pd.concat([tmp[subkey], shell_c[key][subkey]])
            else:
                tmp = pd.concat([tmp, shell_c[key]])
        shell_c = tmp

    # put shell into df
    init.dance_dfs["C"] = shell_c



