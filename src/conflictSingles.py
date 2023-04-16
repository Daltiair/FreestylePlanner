import math
import pandas as pd
import init
from conflict import solvedLogic
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictLog, \
    ResolverConflictItemCouple
from nconflictSingles import ResolveNOrderSingles
import traceback


def resolveConflictSingles(roomid, dance_df, log, heat, heat_list, instructors_available_for_heat, ev):
    resolverLog = ResolverConflictLog()
    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    if init.debug:
        for level in instructors_available_for_heat:
            print(level)
    if init.solution == 0:
        init.solution[0] = 1  # start the solution logic
    if init.solved[0] == -1:  # Termination after solution number is 10
        return -1

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
    order = 1  # set the starting order
    init.presolved = init.solved.copy()
    # presolved = init.presolved[order-1]
    solution_num = 0  # set the starting solution number for this order
    while nordersolved:
        # loop over all conflicts for this heat's roomid
        for con_num, conflict in enumerate(conflicts):
            try:
                # Gather data
                nconflict_counter = 0
                print("")
                print("1st order of", conflict.getInstructor(), 'code', conflict.getCode(), "solvoing for roomid", roomid, heat.getDiv()[roomid])
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
                    conflict_entry = heat.getRoster()[conflict_room][conflict_index].copy(True)
                    inst_tree_node = getNode(init.inst_tree, conflict_div)
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
                        if possible_inst != conflict_inst and possible_inst not in instructors_list and (possible_inst not in log.getInstructorsList(roomid)):
                            solution_num += 1
                            if init.solution[order-1] > solution_num:
                                print("Solution already attemped moving to another solution")
                                continue
                            solvedLogic(order-1)
                            # instructors_in_heat[conflict_room][conflict_index] = possible_inst  # redundant
                            instructor_data = init.df_inst[init.df_inst["Dancer #"] == possible_inst].reset_index(drop=True)
                            conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                            conflict_entry.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                            conflict_entry.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                            heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                            log.clearConflict(conflict_inst, -1)
                            log.clearConflict(possible_inst, -1)  # Clear the one changed to as well
                            if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                instructors_available_for_heat[conflict_room].append(conflict_inst)
                            if possible_inst in instructors_available_for_heat[conflict_room]:
                                instructors_available_for_heat[conflict_room].remove(possible_inst)
                            print("Resolved Conflict by changing instructor", conflict_inst, "to", possible_inst,
                                  "matched with contestant", conflict_entry.loc[0, contestant_col])
                            return 1
                        elif possible_inst != conflict_inst:
                            # Find index of this nth conflict
                            for i, room in enumerate(instructors_in_heat):
                                if possible_inst in room:
                                    nconflict_index = room.index(possible_inst)
                                    nconflict_room = i
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    resolverconflict = ResolverConflictItemSingle(1, nconflict_div, -1, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, possible_inst, conflict, [])
                                    nconflict_counter += 1
                                    resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, 'Internal Conflict with Inst', possible_inst, "div", nconflict_div)
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
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "instructor", conflict_inst, "div", nconflict_div)
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
                                raise Exception("Instructor is in Singles list", conflict_inst)
                        if sing_dup:
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                            nconflict_counter += 1
                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room,nconflict_index, "contestant", conflict_contestant, 'div', nconflict_div)
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
                                raise Exception("Instructor is in Couple list", conflict_inst)
                        if sing_dup:
                            resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, swapper)
                            nconflict_counter += 1
                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,"contestant", conflict_contestant, 'div', nconflict_div)
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
                                    if inst in instructors:
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
                                        raise Exception("Instructor is in Couple list", inst)
                                # if no conflicts make the swap with entry index i
                                if not dup: #and inst not in log.getInstructorsList(roomid):
                                    solution_num += 1
                                    if init.solution[order - 1] > solution_num:
                                        print("Solution already attemped moving to another solution")
                                        index_iter += 1
                                        dup = False
                                        continue
                                    solvedLogic(order - 1)
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
                        print("Other Heat")
                        tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                        print('Heat in question')
                        heat.replaceContestant(conflict_room, conflict_index, tmp)
                        if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                            instructors_available_for_heat[conflict_room].append(conflict_inst)
                        if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                            instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                        log.clearConflict(conflict_inst, -1)
                        log.clearConflict(heat.getInstructors()[conflict_room][conflict_index], -1)
                        print("Resolved Conflict by swapping out", conflict_contestant, conflict_inst, "and in", heat.getSingles()[conflict_room][conflict_index], heat.getInstructors()[conflict_room][conflict_index], "from heat", heat_index)
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
                    inst2sing_node = getNode(init.inst2sing_tree, heat.getDiv()[roomid])
                    inst_tree_node = getNode(init.inst_tree, heat.getDiv()[roomid])
                    print(inst2sing_node, heat.getDiv()[roomid])
                    possible_matches = inst2sing_node[free_inst]
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
                                conflict_entry = heat.getRoster()[conflict_room][conflict_index].copy(True)
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
                                possible_changes = inst2sing_node[conflict_inst]
                                for fix in possible_changes:
                                    if dance_df[dance_df[contestant_col] == fix].empty or fix in singles_list:
                                        continue
                                    solution_num += 1
                                    if init.solution[order-1] > solution_num:
                                        print("Solution already attemped moving to another solution")
                                        continue
                                    solvedLogic(order-1)
                                    same_inst = conflict_entry.loc[0, inst_col]  # save the inst, pair with new contestant
                                    same_fname = conflict_entry.loc[0, inst_fname]  # save the inst, pair with new contestant
                                    same_lname = conflict_entry.loc[0, inst_lname]  # save the inst, pair with new contestant
                                    tree_prechanges = list(inst_tree_node.keys())
                                    # Add the removed entry to the pool, make sure to add back to inst tree as well
                                    contestant_data = dance_df[dance_df[contestant_col] == fix].reset_index(drop=True)
                                    if dance_df[dance_df[contestant_col] == each].empty:
                                        print("adding", each, "back to the pool", conflict_div)
                                        conflict_entry.loc[0, inst_fname] = ""
                                        conflict_entry.loc[0, inst_lname] = ""
                                        conflict_entry.loc[0, inst_col] = ""
                                        conflict_entry.loc[0, init.ev] = 1
                                        dance_df = pd.concat([dance_df, conflict_entry])
                                        updateDanceDfs(init.dance_dfs, dance_df, conflict_div, conflict_div)
                                    else:
                                        dance_df.loc[dance_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] = dance_df.loc[dance_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] + 1
                                    conflict_entry = contestant_data.copy(True)
                                    conflict_entry.loc[0, inst_col] = same_inst
                                    conflict_entry.loc[0, inst_fname] = same_fname
                                    conflict_entry.loc[0, inst_lname] = same_lname
                                    tmp = heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                                    # Remove newly placed entry from pool
                                    if dance_df.loc[dance_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev].values[0] == 1:
                                        dance_df = dance_df.reset_index(drop=True)
                                        dance_df = dance_df.drop(dance_df[dance_df[contestant_col] == contestant_data.loc[0, contestant_col]].index)
                                        print("Removing", contestant_data.loc[0, contestant_col], "from pool")
                                        updateDanceDfs(init.dance_dfs, dance_df, conflict_div, conflict_div)
                                    else:
                                        dance_df.loc[dance_df[contestant_col] == contestant_data.loc[0, contestant_col], ev] = contestant_data.loc[0, ev] - 1
                                    if not dance_df[dance_df.loc[:, ev] < 0].empty:
                                        pass
                                    updateDanceDfs(init.dance_dfs, dance_df, conflict_div, conflict_div)
                                    init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                                    inst_tree_node = getNode(init.inst_tree, conflict_div)
                                    # Only add in new instructors due to this switch
                                    instructors_available_for_heat[roomid].extend([z for z in list(inst_tree_node.keys()) if z not in init.starting_instructors_for_heat[roomid]])
                                    instructors_available_for_heat[roomid].extend([z for z in list(inst_tree_node.keys()) if z not in tree_prechanges])
                                    set(instructors_available_for_heat[roomid])
                                    log.clearConflict(conflict_inst, -1)
                                    print("Resolved Conflict by swapping", each, conflict_inst, "to contestant", contestant_data.loc[0, contestant_col], contestant_data.loc[0, inst_col])
                                    return 1

                    # Check if conflict can be swapped with an entry in a previous heat
                    # loop heat_list and check metadata
                    print("No internal Contestant fix found checking prev heats, count", heat_list.getHeatCount())
                    for i, conflict_contestant in enumerate(check_in_heat):
                        # TODO also look if contestants are in the pool if not the swaps are useless
                        conflict_room = room_of_conflict[i]
                        conflict_index = index_of_conflict[i]
                        conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                        conflict_div = heat.getDiv()[conflict_room]
                        conflict_entry = heat.getRoster()[conflict_room][conflict_index].copy(True)
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
                            for j, every in enumerate(placed_inst):
                                if conflict_contestant in every:
                                    sing_dup = True
                                    raise Exception("Single Contestant is in Instructor list", conflict_contestant)
                                if conflict_inst in every:
                                    nconflict_index = every.index(conflict_inst)
                                    nconflict_room = j
                                    nconflict_div = each.getDiv()[nconflict_room]
                                    inst_dup = True
                            if inst_dup:
                                nconflict_counter += 1
                                resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, [check_in_heat, free_inst, swapper])
                                resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "instructor", conflict_inst, 'div', nconflict_div)
                                dup = True
                            # Check this heats singles
                            placed_sing = each.getSingles()
                            inst_dup = False
                            sing_dup = False
                            for j, every in enumerate(placed_sing):
                                if conflict_contestant in every:
                                    nconflict_index = every.index(conflict_contestant)
                                    nconflict_room = j
                                    nconflict_div = each.getDiv()[nconflict_room]
                                    sing_dup = True
                                if conflict_inst in every:
                                    inst_dup = True
                                    raise Exception("Instructor is in Singles list", conflict_inst)
                            if sing_dup:
                                nconflict_counter += 1
                                resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", conflict_contestant, "div", nconflict_div)
                                dup = True
                            # Check this heats singles
                            placed_coup = each.getCouples()
                            inst_dup = False
                            sing_dup = False
                            for j, every in enumerate(placed_coup):
                                if conflict_contestant in every:
                                    sing_dup = True
                                    nconflict_room = j
                                    nconflict_index = every.index(conflict_contestant)
                                    nconflict_div = each.getiv()[nconflict_room]
                                if conflict_inst in every:
                                    raise Exception("Instructor is in Couple list", conflict_inst)
                            if sing_dup:
                                nconflict_counter += 1
                                resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", conflict_contestant, "div", nconflict_div)
                                dup = True
                            if dup:
                                continue
                            # Find an entry in the previous heat room that has no conflicts with current heat
                            if each.getDiv().count(conflict_div) > 1:
                                past_heat_iter = each.getDiv().count(conflict_div)
                            else:
                                past_heat_iter = 1
                            start_at = 0
                            for z in range(past_heat_iter):  # Catches any heat that has multi same division floors
                                swapping_room = each.getDiv().index(conflict_div, start_at)
                                start_at = swapping_room
                                index_iter = 0
                                index_2_swap = -1
                                for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
                                    if contestant in possible_matches:  # If the contestant is in possible matches then it won't solve anything
                                        if inst != free_inst:  # If the instructor is also the one trying to be use it will solve nothing
                                            index_iter += 1
                                            continue
                                    swappee = [heat_index, swapping_room, index_iter]
                                    for j, singles in enumerate(heat.getSingles()):
                                        if contestant in singles:
                                            dup = True
                                            nconflict_index = singles.index(contestant)
                                            nconflict_room = j
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            nconflict_counter += 1
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "contestant", contestant)
                                    for j, instructors in enumerate(heat.getInstructors()):
                                        if inst in instructors:
                                            dup = True
                                            nconflict_index = instructors.index(inst)
                                            nconflict_room = j
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            # Confclit to check og heat of nth conflict
                                            # nconflict_counter += 1
                                            # resolverconflict = ResolverConflictItemSingle(3, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [check_in_heat, free_inst])
                                            # resolverLog.addConflict(resolverconflict)
                                            # To check prev heat with nth conflict
                                            nconflict_counter += 1
                                            resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), "instructor", inst)
                                    for j, couples in enumerate(heat.getCouples()):
                                        if contestant in couples:
                                            dup = True
                                            nconflict_index = couples.index(contestant)
                                            nconflict_room = j
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            nconflict_counter += 1
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(5, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLog.addConflict(resolverconflict, con_num, nconflict_counter)
                                        if inst in couples:
                                            dup = True
                                            raise Exception("Instructor is in Couple list", inst)
                                    # if no conflicts make the swap with entry index i
                                    if not dup:
                                        solution_num += 1
                                        if init.solution[order - 1] > solution_num:
                                            print("Solution already attemped moving to another solution")
                                            index_iter += 1
                                            dup = False
                                            continue
                                        solvedLogic(order - 1)
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
                            print("Other Heat")
                            tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                            print('Heat in question')
                            heat.replaceContestant(conflict_room, conflict_index, tmp)
                            # Update instructor metadata for this heat
                            # add instructor back into instructor list only if not in list and still in Instructor tree
                            if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                instructors_available_for_heat[conflict_room].append(conflict_inst)
                            if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                                instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                            log.clearConflict(conflict_inst, -1)
                            log.clearConflict(heat.getInstructors()[conflict_room][conflict_index], -1)
                            print("Resolved Conflict by swapping out", conflict_contestant, conflict_inst, "and in", heat.getSingles()[conflict_room][conflict_index], heat.getInstructors()[conflict_room][conflict_index], "from heat", heat_index)
                            return 1
            except Exception:
                print(traceback.format_exc())
                print()
        # Try to solve 2+ order conflicts
        print("No 1st order solutions found")
        # If the next order has not been attempted yet, stops resetting solution if stuck between orders
        if init.solution[order] == 0:
            init.solution[order] = 1
        if init.solved[order] == -1:  # Termination after solution number reaches max
            return -1
        resolve = ResolveNOrderSingles(log, resolverLog, order+1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])  # Update dance_df from a potential nth change
        if init.debug:
            countInstances(heat, heat_list)
            for level in instructors_available_for_heat:
                print(level)
            for check in heat_list.getRostersList():
                checkheat(check)
            checkheat(heat)
        if resolve != -1:
            nordersolved = True
            resolverLog.clearConflicts()
        else:
            return -1
