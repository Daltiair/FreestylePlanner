import pandas as pd
import os
import random
import init
from init import buildInstTree, deleteEmpty, buildInst2SingTree, checkheat
from methods import partitionData, sliceDfs, PoachPrevHeatsSingles, PoachPrevHeatsCouples, findUnique, findContestantCount, findInstCount, backfill
from conflict import resolveConflictSingles, resolveConflictCouples, resetSolutionLogic
from init import updateDanceDfs, getNode, buildInstTree, instructorOperation
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ConflictItemCouple
from output import buildEvent, makeHeatDict, buildEventfast

'''
    Loop through all dances in the heats dictionary depth first create all heats and store them
    inside a list at the the lowest order dictionary
    ex: {'Rhythm': {'Closed': {"Closed ChaCha" : [Heat1, Heat2, ..., Heatn]
                               "Closed East Coast Swing" : [Heat1, Heat2, ..., Heatn]}
                    .
                    .
                    .
                  }
        }
    '''
def Selection(heats):
    # Slice Contestant dfs based on levels
    contestant_data = sliceDfs(init.df_sing, init.df_coup)

    # Used for easy access to dfs sliced by level
    AB = 0
    FB = 1
    AS = 2
    FS = 3
    AG = 4
    FG = 5

    tot_current_heats = 0  # Current total heats made
    # For each genre
    genres = list(heats.keys())
    for each in genres:
        # For each syllabus in genre
        syllabus = list(heats[each].keys())
        for every in syllabus:
            # For each event in that syllabus event
            events = list(heats[each][every].keys())
            if events == []:
                continue
            for ev in events:
                init.ev = ev
                init.dance_dfs = {"C": {}, "S": {"Lead": {}, "Follow": {}}}
                l_keys = [AB, FB, AS, FS, AG, FG]
                dance_heat_count = 0  # current Heat count for this dance event
                tot_holes = []  # number of open spaces in the heats made to reach the maximum number per heat
# ------------------------------------------ Build dfs for Selection ---------------------------------------------------
                # Slice dfs based on participation in dance event 'ev', level, type, age
                # Add identifier column Couple dfs and reformat to be ready for heat sheet print, Singles done later
                eventrow = init.df_cat.loc[init.df_cat['Dance'] == ev].reset_index(drop=True)
                couples_per_floor = int(eventrow.loc[:, "Couples Per Floor"][0])
                acceptablecouples = int(couples_per_floor/2)+2
                div = eventrow.loc[:, 'Event Divisions'][0]
                if type(div) == float:  # if blank
                    div = ["n"]
                else:
                    div = eventrow.loc[:, 'Event Divisions'][0].split(";")

                # Use Combine Age Brackets field to set up dance dfs tree
                eventages_s = []
                combineage_s = eventrow.loc[:, 'Combine Age Brackets'][0]
                if type(combineage_s) == float:  # if blank
                    eventages_s = init.age_brackets.copy()
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
                            raise Exception("Combine Age Brackets for", ev, "has a number outside", "1-" + str(len(init.age_brackets)))
                        for j in range(last-first):
                            eventage[first+j-1].clear()
                    for entry in eventage:
                        if entry != []:
                            eventages_s.append(entry[0])
                # Use Combine Age Brackets field to set up dance dfs tree
                eventages_c = []
                combineage_c = eventrow.loc[:, 'Combine Age Brackets'][0]
                if type(combineage_c) == float:  # if blank
                    eventages_c = init.age_brackets.copy()
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
                            raise Exception("Combine Age Brackets for", ev, "has a number outside", "1-" + str(len(init.age_brackets)))
                        for j in range(last - first):
                            eventage[first + j - 1].clear()
                    for entry in eventage:
                        if entry != []:
                            eventages_c.append(entry[0])

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
                        if last-1 >= len(init.lvls) or first < 0:
                            raise Exception("Combine Levels for", ev, "has a number outside 1-6")
                        for j in range(last - first):
                            lvlnames_c[first + j].clear()
                            concat_data_c.append(contestant_data['Couple'][first + j])
                            lvlcombos_c[first + j].clear()
                        concat_data_c.append(contestant_data['Couple'][last])
                        lvlcombos_c[last] = [pd.concat(concat_data_c)]
                    for i, entry in enumerate(lvlnames_c):
                        if entry != []:
                            if entry[0] in lasts:
                                tmp = entry[0]
                                entry[0] = firsts[lasts.index(entry[0])] + "-" + entry[0]
                                del firsts[lasts.index(tmp)]
                            init.eventlvlnames_c.append(entry[0])
                    for i, entry in enumerate(lvlcombos_c):
                        if entry != []:
                            eventlvls_c.append(entry[0])
                    contestant_data["Couple"] = eventlvls_c

                # Use Combine Levels field to set up dance dfs tree for Singles
                eventlvls_s = []
                combinelvls_s = eventrow.loc[:, 'Combine Levels'][0]
                if type(combinelvls_s) == float:  # if blank
                    init.eventlvlnames_s = init.lvls.copy()
                else:
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
                            raise Exception("Combine Levels for", ev, "has a number outside 1-6")
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
                                del firsts[lasts.index(tmp)]
                            init.eventlvlnames_s.append(entry[0])
                    for i, entry in enumerate(lvlcombos_s):
                        if entry != []:
                            eventlvls_s.append(entry[0])
                    contestant_data["Single"] = eventlvls_s

                # Build Couples df for this event broken down by all metrics
                if ev in init.df_coup.columns:
                    shell_c = {}
                    for Couple, lvl in zip(contestant_data['Couple'], init.eventlvlnames_c):
                        Couple = Couple[Couple[ev] > 0]
                        init.dance_dfs["C"][lvl] = {}
                        shell_c[lvl] = {}
                        if not Couple.empty:  # Couple df operations
                            Couple['type id'] = 'C'
                            Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Lead Age',
                                             'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age',
                                             'Level', 'School', ev]]
                            if div.count('t') == 0 or div.count("T") == 0:
                                Couple["Instructor Dancer #'s"] = ''
                            for i, age in enumerate(eventages_c):
                                # Slice Couple so that it is inside age bracket
                                if i == 0:  # Set bounds of age bracket
                                    lower = 18
                                    upper = age
                                else:
                                    lower = eventages_c[i - 1] + 1
                                    upper = age
                                # Split the df based on which age is lower and then add them together at the end
                                sliced_f = Couple[Couple["Lead Age"] >= Couple["Follow Age"]]
                                sliced_f = sliced_f[(lower <= sliced_f["Follow Age"]) & (sliced_f["Follow Age"] <= upper)]
                                sliced_l = Couple[Couple["Lead Age"] < Couple["Follow Age"]]
                                sliced_l = sliced_l[(lower <= sliced_l["Lead Age"]) & (sliced_l["Lead Age"] <= upper)]
                                shell_c[lvl][age] = pd.concat([sliced_l, sliced_f])
                        else:
                            for i, age in enumerate(eventages_c):
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
                else:
                    del init.dance_dfs["C"]

                if ev in init.df_sing.columns:
                    shell_s = {"Lead": {}, "Follow": {}}
                    # shell_i = {"Lead": {}, "Follow": {}}
                    for Single, lvl in zip(contestant_data['Single'], init.eventlvlnames_s):
                        Single = Single[Single[ev] > 0]
                        init.dance_dfs["S"]["Lead"][lvl] = {}
                        init.dance_dfs["S"]["Follow"][lvl] = {}
                        shell_s["Lead"][lvl] = {}
                        # shell_i["Lead"][lvl] = {}
                        shell_s["Follow"][lvl] = {}
                        # shell_i["Follow"][lvl] = {}
                        if not Single.empty:
                            if not Single[Single['Lead/Follow'] == 'Lead'].empty:
                                df = Single[(Single['Lead/Follow'] == 'Lead') | (Single['Lead/Follow'] == 'L')]
                                df.loc[:,'type id'] = 'L'
                                df = df.rename(columns={'First Name': 'Lead First Name', 'Last Name': 'Lead Last Name',
                                                        'Dancer #': 'Lead Dancer #', "Age": "Lead Age"})
                                df['Follow First Name'] = ''
                                df['Follow Last Name'] = ''
                                df['Follow Age'] = ''
                                df['Follow Dancer #'] = ''
                                df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age", "Follow Age", "Instructor Dancer #'s",
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]
                                for i, age in enumerate(eventages_s):
                                    # SLice so that it is inside age bracket
                                    if i == 0:  # Set bounds of age bracket
                                        lower = 18
                                        upper = age
                                    else:
                                        lower = eventages_s[i - 1] + 1
                                        upper = age
                                    # Split the df based on which age is lower and then add them together at the end
                                    sliced_l = df[(lower <= df["Lead Age"]) & (df["Lead Age"] <= upper)]
                                    shell_s["Lead"][lvl][age] = sliced_l
                            else:
                                for i, age in enumerate(eventages_s):
                                    init.dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                                    shell_s["Lead"][lvl][age] = pd.DataFrame()
                                    # shell_i["Lead"][lvl][age] = pd.DataFrame()

                            if not Single[Single['Lead/Follow'] == 'Follow'].empty:

                                df2 = Single[Single['Lead/Follow'] == 'Follow']
                                df2.loc[:,'type id'] = 'F'
                                df2 = df2.rename(columns={'First Name': 'Follow First Name', 'Last Name': 'Follow Last Name',
                                                    'Dancer #': 'Follow Dancer #', "Age": "Follow Age"})
                                df2['Lead First Name'] = ''
                                df2['Lead Last Name'] = ''
                                df2['Lead Age'] = ''
                                df2['Lead Dancer #'] = ''
                                df2 = df2[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age" , "Instructor Dancer #'s",
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age', 'Level', 'School', ev]]
                                for i, age in enumerate(eventages_s):
                                    # SLice Couple so that it is inside age bracket
                                    if i == 0:  # Set bounds of age bracket
                                        lower = 18
                                        upper = age
                                    else:
                                        lower = eventages_s[i - 1] + 1
                                        upper = age
                                    # Split the df based on which age is lower and then add them together at the end
                                    sliced_f = df2[(lower <= df2["Follow Age"]) & (df2["Follow Age"] <= upper)]
                                    shell_s["Follow"][lvl][age] = sliced_f
                            else:
                                for i, age in enumerate(eventages_s):
                                    init.dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                                    shell_s["Follow"][lvl][age] = pd.DataFrame()
                                    # shell_i["Follow"][lvl][age] = pd.DataFrame()
                        else:
                            for i, age in enumerate(eventages_s):
                                init.dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                                init.dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                                shell_s["Follow"][lvl][age] = pd.DataFrame()
                                shell_s["Lead"][lvl][age] = pd.DataFrame()
                        # Add together dfs based on the division metrics of this event
                        if div.count('A') == 0 and div.count('a') == 0:
                            # Lead concat
                            for lvl in shell_s["Lead"].keys():
                                for i, key in enumerate(shell_s["Lead"][lvl].keys()):
                                    if i == 0:
                                        tmp = shell_s["Lead"][lvl][key]
                                        continue
                                    tmp = pd.concat([tmp, shell_s["Lead"][lvl][key]])
                                shell_s["Lead"][lvl] = tmp

                            # Follow Concat
                            for lvl in shell_s["Follow"].keys():
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

                        # put shells into df
                        init.dance_dfs["S"] = shell_s
                else:
                    del init.dance_dfs["S"]

                # If Couples and Singles need to be combined
                if div.count('T') == 0 and div.count('t') == 0 and (init.dance_dfs.get("S") is not None) and (init.dance_dfs.get("C") is not None):
                    for i, key in enumerate(init.dance_dfs.keys()):
                        if i == 0:
                            tmp = init.dance_dfs[key]
                            continue
                        if type(tmp) is dict:  # Go down the tree and combine the corresponding N nodes
                            for subkey in tmp.keys():
                                if type(tmp[subkey]) is dict:
                                    for subkey2 in tmp[subkey].keys():
                                        tmp[subkey][subkey2] = pd.concat([tmp[subkey][subkey2], init.dance_dfs[key][subkey][subkey2]])
                                else:
                                    tmp[subkey] = pd.concat([tmp[subkey], init.dance_dfs[key][subkey]])
                        else:
                            tmp = pd.concat([tmp, init.dance_dfs[key]])
                    init.dance_dfs["A"] = tmp
                    del init.dance_dfs["S"]
                    del init.dance_dfs["C"]

                    del shell_s
                    del shell_c

                # # Set Holes
                # for key in keys:
                #     if init.dance_dfs_dict_s[key].empty:
                #         tot_holes.append(-1)
                #     else:
                #         tot_holes.append(0)

                # Check if current dfs are empty, and remove them
                deleteEmpty(init.dance_dfs)
                # if both Pools are totally empty continue
                # In this case it would only happen if there were no entries to current dance 'ev'
                floors = eventrow.loc[:, 'Floors'][0]
                heat_list = HeatList([], floors, couples_per_floor, eventages_s, eventages_c, init.eventlvlnames_s, init.eventlvlnames_c)  # list of individual heats for the current dance 'ev'
                if len(init.dance_dfs) == 0:
                    print("No data in this category", ev)
                    heat_list = -1
                    continue
                pre_dance_dfs = init.dance_dfs.copy()
                init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                init.inst2sing_tree = buildInst2SingTree(init.dance_dfs, {}, ev)
                pre_inst_tree = init.inst_tree.copy()
# ---------------------------------------------- Selection Process -----------------------------------------------------
                if init.dance_dfs.get("S") is None:
                    singles_empty = True
                else:
                    singles_empty = False  # True when all singles are in heats for this event 'ev'
                if init.dance_dfs.get("C") is None:
                    couples_empty = True
                else:
                    couples_empty = False  # True when all singles are in heats for this event 'ev'
                split_mode = False
                while init.dance_dfs.get("D") is None:  # while there are contestants in the dfs still
                    heat_roster = []  # holds full contestant data for a heat, each element is a list for a dance floor
                    fin_rooms = []  # marks a room as finished with a 1
                    instructors_in_heat = []  # Holds instructor numbers for quick reference
                    singles_in_heat = []  # Holds contestant number for quick reference
                    couples_in_heat = []  # Holds Couples number for quick ref.
                    # couples_in_heat format [[1 Lead #,1 Follow #,...,N Follow #],...[1 Lead #,1 Follow #,..., N Follow #]]
                    deleteEmpty(init.dance_dfs)
                    init.inst_tree = buildInstTree(init.dance_dfs, {}, init.ev)
                    floor_info = pickDfs(ev, init.dance_dfs, init.inst_tree, floors, div, eventages_s, eventages_c, couples_per_floor)
                    for floor in range(floors):
                        heat_roster.append([])
                        instructors_in_heat.append([])
                        singles_in_heat.append([])
                        couples_in_heat.append([])
                        fin_rooms.append(0)
                    heat_finished = False
                    # selection_dfs = []
                    s_floors = []
                    sfin_rooms = []
                    c_floors = []
                    cfin_rooms = []
                    a_floors = []
                    afin_rooms = []
                    # Separate out singles and couple assigned floors
                    if 't' in div or 'T' in div:
                        for floor in floor_info:
                            if floor[0] == "S":
                                s_floors.append(floor)
                                sfin_rooms.append(0)
                            elif floor[0] == "C":
                                c_floors.append(floor)
                                cfin_rooms.append(0)
                            elif floor[0] == "A":
                                a_floors.append(floor)
                                afin_rooms.append(0)
                    heat_key = each + '-' + every + '-' + ev + '-' + str(len(heat_list.getRostersList()))
                    log = ConflictLog(floor_info)  # make conflict log for this heat
                    # Create list for divison information for heat, floor_info is used for selection only
                    heat_floors = []
                    for info in floor_info:
                        heat_floors.append(info.copy())
                    if len(floor_info) < floors:
                        split_mode = True
                        # Fill in unassigned rooms
                        for floor in range(floors-len(floor_info)):
                            heat_floors.append([])
                    heat = Heat(heat_key, heat_floors, heat_roster, [0 for x in range(floors)], singles_in_heat, instructors_in_heat, couples_in_heat)
                    while not heat_finished:
                        # ---------------------------------------------- Singles ---------------------------------------
                        heat_holes = []
                        for place in floor_info:
                            heat_holes.append(0)
                        # Make Instructors for heat list that will change based on placed contestants and instructors
                        dance_df = []
                        inst_tree_nodes = []
                        inst2sing_tree_nodes = []
                        instructors_available_for_heat = []
                        init.starting_instructors_for_heat = []
                        for roomid, info in enumerate(s_floors):
                            for i, key in enumerate(info):
                                if i == 0:
                                    tmp = init.dance_dfs[key]
                                    tmp2 = init.inst_tree[key]
                                    tmp3 = init.inst2sing_tree[key]
                                elif type(tmp) is dict:
                                    try:
                                        tmp = tmp[key]
                                        tmp2 = tmp2[key]
                                        tmp3 = tmp3[key]
                                    except:
                                        print(info, "Division removed already, likely due to split where this division is empty")
                                        tmp = pd.DataFrame()
                                        tmp2 = pd.DataFrame()
                                        tmp3 = pd.DataFrame()
                            dance_df.append(tmp)
                            inst_tree_nodes.append(tmp2)
                            inst2sing_tree_nodes.append(tmp3)
                            instructors_available_for_heat.append(list(tmp2.keys()))
                            init.starting_instructors_for_heat.append(list(tmp2.keys()))
                        selection_finished = False
                        print("Event " + ev + ", Heat number: " + str(heat_list.getHeatCount()))
                        print(floor_info)
                        print()
                        while not selection_finished:
                            if len(s_floors) == 0:  # If no singles move to couples selection
                                break
                            for roomid, room_info in enumerate(s_floors):  # For each ballroom make 1 instructor/single pair
                                print()
                                print('Selecting for room', roomid, room_info, heat_key)
                                if sfin_rooms[roomid] > 0:  # if room is filled or declared full, continue on
                                    print("Room finished, fin code", sfin_rooms[roomid])
                                    continue
                                placed = False  # Set when a valid instructor/single pair is placed
                                failed = False
                                # instreload = False
                                consecutive = 0  # Stops infinite loops on failed attempts to add candidate to the heat
                                # init.solved = 0  # counts how many resolveConflict() calls for this pair search
                                # init.nsolved = 0  # counts how many resolveConflict() calls for this pair search
                                while (not placed) and not (sfin_rooms[roomid] > 0):  # Find a viable single/inst match
                                    # print(instructors_available_for_heat[roomid])
                                    try:
                                        inst = random.choice(instructors_available_for_heat[roomid])  # get random instructor, will throw error if list at index is empty
                                    except:
                                        print("List empty?")
                                    instructor_taken = False
                                    for selection in instructors_in_heat:
                                        if instructor_taken:
                                            break
                                        if selection.count(inst) > 0:  # Check if instructor is being used in heat
                                            instructor_taken = True
                                            break
                                    if instructor_taken:
                                        # cons = getContestantConflictList(dance_df[roomid], inst, singles_in_heat)
                                        log.addConflict(ConflictItemSingle(1, inst), roomid)
                                        consecutive += 1
                                    else:  # Find a single to pair with this instructor
                                        found = False
                                        # Loop over each row in the df for this level
                                        df_shuffled = dance_df[roomid].sample(frac=1)
                                        for row, entry in df_shuffled.iterrows():
                                            next_contestant = False
                                            if found:
                                                break
                                            # Set column variables based on single type
                                            if entry["type id"] == "L":
                                                contestant_col = "Lead Dancer #"
                                                inst_col = "Follow Dancer #"
                                                inst_fname = "Follow First Name"
                                                inst_lname = "Follow Last Name"
                                            elif entry["type id"] == "F":
                                                contestant_col = "Follow Dancer #"
                                                inst_col = "Lead Dancer #"
                                                inst_fname = "Lead First Name"
                                                inst_lname = "Lead Last Name"
                                            else:
                                                raise Exception("Type id for " + entry + " is invalid")
                                            # Loop over the instructor list for the contestant row
                                            for num in entry["Instructor Dancer #'s"]:
                                                if num == inst:
                                                    for i, rost in enumerate(singles_in_heat):
                                                        if rost.count(entry[contestant_col]) > 0:
                                                            next_contestant = True
                                                    if not next_contestant:
                                                        # Set candidate to this single/inst match
                                                        candidate = entry.to_frame().T
                                                        candidate = candidate.reset_index(drop=True)
                                                        instructor_data = init.df_inst[init.df_inst["Dancer #"] == inst].reset_index(drop=True)
                                                        candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                                                        candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                                                        candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                                                        found = True
                                                        break
                                        if found:
                                            # Remove/add to tracking data structs
                                            heat.addEntry(candidate, roomid)
                                            heat_roster = heat.getRoster()
                                            instructors_in_heat = heat.getInstructors()
                                            singles_in_heat = heat.getSingles()
                                            instructors_available_for_heat[roomid].remove(inst)
                                            print("Candidate placed: ")
                                            print(candidate.loc[0, contestant_col], inst, 'room', roomid)
                                            resetSolutionLogic()
                                            log.clearConflict(inst, -1)  # Clear the conflict from all rooms for this newply placed inst
                                            for opt in candidate.loc[:, "Instructor Dancer #'s"][0]:
                                                if inst_tree_nodes[roomid].get(opt) is not None:
                                                    if inst_tree_nodes[roomid][opt] == 1:
                                                        del inst_tree_nodes[roomid][opt]
                                                        if opt in instructors_available_for_heat[roomid]:
                                                            instructors_available_for_heat[roomid].remove(opt)
                                                    else:
                                                        inst_tree_nodes[roomid][opt] -= 1
                                                else:
                                                    pass
                                            # Remove the placed candidate from the df, or -1 if multi-entry
                                            if candidate.loc[:, ev][0] == 1:
                                                dance_df[roomid] = dance_df[roomid].reset_index(drop=True)
                                                dance_df[roomid] = dance_df[roomid].drop(dance_df[roomid][dance_df[roomid][contestant_col] == candidate.loc[0, contestant_col]].index)
                                            else:
                                                dance_df[roomid].loc[dance_df[roomid].loc[:, contestant_col] == candidate.loc[0, contestant_col], ev] = candidate.loc[0, ev] - 1
                                            placed = True
                                            # Check if current level df is empty after a placed candidate
                                            if dance_df[roomid].empty:
                                                print("Division empty", room_info)
                                                sfin_rooms[roomid] = 1
                                                updateDanceDfs(init.dance_dfs, dance_df[roomid], room_info, room_info)
                                                # deleteEmpty(init.dance_dfs)
                                                if init.dance_dfs.get("S") is None:
                                                    singles_empty = True
                                        else:
                                            log.addConflict(ConflictItemSingle(2, inst), roomid)
                                            consecutive += 1
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        print("Instructors for", room_info, "all gone")
                                    # Deal with conflicts if reached conflict limit
                                    if consecutive > init.max_conflicts:
                                        # first update the dance dfs
                                        for df, info in zip(dance_df, s_floors):
                                            updateDanceDfs(init.dance_dfs, df, info, info)
                                        resolve = resolveConflictSingles(roomid, dance_df, inst_tree_nodes, log, heat, heat_list, instructors_available_for_heat, inst2sing_tree_nodes, ev)
                                        for level in instructors_available_for_heat:
                                            print(level)
                                        if len(instructors_available_for_heat[roomid]) == 0:
                                            print("Instructors for", room_info, "all gone")
                                        for check in heat_list.getRostersList():
                                            checkheat(check)
                                        checkheat(heat)
                                        # Check if any instructors lists are now empty
                                        for i, room in enumerate(instructors_available_for_heat):
                                            if room != []:  # If instructors for heat not empty do nothing
                                                continue
                                            if sfin_rooms[i] > 0:  # Must not be finished already
                                                continue
                                            if len(singles_in_heat[i]) < couples_per_floor and dance_df[i].shape[0] >= 1:
                                                print("Adding Instructors back in, may only have a few available need to swap around contestants")
                                                before_reload = instructors_available_for_heat[i].copy()
                                                instructors_available_for_heat[i] = list(inst_tree_nodes[i].keys())
                                                if instructors_available_for_heat[i] == before_reload:  # If list still empty or forced, mark room as finished
                                                    print("Instructor list still empty after a refresh, mark room as finished")
                                                    sfin_rooms[i] = 1
                                                elif sfin_rooms[i] == 2:
                                                    print("Room is already forced a finish, not reloading instructors")
                                            else:
                                                sfin_rooms[i] = 1
                                        if resolve == 1:
                                            failed = False
                                            consecutive = 0
                                        elif not failed: #and len(instructors_available_for_heat)[roomid] < len(list(inst_tree_nodes[roomid].keys())):
                                            # If first time failing try to add the instructors in the pool back into the picking list, the selection earlier might have just been unlucky in selection
                                            # meaning it saved a subset of similar instructor clusters stopping the selection process from even considering them
                                            failed = True
                                            print("Failed to resolve conflict adding back instructors in pool for more selector options")
                                            before_reload = instructors_available_for_heat[roomid].copy()
                                            instructors_available_for_heat[roomid] = list(inst_tree_nodes[roomid].keys())
                                            if instructors_available_for_heat[roomid] == before_reload:  # If list still empty or forced, mark room as finished
                                                print("Instructor List unchanged after a refresh, mark room as forced finished")
                                                sfin_rooms[roomid] = 2
                                        elif failed:
                                            print("Failed to Resolve conflicts 2nd time, forcing finish to room", roomid)
                                            sfin_rooms[roomid] = 2  # force a finish
                                    # Determine if room is finished
                                    if len(heat_roster[roomid]) == couples_per_floor:
                                        print("Room full", room_info)
                                        sfin_rooms[roomid] = 1
                                        if init.dance_dfs.get("S") is None:
                                            singles_empty = True
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        print("Instructors for", room_info, "all gone")
                                        if len(singles_in_heat[roomid]) < couples_per_floor and dance_df[roomid].shape[0] >= 1:
                                            print("Adding Instructors back in, may only have a few available need to swap around contestants")
                                            before_reload = instructors_available_for_heat[roomid].copy()
                                            instructors_available_for_heat[roomid] = list(inst_tree_nodes[roomid].keys())
                                            if instructors_available_for_heat[roomid] == before_reload:  # If list still empty or forced, mark room as finished
                                                print("Instructor list still empty after a refresh, mark room as finished")
                                                sfin_rooms[roomid] = 1
                                            elif sfin_rooms[roomid] == 2:
                                                print("Room is already forced a finish, not reloading instructors")
                                                sfin_rooms[roomid] = 2
                                        else:
                                            sfin_rooms[roomid] = 1
                                    # Determine if backfill needed
                                    if sfin_rooms[roomid] > 0 and dance_df[roomid][init.ev].sum() < acceptablecouples:
                                        if dance_df[roomid].shape[0] != 0 and heat_list.getDivisionHoleCount(room_info) > 0:
                                            print("Not enough contestants left to make an acceptable heat")
                                            backfill(dance_df[roomid], room_info, heat_list, couples_per_floor, ev)
                                            updateDanceDfs(init.dance_dfs, dance_df[roomid], room_info, room_info)
                                            deleteEmpty(init.dance_dfs)
                                            if init.dance_dfs.get("S") is None:
                                                singles_empty = True
                                    if singles_empty:
                                        print("Singles Empty for", ev)
                                        for i, info in enumerate(sfin_rooms):
                                            if sfin_rooms[i] == 0:
                                                sfin_rooms[i] = 1
                                    # Determine if heat finished
                                    if (sfin_rooms.count(1) + sfin_rooms.count(2)) == len(s_floors):
                                        selection_finished = True
                                        print("Singles Selection Finished for heat", heat_key)
                        heat.printHeat()
                        # Determine if poach needed
                        for roomid, room_info in enumerate(s_floors):
                            if len(heat.getRoster()[roomid]) < acceptablecouples:
                                PoachPrevHeatsSingles(roomid, room_info, dance_df[roomid], heat, heat_list, acceptablecouples)
                        # Update the OG DF tree with all the placments
                        for df, info in zip(dance_df, s_floors):
                            updateDanceDfs(init.dance_dfs, df, info, info)
                        deleteEmpty(init.dance_dfs)  # Remove the keys from the tree that are empty
                        if singles_empty:
                            init.dance_dfs["D"] = 1
                        # ---------------------------------------------- Couples ---------------------------------------
                        if len(c_floors) > 0:  # if a couples key has been picked
                            print("Selecting Couples")
                            for roomid, info in enumerate(c_floors):
                                for i, key in enumerate(info):
                                    if i == 0:
                                        tmp = init.dance_dfs[key]
                                        continue
                                    if type(tmp) is dict:
                                        try:
                                            tmp = tmp[key]
                                        except:
                                            print(info, "Division removed already, likely due to split where this division is empty")
                                            tmp = pd.DataFrame()
                                dance_df.append(tmp)
                            # Loop rooms, backfill or filling new room to completion before moving to the next room
                            for roomid, room_info in enumerate(c_floors):
                                # If room finished
                                if cfin_rooms[roomid] > 0:
                                    continue
                                print('Selecting for room', roomid, room_info)
                                consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                                init.solved = 0  # counts how many resolveConflict() calls for this heat
                                init.nsolved = 0  # counts how many resolveConflict() calls for this heat
                                # Get suitable candidates from the df of the current division
                                if len(s_floors) > 0:
                                    singles_index = len(s_floors)-1
                                else:
                                    singles_index = 0
                                while len(heat_roster[roomid+singles_index]) < init.max_dance_couples and cfin_rooms[roomid] == 0:
                                    if consecutive > init.max_conflicts:
                                        resolve = resolveConflictCouples(roomid, dance_df, inst_tree_nodes, log, heat, heat_list, instructors_available_for_heat, inst2sing_tree_nodes, ev)
                                        # TODO CHeck the meta data lists after a resolve
                                        if resolve == 1:
                                            consecutive = 0
                                        else:
                                            cfin_rooms[roomid] = 2  # force a finish
                                            if (cfin_rooms.count(1) + cfin_rooms.count(2)) == len(c_floors):
                                                break
                                            continue
                                    candidate = dance_df[roomid+singles_index].sample(ignore_index=True)  # Pick out random entry from df, may need to have try catch
                                    # Check candidate has no one already in heat
                                    dup_sing = False
                                    dup_inst = False
                                    dup_coup = False
                                    if candidate.loc[0, 'type id'] == 'C':
                                        number = candidate.loc[0, 'Lead Dancer #']
                                        fnumber = candidate.loc[0, 'Follow Dancer #']
                                        # TODO copy this section to 'A' as well
                                        # Check contestants in heat
                                        for selection in singles_in_heat:
                                            if dup_sing:
                                                break
                                            if selection.count(number) > 0:  # Check if Lead is being used in heat
                                                dup_sing = True
                                                break
                                            if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                                                dup_sing = True
                                                break
                                        # Check Instructors in heat
                                        for selection in instructors_in_heat:
                                            if dup_inst:
                                                break
                                            if selection.count(number) > 0:  # Check if Lead is being used in heat
                                                dup_inst = True
                                                break
                                            if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                                                dup_inst = True
                                                break
                                        # Check couples in heat
                                        for selection in couples_in_heat:
                                            if dup_coup:
                                                break
                                            if selection.count(number) > 0:  # Check if Lead is being used in heat
                                                dup_coup = True
                                                break
                                            if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                                                dup_coup = True
                                                break
                                    if dup_sing or dup_inst or dup_coup:
                                        consecutive += 1  # stop infinite looping when list has no candidate to add to this heat
                                        # Add to the conflict log
                                        if dup_sing:
                                            conflict = ConflictItemCouple(2, number, fnumber)
                                            log.addConflict(conflict, roomid+singles_index)
                                            continue
                                        if dup_coup:
                                            conflict = ConflictItemCouple(1, number, fnumber)
                                            log.addConflict(conflict, roomid+singles_index)
                                            continue
                                        if dup_inst:
                                            raise Exception("Couple in Instructor list", number, fnumber)
                                    # # Check if instructor inside heat, only for Singles
                                    # if candidate.loc[:, 'type id'][0] != "C":  # if not a couple entry
                                    #     # Set which column will be used based on Leader or Follower single
                                    #     if candidate.loc[:, 'type id'][0] == 'F':
                                    #         inst_col = 'Lead Dancer #'
                                    #     else:
                                    #         inst_col = 'Follow Dancer #'
                                    #
                                    #     potential_instructors = candidate[inst_col].tolist()[0]
                                    #     # loop through potential_instructors list,
                                    #     # if not in heat already, keep the list in case of a later swap
                                    #     # add to heat roster and instructors_in_heat
                                    #     for inst in potential_instructors:
                                    #         found = False
                                    #
                                    #         for lev in instructors_in_heat:
                                    #         for lev in instructors_in_heat:
                                    #             if lev.count(inst) != 0:
                                    #                 found = True
                                    #                 break
                                    #         if not found:
                                    #             instructors_in_heat[roomlvl].append(inst)
                                    #             added = True
                                    #             break
                                    # instructors_in_heat[roomlvl].append(-1)
                                    else:  # Else = there are no conflicts
                                        # if candidate possible add to the roster, remove that entry from the pool
                                        heat.addEntry(candidate, roomid+singles_index)
                                        print("Candidate placed: ")
                                        print("Lead", number, "Follow", fnumber, "heat num", heat_list.getHeatCount()+1, 'room', roomid+singles_index, room_info)
                                        print()
                                        col = "Lead Dancer #"
                                        fcol = "Follow Dancer #"
                                        # if last or only entry remove it from query_df
                                        if candidate.loc[0, ev] == 1:
                                            dance_df[roomid+singles_index] = dance_df[roomid+singles_index].reset_index(drop=True)
                                            dance_df[roomid+singles_index] = dance_df[roomid+singles_index].drop(dance_df[roomid+singles_index][(dance_df[roomid+singles_index][col] == candidate.loc[0, col]) & (dance_df[roomid+singles_index][fcol] == candidate.loc[0, fcol])].index)
                                        else:
                                            dance_df[roomid+singles_index].loc[(dance_df[roomid+singles_index].loc[:, col] == candidate.loc[0, col]) & (dance_df[roomid+singles_index].loc[:, fcol] == candidate.loc[0, fcol]), ev] = candidate.loc[0, ev] - 1
                                        # Add candidate data to tracker lists
                                        heat_roster = heat.getRoster()
                                        couples_in_heat = heat.getCouples()
                                        # Check if current df is empty after adding the candidate
                                        if dance_df[roomid+singles_index].empty:
                                            cfin_rooms[roomid] = 1
                                            updateDanceDfs(init.dance_dfs, dance_df[roomid+singles_index], room_info, room_info)
                                            deleteEmpty(init.dance_dfs)  # Clean up parent levels if needed
                                            if init.dance_dfs.get("C") is None:
                                                couples_empty = True
                                            if len(heat.getRoster()[roomid]) < acceptablecouples:
                                                PoachPrevHeatsCouples(roomid, room_info, dance_df[roomid], heat, heat_list, acceptablecouples)
                                    if len(heat_roster[roomid+singles_index]) == couples_per_floor:
                                        cfin_rooms[roomid] = 1
                                        if dance_df[roomid+singles_index].shape[0] < int(couples_per_floor/2) and dance_df[roomid+singles_index].shape[0] != 0:
                                            if dance_df[roomid+singles_index][ev].sum() < heat_list.getDivisionHeatCount(room_info):
                                                # backfill(dance_df[roomid+singles_index], room_info, heat_list, couples_per_ballroom, ev, init.df_inst)
                                                updateDanceDfs(init.dance_dfs, dance_df[roomid+singles_index], room_info, room_info)
                                                deleteEmpty(init.dance_dfs)
                                                if init.dance_dfs.get("C") is None:
                                                    couples_empty = True
                                            else:
                                                print("Not enough heats to backfill")
                                        break
                                    if couples_empty:
                                        for i, info in enumerate(cfin_rooms):
                                            if cfin_rooms[i] == 0:
                                                cfin_rooms[i] = 1
                                    if init.solved == init.maxsolves and len(heat_roster[roomid+singles_index]) != couples_per_floor:
                                        cfin_rooms[roomid] = 2  # Forced finish
                                    # if consecutive == max_conflicts and (heat_list.getDivisionHeatCount(room_info) == 0):  # if conflicts and no previous heats
                                    #     cfin_rooms[roomid] = 2  # Forced finish
                                    # Determine if heat finished
                                if (cfin_rooms.count(1) + cfin_rooms.count(2)) == len(c_floors):
                                    break
                            for df, info in zip(dance_df, c_floors):
                                updateDanceDfs(init.dance_dfs, df, info, info)
    # ------------------------------------------------- Double up on unused rooms --------------------------------------
                        # If levels < ballrooms and not in split mode already, figure out if the current selection pool can be put into open room(s)
                        if split_mode and (not (singles_empty and couples_empty)):
                            print('Spliting a Division on the floor')
                            # Sanity Check all the current floors
                            splits_count = [[0, 0, 0]]
                            splits_info = [[0]]
                            for i, info in enumerate(floor_info):
                                # Find meta data for singles list
                                if info[0] == "S" and init.dance_dfs.get("S") is not None:
                                    unique = findUnique(pre_inst_tree, s_floors, info)
                                    if not unique > couples_per_floor*(floor_info.count(info)+1):  # If room cannot be split due to instructor constraints
                                        continue
                                    count = findContestantCount(init.dance_dfs, info, ev)
                                    # if len(leftover_inst) < count:
                                    #     count = len(leftover_inst)
                                elif init.dance_dfs.get("C") is not None:
                                    count = findContestantCount(init.dance_dfs, info, ev)
                                if count == None:
                                    continue
                                count.append(int(count[0]/couples_per_floor))  # find out how many rooms div can occupy
                                for i, split in enumerate(splits_count):  # order largest to smallest count
                                    if split[1] > count[1]:
                                        continue
                                    else:
                                        splits_count.insert(i, count)
                                        splits_info.insert(i, info)
                                        break
                            # Loop over all rooms in heat
                            splits_count = splits_count[:-1]   # remove termination character
                            splits_info = splits_info[:-1]   # remove termination character
                            takefrom_count = []
                            for data in splits_count:
                                takefrom_count.append(data.copy())
                            takefrom_info = []
                            for data in splits_info:
                                takefrom_info.append(data.copy())
                            while split_mode:  # While loop to allow for multiple div split
                                splititer = 0
                                for i, vacant in enumerate(heat_roster):
                                    if len(vacant) > 0 or (len(floor_info)-1) >= i:  # If room is already in use, continue loop
                                        continue
                                    if len(takefrom_count) == 0:
                                        break
                                    # Choose the largest div, then re-organize the list after picking
                                    floor_info.append(takefrom_info[0])
                                    log.addRoom(takefrom_info[0])
                                    if 't' in div or 'T' in div:
                                        if splits_info[0][0] == "S":
                                            s_floors.append(takefrom_info[0])
                                            sfin_rooms.append(0)
                                        else:
                                            c_floors.append(takefrom_info[0])
                                            cfin_rooms.append(0)
                                    # Decrement the counts
                                    takefrom_count[0][0] -= couples_per_floor
                                    takefrom_count[0][1] -= couples_per_floor
                                    splits_count[splititer][0] -= couples_per_floor
                                    splits_count[splititer][1] -= couples_per_floor
                                    if takefrom_count[0][1] < couples_per_floor: # If next split cannot make a full room
                                        # If empty after selection or other splits exist
                                        if len(takefrom_count) > 1 or takefrom_count[0][1] <= 0:
                                            # replace = takefrom_count[0].copy()
                                            del takefrom_count[0]
                                            if splits_count[splititer][0] <= 0:
                                                del splits_count[splititer]
                                            splititer += 1
                                            del takefrom_info[0]
                                    # for i, split in enumerate(takefrom_count):  # order largest to smallest count
                                    #     if split[1][1] > replace[1]:
                                    #         continue
                                    #     else:
                                    #         splits_count.insert(i, count)
                                    #         splits_info.insert(i, info)
                                    #         break
                                if len(splits_count) == 0 or len(floor_info) == floors:
                                    split_mode = False
                            print("Done spliting new floor breakdown", floor_info)
                        else:
                            heat_finished = True
                    for check in heat_list.getRostersList():
                        checkheat(check)
                    heat.calculateHoles(couples_per_floor)
                    heat_list.appendList(heat)  # add completed heat to the HeatList obj
                    split_mode = False
                    dance_heat_count += 1
                    tot_current_heats += 1
                    # heats[each][every][ev] = heat_list
                    # buildEventfast(heats, eventName)
                    if tot_current_heats > init.max_heats:
                        print("Exceeded max heats for event time metrics")
                    if singles_empty and couples_empty:
                        init.dance_dfs["D"] = 1
                if heats[each][every].get(ev) is not None:
                    heats[each][every][ev] = heat_list
                    print(ev, "finished Selection with", dance_heat_count, "Heats")
    buildEvent(heats, init.eventName)


def pickDfs(ev, dance_dfs, inst_tree, floors, div, eventages_s, eventages_c, couples_per_floor):
    print()
    # l_keys = [0, 1, 2, 3, 4, 5]

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
                if getNode(inst_tree, every) == {}:  # Check if node is there
                    if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                        prio += 1
                    continue
                if every not in picked_keys:  # add to picked list only if that key combo is not in already
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
                    if prio_c[prio][
                        0] == "S":  # Make sure to give the correct age brackets for selection, based on the possible keys
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