import init
from init import *
import random
from Structures import ConflictItemSingle
from conflictSingles import resolveConflictSingles
from conflict import resetSolutionLogic
from debug import countInstances, checkheat
from methods import backfill


def selectionSingles(heat, heat_list, s_floors, sfin_rooms, instructors_available_for_heat, log, couples_per_floor, acceptablecouples):
    heat_key = heat.getKey()
    instructors_in_heat = heat.getInstructors()
    singles_in_heat = heat.getSingles()
    couples_in_heat = heat.getCouples()
    heat_roster = heat.getRoster()
    selection_finished = False
    while not selection_finished:
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
                dance_df = getNode(init.dance_dfs, room_info)
                inst_tree_node = getNode(init.inst_tree, room_info)
                inst = random.choice(instructors_available_for_heat[roomid])  # get random instructor, will throw error if list at index is empty
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
                        init.logString += "\n" + str(candidate.loc[0, contestant_col]) + str(inst) + str('room') + str(
                            roomid)
                        resetSolutionLogic()
                        log.clearConflict(inst, -1)  # Clear the conflict from all rooms for this newply placed inst
                        # Remove the placed candidate from the df, or -1 if multi-entry
                        if candidate.loc[:, init.ev][0] == 1:
                            print("removing", candidate.loc[:, contestant_col][0], "from pool")
                            dance_df = dance_df.reset_index(drop=True)
                            dance_df = dance_df.drop(
                                dance_df[dance_df[contestant_col] == candidate.loc[0, contestant_col]].index)
                        else:
                            dance_df.loc[dance_df.loc[:, contestant_col] == candidate.loc[0, contestant_col], init.ev] = \
                            candidate.loc[0, init.ev] - 1
                        updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
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
                    resolve = resolveConflictSingles(roomid, dance_df, log, heat, heat_list,
                                                     instructors_available_for_heat, init.ev)
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
                            print(
                                "Adding Instructors back in, may only have a few available need to swap around contestants")
                            before_reload = instructors_available_for_heat[i].copy()
                            instructors_available_for_heat[i] = list(inst_tree_node.keys())
                            if instructors_available_for_heat[
                                i] == before_reload:  # If list still empty or forced, mark room as finished
                                print("Instructor list still empty after a refresh, mark room as finished")
                                sfin_rooms[i] = 1
                            elif sfin_rooms[i] == 2:
                                print("Room is already forced a finish, not reloading instructors")
                        else:
                            sfin_rooms[i] = 1
                    if resolve == 1:
                        failed = False
                        consecutive = 0
                    elif not failed:  # and len(instructors_available_for_heat)[roomid] < len(list(inst_tree_nodes[roomid].keys())):
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
                        print(
                            "Adding Instructors back in, may only have a few available need to swap around contestants")
                        before_reload = instructors_available_for_heat[roomid].copy()
                        instructors_available_for_heat[roomid] = list(inst_tree_node.keys())
                        if instructors_available_for_heat[
                            roomid] == before_reload:  # If list still empty or forced, mark room as finished
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
                        backfill(dance_df, room_info, heat_list, couples_per_floor, init.ev)
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
                    print("Singles Empty for", init.ev)
                    for i, info in enumerate(sfin_rooms):
                        if sfin_rooms[i] == 0:
                            sfin_rooms[i] = 1
                # Determine if heat finished
                if (sfin_rooms.count(1) + sfin_rooms.count(2)) == len(s_floors):
                    selection_finished = True
                    print("Singles Selection Finished for heat", heat_key)