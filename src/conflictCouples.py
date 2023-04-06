import math
import pandas as pd
import init
from conflict import solvedLogic
from conflictSingles import resolveConflictSingles
from debug import countInstances,checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import *
from nconflictCouples import ResolveNOrderCouples


def resolveConflictCouples(roomid, dance_df, log, heat, heat_list, instructors_available_for_heat, ev):

    resolverLog = ResolverConflictLog()
    # Create a new log for the singles conflicts
    singlelog = ConflictLog()

    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    couples_in_heat = heat.getCouples()

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
    order = 1
    init.presolved = init.solved.copy()
    # presolved = init.presolved[order-1]

    solution_num = 1
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
                        nconflict_div = heat.getDiv()[i]
                        conflict_df = getNode(init.dance_dfs, nconflict_div)
                        singleconflict = ConflictItemSingle(2, heat.getInstructors()[nconflict_room][nconflict_index])
                        singlelog.addConflict(singleconflict, con_num)
                # After logging the conflicts run the singles resolver, this should look to change the contestants or swap the entry out and solve any Nth conflicts to make it happen
                resolveConflictSingles(conflict_room, conflict_df, singlelog, heat, heat_list, instructors_available_for_heat, ev)

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
                conflict_entry = heat.getRoster()[conflict_room][conflict_index].copy(True)
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
                            print("external conflict with heat,room,index", heat_index, nconflict_room, nconflict_index, "contestant", nconflict_lf, "div", nconflict_div)
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
                    tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
                    heat.replaceContestant(conflict_room, conflict_index, tmp)
                    log.clearConflict(-1, [conflict_lead, conflict_follow])
                    print("Resolved Conflict by swapping", conflict_lead, conflict_follow, "and", heat.getCouples()[conflict_room][conflict_index],
                          heat.getCouples()[conflict_room][conflict_index + 1], "from heat", heat_index)
                    return 1
    print("no", order-1, 'solutions found')
    # If the next order has not been attempted yet, stops resetting solution if stuck between orders
    if init.solution[order] == 0:
        init.solution[order] = 1
    resolve = ResolveNOrderCouples(resolverLog, order + 1, heat, heat_list, dance_df, roomid, instructors_available_for_heat, ev)
    if resolve != -1:
        nordersolved = True
        resolverLog.clearConflicts()
    else:
        return -1