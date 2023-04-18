import init
from init import *
import random
from Structures import ConflictItemCouple, ConflictItemSingle
from conflictAll import resolveConflictAll
from conflict import resetSolutionLogic
from debug import countInstances, checkheat
from methods import backfill


def selectionAlltype(heat, heat_list, a_floors, afin_rooms, instructors_available_for_heat, log_s, log_c, couples_per_floor, acceptablecouples):
    print("Selecting All Type")
    singles_in_heat = heat.getSingles()
    couples_in_heat = heat.getCouples()
    instructors_in_heat = heat.getInstructors()
    heat_roster = heat.getRoster()
    heat_key = heat.getKey()
    selection_finished = False
    while not selection_finished:
        for roomid, room_info in enumerate(a_floors):  # For each ballroom make 1 instructor/single pair
            print()
            init.logString += "\n"
            init.logString += "\n" + 'Selecting for room' + str(roomid) + str(room_info) + str(heat_key)
            if afin_rooms[roomid] > 0:  # if room is filled or declared full, continue on
                print("Room finished, fin code", afin_rooms[roomid])
                # init.logString += "\n" + "Room finished, fin code", str(sfin_rooms[roomid])
                continue
            print('Selecting for room', roomid, room_info, heat_key)
            placeable = False  # Set when a valid instructor/single pair is placed
            failed = False
            consecutive = 0  # Stops infinite loops on failed attempts to add candidate to the heat
            while (not placeable) and not (afin_rooms[roomid] > 0):  # Find a viable single/inst match
                dance_df = getNode(init.dance_dfs, room_info)
                inst_tree_node = getNode(init.inst_tree, room_info)
                # Get suitable candidates from the df of the current division
                candidate = dance_df.sample(ignore_index=True)  # Pick out random entry from df, may need to have try catch
                typeid = candidate.loc[0, "type id"]
                if typeid == "C":
                    # Check candidate has no one already in heat
                    dup_singl = False
                    dup_singf = False
                    dup_inst = False
                    dup_coup = False
                    number = candidate.loc[0, 'Lead Dancer #']
                    fnumber = candidate.loc[0, 'Follow Dancer #']
                    # Check Single contestants in heat
                    for i, selection in enumerate(singles_in_heat):
                        if selection.count(number) > 0:  # Check if Lead is being used in heat
                            dup_singl = True
                            instl = singles_in_heat[i][selection.index(number)]
                            break
                        if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                            dup_singf = True
                            instf = singles_in_heat[i][selection.index(fnumber)]
                            break
                    # Check Instructors in heat
                    for selection in instructors_in_heat:
                        if selection.count(number) > 0:  # Check if Lead is being used in heat
                            dup_inst = True
                            break
                        if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                            dup_inst = True
                            break
                    # Check couples in heat
                    for selection in couples_in_heat:
                        if selection.count(number) > 0:  # Check if Lead is being used in heat
                            dup_coup = True
                            break
                        if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                            dup_coup = True
                            break
                    if dup_singl or dup_singf or dup_inst or dup_coup:
                        placeable = False
                        # Add to the conflict log
                        if dup_singl:
                            conflict = ConflictItemSingle(2, instl)
                            log_s.addConflict(conflict, roomid)
                        if dup_singf:
                            conflict = ConflictItemSingle(2, instf)
                            log_s.addConflict(conflict, roomid)
                        if dup_coup:
                            conflict = ConflictItemCouple(1, number, fnumber)
                            log_c.addConflict(conflict, roomid)
                        if dup_inst:
                            raise Exception("Couple in Instructor list", number, fnumber)
                    else:
                        placeable = True
                else:  # If a single entry
                    inst = random.choice(instructors_available_for_heat[roomid])  # get random instructor, will throw error if list at index is empty
                    instructor_taken = False
                    for selection in instructors_in_heat:
                        if instructor_taken:
                            break
                        if selection.count(inst) > 0:  # Check if instructor is being used in heat
                            instructor_taken = True
                            break
                    if instructor_taken:
                        log_s.addConflict(ConflictItemSingle(1, inst), roomid)
                        consecutive += 1
                    else:  # Find a single to pair with this instructor
                        # Loop over each row in the df for this level
                        df_shuffled = dance_df[dance_df["type id"] != "C"].sample(frac=1)
                        for row, entry in df_shuffled.iterrows():
                            next_contestant = False
                            if placeable:
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
                                    for i, rost in enumerate(couples_in_heat):
                                        # If there is a couple causing a conflict with this single
                                        if rost.count(entry[contestant_col]) > 0:
                                            next_contestant = True
                                            l = entry["Lead Dancer #"]
                                            f = entry["Follow Dancer #"]
                                            log_c.addConflict(ConflictItemCouple(1, l, f), roomid)
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
                                        placeable = True
                                        break
                        if not placeable:
                            log_s.addConflict(ConflictItemSingle(2, inst), roomid)
                if placeable:  # There are no conflicts
                    # if candidate possible add to the roster, remove that entry from the pool
                    heat.addEntry(candidate, roomid)
                    resetSolutionLogic()
                    print()
                    print("Candidate placed: ")
                    if typeid == "C":
                        print("Lead", number, "Follow", fnumber, 'room', roomid, room_info, heat_key)
                        col = "Lead Dancer #"
                        fcol = "Follow Dancer #"
                        # if last or only entry remove it from query_df
                        if candidate.loc[0, init.ev] == 1:
                            dance_df = dance_df.reset_index(drop=True)
                            dance_df = dance_df.drop(dance_df[(dance_df[col] == candidate.loc[0, col]) & (dance_df[fcol] == candidate.loc[0, fcol])].index)
                        else:
                            dance_df.loc[(dance_df.loc[:, col] == candidate.loc[0, col]) & (dance_df.loc[:, fcol] == candidate.loc[0, fcol]), init.ev] = candidate.loc[0, init.ev] - 1
                        updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                    else:  # If a single candidate
                        print(candidate.loc[0, contestant_col], inst, 'room', roomid)
                        if candidate.loc[:, init.ev][0] == 1:
                            print("removing", candidate.loc[:, contestant_col][0], "from pool")
                            dance_df = dance_df.reset_index(drop=True)
                            dance_df = dance_df.drop(dance_df[dance_df[contestant_col] == candidate.loc[0, contestant_col]].index)
                        else:
                            dance_df.loc[dance_df.loc[:, contestant_col] == candidate.loc[0, contestant_col], init.ev] = candidate.loc[0, init.ev] - 1
                        updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                        init.inst_tree = buildInstTree(init.dance_dfs, {}, init.ev)
                        inst_tree_node = getNode(init.inst_tree, room_info)
                    # Check if current df is empty after adding the candidate
                    if dance_df.empty:
                        print("Division Empty", room_info)
                        afin_rooms[roomid] = 1
                        deleteEmpty(init.dance_dfs)  # Clean up parent levels if needed
                else:
                    consecutive += 1
                # Resolve Conflicts, if needed
                if consecutive >= init.max_conflicts:
                    resolve = resolveConflictAll(roomid, log_s, log_c, heat, heat_list, instructors_available_for_heat, init.ev)
                    dance_df = getNode(init.dance_dfs, room_info)
                    # Check if any instructors lists are now empty
                    for i, room in enumerate(instructors_available_for_heat):
                        if room != []:  # If instructors for heat not empty do nothing
                            continue
                        if afin_rooms[i] > 0:  # Must not be finished already
                            continue
                        if len(heat_roster[i]) < couples_per_floor and dance_df.shape[0] >= 1:
                            print("Adding Instructors back in, may only have a few available need to swap around contestants")
                            before_reload = instructors_available_for_heat[i].copy()
                            instructors_available_for_heat[i] = list(inst_tree_node.keys())
                            # if instructors_available_for_heat[i] == before_reload:  # If list still empty or forced, mark room as finished
                            #     print("Instructor list still empty after a refresh, mark room as finished")
                            #     afin_rooms[i] = 1
                            # elif afin_rooms[i] == 2:
                            #     print("Room is already forced a finish, not reloading instructors")
                        # else:
                        #     afin_rooms[i] = 1
                    if init.debug:
                        countInstances(heat, heat_list)
                        for check in heat_list.getRostersList():
                            checkheat(check)
                        checkheat(heat)
                    if resolve == 1:
                        failed = False
                        consecutive = 0
                    else:  # If failed to resolve
                        if not failed: # and len(instructors_available_for_heat)[roomid] < len(list(inst_tree_nodes[roomid].keys())):
                            # If first time failing try to add the instructors in the pool back into the picking list, the selection earlier might have just been unlucky in selection
                            # meaning it saved a subset of similar instructor clusters stopping the selection process from even considering them
                            failed = True
                            print("Failed to resolve conflict adding back instructors in pool for more selector options")
                            before_reload = instructors_available_for_heat[roomid].copy()
                            instructors_available_for_heat[roomid] = list(inst_tree_node.keys())
                        else:
                            afin_rooms[roomid] = 2  # force a finish
                            print("Failed to resolve conflict, forcing finish", room_info)
                # Determine if the room is finished
                if len(heat_roster[roomid]) == couples_per_floor:
                    afin_rooms[roomid] = 1
                if len(instructors_available_for_heat[roomid]) == 0:
                    print("Instructors for", room_info, "all gone")
                    if len(heat_roster[roomid]) < couples_per_floor and dance_df.shape[0] >= 1:
                        print("Adding Instructors back in, may only have a few available")
                        before_reload = instructors_available_for_heat[roomid].copy()
                        instructors_available_for_heat[roomid] = list(inst_tree_node.keys())
                        if instructors_available_for_heat[roomid] == before_reload:  # If list still empty or forced, mark room as finished
                            print("Instructor list still empty after a refresh, mark room as finished")
                            afin_rooms[roomid] = 1
                        elif afin_rooms[roomid] == 2:
                            print("Room is already forced a finish, not reloading instructors")
                            afin_rooms[roomid] = 2
                    else:
                        afin_rooms[roomid] = 1
                # Determine if backfill needed
                if afin_rooms[roomid] > 0 and dance_df[init.ev].sum() < acceptablecouples:
                    if dance_df.shape[0] != 0 and heat_list.getDivisionHoleCount(room_info) > 0:
                        backfill(dance_df, room_info, heat_list, couples_per_floor, init.ev)
                        updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                        deleteEmpty(init.dance_dfs)
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
                    else:
                        print("Not enough holes to backfill")
                if init.dance_dfs.get("A") is None:
                    for i, info in enumerate(afin_rooms):
                        if afin_rooms[i] == 0:
                            afin_rooms[i] = 1
                # Determine if heat finished
                if (afin_rooms.count(1) + afin_rooms.count(2)) == len(a_floors):
                    break