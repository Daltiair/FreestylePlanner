import pandas as pd
import init
from conflict import solvedLogic
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictLog, \
    ResolverConflictItemCouple
import traceback


def ResolveNOrderSingles(log, resolverlog, order, heat, heat_list, roomid, instructors_available_for_heat, ev):
    resolverLogn = ResolverConflictLog()
    conflicts = resolverlog.getRoomlog()
    if init.debug:
        for level in instructors_available_for_heat:
            print(level)
    solutioncount = 0  # holds which solution in the chain I am on
    # Loop over N order Conflicts
    conflictlisti = 0
    solution_num = 0
    nordersolved = True  # assume the nth order is solved
    while nordersolved:
        while conflictlisti < len(conflicts['conf_list']):
            try:
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
                conflict_entry = conflict_heat.getRoster()[conflict_room][conflict.getNConflictIndex()].copy()

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
                    print("Instructor in question", conflict.getConflictNumber(), 'paired with', conflict_contestant, 'in heat', conflict_heat_index, conflict_div)
                    conflict_inst = conflict.getConflictNumber()
                    instructors_list = []
                    for each in instructors_to_compare:
                        for every in each:
                            instructors_list.append(every)
                    swapper = [conflict_heat_index, conflict_room, conflict_index]
                    inst_tree_node = getNode(init.inst_tree, conflict_div)
                    # See if contestant has another free instructor to rid conflict
                    for possible_inst in conflict_entry.loc[0, "Instructor Dancer #'s"]:
                        # if instructor is not conflict instructor and not being used in heat
                        if possible_inst != conflict_inst and possible_inst not in instructors_list:
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
                            conflict_heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                            if conflict_heat_index == -1:
                                if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                    instructors_available_for_heat[conflict_room].append(conflict_inst)
                                if possible_inst in instructors_available_for_heat[conflict_room]:
                                    instructors_available_for_heat[conflict_room].remove(possible_inst)
                                log.clearConflict(possible_inst, -1)  # Clear out the conflict of new instructor
                                log.clearConflict(conflict_inst, -1)  # Clear out the conflict of the new instructor
                            print("Resolved " + str(order) + " order conflict by changing instructor", conflict_inst, "to", possible_inst, "in heat", conflict_heat_index, conflict_div)
                            return nminus
                        elif possible_inst != conflict_inst:
                            # Find index of this nth conflict
                            for j, room in enumerate(instructors_to_compare):
                                if possible_inst in room:
                                    nconflict_index = room.index(possible_inst)
                                    nconflict_room = j
                                    nconflict_div = conflict_heat.getDiv()[nconflict_room] # TODO have repeating conflicts here
                            resolverconflict = ResolverConflictItemSingle(1, nconflict_div, conflict_heat_index,
                                                                          nconflict_room, nconflict_index,
                                                                          instructors_in_heat, singles_in_heat,
                                                                          possible_inst, conflict, swapper)

                            nconflict_counter += 1
                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, 'Internal Conflict with Inst', possible_inst)
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
                                raise Exception("Single Contestant is in Instructor list", conflict_contestant)
                            if conflict_inst in every:
                                nconflict_index = every.index(conflict_inst)
                                nconflict_room = i
                                nconflict_div = each.getDiv()[nconflict_room]
                                inst_dup = True
                        if inst_dup:
                            resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, swapper)
                            nconflict_counter += 1
                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
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
                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                  "contestant", conflict_contestant, "div", nconflict_div)
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
                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                  "contestant", conflict_contestant, "div", nconflict_div)
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
                            index_2_swap = -1
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
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
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
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "instructor", inst, "Conflict for Heat in question")
                                        # To check prev heat with nth conflict
                                        nconflict_counter += 1
                                        resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper,swappee])
                                        resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
                                              placed_sing[swapping_room].index(contestant), "instructor", inst, " Conflict for heat to swap from")
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
                                        print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "contestant", contestant)
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
                        conflict_heat.replaceContestant(conflict_room, conflict_index, tmp)
                        if conflict_heat_index == -1:
                            if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                instructors_available_for_heat[conflict_room].append(conflict_inst)
                            if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                                instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                            log.clearConflict(conflict_inst, -1)
                            log.clearConflict(conflict_heat.getInstructors()[conflict_room][conflict_index], -1)
                        print("Resolved " + str(order) + " order conflict by swapping out", conflict_contestant, conflict_inst, "and in", conflict_heat.getSingles()[conflict_room][conflict_index], conflict_heat.getInstructors()[conflict_room][conflict_index], "in heats", heat_index, conflict_heat_index)
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
                    # Check all possible singles to be matched with
                    conflict_df = getNode(init.dance_dfs, conflict_div)
                    inst_tree_node = getNode(init.inst_tree, conflict_div)
                    inst2sing_node = getNode(init.inst2sing_tree, conflict_div)
                    possible_matches = inst2sing_node[free_inst]
                    for each in possible_matches:
                        if type(conflict_df) != dict:  # If this is a past heat that has finsihed already skip looking into pool
                            # For every room
                            for i, every in enumerate(singles_to_compare):
                                if each in every:  # if room has a possible match for this instructor
                                    print("Contestant in question", each, "paired with", conflict_heat.getInstructors()[conflict_room][singles_to_compare[i].index(each)], "in heat", conflict_heat_index, conflict_div)
                                    check_in_heat.append(each)
                                    room_of_conflict.append(i)
                                    index_of_conflict.append(every.index(each))
                                    # Find index of this conflict
                                    for j, room in enumerate(singles_to_compare):
                                        if each in room:
                                            conflict_index = room.index(each)
                                            conflict_room = j
                                            conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                                            conflict_entry = conflict_heat.getRoster()[conflict_room][conflict_index].copy(True)
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
                                    possible_changes = inst2sing_node[conflict_inst]
                                    for fix in possible_changes:
                                        if conflict_df[conflict_df[contestant_col] == fix].empty or fix in singles_list:
                                            continue
                                        solution_num += 1
                                        if init.solution[order-1] > solution_num:
                                            print("Solution already attemped moving to another solution")
                                            continue
                                        solvedLogic(order-1)
                                        same_inst = conflict_entry.loc[0, inst_col]  # save the inst, pair with new contestant
                                        same_fname = conflict_entry.loc[0, inst_fname]  # save the inst, pair with new contestant
                                        same_lname = conflict_entry.loc[0, inst_lname]  # save the inst, pair with new contestant
                                        if conflict_div in heat.getDiv():
                                            tree_prechanges = list(inst_tree_node.keys())
                                        # Add the removed entry back to the pool
                                        contestant_data = conflict_df[conflict_df[contestant_col] == fix].reset_index(drop=True)
                                        if conflict_df[conflict_df[contestant_col] == each].empty:
                                            conflict_entry.loc[0, inst_fname] = ""
                                            conflict_entry.loc[0, inst_lname] = ""
                                            conflict_entry.loc[0, inst_col] = ""
                                            conflict_entry.loc[0, init.ev] = 1
                                            print("adding", each, "to the df")
                                            conflict_df = pd.concat([conflict_df, conflict_entry])
                                            updateDanceDfs(init.dance_dfs, conflict_df, conflict_div, conflict_div)
                                        else:
                                            print("increment", each, "by 1")
                                            conflict_df.loc[conflict_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] = conflict_df.loc[conflict_df.loc[:, contestant_col] == conflict_entry.loc[0, contestant_col], ev] + 1
                                        # Insert entry to Heat
                                        conflict_entry = contestant_data.copy(True)
                                        conflict_entry.loc[0, inst_col] = same_inst
                                        conflict_entry.loc[0, inst_fname] = same_fname
                                        conflict_entry.loc[0, inst_lname] = same_lname
                                        tmp = conflict_heat.replaceContestant(conflict_room, conflict_index, conflict_entry)
                                        # Remove newly placed entry from pool
                                        if conflict_df.loc[conflict_df[contestant_col] == conflict_entry.loc[0, contestant_col], ev].values[0] == 1:
                                            print("removing", fix, "from the df pool")
                                            conflict_df = conflict_df.reset_index(drop=True)
                                            conflict_df = conflict_df.drop(conflict_df[conflict_df[contestant_col] == contestant_data.loc[0, contestant_col]].index)
                                            updateDanceDfs(init.dance_dfs, conflict_df, conflict_div, conflict_div)
                                        else:
                                            print("decrement", fix, "from the df")
                                            conflict_df.loc[conflict_df.loc[:, contestant_col] == contestant_data.loc[0, contestant_col], ev] = contestant_data.loc[0, ev] - 1
                                        updateDanceDfs(init.dance_dfs, conflict_df, conflict_div, conflict_div)
                                        init.inst_tree = buildInstTree(init.dance_dfs, {}, ev)
                                        # If a division that is in current heat
                                        if conflict_div in heat.getDiv():
                                            roominq = heat.getDiv().index(conflict_div)
                                            inst_tree_node = getNode(init.inst_tree, conflict_div)
                                            print("adding to inst list", [z for z in list(inst_tree_node.keys()) if z not in init.starting_instructors_for_heat[roominq]])
                                            print("adding to inst list", [z for z in list(inst_tree_node.keys()) if z not in tree_prechanges])
                                            instructors_available_for_heat[roominq].extend([z for z in list(inst_tree_node.keys()) if z not in init.starting_instructors_for_heat[roominq]])
                                            instructors_available_for_heat[roominq].extend([z for z in list(inst_tree_node.keys()) if z not in tree_prechanges])
                                            set(instructors_available_for_heat[roominq])
                                        print("Resolved " + str(order) + " order conflict by swapping", conflict_contestant, conflict_inst, "to contestant", contestant_data.loc[0,contestant_col], "in heat", conflict_heat_index)
                                        return nminus

                    # Check if conflict can be swapped with an entry in a previous heat
                    # loop heat_list and check metadata
                    print("no internal solution found checking past heats")
                    for i, conflict_contestant in enumerate(check_in_heat):
                        conflict_room = room_of_conflict[i]
                        conflict_index = index_of_conflict[i]
                        conflict_inst = instructors_in_heat[conflict_room][conflict_index]
                        conflict_div = conflict_heat.getDiv()[conflict_room]
                        conflict_entry = conflict_heat.getRoster()[conflict_room][conflict_index].copy(True)
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
                                resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_inst, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", conflict_contestant, "div", nconflict_div)
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
                                resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "instructor", conflict_inst, "div", nconflict_div)
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
                                    nconflict_div = each.getDiv()[nconflict_room]
                                if conflict_inst in every:
                                    raise Exception("Instructor is in Couple list", conflict_inst)
                            if sing_dup:
                                resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room, nconflict_index, instructors_in_heat, singles_in_heat, conflict_contestant, conflict, [check_in_heat, free_inst, swapper])
                                nconflict_counter += 1
                                resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index,
                                      "contestant", conflict_contestant, "div", nconflict_div)
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
                                    swappee = [heat_index, swapping_room, index_iter]
                                    if contestant in possible_matches:  # If the contestant is in possible matches then it won't solve anything
                                        if inst != free_inst:  # If the instructor switched is the one to be freed it will not solve the conflict
                                            index_iter += 1
                                            continue
                                    for j, singles in enumerate(conflict_heat.getSingles()):
                                        if contestant in singles:
                                            dup = True
                                            nconflict_counter += 1
                                            nconflict_index = singles.index(contestant)
                                            nconflict_room = j
                                            nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room] , contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            nconflict_counter += 1
                                            resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_sing[swapping_room].index(contestant), "Contestant", contestant, nconflict_div)
                                    for j, instructors in enumerate(conflict_heat.getInstructors()):
                                        if inst in instructors:
                                            dup = True
                                            nconflict_index = instructors.index(inst)
                                            nconflict_room = j
                                            nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                            # Conflict to check og heat of nth conflict
                                            # resolverconflict = ResolverConflictItemSingle(3, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            # nconflict_counter += 1
                                            # resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            nconflict_counter += 1
                                            resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index, swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), "instructor", inst, nconflict_div)
                                    for j, couples in enumerate(conflict_heat.getCouples()):
                                        if contestant in couples:
                                            dup = True
                                            nconflict_counter += 1
                                            nconflict_index = couples.index(contestant)
                                            nconflict_room = j
                                            nconflict_div = conflict_heat.getDiv()[nconflict_room]
                                            # Conflict to check og heat of nth conflict
                                            resolverconflict = ResolverConflictItemSingle(5, nconflict_div, conflict_heat_index, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            nconflict_counter += 1
                                            resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index, swapping_room, placed_sing[swapping_room].index(contestant), instructors_in_heat, singles_in_heat, contestant, conflict, [swapper, swappee, check_in_heat, free_inst])
                                            resolverLogn.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index, swapping_room,
                                                  placed_sing[swapping_room].index(contestant), "contestant", contestant, nconflict_div)
                                            if inst in couples:
                                                dup = True
                                                raise Exception("Instructor is in Couple list", inst)
                                    # if no conflicts make the swap with entry index
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
                            conflict_heat.replaceContestant(conflict_room, conflict_index, tmp)
                            if conflict_heat_index == -1:  # if working on the current heat
                                if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                    instructors_available_for_heat[conflict_room].append(conflict_inst)
                                if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                                    instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                                log.clearConflict(conflict_inst, -1)  # Clear out the inst swapped out
                                log.clearConflict(conflict_heat.getInstructors()[conflict_room][conflict_index], -1)  # Clear out the inst swapped in if there
                            print("Resolved " + str(order) + " order conflict by swapping in", conflict_contestant, conflict_inst, "and out", conflict_heat.getSingles()[conflict_room][conflict_index], conflict_heat.getInstructors()[conflict_room][conflict_index], "in heats", heat_index, conflict_heat_index)
                            return nminus
                conflictlisti += 1
            except Exception:
                print(traceback.format_exc())
                conflictlisti += 1
        print("no", order, 'solutions found')
        if order < init.maxorder:
            # If the next order has not been attempted yet, stops resetting solution if stuck between orders
            if init.solution[order] == 0:
                init.solution[order] = 1
            if init.solved[order] == -1:  # Termination after solution number is 10
                return -1
            resolve = ResolveNOrderSingles(log, resolverLogn, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
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
            if resolve != -1:
                conflictlisti = resolve-1  # -1 because index starts at 0
                resolverLogn.clearConflicts()  # clear conflicts, avoid repeating conflicts of previous n order solves
            else:
                return -1
        else:
            return -1


        