import math
import pandas as pd
import init
from conflict import solvedLogic
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictItemCouple
from Heat import Heat, HeatList
from ConflictLog import ConflictLog, ResolverConflictLog
import traceback


def ResolveNOrderCouples(log, resolverlog, order, heat, heat_list, roomid, instructors_available_for_heat, ev):
    resolverLogn = ResolverConflictLog()
    singlelog = ConflictLog()
    conflicts = resolverlog.getRoomlog()

    # Loop over N order Conflicts
    conflictlisti = 0
    nordersolved = True  # assume the nth order is solved
    solution_num = 0
    while nordersolved:
        while conflictlisti < len(conflicts['conf_list']):
            try:
                # Get metadata
                nconflict_counter = 0
                print()
                conflict = conflicts["conf_list"][conflictlisti]
                i = conflictlisti
                if order == 2:
                    print(order, "order solution of", conflict.getPrevConflict().getLead(), conflict.getPrevConflict().getFollow(), "code", conflict.getPrevConflict().getCode())
                else:
                    print(order, "order solution of", conflict.getPrevConflict().getConflictNums(), "code", conflict.getCode())
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
                conflict_entry = conflict_heat.getRoster()[conflict_room][conflict.getNConflictIndex()].copy(True)

                # instructors_to_compare = instructors_in_conflict
                singles_to_compare = singles_in_conflict
                couples_to_compare = couples_in_conflict

                conflict_lead = conflict.getConflictNums()[0]
                conflict_follow = conflict.getConflictNums()[1]

                swapper = [-1, conflict_room, conflict_index]
                # conflict_entry = heat.getRoster()[conflict_room][conflict_index]
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
                                raise Exception("Couples Contestant is in Instructor list", conflict_lead)
                            if conflict_follow in every:
                                f_dup = True
                                raise Exception("Couples Contestant is in Instructor list", conflict_follow)
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
                                print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", nconflict_lf, "div", nconflict_div)
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
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", [conflict_lead, conflict_follow], "div", nconflict_div)
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
                                        solution_num += 1
                                        if init.solution[order - 1] > solution_num:
                                            print("Solution already attemped moving to another solution")
                                            index_iter += 1
                                            dup = False
                                            continue
                                        solvedLogic(order - 1)
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
                        if conflict_heat_index == -1:  # if working on the current heat
                            log.clearConflict(-1, [conflict_lead, conflict_follow])  # Clear out the couple swapped out
                            clearinglist = [conflict_heat.getCouples()[conflict_room][conflict_index],
                                            conflict_heat.getCouples()[conflict_room][conflict_index+1]]
                            log.clearConflict(-1, clearinglist)  # Clear out the couple swapped in, if there
                        print("Resolved Conflict by swapping", conflict_lead, conflict_follow, "and",
                              heat.getCouples()[conflict_room][conflict_index],
                              heat.getCouples()[conflict_room][conflict_index + 1], "from heat", heat_index)
                        break
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
            dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
            resolve = ResolveNOrderCouples(log, resolverLogn, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
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
                conflictlisti = resolve - 1  # -1 because index starts at 0
                resolverLogn.clearConflicts()  # clear conflicts, avoid repeating conflicts of previous n order solves
            else:
                return -1
        else:
            return -1

