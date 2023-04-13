import pandas as pd
import os
import random
import init
from debug import *
from init import buildInstTree, deleteEmpty, buildInst2SingTree
from methods import *
from conflictSingles import resolveConflictSingles
from conflictCouples import resolveConflictCouples
from conflict import resetSolutionLogic
from init import updateDanceDfs, getNode, buildInstTree, instructorOperation
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ConflictItemCouple
from output import buildEvent, makeHeatDict, buildEventfast
from selection_singles import selectionSingles
from selection_couples import selectionCouples

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
                filename = ev + ".txt"
                filepath = os.getcwd().replace('\src', "") + "\\Log" + "\\" + str(each) + "\\" + str(every) + "\\"
                logfile = filepath + filename
                try:
                    os.makedirs(filepath)
                except:
                    print("Filepath", filepath, "already exists")
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

                # Build Couples df for this event broken down by all metrics
                # Slice Contestant dfs based on levels
                raw_contestant_data = sliceDfs(init.df_sing, init.df_coup)
                if ev in init.df_coup.columns:
                    init.eventlvlnames_c = []
                    init.eventages_c = []
                    setupCouplesEvent(eventrow, raw_contestant_data)
                else:  # If there are no Couples for this event
                    del init.dance_dfs["C"]
                    init.eventlvlnames_c = []
                    init.eventages_c = []

                # Build singles df for this event
                if ev in init.df_sing.columns:
                    init.eventlvlnames_s = []
                    init.eventages_s = []
                    setupSinglesEvent(eventrow, raw_contestant_data)
                else:
                    del init.dance_dfs["S"]
                    init.eventlvlnames_s = []
                    init.eventages_s = []

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

                # Check if current dfs are empty, and remove them
                deleteEmpty(init.dance_dfs)
                # if both Pools are totally empty continue
                # In this case it would only happen if there were no entries to current dance 'ev'
                floors = eventrow.loc[:, 'Floors'][0]
                heat_list = HeatList([], floors, couples_per_floor, init.eventages_s, init.eventages_c, init.eventlvlnames_s, init.eventlvlnames_c)  # list of individual heats for the current dance 'ev'
                if len(init.dance_dfs) == 0:
                    print("No data in this category", ev)
                    init.logString += "\n" + "No data in this category " + ev
                    heat_list = -1
                    continue
                pre_dance_dfs = init.dance_dfs.copy()
                init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                init.inst2sing_tree = buildInst2SingTree(init.dance_dfs, {}, ev)
                pre_inst_tree = init.inst_tree.copy()
# ---------------------------------------------- Selection Process -----------------------------------------------------
                # Check if dfs are empty
                if init.dance_dfs.get("S") is None:
                    singles_empty = True
                else:
                    singles_empty = False
                if init.dance_dfs.get("C") is None:
                    couples_empty = True
                else:
                    couples_empty = False
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
                    floor_info = pickDfs(ev, init.dance_dfs, init.inst_tree, floors, div, init.eventages_s, init.eventages_c, couples_per_floor)
                    for floor in range(floors):
                        heat_roster.append([])
                        instructors_in_heat.append([])
                        singles_in_heat.append([])
                        couples_in_heat.append([])
                        fin_rooms.append(0)
                    heat_finished = False
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
                        # Make Instructors for heat list that will change based on placed contestants and instructors
                        instructors_available_for_heat = []
                        init.starting_instructors_for_heat = []
                        for roomid, info in enumerate(s_floors):
                            tmp2 = getNode(init.inst_tree, info)
                            instructors_available_for_heat.append(list(tmp2.keys()))
                            init.starting_instructors_for_heat.append(list(tmp2.keys()))
                        selection_finished = False
                        print("Event " + ev + ", Heat number: " + str(heat_list.getHeatCount()))
                        print(floor_info)
                        print()
                        init.debug_floors = s_floors
                        init.logString += "\n" + "Event " + ev + ", Heat number: " + str(heat_list.getHeatCount())
                        if len(s_floors) != 0:  # If no singles move to couples selection
                            selectionSingles(heat, heat_list, s_floors, sfin_rooms, instructors_available_for_heat, log, couples_per_floor, acceptablecouples)
                            heat.printHeat()
                            # Determine if poach needed
                            for roomid, room_info in enumerate(s_floors):
                                if len(heat.getRoster()[roomid]) < acceptablecouples:
                                    PoachPrevHeatsSingles(roomid, room_info, heat, heat_list, acceptablecouples)
                            if init.debug:
                                if init.count:
                                    countInstances(heat, heat_list)
                                if init.inst:
                                    for level in instructors_available_for_heat:
                                        print(level)
                                if init.check:
                                    for check in heat_list.getRostersList():
                                        checkheat(check)
                                    checkheat(heat)
                            if init.dance_dfs.get("S") is None and init.singles_only:
                                init.dance_dfs["D"] = 1
                        # ---------------------------------------------- Couples ---------------------------------------
                        if len(c_floors) != 0:  # if a couples key has been picked
                            if len(s_floors) > 0:
                                singles_index = len(s_floors) - 1
                            else:
                                singles_index = 0
                            selectionCouples(heat, heat_list, singles_index, c_floors, cfin_rooms, instructors_available_for_heat, log, couples_per_floor, acceptablecouples)
                            # Determine if poach needed
                            for roomid, room_info in enumerate(c_floors):
                                if len(heat.getRoster()[roomid]) < acceptablecouples:
                                    PoachPrevHeatsCouples(roomid, room_info, heat, heat_list, acceptablecouples)
                            if init.debug:
                                if init.count:
                                    countInstances(heat, heat_list)
                                if init.inst:
                                    for level in instructors_available_for_heat:
                                        print(level)
                                if init.check:
                                    for check in heat_list.getRostersList():
                                        checkheat(check)
                                    checkheat(heat)
                            if init.dance_dfs.get("C") is None and init.couples_only:
                                init.dance_dfs["D"] = 1
    # ------------------------------------------------- Double up on unused rooms --------------------------------------
                        # If levels < floors and in split mode and floors were not all forced finihsed
                        # figure out if the current selection pool can be put into open room(s)
                        statement_floors = sfin_rooms + cfin_rooms
                        if split_mode and (not (singles_empty and couples_empty)) and statement_floors.count(1) > 0:
                            print('Spliting a Division on the floor')
                            # Sanity Check all the current floors
                            splits_count = [[0, 0, 0]]
                            splits_info = [[0]]
                            for i, info in enumerate(floor_info):
                                # Find meta data for singles list
                                if info[0] == "S":
                                    if sfin_rooms[i] > 1:  # If the room was forced finished
                                        print(info, "was forced finished, not able to be split")
                                        continue
                                    unique = findUnique(pre_inst_tree, copyList(s_floors), info)
                                    if not unique >= acceptablecouples*(floor_info.count(info)+1):  # If room cannot be split due to instructor constraints
                                        continue
                                    count = findContestantCount(init.dance_dfs, info, ev)
                                else:  # if a couples division
                                    if cfin_rooms[i-singles_index] > 1:  # if room was forced finished
                                        print(info, "was forced finished, not able to be split")
                                        continue
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
                            if splits_count == [] or splits_info == []:  # If no level was found to be split-able
                                print("No level in heat found to be able to be split, heat is now finished and appended to list")
                                split_mode = False
                                heat_finished = True
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
                                    if takefrom_count[0][1] < couples_per_floor:  # If next split cannot make a full room
                                        # If empty after selection or other splits exist
                                        if len(takefrom_count) > 1 or takefrom_count[0][1] <= 0:
                                            # replace = takefrom_count[0].copy()
                                            del takefrom_count[0]
                                            if splits_count[splititer][0] <= 0:
                                                del splits_count[splititer]
                                            splititer += 1
                                            del takefrom_info[0]
                                if len(splits_count) == 0 or len(floor_info) == floors:
                                    split_mode = False
                            print("Done spliting new floor breakdown", floor_info)
                            heat.fillDivision(floor_info)
                        else:
                            heat_finished = True
                    for check in heat_list.getRostersList():
                        checkheat(check)
                    checkheat(heat)
                    heat.calculateHoles(couples_per_floor)
                    heat_list.appendList(heat)  # add completed heat to the HeatList obj
                    split_mode = False
                    dance_heat_count += 1
                    tot_current_heats += 1
                    if tot_current_heats > init.max_heats:
                        print("Exceeded max heats for event time metrics")
                    if init.dance_dfs.get("S") is None and init.dance_dfs.get("C") is None:
                        init.dance_dfs["D"] = 1
                if heats[each][every].get(ev) is not None:
                    heats[each][every][ev] = heat_list
                    print(init.ev, "finished Selection with", dance_heat_count, "Heats")
                    with open(logfile, "w+") as f:
                        f.write(init.logString)
    buildEvent(heats, init.eventName)
