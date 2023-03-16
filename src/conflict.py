import math
import pandas as pd
import init
from init import getNode, updateDanceDfs, buildInstTree
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictLog, \
    ResolverConflictItemCouple


def resolveConflictSingles(roomid, dance_df, inst_tree_nodes, log, heat, heat_list, solved, instructors_available_for_heat, inst2sing_tree_nodes, ev):
    resolverLog = ResolverConflictLog()
    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    presolved = solved

    roomlog = log.getRoomlog()
    mode_inst = roomlog[roomid]["mode_inst"][0]
    # mode_code = roomlog[roomid]["mode_code"]
    roomdiv = roomlog[roomid]["div"]
    conflicts = []

    # get all conflicts with mode instructor first
    for each in roomlog[roomid]["conf_list"]:
        if each.getInstructor() == mode_inst:
            conflicts.append(each)
    # get all other conflicts
    for each in roomlog[roomid]["conf_list"]:
        if each.getInstructor() != mode_inst:
            conflicts.append(each)

    nordersolved = True
    conflictlisti = 0
    while nordersolved:
        # loop over all conflicts for this heat's roomid
        for con_num, conflict in enumerate(conflicts):
            # Gather data
            nconflict_counter = 0
            print("")
            print("1st order of", conflict.getInstructor(), 'code', conflict.getCode())
            instructors_list = []
            conflict_inst = conflict.getInstructor()

            # if the instructor is not free
            if conflict.getCode() == 1:
                # Locate where instructor taken and whom with
                for i, each in enumerate(instructors_in_heat):
                    if conflict_inst in each:
                        conflict_room = i
                        conflict_index = each.index(conflict_inst)
                        conflict_div = heat.getDiv()[conflict_room]
                        conflict_contestant = singles_in_heat[conflict_room][conflict_index]
                    for every in each:
                        instructors_list.append(every)
                print("Instructor in question", conflict_inst, 'paired with', conflict_contestant, 'in room', conflict_room, conflict_div)
                swapper = [-1, conflict_room, conflict_index]
                conflict_entry = heat.getRoster()[conflict_room][conflict_index]
                # Set column variables based on single type
                if conflict_entry.loc[0, "type id"] == "L":
                    contestant_col = "Lead Dancer #"
                    cont_fname = "Lead First Name"
                    cont_lname = "Lead Last Name"
                    inst_col = "Follow Dancer #"
                    inst_fname = "Follow First Name"
                    inst_lname = "Follow Last Name"
                elif conflict_entry.loc[0, "type id"] == "F":
                    contestant_col = "Follow Dancer #"
                    cont_fname = "Follow First Name"
                    cont_lname = "Follow Last Name"
                    inst_col = "Lead Dancer #"
                    inst_fname = "Lead First Name"
                    inst_lname = "Lead Last Name"
                else:
                    raise Exception("Type id for " + conflict_entry + " is invalid")
                # See if that contestant has another free instructor
                for possible_inst in conflict_entry.loc[0, "Instructor Dancer #'s"]:
                    # if instructor is not conflict instructor and not being used in heat
                    if possible_inst != conflict_inst and possible_inst not in instructors_list and solved < 10:
                        solved += 1
                        instructors_in_heat[conflict_room][conflict_index] = possible_inst  # redundant
                        instructor_data = init.df_inst[init.df_inst["Dancer #"] == possible_inst].reset_index(drop=True)
                        conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                        conflict_entry.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                        conflict_entry.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                        heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                        break
                    elif possible_inst != conflict_inst and solved < 35:
                        # Find index of this nth conflict
                        for i, room in enumerate(instructors_in_heat):
                            if possible_inst in room:
                                nconflict_index = room.index(possible_inst)
                                nconflict_room = i
                                nconflict_div = heat.getDiv()[nconflict_room]
                        resolverconflict = ResolverConflictItemSingle(1, nconflict_div, -1, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, possible_inst, conflict, [])
                        nconflict_counter += 1
                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, 'Internal Conflict with Inst', possible_inst)
                if presolved != solved:
                    log.clearConflict(conflict_inst, -1)
                    log.clearConflict(possible_inst, -1)  # Clear the one changed to as well
                    instructors_available_for_heat[conflict_room].append(conflict_inst)
                    if possible_inst in instructors_available_for_heat[conflict_room]:
                        instructors_available_for_heat[conflict_room].remove(possible_inst)
                    print("Resolved Conflict by changing instructor", conflict_inst, "to", possible_inst, "contestant", conflict_entry.loc[0, contestant_col])
                    return 1
                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                print('No internal instructor fix found checking prev heats, count', heat_list.getHeatCount())
                if heat_list.getDivisionHeatCount(conflict_div) == 0:
                    print("No prev heats with this division")
                for heat_index, each in enumerate(heat_list.getRostersList()):
                    # Check if heat has division
                    if conflict_div not in each.getDiv():
                        continue
                    # Check this heat's instructors
                    placed_inst = each.getInstructors()
                    dup = False
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_inst):
                        if conflict_contestant in every:
                            sing_dup = True
                            raise Exception("Single Contestant is in Instructor list")
                        if conflict_inst in every:
                            nconflict_index = every.index(conflict_inst)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            inst_dup = True
                    if inst_dup:
                        resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, swapper)
                        nconflict_counter += 1
                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room,nconflict_index, "instructor", conflict_inst)
                        dup = True
                    # Check this heats singles
                    placed_sing = each.getSingles()
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_sing):
                        if conflict_contestant in every:
                            nconflict_index = every.index(conflict_contestant)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            sing_dup = True
                        if conflict_inst in every:
                            inst_dup = True
                            raise Exception("Instructor is in Singles list ")
                    if sing_dup:
                        resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                        nconflict_counter += 1
                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room,nconflict_index, "contestant", conflict_contestant)
                        dup = True
                    # Check this heats singles
                    placed_coup = each.getCouples()
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_coup):
                        if conflict_contestant in every:
                            sing_dup = True
                            nconflict_room = i
                            nconflict_index = every.index(conflict_contestant)
                            nconflict_div = each.getDiv()[nconflict_room]
                        if conflict_inst in every:
                            raise Exception("Instructor is in Couple list ")
                    if sing_dup:
                        resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                        nconflict_counter += 1
                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,"contestant", conflict_contestant)
                        dup = True
                    if dup:
                        continue
                    # Find an entry in the previous heat room that has no conflicts with current heat
                    if each.getDiv().count(conflict_div) > 1:
                        past_heat_iter = each.getDiv().count(conflict_div)
                    else:
                        past_heat_iter = 1
                    start_at = 0
                    for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                        swapping_room = each.getDiv().index(conflict_div, start_at)
                        print("Looking for Swappee in heat, room", heat_index, swapping_room)
                        start_at = swapping_room
                        index_iter = 0
                        index_2_swap = -1
                        for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
                            swappee = [heat_index, swapping_room, index_iter]
                            for i, singles in enumerate(heat.getSingles()):
                                if contestant in singles and contestant != conflict_contestant: # make sure the conflict is not because it has some inst trying to be freed
                                    dup = True
                                    nconflict_index = singles.index(contestant)
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    # Conflict to check the og heat entry nth conflict
                                    # TODO I think checking the OG entry may cause an issue or unneeded checks because changing the initial conflict could make the solution invalid
                                    # resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [])
                                    # resolverLog.addConflict(resolverconflict)
                                    # conflict to check the previous heat entry nth conflict
                                    resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper,swappee])
                                    nconflict_counter += 1
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "contestant", contestant)
                            for i, instructors in enumerate(heat.getInstructors()):
                                if inst in instructors and inst != conflict_inst: # make sure the conflict is not because it has some inst trying to be freed
                                    dup = True
                                    nconflict_index = instructors.index(inst)
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    nconflict_counter += 1
                                    # Conflict to check the og heat entry nth conflict
                                    resolverconflict = ResolverConflictItemSingle(3, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [swapper,swappee])
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # conflict to check the previous heat entry nth conflict
                                    resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee])
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
                                          placed_inst[swapping_room].index(inst), 'inst', inst)
                            for i, couples in enumerate(heat.getCouples()):
                                if contestant in couples:
                                    dup = True
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    nconflict_index = couples.index(contestant)
                                    nconflict_counter += 1
                                    resolverconflict = ResolverConflictItemSingle(5, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper,swappee])
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                if inst in couples:
                                    dup = True
                                    raise Exception("Instructor is in Couple list ")
                            # if no conflicts make the swap with entry index i
                            if not dup:
                                index_2_swap = index_iter
                                break
                            index_iter += 1
                            dup = False
                        if not dup:
                            break
                    # if no suitable entry found, continue to another heat
                    if index_2_swap == -1:
                        continue
                    # if there are no duplicates, swap
                    solved += 1
                    tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                    heat.replaceContestant(conflict_room, conflict_index, tmp)
                    instructors_available_for_heat[conflict_room].append(conflict_inst)
                    if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                        instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                    break
                if presolved != solved:
                    log.clearConflict(conflict_inst, -1)
                    print("Resolved Conflict by swapping", conflict_contestant, conflict_inst, "and", heat.getSingles()[conflict_room][conflict_index], heat.getInstructors()[conflict_room][conflict_index], "from heat", heat_index)
                    return 1

            # If there are no free contestants
            if conflict.getCode() == 2:
                check_in_heat = []
                room_of_conflict = []
                index_of_conflict = []
                free_inst = conflict_inst  # The instructor to be matched with a single
                singles_list = []
                for each in singles_in_heat:
                    for every in each:
                        singles_list.append(every)
                # Check all possible singles to be matched with
                possible_matches = inst2sing_tree_nodes[roomid][free_inst]
                for each in possible_matches:
                    # For every room
                    print('Contestant in question', each)
                    for i, every in enumerate(singles_in_heat):
                        if each in every:  # if room has a possible match for this instructor
                            check_in_heat.append(each)
                            room_of_conflict.append(i)
                            index_of_conflict.append(every.index(each))
                            # Find index of this conflict
                            conflict_index = every.index(each)
                            conflict_room = i
                            conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                            conflict_entry = heat.getRoster()[conflict_room][conflict_index]
                            conflict_div = heat.getDiv()[conflict_room]
                            if conflict_entry.loc[0, "type id"] == "L":
                                contestant_col = "Lead Dancer #"
                                cont_fname = "Lead First Name"
                                cont_lname = "Lead Last Name"
                                inst_col = "Follow Dancer #"
                                inst_fname = "Follow First Name"
                                inst_lname = "Follow Last Name"
                            elif conflict_entry.loc[0, "type id"] == "F":
                                contestant_col = "Follow Dancer #"
                                cont_fname = "Follow First Name"
                                cont_lname = "Follow Last Name"
                                inst_col = "Lead Dancer #"
                                inst_fname = "Lead First Name"
                                inst_lname = "Lead Last Name"
                            else:
                                raise Exception("Type id for ", conflict_entry, " is invalid")
                            # Look over possible changes to see if the placed one could change
                            possible_changes = inst2sing_tree_nodes[conflict_room][conflict_inst]
                            for fix in possible_changes:
                                if dance_df[roomid][dance_df[roomid][contestant_col] == fix].empty or fix in singles_list:
                                    continue
                                solved += 1
                                # Add the removed entry to the pool, make sure to add back to inst tree as well
                                contestant_data = dance_df[roomid][dance_df[roomid][contestant_col] == fix].reset_index(drop=True)
                                if dance_df[roomid][dance_df[roomid][contestant_col] == each].empty:
                                    conflict_entry.loc[0, inst_fname] = ""
                                    conflict_entry.loc[0, inst_lname] = ""
                                    conflict_entry.loc[0, inst_col] = ""
                                    dance_df[roomid] = pd.concat([dance_df[roomid], conflict_entry])
                                else:
                                    dance_df[roomid].loc[dance_df[roomid].loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] = dance_df[roomid].loc[dance_df[roomid].loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] + 1
                                singles_in_heat[conflict_room][conflict_index] = fix  # redundant
                                # conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                                conflict_entry.loc[0, inst_fname] = contestant_data.loc[0, cont_fname]
                                conflict_entry.loc[0, inst_lname] = contestant_data.loc[0, cont_lname]
                                conflict_entry.loc[0, contestant_col] = contestant_data.loc[0, contestant_col]
                                tmp = heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                                # Remove newly placed entry from pool
                                if dance_df[roomid].loc[dance_df[roomid].loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev].values[0] == 1:
                                    dance_df[roomid] = dance_df[roomid].drop(dance_df[roomid][dance_df[roomid][contestant_col] == contestant_data.loc[0, contestant_col]].index)
                                    updateDanceDfs(init.dance_dfs, dance_df[roomid], conflict_div)
                                else:
                                    dance_df[roomid].loc[dance_df[roomid][contestant_col] == contestant_data.loc[0, contestant_col], ev] = contestant_data.loc[0, ev] - 1
                                init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                                inst_tree_nodes[roomid] = getNode(init.inst_tree, conflict_div)
                                if presolved != solved:
                                    log.clearConflict(conflict_inst, -1)
                                    print("Resolved Conflict by swapping", each, conflict_inst, "to contestant", contestant_data.loc[0, contestant_col], contestant_data.loc[0, inst_col])
                                    return 1

                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                print("No internal Contestant fix found checking prev heats, count", heat_list.getHeatCount())
                for i, conflict_contestant in enumerate(check_in_heat):
                    conflict_room = room_of_conflict[i]
                    conflict_index = index_of_conflict[i]
                    conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                    conflict_div = heat.getDiv()[conflict_room]
                    swapper = [-1, conflict_room, conflict_index]
                    print('Contestant in question', conflict_contestant)
                    if heat_list.getDivisionHeatCount(conflict_div) == 0:
                        print("No prev heats with this division", conflict_div)
                    for heat_index, each in enumerate(heat_list.getRostersList()):
                        # Check if heat has division
                        if conflict_div not in each.getDiv():
                            continue
                        # Check this heat's instructors
                        placed_inst = each.getInstructors()
                        dup = False
                        inst_dup = False
                        sing_dup = False
                        for i, every in enumerate(placed_inst):
                            if conflict_contestant in every:
                                sing_dup = True
                                raise Exception("Single Contestant is in Instructor list")
                            if conflict_inst in every:
                                nconflict_index = every.index(conflict_inst)
                                nconflict_room = i
                                nconflict_div = each.getDiv()[nconflict_room]
                                inst_dup = True
                        if inst_dup:
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, [check_in_heat, free_inst, swapper])
                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                  "instructor", conflict_inst)
                            dup = True
                        # Check this heats singles
                        placed_sing = each.getSingles()
                        inst_dup = False
                        sing_dup = False
                        for i, every in enumerate(placed_sing):
                            if conflict_contestant in every:
                                nconflict_index = every.index(conflict_contestant)
                                nconflict_room = i
                                nconflict_div = each.getDiv()[nconflict_room]
                                sing_dup = True
                            if conflict_inst in every:
                                inst_dup = True
                                raise Exception("Instructor is in Singles list ")
                        if sing_dup:
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                  "contestant", conflict_contestant)
                            dup = True
                        # Check this heats singles
                        placed_coup = each.getCouples()
                        inst_dup = False
                        sing_dup = False
                        for i, every in enumerate(placed_coup):
                            if conflict_contestant in every:
                                sing_dup = True
                                nconflict_room = i
                                nconflict_index = every.index(conflict_contestant)
                                nconflict_div = each.getiv()[nconflict_room]
                            if conflict_inst in every:
                                raise Exception("Instructor is in Couple list ")
                        if sing_dup:
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index,
                                  "contestant", conflict_contestant)
                            dup = True
                        if dup:
                            continue
                        # Find an entry in the previous heat room that has no conflicts with current heat
                        if each.getDiv().count(conflict_div) > 1:
                            past_heat_iter = each.getDiv().count(conflict_div)
                        else:
                            past_heat_iter = 1
                        start_at = 0
                        for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                            swapping_room = each.getDiv().index(conflict_div, start_at)
                            start_at = swapping_room
                            index_iter = 0
                            index_2_swap = -1
                            for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
                                swappee = [heat_index, swapping_room, index_iter]
                                for i, singles in enumerate(heat.getSingles()):
                                    if contestant in singles or contestant in possible_matches:  # If the contestant is in possible matches then it won't solve anything
                                        dup = True
                                        if contestant in singles and contestant != conflict_contestant:
                                            nconflict_index = singles.index(contestant)
                                            nconflict_room = i
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            nconflict_counter += 1
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                        # To check prev heat with nth conflict
                                        resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
                                              placed_sing[swapping_room].index(contestant), "contestant", contestant)
                                for i, instructors in enumerate(heat.getInstructors()):
                                    if (inst in instructors and inst != conflict_inst) or inst == free_inst:  # If the instructor is also the one trying to be use it will solve nothing
                                        dup = True
                                        if inst in instructors and inst != conflict_inst:
                                            nconflict_index = instructors.index(inst)
                                            nconflict_room = i
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            # Confclit to check og heat of nth conflict
                                            # resolverconflict = ResolverConflictItemSingle(3, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [check_in_heat, free_inst])
                                            # resolverLog.addConflict(resolverconflict)
                                        # To check prev heat with nth conflict
                                        nconflict_counter += 1
                                        resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
                                              placed_inst[swapping_room].index(inst), "instructor", inst)
                                for i, couples in enumerate(heat.getCouples()):
                                    if contestant in couples or contestant in possible_matches:
                                        dup = True
                                        if contestant in couples:
                                            nconflict_index = couples.index(contestant)
                                            nconflict_room = i
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            nconflict_counter += 1
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(5, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    if inst in couples:
                                        dup = True
                                        raise Exception("Instructor is in Couple list ")
                                # if no conflicts make the swap with entry index i
                                if not dup:
                                    index_2_swap = index_iter
                                    break
                                index_iter += 1
                                dup = False
                            if not dup:
                                break
                        # if no suitable entry found, continue to another heat
                        if index_2_swap == -1:
                            continue
                        # if there are no duplicates, swap
                        solved += 1
                        tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                        heat.replaceContestant(conflict_room, conflict_index, tmp)
                        # Update instructor metadata for this heat
                        instructors_available_for_heat[conflict_room].append(conflict_inst)
                        if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                            instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                        break
                if presolved != solved:
                    log.clearConflict(conflict_inst, -1)
                    print("Resolved Conflict by swapping", conflict_contestant, conflict_inst, "and ", heat.getSingles()[conflict_room][conflict_index], heat.getInstructors()[conflict_room][conflict_index],"from heat", heat_index)
                    return 1
        # TODO if all else fails try swapping with a pool entry
        # Try to solve 2+ order conflicts
        if presolved == solved:
            print("No 1st order solutions found")
            order = 2
            maxorder = 3
            resolve = ResolveNOrderSingles(resolverLog, solved, order, maxorder, heat, heat_list, dance_df, inst_tree_nodes, roomid, instructors_available_for_heat, ev)
            if resolve != -1:
                nordersolved = True
                resolverLog.clearConflicts()
            else:
                return -1
        else:
            log.clearConflict(conflict_inst, -1)


def ResolveNOrderSingles(resolverlog, solved, order, maxorder, heat, heat_list, dance_df, inst_tree_nodes, roomid, instructors_available_for_heat, ev):
    resolverLogn = ResolverConflictLog()
    conflicts = resolverlog.getRoomlog()

    # Loop over N order Conflicts
    conflictlisti = 0
    nordersolved = True  # assume the nth order is solved
    while nordersolved:
        while conflictlisti < len(conflicts['conf_list']):
            # Get metadata
            nconflict_counter = 0
            print()
            conflict = conflicts["conf_list"][conflictlisti]
            i = conflictlisti
            if order == 2:
                print(order, "order solution of", conflict.getPrevConflict().getInstructor(), "code", conflict.getPrevConflict().getCode())
            else:
                print(order, "order solution of", conflict.getPrevConflict().getConflictNumber(), "code", conflict.getCode())
            print("solving for conflict #", conflicts["print_index"][i])

            conflict_heat_index = conflicts["heat_index"][i]
            conflict_room = conflicts["roomid"][i]
            conflict_index = conflict.getNConflictIndex()
            conflict_div = conflicts['div'][i]
            nminus = conflicts["nminus"][i]
            con_num = conflictlisti
            aux = conflict.getAux()

            if conflict_heat_index != -1:
                conflict_heat = heat_list.getRostersList()[conflict_heat_index]
            else:
                conflict_heat = heat

            singles_in_heat = conflict_heat.getSingles()
            singles_in_conflict = conflict.getContestants()
            instructors_in_heat = conflict_heat.getInstructors()
            instructors_in_conflict = conflict.getInstructors()
            conflict_entry = conflict_heat.getRoster()[conflict_room][conflict.getNConflictIndex()]

            instructors_to_compare = instructors_in_heat
            singles_to_compare = singles_in_heat

            conflict_contestant = singles_in_heat[conflict_room][conflict_index]
            conflict_inst = instructors_in_heat[conflict_room][conflict_index]

            # Set column variables based on single type
            if conflict_entry.loc[0, "type id"] == "L":
                contestant_col = "Lead Dancer #"
                cont_fname = "Lead First Name"
                cont_lname = "Lead Last Name"
                inst_col = "Follow Dancer #"
                inst_fname = "Follow First Name"
                inst_lname = "Follow Last Name"
            elif conflict_entry.loc[0, "type id"] == "F":
                contestant_col = "Follow Dancer #"
                cont_fname = "Follow First Name"
                cont_lname = "Follow Last Name"
                inst_col = "Lead Dancer #"
                inst_fname = "Lead First Name"
                inst_lname = "Lead Last Name"
            else:
                raise Exception("Type id for " + conflict_entry + " is invalid")

            # if the instructor is not free
            if conflict.getCode() == 1 or conflict.getCode() == 3:
                # Get meta data
                print("Instructor in question", conflict.getConflictNumber(), 'paired with', conflict_contestant, 'in heat', conflict_heat_index)
                conflict_inst = conflict.getConflictNumber()
                instructors_list = []
                for each in instructors_to_compare:
                    for every in each:
                        instructors_list.append(every)
                swapper = [conflict_heat_index, conflict_room, conflict_index]
                # See if contestant has another free instructor to rid conflict
                for possible_inst in conflict_entry.loc[0, "Instructor Dancer #'s"]:
                    # if instructor is not conflict instructor and not being used in heat
                    if possible_inst != conflict_inst and possible_inst not in instructors_list and solved < 5:
                        instructors_in_heat[conflict_room][conflict_index] = possible_inst  # redundant
                        instructor_data = init.df_inst[init.df_inst["Dancer #"] == possible_inst].reset_index(drop=True)
                        conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                        conflict_entry.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                        conflict_entry.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                        conflict_heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                        if conflict_heat_index == -1:
                            instructors_available_for_heat[conflict_room].append(conflict_inst)
                            if possible_inst in instructors_available_for_heat[conflict_room]:
                                instructors_available_for_heat[conflict_room].remove(possible_inst)
                        print("Resolved " + str(order) + " order conflict by changing instructor", conflict_inst, "to", possible_inst, "in heat", conflict_heat_index)
                        return nminus
                    elif possible_inst != conflict_inst:
                        # Find index of this nth conflict
                        for i, room in enumerate(instructors_to_compare):
                            if possible_inst in room:
                                nconflict_index = room.index(possible_inst)
                                nconflict_room = i
                                nconflict_div = conflict_heat.getDiv()[nconflict_room] # TODO have repeating conflicts here
                        try:
                            resolverconflict = ResolverConflictItemSingle(1, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, possible_inst, conflict, swapper)
                            nconflict_counter += 1
                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                            print('Internal Conflict with Inst', possible_inst)
                        except:
                            print("nconflict error")
                            pass
                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                print("No internal solution found checking prev heats")
                if heat_list.getDivisionHeatCount(conflict_div) == 0:
                    print("No prev heats with this division")
                for heat_index, each in enumerate(heat_list.getRostersList()):
                    # Check if same heat as heat in question
                    if heat_index == conflict_heat_index:
                        continue
                    # Check if heat has division
                    if conflict_div not in each.getDiv():
                        continue
                    # Check this heat's instructors
                    placed_inst = each.getInstructors()
                    dup = False
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_inst):
                        if conflict_contestant in every:
                            sing_dup = True
                            raise Exception("Single Contestant is in Instructor list")
                        if conflict_inst in every:
                            nconflict_index = every.index(conflict_inst)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            inst_dup = True
                    if inst_dup:
                        resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, swapper)
                        nconflict_counter += 1
                        resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                        print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "instructor", conflict_inst)
                        dup = True
                    # Check this heats singles
                    placed_sing = each.getSingles()
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_sing):
                        if conflict_contestant in every:
                            nconflict_index = every.index(conflict_contestant)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            sing_dup = True
                        if conflict_inst in every:
                            inst_dup = True
                            raise Exception("Instructor is in Singles list ")
                    if sing_dup:
                        resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                        nconflict_counter += 1
                        resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                        print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                              "contestant", conflict_contestant)
                        dup = True
                    # Check this heats singles
                    placed_coup = each.getCouples()
                    inst_dup = False
                    sing_dup = False
                    for i, every in enumerate(placed_coup):
                        if conflict_contestant in every:
                            sing_dup = True
                            nconflict_room = i
                            nconflict_index = every.index(conflict_contestant)
                            nconflict_div = each.getDiv()[nconflict_room]
                        if conflict_inst in every:
                            raise Exception("Instructor is in Couple list ")
                    if sing_dup:
                        resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                        nconflict_counter += 1
                        resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                        print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                              "contestant", conflict_contestant)
                        dup = True
                    if dup:
                        continue
                    # Find an entry in the previous heat room that has no conflicts with current heat
                    if each.getDiv().count(conflict_div) > 1:
                        past_heat_iter = each.getDiv().count(conflict_div)
                    else:
                        past_heat_iter = 1
                    start_at = 0
                    for j in range(past_heat_iter):
                        swapping_room = each.getDiv().index(conflict_div, start_at)
                        start_at = swapping_room
                        index_iter = 0
                        index_to_swap = -1
                        for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
                            swappee = [heat_index, swapping_room, index_iter]
                            for i, singles in enumerate(singles_to_compare):
                                if contestant in singles:
                                    dup = True
                                    nconflict_index = singles.index(contestant)
                                    nconflict_room = i
                                    nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                    # nth Conflict in the og heat, only need to check it will work with the heat to swap
                                    resolverconflict = ResolverConflictItemSingle(4, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper,swappee])
                                    nconflict_counter += 1
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # To check prev heat with nth conflict, only check it will work with the heat to swap
                                    resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper,swappee])
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                          placed_sing[swapping_room].index(contestant), "contestant", contestant)
                            for i, instructors in enumerate(conflict_heat.getInstructors()):
                                if inst in instructors:
                                    dup = True
                                    nconflict_index = instructors.index(inst)
                                    nconflict_room = i
                                    nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                    # Conflict in the og heat
                                    resolverconflict = ResolverConflictItemSingle(3, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [swapper,swappee])
                                    nconflict_counter += 1
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # To check prev heat with nth conflict
                                    resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper,swappee])
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                          placed_sing[swapping_room].index(contestant), "instructor", inst)
                            for i, couples in enumerate(conflict_heat.getCouples()):
                                if contestant in couples:
                                    dup = True
                                    nconflict_index = couples.index(contestant)
                                    nconflict_room = i
                                    nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                    # Conflict in the og heat
                                    resolverconflict = ResolverConflictItemSingle(5, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper,swappee])
                                    nconflict_counter += 1
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # To check prev heat with nth conflict
                                    resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper,swappee])
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                          placed_sing[swapping_room].index(contestant), "contestant", contestant)
                                if inst in couples:
                                    dup = True
                                    raise Exception("Instructor is in Couple list ")
                            # if no conflicts make the swap with entry index i
                            if not dup:
                                index_2_swap = index_iter
                                break
                            index_iter += 1
                            dup = False
                        if not dup:
                            break
                    # if no suitable entry found, continue to another heat
                    if index_2_swap == -1:
                        continue
                    # if there are no duplicates, swap
                    tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                    conflict_heat.replaceContestant(conflict_room, conflict_index, tmp)
                    if conflict_heat_index == -1:
                        instructors_available_for_heat[conflict_room].append(conflict_inst)
                        if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                            instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                    print("Resolved " + str(order) + " order conflict by swapping", conflict_contestant, conflict_inst, "and", conflict_heat.getSingles()[conflict_room][conflict_index], conflict_heat.getInstructors()[conflict_room][conflict_index], "in heats", heat_index, conflict_heat_index)
                    return nminus

            # If there are no free contestants
            if conflict.getCode() == 2 or conflict.getCode() == 4:
                check_in_heat = []
                room_of_conflict = []
                index_of_conflict = []
                free_inst = conflict_inst  # The instructor to be matched with a single
                singles_list = []
                instructors_list = []
                for each in singles_to_compare:
                    for every in each:
                        singles_list.append(every)
                for each in instructors_to_compare:
                    for every in each:
                        instructors_list.append(every)
                if conflict_heat_index == -1:  # If the conflict is in the og heat set df pool as oone to modify and check
                    conflict_df = dance_df[conflict_room]
                else:  # If the conflict attempting a resolve is in external heat, set df as one in dance df
                    conflict_df = getNode(init.dance_dfs, conflict_div)
                # Check all possible singles to be matched with
                inst2sing_tree_node = getNode(init.inst2sing_tree, conflict_div)
                possible_matches = inst2sing_tree_node[free_inst]
                for each in possible_matches:
                    # For every room
                    for i, every in enumerate(singles_to_compare):
                        if each in every:  # if room has a possible match for this instructor
                            print("Contestant in question", each, "paired with", conflict_heat.getInstructors()[conflict_room][singles_to_compare[i].index(each)], "in heat", conflict_heat_index)
                            check_in_heat.append(each)
                            room_of_conflict.append(i)
                            index_of_conflict.append(every.index(each))
                            # Find index of this conflict
                            for i, room in enumerate(singles_to_compare):
                                if each in room:
                                    conflict_index = room.index(each)
                                    conflict_room = i
                                    conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                                    conflict_entry = conflict_heat.getRoster()[conflict_room][conflict_index]
                                    if conflict_entry.loc[0, "type id"] == "L":
                                        contestant_col = "Lead Dancer #"
                                        cont_fname = "Lead First Name"
                                        cont_lname = "Lead Last Name"
                                        inst_col = "Follow Dancer #"
                                        inst_fname = "Follow First Name"
                                        inst_lname = "Follow Last Name"
                                    elif conflict_entry.loc[0, "type id"] == "F":
                                        contestant_col = "Follow Dancer #"
                                        cont_fname = "Follow First Name"
                                        cont_lname = "Follow Last Name"
                                        inst_col = "Lead Dancer #"
                                        inst_fname = "Lead First Name"
                                        inst_lname = "Lead Last Name"
                                    else:
                                        raise Exception("Type id for " + conflict_entry + " is invalid")
                            # Look over possible changes to see if the place one could change
                            possible_changes = inst2sing_tree_node[conflict_inst]
                            for fix in possible_changes:
                                if conflict_df[conflict_df[contestant_col] == fix].empty or fix in singles_list:
                                    continue
                                # Add the removed entry back to the pool
                                contestant_data = conflict_df[conflict_df[contestant_col] == fix].reset_index(drop=True)
                                if conflict_df[conflict_df[contestant_col] == each].empty:
                                    conflict_entry.loc[0, inst_fname] = ""
                                    conflict_entry.loc[0, inst_lname] = ""
                                    conflict_entry.loc[0, inst_col] = ""
                                    conflict_df = pd.concat([conflict_df, conflict_entry])
                                    if conflict_heat_index != -1:  # If the conflict is in a previous heat update the df tree
                                        updateDanceDfs(init.dance_dfs, conflict_df, conflict_div)
                                    else:
                                        dance_df[conflict_room] = conflict_df  # if conflict in og heat update the dance_df list
                                else:
                                    conflict_df.loc[conflict_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] = conflict_df.loc[conflict_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] + 1
                                for num in conflict_entry.loc[:, "Instructor Dancer #'s"][0]:  # Add these instructors back into the tree
                                    if conflict_div in heat.getDiv():  # If the conflict div is part of heats selection, add instructor data to the tree node
                                        if inst_tree_nodes[heat.getDiv().index(conflict_div)].get(num) is None:
                                            inst_tree_nodes[conflict_room][num] = 1
                                            if num not in instructors_available_for_heat[conflict_room] and num != conflict_inst:
                                                instructors_available_for_heat[conflict_room].appped(num)
                                        else:
                                            inst_tree_nodes[conflict_room][num] += 1
                                singles_in_heat[conflict_room][conflict_index] = fix  # redundant
                                # conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                                conflict_entry.loc[0, inst_fname] = contestant_data.loc[0, cont_fname]
                                conflict_entry.loc[0, inst_lname] = contestant_data.loc[0, cont_lname]
                                conflict_entry.loc[0, contestant_col] = contestant_data.loc[0, contestant_col]
                                tmp = conflict_heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                                # Remove newly placed entry from pool
                                if conflict_df.loc[conflict_df[contestant_col] == conflict_entry.loc[0, contestant_col], ev].values[0] == 1:
                                    conflict_df = conflict_df.drop(conflict_df[conflict_df[contestant_col] == contestant_data.loc[0, contestant_col]].index)
                                    if conflict_heat_index != -1:  # If the conflict is in a previous heat update the df tree
                                        init.dance_dfs = updateDanceDfs(init.dance_dfs, conflict_df, conflict_div)
                                    else:
                                        dance_df[conflict_room] = conflict_df  # if conflict in og heat update the dance_df list
                                        init.dance_dfs = updateDanceDfs(init.dance_dfs, conflict_df, conflict_div)
                                else:
                                    conflict_df.loc[conflict_df.loc[:, contestant_col] == contestant_data.loc[0, contestant_col], ev] = contestant_data.loc[0, ev] - 1
                                init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                                if conflict_div in heat.getDiv():
                                    inst_tree_nodes[heat.getDiv().index(conflict_div)] = getNode(init.inst_tree, conflict_div)
                                print("Resolved " + str(order) + " order conflict by swapping", conflict_contestant, conflict_inst, "to", contestant_data.loc[0,contestant_col], contestant_data.loc[0,inst_col], "in heat", conflict_heat_index)
                                return nminus

                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                    print("no internal solution found checking past heats")
                    for i, conflict_contestant in enumerate(check_in_heat):
                        conflict_room = room_of_conflict[i]
                        conflict_index = index_of_conflict[i]
                        conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                        conflict_div = conflict_heat.getDiv()[conflict_room]
                        print("Contestant in question", conflict_contestant)
                        if heat_list.getDivisionHeatCount(conflict_div) == 0:
                            print("No prev heats with this division")
                        swapper = [conflict_heat_index, conflict_room, conflict_index]
                        for heat_index, each in enumerate(heat_list.getRostersList()):
                            # Check if heat has division
                            if conflict_div not in each.getDiv():
                                continue
                            if conflict_heat_index == heat_index:
                                continue
                            # Check this heat's instructors
                            placed_inst = each.getInstructors()
                            dup = False
                            inst_dup = False
                            sing_dup = False
                            for i, every in enumerate(placed_inst):
                                if conflict_contestant in every:
                                    sing_dup = True
                                    raise Exception("Single Contestant is in Instructor list")
                                if conflict_inst in every:
                                    nconflict_index = every.index(conflict_inst)
                                    nconflict_room = i
                                    nconflict_div = each.getDiv()[nconflict_room]
                                    inst_dup = True
                            if inst_dup:
                                resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                      "contestant", conflict_contestant)
                                dup = True
                            # Check this heats singles
                            placed_sing = each.getSingles()
                            inst_dup = False
                            sing_dup = False
                            for i, every in enumerate(placed_sing):
                                if conflict_contestant in every:
                                    nconflict_index = every.index(conflict_contestant)
                                    nconflict_room = i
                                    nconflict_div = each.getDiv()[nconflict_room]
                                    sing_dup = True
                                if conflict_inst in every:
                                    inst_dup = True
                                    raise Exception("Instructor is in Singles list ")
                            if sing_dup:
                                resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                      "instructor", conflict_inst)
                                dup = True
                            # Check this heats singles
                            placed_coup = each.getCouples()
                            inst_dup = False
                            sing_dup = False
                            for i, every in enumerate(placed_coup):
                                if conflict_contestant in every:
                                    sing_dup = True
                                    nconflict_room = i
                                    nconflict_index = every.index(conflict_contestant)
                                    nconflict_div = each.getDiv()[nconflict_room]
                                if conflict_inst in every:
                                    raise Exception("Instructor is in Couple list ")
                            if sing_dup:
                                resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                      "contestant", conflict_contestant)
                                dup = True
                            if dup:
                                continue
                            # Find an entry in the previous heat room that has no conflicts with current heat
                            if each.getDiv().count(conflict_div) > 1:
                                past_heat_iter = each.getDiv().count(conflict_div)
                            else:
                                past_heat_iter = 1
                            start_at = 0
                            for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                                swapping_room = each.getDiv().index(conflict_div, start_at)
                                start_at = swapping_room
                                index_iter = 0
                                index_to_swap = -1
                                for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
                                    swappee = [heat_index, swapping_room, index_iter]
                                    for i, singles in enumerate(conflict_heat.getSingles()):
                                        if contestant in singles or contestant in possible_matches:  # If the contestant is in possible matches then it won't solve anything
                                            dup = True
                                            nconflict_counter += 1
                                            if contestant in singles:
                                                nconflict_index = singles.index(contestant)
                                                nconflict_room = i
                                                nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                                # Conflict to check og heat of nth conflict
                                                resolverconflict = ResolverConflictItemSingle(4, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room] , contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                                  placed_sing[swapping_room].index(contestant), "instructor", inst)
                                    for i, instructors in enumerate(conflict_heat.getInstructors()):
                                        if inst in instructors or inst == free_inst:  # If the instructor is also the one trying to be use it will solve nothing
                                            dup = True
                                            nconflict_index = instructors.index(inst)
                                            nconflict_room = i
                                            nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(3, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            nconflict_counter += 1
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                                  placed_sing[swapping_room].index(contestant), "contestant", contestant)
                                    for i, couples in enumerate(conflict_heat.getCouples()):
                                        if contestant in couples or contestant in possible_matches:
                                            dup = True
                                            nconflict_counter += 1
                                            if contestant in couples:
                                                nconflict_index = couples.index(contestant)
                                                nconflict_room = i
                                                nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                                # Conflict to check og heat of nth conflict
                                                resolverconflict = ResolverConflictItemSingle(5, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print("Swappee conflict in heat,room,index", heat_index, swapping_room,
                                                  placed_sing[swapping_room].index(contestant), "contestant", contestant)
                                        if inst in couples:
                                            dup = True
                                            raise Exception("Instructor is in Couple list ")
                                    # if no conflicts make the swap with entry index i
                                    if not dup:
                                        index_2_swap = index_iter
                                        break
                                    index_iter += 1
                                    dup = False
                                if not dup:
                                    break
                            # if no suitable entry found, continue to another heat
                            if index_2_swap == -1:
                                continue
                            # if there are no duplicates, swap
                            tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                            conflict_heat.replaceContestant(conflict_room, conflict_index, tmp)
                            if conflict_heat_index == -1:
                                instructors_available_for_heat[conflict_room].append(conflict_inst)
                                if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                                    instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                            print("Resolved " + str(order) + " order conflict by swapping", conflict_contestant, conflict_inst, "and", conflict_heat.getSingles()[conflict_room][conflict_index], conflict_heat.getInstructors()[conflict_room][conflict_index], "in heats", heat_index, conflict_heat_index)
                            return nminus
            conflictlisti += 1
        print("no", order, 'solutions found')
        if order < maxorder:
            resolve = ResolveNOrderSingles(resolverLogn, order + 1, maxorder, heat, heat_list, dance_df, inst_tree_nodes, roomid, instructors_available_for_heat, ev)
            if resolve != -1:
                conflictlisti = resolve
            else:
                return -1
        else:
            return -1
        resolverLogn.clearConflicts()


def resolveConflictCouples(roomid, dance_df, inst_tree_nodes, log, heat, heat_list, solved, instructors_available_for_heat, inst2sing_tree_nodes, ev):

    resolverLog = ResolverConflictLog()
    # Create a new log for the singles conflicts
    singlelog = ConflictLog()

    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    couples_in_heat = heat.getCouples()
    presolved = solved

    conflicts = []
    roomlog = log.getRoomlog()
    mode_cont = roomlog[roomid]["mode_cont"][0]

    # get all conflicts with mode instructor first
    for each in roomlog[roomid]["conf_list"]:
        if each.getLead() == mode_cont and each.getCode() != 2:
            conflicts.append(each)
    # get other conflicts
    for each in roomlog[roomid]["conf_list"]:
        if each.getLead() != mode_cont and each.getCode != 2:
            conflicts.append(each)
    # add single conflicts last
    for each in roomlog[roomid]["conf_list"]:
        if each.getCode == 2:
            conflicts.append(each)

    nordersolved = True
    conflictlisti = 0
    while nordersolved:
        # loop over all conflicts for this heat's roomid
        for con_num, conflict in enumerate(conflicts):
            # Gather data
            nconflict_counter = 0
            print("")
            print("1st order of", conflict.getLead(), conflict.getFollow(), 'code', conflict.getCode())
            couples_list = []
            conflict_lead = conflict.getLead()
            conflict_follow = conflict.getFollow()

            # If the conflict involves a Singles entry
            if conflict.getCode() == 2:
                for i, each in enumerate(singles_in_heat):  # Locate the conflicts with the singles
                    if conflict_lead in each or conflict_follow in each:  # Make sure to account for both Lead and Follow, both could be in this heat's single room(s)
                        nconflict_room = i
                        if conflict_lead in each:
                            nconflict_index = each.index(conflict_lead)
                        if conflict_follow in each:
                            nconflict_index = each.index(conflict_follow)
                        singleconflict = ConflictItemSingle(2, heat.getInstructors()[nconflict_room][nconflict_index])
                        singlelog.addConflict(singleconflict, con_num)
                # After logging the conflicts run the singles resolver, this should look to change the contestants or swap the entry out and solve any Nth conflicts to make it happen
                resolveConflictSingles(conflict_room, dance_df, inst_tree_nodes, singlelog, heat, heat_list, solved, instructors_available_for_heat, inst2sing_tree_nodes, ev)

            if conflict.getCode() == 1:
                # Locate where couples conflict is
                for i, each in enumerate(couples_in_heat):
                    if conflict_lead in each:
                        conflict_room = i
                        conflict_index = int(each.index(conflict_lead)/2)
                        conflict_div = heat.getDiv()[conflict_room]
                    if conflict_follow in each:
                        conflict_room = i
                        conflict_index = int((each.index(conflict_follow) - 1)/2)
                        conflict_div = heat.getDiv()[conflict_room]
                    for every in each:
                        couples_list.append(every)
                swapper = [-1, conflict_room, conflict_index]
                conflict_entry = heat.getRoster()[conflict_room][conflict_index]
                print("Couple in question", conflict_lead, conflict_follow, "in room", conflict_room, conflict_div)
                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                print('Checking prev heats, count', heat_list.getHeatCount())
                if heat_list.getDivisionHeatCount(conflict_div) == 0:
                    print("No prev heats with this division")
                    continue
                single_conflicts = []
                for heat_index, each in enumerate(heat_list.getRostersList()):
                    # Check if heat has division
                    if conflict_div not in each.getDiv():
                        continue
                    # Check this heat's instructors
                    placed_inst = each.getInstructors()
                    dup = False
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_inst):
                        if conflict_lead in every:
                            l_dup = True
                            raise Exception("Couples Contestant is in Instructor list")
                        if conflict_follow in every:
                            f_dup = True
                            raise Exception("Couples Contestant is in Instructor list")
                    # Check this heats singles
                    placed_sing = each.getSingles()
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_sing):
                        if conflict_lead in every:
                            l_dup = True
                            nconflict_index = int(each.index(conflict_lead)/2)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_lf = conflict_lead
                        if conflict_follow in every:
                            # Throw this in to avoid double conflicts
                            f_dup = True
                            nconflict_index = int((each.index(conflict_follow)-1)/2)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_lf = conflict_follow
                        if l_dup or f_dup:
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, couples_in_heat, singles_in_heat, [conflict_lead, conflict_follow], conflict, [])
                            single_conflicts.append([resolverconflict, con_num])
                            # resolverLog.addConflict(resolverconflict, con_num)
                            print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", nconflict_lf)
                            dup = True
                    # Check this heats couples
                    placed_coup = each.getCouples()
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_coup):
                        if conflict_lead in every:
                            if f_dup and nconflict_index == every.index(conflict_lead) and nconflict_room == i and nconflict_div == each.getDiv()[nconflict_room]:
                                pass
                            else:
                                l_dup = True
                                nconflict_room = i
                                nconflict_index = int((every.index(conflict_lead)) / 2)
                                nconflict_div = each.getDiv()[nconflict_room]
                        if conflict_follow in every:
                            # Throw this in to avoid double conflicts
                            if l_dup and nconflict_index == every.index(conflict_follow) and nconflict_room == i and nconflict_div == each.getDiv()[nconflict_room]:
                                pass
                            else:
                                f_dup = True
                                nconflict_index = int((every.index(conflict_follow) - 1) / 2)  # -1 so it is the conflict entry itself
                                nconflict_room = i
                                nconflict_div = each.getDiv()[nconflict_room]
                    if l_dup or f_dup:
                        nconflict_counter += 1
                        resolverconflict = ResolverConflictItemCouple(2, nconflict_div, heat_index, nconflict_room, nconflict_index, couples_in_heat, singles_in_heat, [conflict_lead, conflict_follow], conflict, swapper)
                        resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", [conflict_lead, conflict_follow])
                        dup = True
                    if dup:
                        continue
                    # Find an entry in the previous heat room that has no conflicts with current heat
                    if each.getDiv().count(conflict_div) > 1:
                        past_heat_iter = each.getDiv().count(conflict_div)
                    else:
                        past_heat_iter = 1
                    start_at = 0
                    for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                        swapping_room = each.getDiv().index(conflict_div, start_at)
                        print("Looking for Swappee in heat, room", heat_index, swapping_room)
                        start_at = swapping_room
                        index_iter = 0
                        index_2_swap = -1
                        for contestant in placed_coup[swapping_room]:
                            swappee = [heat_index, swapping_room, index_iter]
                            for i, singles in enumerate(heat.getSingles()):
                                if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                                    dup = True
                                    nconflict_index = singles.index(contestant)
                                    if math.fmod(nconflict_index, 2) == 1:  # If the conflict is a follower set the index to the lead as it is the same as entry
                                        nconflict_index = nconflict_index-1
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    # Conflict to check the og heat entry nth conflict
                                    resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [])
                                    single_conflicts.append([resolverconflict, con_num])
                                    # resolverLog.addConflict(resolverconflict, con_num)
                                    # conflict to check the previous heat entry nth conflict
                                    # resolverconflict = ResolverConflictItemCouple(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), singles_in_heat, contestant, conflict, [swapper, swappee])
                                    # resolverLog.addConflict(resolverconflict, con_num)
                                    print("Single-Couple Conflict, Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "contestant", contestant)
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
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    nconflict_index = couples.index(contestant)
                                    nconflict_counter += 1
                                    if math.fmod(nconflict_index, 2) == 1:  # If the conflict is a follower set the index to the lead as it is the same as entry
                                        nconflict_index = nconflict_index - 1
                                    nconflict_index = int(nconflict_index/2)
                                    resolverconflict = ResolverConflictItemCouple(2, nconflict_div, -1, nconflict_room, nconflict_index, placed_coup[swapping_room], placed_sing[swapping_room], [conflict_lead, conflict_follow], conflict, [swapper, swappee])
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print("Couple Conflict, Swappee conflict in heat,room,index", heat_index, swapping_room, placed_coup[swapping_room].index(contestant), "contestant", contestant)
                            # if no conflicts with both lead and follow, make the swap with entry index i
                            if math.fmod(index_iter, 2) == 1:
                                if not dup:
                                    index_iter -= 1
                                    index_2_swap = int(index_iter/2)
                                    break
                                dup = False
                            index_iter += 1
                        if not dup:
                            break
                    # if no suitable entry found, continue to another heat
                    if index_2_swap == -1:
                        continue
                    # if there are no duplicates, swap
                    solved += 1
                    tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                    heat.replaceContestant(conflict_room, conflict_index, tmp)
                    break
                if presolved != solved:
                    log.clearConflict(-1, [conflict_lead, conflict_follow])
                    print("Resolved Conflict by swapping", conflict_lead, conflict_follow, "and", heat.getCouples()[conflict_room][conflict_index], heat.getCouples()[conflict_room][conflict_index+1], "from heat", heat_index)
                    return 1
    order = 2
    maxorder = 3
    print("no", order-1, 'solutions found')
    if presolved == solved:
        resolve = ResolveNOrderCouples(resolverLog, order + 1, maxorder, heat, heat_list, dance_df, inst_tree_nodes, roomid, instructors_available_for_heat, ev)
        if resolve != -1:
            nordersolved = True
            resolverLog.clearConflicts()
        else:
            return -1
    resolverLog.clearConflicts()


def ResolveNOrderCouples(resolverlog, order, maxorder, heat, heat_list, dance_df, inst_tree_nodes, roomid, instructors_available_for_heat, ev):
    resolverLogn = ResolverConflictLog()
    singlelog = ConflictLog()
    conflicts = resolverlog.getRoomlog()

    # Loop over N order Conflicts
    conflictlisti = 0
    nordersolved = True  # assume the nth order is solved
    while nordersolved:
        while conflictlisti < len(conflicts['conf_list']):
            # Get metadata
            nconflict_counter = 0
            print()
            conflict = conflicts["conf_list"][conflictlisti]
            i = conflictlisti
            if order == 2:
                print(order, "order solution of", conflict.getPrevConflict().getInstructor(), "code", conflict.getPrevConflict().getCode())
            else:
                print(order, "order solution of", conflict.getPrevConflict().getConflictNumber(), "code", conflict.getCode())
            print("solving for conflict #", conflicts["print_index"][i])
            conflict_heat_index = conflicts["heat_index"][i]
            conflict_room = conflicts["roomid"][i]
            conflict_index = conflict.getNConflictIndex()
            conflict_div = conflicts['div'][i]
            nminus = conflicts["nminus"][i]
            con_num = conflictlisti
            aux = conflict.getAux()

            if conflict_heat_index != -1:
                conflict_heat = heat_list.getRostersList()[conflict_heat_index]
            else:
                conflict_heat = heat

            singles_in_heat = conflict_heat.getSingles()
            singles_in_conflict = conflict.getSingles()
            couples_in_heat = conflict_heat.getCouples()
            couples_in_conflict = conflict.getCouples()
            instructors_in_heat = conflict_heat.getInstructors()
            # instructors_in_conflict = conflict.getInstructors()
            conflict_entry = conflict_heat.getRoster()[conflict_room][conflict.getNConflictIndex()]

            # instructors_to_compare = instructors_in_conflict
            singles_to_compare = singles_in_conflict
            couples_to_compare = couples_in_conflict

            conflict_lead = conflict.getConflictNums()[0]
            conflict_follow = conflict.getConflictNums()[1]

            swapper = [-1, conflict_room, conflict_index]
            conflict_entry = heat.getRoster()[conflict_room][conflict_index]
            # conflict_inst = instructors_in_heat[conflict_room][conflict_index]

            # If the conflict involves a Singles entry, but can only be a
            if conflict.getCode() == 4:
                conflict_contestant = singles_in_heat[conflict_room][conflict_index]
                for i, each in enumerate(singles_to_compare):  # Locate the conflicts with the singles
                    if conflict_lead in each or conflict_follow in each:  # Make sure to account for both Lead and Follow, both could be in this heat's single room(s)
                        nconflict_room = i
                        if conflict_lead in each:
                            nconflict_index = each.index(conflict_lead)
                        if conflict_follow in each:
                            nconflict_index = each.index(conflict_follow)
                        singleconflict = ConflictItemSingle(2, heat.getInstructors()[nconflict_room][nconflict_index])
                        singlelog.addConflict(singleconflict, con_num)
                # After logging the conflicts run the singles resolver, this should look to change the contestants or swap the entry out and solve any Nth conflicts to make it happen
                # resolveConflictSingles(conflict_room, dance_df, inst_tree_nodes, singlelog, heat, heat_list, solved, instructors_available_for_heat, inst2sing_tree_nodes, ev)

            if conflict.getCode() == 1 or conflict.getCode() == 2:
                # Locate where couples conflict is
                couples_list = []
                for i, each in enumerate(couples_in_conflict):
                    for every in each:
                        couples_list.append(every)
                print("Couple in question", conflict_lead, conflict_follow, "in heat", conflict_heat_index)
                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                print('Checking prev heats, count', heat_list.getHeatCount())
                if heat_list.getDivisionHeatCount(conflict_div) == 0:
                    print("No prev heats with this division")
                    continue
                single_conflicts = []
                for heat_index, each in enumerate(heat_list.getRostersList()):
                    # Check if heat has division
                    if conflict_div not in each.getDiv():
                        continue
                    if conflict_heat_index == heat_index:  # If same heat skip it
                        continue
                    # Check this heat's instructors
                    placed_inst = each.getInstructors()
                    dup = False
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_inst):
                        if conflict_lead in every:
                            l_dup = True
                            raise Exception("Couples Contestant is in Instructor list")
                        if conflict_follow in every:
                            f_dup = True
                            raise Exception("Couples Contestant is in Instructor list")
                    # Check this heats singles
                    placed_sing = each.getSingles()
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_sing):
                        if conflict_lead in every:
                            l_dup = True
                            nconflict_index = every.index(conflict_lead)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_lf = conflict_lead
                        if conflict_follow in every:
                            # Throw this in to avoid double conflicts
                            f_dup = True
                            nconflict_index = every.index(conflict_follow)
                            nconflict_room = i
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_lf = conflict_follow
                        if l_dup or f_dup:
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, couples_in_heat, singles_in_heat, [conflict_lead, conflict_follow], conflict, [])
                            single_conflicts.append([resolverconflict, con_num])
                            # resolverLog.addConflict(resolverconflict, con_num)
                            print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", nconflict_lf)
                            dup = True
                    # Check this heats singles
                    placed_coup = each.getCouples()
                    l_dup = False
                    f_dup = False
                    for i, every in enumerate(placed_coup):
                        if conflict_lead in every:
                            if f_dup and nconflict_index == every.index(conflict_lead) and nconflict_room == i and nconflict_div == each.getDiv()[nconflict_room]:
                                pass
                            else:
                                l_dup = True
                                nconflict_room = i
                                nconflict_index = int(every.index(conflict_lead) / 2)
                                nconflict_div = each.getDiv()[nconflict_room]
                        if conflict_follow in every:
                            # Throw this in to avoid double conflicts
                            if l_dup and nconflict_index == every.index(conflict_follow) and nconflict_room == i and nconflict_div == each.getDiv()[nconflict_room]:
                                pass
                            else:
                                f_dup = True
                                nconflict_index = int((every.index(conflict_follow) - 1) / 2)  # -1 so it is the conflict entry itself
                                nconflict_room = i
                                nconflict_div = each.getDiv()[nconflict_room]
                    if l_dup or f_dup:
                        nconflict_counter += 1
                        resolverconflict = ResolverConflictItemCouple(5, nconflict_div, heat_index, nconflict_room, nconflict_index, couples_in_heat, singles_in_heat, [conflict_lead, conflict_follow], conflict, swapper)
                        resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                        print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", [conflict_lead, conflict_follow])
                        dup = True
                    if dup:
                        continue
                    # Find an entry in the previous heat room that has no conflicts with current heat
                    if each.getDiv().count(conflict_div) > 1:
                        past_heat_iter = each.getDiv().count(conflict_div)
                    else:
                        past_heat_iter = 1
                    start_at = 0
                    for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                        swapping_room = each.getDiv().index(conflict_div, start_at)
                        print("Looking for Swappee in heat, room", heat_index, swapping_room)
                        start_at = swapping_room
                        index_iter = 0
                        index_2_swap = -1
                        for contestant in zip(placed_coup[swapping_room]):
                            swappee = [heat_index, swapping_room, index_iter]
                            for i, singles in enumerate(heat.getSingles()):
                                if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                                    dup = True
                                    nconflict_index = singles.index(contestant)
                                    if math.fmod(nconflict_index, 2) == 1:  # If the conflict is a follower set the index to the lead as it is the same as entry
                                        nconflict_index = nconflict_index-1
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    # Conflict to check the og heat entry nth conflict
                                    resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [])
                                    single_conflicts.append([resolverconflict, con_num])
                                    # resolverLog.addConflict(resolverconflict, con_num)
                                    # conflict to check the previous heat entry nth conflict
                                    # resolverconflict = ResolverConflictItemCouple(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), singles_in_heat, contestant, conflict, [swapper, swappee])
                                    # resolverLog.addConflict(resolverconflict, con_num)
                                    print("Single-Couple Conflict, Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "contestant", contestant)
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
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    nconflict_index = couples.index(contestant)
                                    nconflict_counter += 1
                                    if math.fmod(nconflict_index, 2) == 1:  # If the conflict is a follower set the index to the lead as it is the same as entry
                                        nconflict_index = nconflict_index - 1
                                    nconflict_index = int(nconflict_index/2)
                                    resolverconflict = ResolverConflictItemCouple(2, nconflict_div, -1, nconflict_room, nconflict_index, placed_coup[swapping_room], placed_sing[swapping_room], [conflict_lead, conflict_follow], conflict, [swapper, swappee])
                                    resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, "Couple Conflict, Swappee conflict in heat,room,index", heat_index, swapping_room, placed_coup[swapping_room].index(contestant), "contestant", contestant)
                            # if no conflicts make the swap with entry index i
                            if math.fmod(index_iter, 2) == 1:
                                if not dup:
                                    index_iter -= 1
                                    index_2_swap = int(index_iter / 2)
                                    break
                                dup = False
                            index_iter += 1
                        if not dup:
                            break
                    # if no suitable entry found, continue to another heat
                    if index_2_swap == -1:
                        continue
                    # if there are no duplicates, swap
                    tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                    heat.replaceContestant(conflict_room, conflict_index, tmp)
                    break