import math
import pandas as pd
import init
from conflict import solvedLogic
from conflictSingles import resolveConflictSingles
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictItemCouple
from Heat import Heat, HeatList
from ConflictLog import ConflictLog, ResolverConflictLog
from nconflictCouples import ResolveNOrderCouples
import traceback


def resolveConflictAllSC(roomid, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev):
    """Resolves Single conflicts with Couple entries, always run after Singles to Singles Resolver has failed
        looks for a couple entry in the past heats to swap in place of the single causing the conflict.
        Instead of having a code specific algorithm just make the changes I need along the way.
        Any Singles that could swap with a single only change will be handled in ResolveNOrderConflictSS

                   Parameters
                   ----------
                   roomid : int
                       Room currently being selected for
                   dance_df : Pandas DataFrame
                       Current pool of contestants
                   log_s : ConflictLog
                       Structure that holds single conflicts of the current heat

                   Returns
                   -------
                   int: 1 = a resolved conflict, -1 = failed to find a resolution

                   """
    resolverLog_c = ResolverConflictLog()
    resolverLog_s = ResolverConflictLog()
    # Create a new log for the singles conflicts
    singlelog = ConflictLog()

    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    couples_in_heat = heat.getCouples()

    conflicts = []
    roomlog = log_s.getRoomlog()
    mode_inst = roomlog[roomid]["mode_inst"][0]
    # mode_code = roomlog[roomid]["mode_code"]
    roomdiv = roomlog[roomid]["div"]

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
    order = 1
    init.presolved = init.solved.copy()
    # presolved = init.presolved[order-1]

    solution_num = 0
    while nordersolved:
        # loop over all conflicts for this heat's roomid
        for con_num, conflict in enumerate(conflicts):
            try:
                # Gather data
                nconflict_counter = 0
                print("")
                print("SC 1st order of", conflict.getInstructor(), 'code', conflict.getCode(), "solving for roomid", roomid, heat.getDiv()[roomid])
                instructors_list = []
                conflict_inst = conflict.getInstructor()

                if conflict.getCode() == 1:
                    # Locate where couples conflict is
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
                    if conflict_entry.loc[0, "type id"] == "L":
                        contestant_col = "Lead Dancer #"
                        cont_fname = "Lead First Name"
                        cont_lname = "Lead Last Name"
                        inst_col = "Follow Dancer #"
                        inst_fname = "Follow First Name"
                        inst_lname = "Follow Last Name"
                        conflict_lead = conflict_contestant
                        conflict_follow = conflict_inst
                    elif conflict_entry.loc[0, "type id"] == "F":
                        contestant_col = "Follow Dancer #"
                        cont_fname = "Follow First Name"
                        cont_lname = "Follow Last Name"
                        inst_col = "Lead Dancer #"
                        inst_fname = "Lead First Name"
                        inst_lname = "Lead Last Name"
                        conflict_lead = conflict_inst
                        conflict_follow = conflict_contestant
                    else:
                        raise Exception("Type id for " + conflict_entry + " is invalid")
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
                            resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, instructors_in_heat,
                                                                          singles_in_heat, conflict_inst, conflict,
                                                                          swapper)
                            nconflict_counter += 1
                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room,
                                  nconflict_index, "instructor", conflict_inst, "div", nconflict_div)
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
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, instructors_in_heat,
                                                                          singles_in_heat, conflict_contestant,
                                                                          conflict,
                                                                          swapper)
                            nconflict_counter += 1
                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room,
                                  nconflict_index, "contestant", conflict_contestant, 'div', nconflict_div)
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
                            # TODO Change this to a couple conflict
                            resolverconflict = ResolverConflictItemSingle(5, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, instructors_in_heat,
                                                                          singles_in_heat, conflict_contestant,
                                                                          conflict,
                                                                          swapper)
                            nconflict_counter += 1
                            resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index, "contestant", conflict_contestant, 'div', nconflict_div)
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

                                if contestant == -1:  # If a blank space skip
                                    index_iter += 1
                                    continue
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
                                        resolverLog_s.append([resolverconflict, con_num])
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
                                        resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                                        print("Couple Conflict, Swappee conflict in heat,room,index", heat_index, swapping_room, placed_coup[swapping_room].index(contestant), "contestant", contestant)
                                # if no conflicts with both lead and follow, make the swap with entry index i
                                if math.fmod(index_iter, 2) == 1:
                                    if not dup:
                                        solution_num += 1
                                        if init.solution[order - 1] > solution_num:
                                            print("Solution already attemped moving to another solution")
                                            index_iter += 1
                                            dup = False
                                            continue
                                        index_iter -= 1
                                        index_2_swap = int(index_iter / 2)
                                        solvedLogic(order - 1)
                                        break
                                    dup = False
                                index_iter += 1
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
                        # Instructor swapped out
                        if conflict_inst not in instructors_available_for_heat[conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                            instructors_available_for_heat[conflict_room].append(conflict_inst)
                        log_s.clearConflict(conflict_inst, -1)
                        clearinglist = [heat.getCouples()[conflict_room][conflict_index*2],
                                        heat.getCouples()[conflict_room][(conflict_index*2) + 1]]
                        log_c.clearConflict(-1, clearinglist)  # Clear out the couple swapped in, if there
                        print("Resolved Conflict by swapping", conflict_contestant, conflict_inst, "and", heat.getCouples()[conflict_room][conflict_index*2],
                              heat.getCouples()[conflict_room][(conflict_index*2) + 1], "from heat", heat_index)
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
                    possible_matches = inst2sing_node[free_inst]
                    for each in possible_matches:
                        print('Contestant in question', each)
                        # Find all the contestants that are causing the conflict
                        for i, every in enumerate(singles_in_heat):
                            if each in every:  # if room has a possible match for this instructor
                                check_in_heat.append(each)
                                room_of_conflict.append(i)
                                index_of_conflict.append(every.index(each))
                                # Find index of this conflict
                    # Check if conflict can be swapped with an entry in a previous heat
                    # loop heat_list and check metadata
                    for i, conflict_contestant in enumerate(check_in_heat):
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
                                resolverconflict = ResolverConflictItemSingle(3, nconflict_div, heat_index,
                                                                              nconflict_room, nconflict_index,
                                                                              instructors_in_heat,
                                                                              singles_in_heat, conflict_inst,
                                                                              conflict, [])
                                resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                      nconflict_room, nconflict_index, "instructor", conflict_inst, 'div',
                                      nconflict_div)
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
                                resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index,
                                                                              nconflict_room, nconflict_index,
                                                                              instructors_in_heat,
                                                                              singles_in_heat, conflict_contestant,
                                                                              conflict, [])
                                resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                      nconflict_room, nconflict_index, "contestant", conflict_contestant, "div",
                                      nconflict_div)
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
                                resolverconflict = ResolverConflictItemSingle(5, conflict_div, heat_index,
                                                                              nconflict_room,nconflict_index,
                                                                              instructors_in_heat,
                                                                              singles_in_heat, conflict_contestant,
                                                                              conflict, [])
                                resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                      nconflict_room, nconflict_index, "contestant", conflict_contestant, "div",
                                      nconflict_div)
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
                                    if contestant in possible_matches:  # If contestant is one of the options it will solve nothing
                                        continue
                                    if contestant == -1 and inst == -1:
                                        index_iter += 1
                                        continue
                                    # If the contestant is in possible matches then it won't solve anything
                                    if contestant in possible_matches:
                                        # If the instructor is also the one trying to be use it will solve nothing
                                        if inst != free_inst:
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
                                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1,
                                                                                          nconflict_room,
                                                                                          nconflict_index,
                                                                                          placed_inst[
                                                                                              swapping_room],
                                                                                          placed_sing[swapping_room],
                                                                                          contestant, conflict, [])
                                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                            # To check prev heat with nth conflict
                                            resolverconflict = ResolverConflictItemSingle(4, conflict_div,
                                                                                          heat_index, swapping_room,
                                                                                          placed_sing[swapping_room].index(contestant),
                                                                                          instructors_in_heat,
                                                                                          singles_in_heat, contestant,
                                                                                          conflict, [])
                                            resolverLog_s.addConflict(resolverconflict, con_num,
                                                                    nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index",
                                                  heat_index, swapping_room, placed_sing[swapping_room].index(contestant),
                                                  "contestant", contestant)
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
                                            resolverconflict = ResolverConflictItemSingle(3, conflict_div,
                                                                                          heat_index, swapping_room,
                                                                                          placed_inst[swapping_room].index(inst),
                                                                                          instructors_in_heat,
                                                                                          singles_in_heat, inst,
                                                                                          conflict, [])
                                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                            print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index,
                                                  swapping_room, placed_inst[swapping_room].index(inst),
                                                  "instructor", inst)
                                    for j, couples in enumerate(heat.getCouples()):
                                        if contestant in couples:
                                            dup = True
                                            nconflict_index = couples.index(contestant)
                                            nconflict_room = j
                                            nconflict_div = heat.getDiv()[nconflict_room]
                                            nconflict_counter += 1
                                            # Conflict to check og heat of nth conflict
                                            # resolverconflict = ResolverConflictItemCouple()
                                            # resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
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
                            if conflict_inst not in instructors_available_for_heat[
                                conflict_room] and inst_tree_node.get(conflict_inst) is not None:
                                instructors_available_for_heat[conflict_room].append(conflict_inst)
                            if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                                instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                            log_s.clearConflict(conflict_inst, -1)
                            clearinglist = [heat.getCouples()[conflict_room][conflict_index * 2],
                                            heat.getCouples()[conflict_room][(conflict_index * 2) + 1]]
                            log_c.clearConflict(-1, clearinglist)  # Clear out the couple swapped in, if there
                            print("Resolved Conflict by swapping out", conflict_contestant, conflict_inst,
                                  "and in", heat.getCouples()[conflict_room][conflict_index*2],
                                  heat.getCouples()[conflict_room][(conflict_index*2) + 1], "from heat", heat_index)
                            return 1
            except Exception:
                print(traceback.format_exc())
                print()
        print("no", order, 'solutions found')
        # If the next order has not been attempted yet, stops resetting solution if stuck between orders
        if init.solution[order] == 0:
            init.solution[order] = 1
        return -1
        # Try to solve N order couples with couples
        # resolve = ResolveNOrderAllCC(log_s, resolverLog, order + 1, heat, heat_list, roomid,
        #                              instructors_available_for_heat, ev)
        # if resolve != -1:
        #     nordersolved = True
        #     resolverLog_c.clearConflicts()
        #     resolverLog_s.clearConflicts()
        # # If there are N order singles conflicts try to solve them with singles
        # elif len(resolverLog_s.getRoomlog()["conf_list"]) > 0:
        #     resolve = ResolveNOrderAllSS(log_s, resolverLog_s, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #     if resolve != -1:
        #         nordersolved = True
        #         resolverLog_c.clearConflicts()
        #         resolverLog_s.clearConflicts()
        #     # If there are N order couples conflicts try to solve them with singles
        #     else:
        #         resolve = ResolveNOrderAllCS(log_s, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #         if resolve != -1:
        #             nordersolved = True
        #             resolverLog_c.clearConflicts()
        #             resolverLog_s.clearConflicts()
        #         # If there are N order Singles conflicts try to solve them with Couples
        #         elif len(resolverLog_s.getRoomlog()["conf_list"]) > 0:
        #             resolve = ResolveNOrderAllSC(log_s, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #             if resolve != -1:
        #                 nordersolved = True
        #                 resolverLog_c.clearConflicts()
        #                 resolverLog_s.clearConflicts()
        #             else:
        #                 return -1
        #         else:
        #             return -1
        # # If there are N order couples conflicts try to solve them with singles
        # else:
        #     resolve = ResolveNOrderAllCS(log_s, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #     if resolve != -1:
        #         nordersolved = True
        #         resolverLog_c.clearConflicts()
        #         resolverLog_s.clearConflicts()
        #     else:
        #         return -1
        dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
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
