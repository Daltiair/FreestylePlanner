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
                if ev in init.df_coup.columns:
                    setupCouplesEvent(eventrow, contestant_data)
                else:  # If there are no Couples for this event
                    del init.dance_dfs["C"]
                    init.eventlvlnames_c = []
                    init.eventages_c = []

                # Build singles df for this event
                if ev in init.df_sing.columns:
                    setupSinglesEvent(eventrow, contestant_data)
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
                # TODO DELETE after testing
                # del init.dance_dfs["S"]
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
                        while not selection_finished:
                            if len(s_floors) == 0:  # If no singles move to couples selection
                                break
                            for roomid, room_info in enumerate(s_floors):  # For each ballroom make 1 instructor/single pair
                                print()
                                init.logString += "\n"
                                print('Selecting for room', roomid, room_info, heat_key)
                                init.logString += "\n" + 'Selecting for room' + str(roomid) + str(room_info) + str(heat_key)
                                if sfin_rooms[roomid] > 0:  # if room is filled or declared full, continue on
                                    print("Room finished, fin code", sfin_rooms[roomid])
                                    # init.logString += "\n" + "Room finished, fin code", str(sfin_rooms[roomid])
                                    continue
                                placed = False  # Set when a valid instructor/single pair is placed
                                failed = False
                                consecutive = 0  # Stops infinite loops on failed attempts to add candidate to the heat
                                while (not placed) and not (sfin_rooms[roomid] > 0):  # Find a viable single/inst match
                                    # print(instructors_available_for_heat[roomid])
                                    dance_df = getNode(init.dance_dfs, room_info)
                                    inst_tree_node = getNode(init.inst_tree, room_info)
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
                                        log.addConflict(ConflictItemSingle(1, inst), roomid)
                                        consecutive += 1
                                    else:  # Find a single to pair with this instructor
                                        found = False
                                        # Loop over each row in the df for this level
                                        df_shuffled = dance_df.sample(frac=1)
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
                                            init.logString += "\n" + "Candidate placed: "
                                            print(candidate.loc[0, contestant_col], inst, 'room', roomid)
                                            init.logString += "\n" + str(candidate.loc[0, contestant_col]) + str(inst) + str('room') + str(roomid)
                                            resetSolutionLogic()
                                            log.clearConflict(inst, -1)  # Clear the conflict from all rooms for this newply placed inst
                                            # Remove the placed candidate from the df, or -1 if multi-entry
                                            if candidate.loc[:, ev][0] == 1:
                                                print("removing", candidate.loc[:, contestant_col][0], "from pool")
                                                dance_df = dance_df.reset_index(drop=True)
                                                dance_df = dance_df.drop(dance_df[dance_df[contestant_col] == candidate.loc[0, contestant_col]].index)
                                                updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                                            else:
                                                dance_df.loc[dance_df.loc[:, contestant_col] == candidate.loc[0, contestant_col], ev] = candidate.loc[0, ev] - 1
                                            init.inst_tree = buildInstTree(init.dance_dfs, {}, init.ev)
                                            inst_tree_node = getNode(init.inst_tree, room_info)
                                            placed = True
                                            # Check if current level df is empty after a placed candidate
                                            if dance_df.empty:
                                                print("Division empty", room_info)
                                                sfin_rooms[roomid] = 1
                                                deleteEmpty(init.dance_dfs)
                                        else:
                                            log.addConflict(ConflictItemSingle(2, inst), roomid)
                                            consecutive += 1
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        print("Instructors for", room_info, "all gone")
                                    # Deal with conflicts if reached conflict limit
                                    if consecutive > init.max_conflicts:
                                        resolve = resolveConflictSingles(roomid, dance_df, log, heat, heat_list, instructors_available_for_heat, ev)
                                        dance_df = getNode(init.dance_dfs, room_info)
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
                                        # Check if any instructors lists are now empty
                                        for i, room in enumerate(instructors_available_for_heat):
                                            if room != []:  # If instructors for heat not empty do nothing
                                                continue
                                            if sfin_rooms[i] > 0:  # Must not be finished already
                                                continue
                                            if len(singles_in_heat[i]) < couples_per_floor and dance_df.shape[0] >= 1:
                                                print("Adding Instructors back in, may only have a few available need to swap around contestants")
                                                before_reload = instructors_available_for_heat[i].copy()
                                                instructors_available_for_heat[i] = list(inst_tree_node.keys())
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
                                        elif not failed: # and len(instructors_available_for_heat)[roomid] < len(list(inst_tree_nodes[roomid].keys())):
                                            # If first time failing try to add the instructors in the pool back into the picking list, the selection earlier might have just been unlucky in selection
                                            # meaning it saved a subset of similar instructor clusters stopping the selection process from even considering them
                                            failed = True
                                            print("Failed to resolve conflict adding back instructors in pool for more selector options")
                                            before_reload = instructors_available_for_heat[roomid].copy()
                                            instructors_available_for_heat[roomid] = list(inst_tree_node.keys())
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
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        print("Instructors for", room_info, "all gone")
                                        if len(singles_in_heat[roomid]) < couples_per_floor and dance_df.shape[0] >= 1:
                                            print("Adding Instructors back in, may only have a few available need to swap around contestants")
                                            before_reload = instructors_available_for_heat[roomid].copy()
                                            instructors_available_for_heat[roomid] = list(inst_tree_node.keys())
                                            if instructors_available_for_heat[roomid] == before_reload:  # If list still empty or forced, mark room as finished
                                                print("Instructor list still empty after a refresh, mark room as finished")
                                                sfin_rooms[roomid] = 1
                                            elif sfin_rooms[roomid] == 2:
                                                print("Room is already forced a finish, not reloading instructors")
                                                sfin_rooms[roomid] = 2
                                        else:
                                            sfin_rooms[roomid] = 1
                                    # Determine if backfill needed
                                    if sfin_rooms[roomid] > 0 and dance_df[init.ev].sum() < acceptablecouples:
                                        if dance_df.shape[0] != 0 and heat_list.getDivisionHoleCount(room_info) > 0:
                                            print("Not enough contestants left to make an acceptable heat")
                                            backfill(dance_df, room_info, heat_list, couples_per_floor, ev)
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
                                            deleteEmpty(init.dance_dfs)
                                    if init.dance_dfs.get("S") is None:
                                        singles_empty = True
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
                        # if singles_empty:
                        #     init.dance_dfs["D"] = 1
                        # ---------------------------------------------- Couples ---------------------------------------
                        if len(c_floors) > 0:  # if a couples key has been picked
                            print("Selecting Couples")
                            # Loop rooms, backfill or filling new room to completion before moving to the next room
                            for roomid, room_info in enumerate(c_floors):
                                # If room finished
                                if cfin_rooms[roomid] > 0:
                                    continue
                                print('Selecting for room', roomid, room_info)
                                dance_df = getNode(init.dance_dfs, room_info)
                                consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                                # Get suitable candidates from the df of the current division
                                if len(s_floors) > 0:
                                    singles_index = len(s_floors)-1
                                else:
                                    singles_index = 0
                                while len(heat_roster[roomid+singles_index]) < couples_per_floor and cfin_rooms[roomid] == 0:
                                    print()
                                    candidate = dance_df.sample(ignore_index=True)  # Pick out random entry from df, may need to have try catch
                                    # Check candidate has no one already in heat
                                    dup_sing = False
                                    dup_inst = False
                                    dup_coup = False
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
                                        col = "Lead Dancer #"
                                        fcol = "Follow Dancer #"
                                        # if last or only entry remove it from query_df
                                        if candidate.loc[0, ev] == 1:
                                            dance_df = dance_df.reset_index(drop=True)
                                            dance_df = dance_df.drop(dance_df[(dance_df[col] == candidate.loc[0, col]) & (dance_df[fcol] == candidate.loc[0, fcol])].index)
                                            updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                                        else:
                                            dance_df.loc[(dance_df.loc[:, col] == candidate.loc[0, col]) & (dance_df.loc[:, fcol] == candidate.loc[0, fcol]), ev] = candidate.loc[0, ev] - 1
                                        # Add candidate data to tracker lists
                                        heat_roster = heat.getRoster()
                                        couples_in_heat = heat.getCouples()
                                        # Check if current df is empty after adding the candidate
                                        if dance_df.empty:
                                            print("Division Empty", room_info)
                                            cfin_rooms[roomid] = 1
                                            updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                                            deleteEmpty(init.dance_dfs)  # Clean up parent levels if needed
                                    # Resolve Conflicts
                                    if consecutive > init.max_conflicts:
                                        resolve = resolveConflictCouples(roomid, dance_df, log, heat, heat_list, instructors_available_for_heat, ev)
                                        dance_df = getNode(init.dance_dfs, room_info)
                                        if init.debug:
                                            countInstances(heat, heat_list)
                                            for check in heat_list.getRostersList():
                                                checkheat(check)
                                            checkheat(heat)
                                        if resolve == 1:
                                            consecutive = 0
                                        else:  # If failed to resolve
                                            cfin_rooms[roomid] = 2  # force a finish
                                            print("Failed to resolve conflict, forcing finish", room_info)
                                    if len(heat_roster[roomid+singles_index]) == couples_per_floor:
                                        cfin_rooms[roomid] = 1
                                    # Determine if backfill needed
                                    if cfin_rooms[roomid] > 0 and dance_df[init.ev].sum() < acceptablecouples:
                                        if dance_df.shape[0] != 0 and heat_list.getDivisionHoleCount(room_info) > 0:
                                            backfill(dance_df, room_info, heat_list, couples_per_floor, ev, init.df_inst)
                                            updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                                            deleteEmpty(init.dance_dfs)
                                        else:
                                            print("Not enough heats to backfill")
                                    if init.dance_dfs.get("C") is None:
                                        couples_empty = True
                                        for i, info in enumerate(cfin_rooms):
                                            if cfin_rooms[i] == 0:
                                                cfin_rooms[i] = 1
                                # Determine if heat finished
                                if (cfin_rooms.count(1) + cfin_rooms.count(2)) == len(c_floors):
                                    break
                            # Determine if poach needed
                            for roomid, room_info in enumerate(c_floors):
                                if len(heat.getRoster()[roomid]) < acceptablecouples:
                                    PoachPrevHeatsCouples(roomid, room_info, heat, heat_list, acceptablecouples)
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
                    if singles_empty and couples_empty:
                        init.dance_dfs["D"] = 1
                if heats[each][every].get(ev) is not None:
                    heats[each][every][ev] = heat_list
                    with open(logfile, "w+") as f:
                        f.write(init.logString)
                    print(init.ev, "finished Selection with", dance_heat_count, "Heats")
    buildEvent(heats, init.eventName)
