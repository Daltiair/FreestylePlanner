import math
import pandas as pd
import init
from conflict import solvedLogic
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import ConflictItemSingle, ResolverConflictItemSingle, ResolverConflictItemCouple
from Heat import Heat, HeatList
from ConflictLog import ConflictLog, ResolverConflictLog
from nconflictSingles import ResolveNOrderSingles
import traceback


def resolveConflictAllCS(roomid, dance_df, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev):
    """Resolves Couple conflicts with Single entries, always run after Couples to Couples Resolver has failed
    looks for a single entry in the past heats to swap in place of the couple causing the conflict.
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
    resolverLog_s = ResolverConflictLog()
    resolverLog_c = ResolverConflictLog()

    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    couples_in_heat = heat.getCouples()

    if init.debug:
        for level in instructors_available_for_heat:
            print(level)
    if init.solution == 0:
        init.solution[0] = 1  # start the solution logic
    if init.solved[0] == -1:  # Termination after solution number is 10
        return -1

    conflicts = []
    roomlog = log_c.getRoomlog()
    mode_cont = roomlog[roomid]["mode_cont"][0]

    # get all conflicts with mode contestant first
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
                print("1st order of", conflict.getLead(), conflict.getFollow(), "solving for roomid", roomid, heat.getDiv()[roomid])
                conflict_lead = conflict.getLead()
                conflict_follow = conflict.getFollow()
                conflict_entry = heat.getRoster()[conflict_room][conflict_index].copy(True)
                couples_list = []
                # Locate where couples conflict is
                for i, each in enumerate(couples_in_heat):
                    if conflict_lead in each and conflict_follow in each:
                        conflict_room = i
                        conflict_index = int(each.index(conflict_lead) / 2)
                        conflict_div = heat.getDiv()[conflict_room]
                    for every in each:
                        couples_list.append(every)
                # Check if conflict can be swapped with an entry in a previous heat
                # loop heat_list and check metadata
                if heat_list.getDivisionHeatCount(conflict_div) == 0:
                    print("No prev heats with this division moving to next conflict", conflict_div)
                    continue
                for heat_index, each in enumerate(heat_list.getRostersList()):
                    # Check if heat has division
                    if conflict_div not in each.getDiv():
                        continue
                    # Check this heat's instructors
                    placed_inst = each.getInstructors()
                    dup = False
                    for j, every in enumerate(placed_inst):
                        if conflict_lead in every or conflict_follow in every:
                            raise Exception("Couple Contestant is in Instructor list", conflict_lead, conflict_follow)
                    # Check this heats singles
                    placed_sing = each.getSingles()
                    for j, every in enumerate(placed_sing):
                        if conflict_lead in every:
                            nconflict_index = every.index(conflict_lead)
                            nconflict_room = j
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, instructors_in_heat,
                                                                          singles_in_heat, conflict_lead,
                                                                          conflict, [])
                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index, "contestant", conflict_lead, "div",
                                  nconflict_div)
                            dup = True
                        if conflict_follow in every:
                            nconflict_index = every.index(conflict_follow)
                            nconflict_room = j
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemSingle(4, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, instructors_in_heat,
                                                                          singles_in_heat, conflict_follow,
                                                                          conflict, [])
                            resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index, "contestant", conflict_follow, "div",
                                  nconflict_div)
                            dup = True
                    # Check this heats couples
                    placed_coup = each.getCouples()
                    for j, every in enumerate(placed_coup):
                        if conflict_lead in every:
                            nconflict_room = j
                            nconflict_index = every.index(conflict_lead)
                            nconflict_div = each.getDiv()[nconflict_room]
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemCouple(2, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, couples_in_heat,
                                                                          singles_in_heat, [conflict_lead, placed_coup[nconflict_index + 1]],
                                                                          conflict, [])
                            resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index, "contestant", conflict_lead, "div",
                                  nconflict_div)
                            dup = True
                        if conflict_follow in every:
                            nconflict_room = j
                            nconflict_index = every.index(conflict_follow)-1
                            nconflict_div = each.getiv()[nconflict_room]
                            nconflict_counter += 1
                            resolverconflict = ResolverConflictItemCouple(2, nconflict_div, heat_index, nconflict_room,
                                                                          nconflict_index, couples_in_heat,
                                                                          singles_in_heat, [placed_coup[nconflict_index], conflict_follow],
                                                                          conflict, [])
                            resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                            print(nconflict_counter, "external conflict with heat,room,index", heat_index,
                                  nconflict_room, nconflict_index, "contestant", conflict_follow, "div",
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
                            if contestant == -1 and inst == -1:
                                index_iter += 1
                                continue
                            swappee = [heat_index, swapping_room, index_iter]
                            for j, singles in enumerate(heat.getSingles()):
                                if contestant in singles:
                                    dup = True
                                    nconflict_index = singles.index(contestant)
                                    nconflict_room = j
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    # nconflict_counter += 1
                                    # # Conflict to check og heat of nth conflict
                                    # resolverconflict = ResolverConflictItemSingle(4, nconflict_div, -1,
                                    #                                               nconflict_room, nconflict_index,
                                    #                                               placed_inst[swapping_room],
                                    #                                               placed_sing[swapping_room],
                                    #                                               contestant, conflict,
                                    #                                               [])
                                    # resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # print(nconflict_counter, "Swappee conflict in heat,room,index", -1,
                                    #       conflict_room, heat.getSingles()[conflict_room][conflict_index], "contestant",
                                    #       contestant)
                                    nconflict_counter += 1
                                    # To check prev heat with nth conflict
                                    resolverconflict = ResolverConflictItemSingle(4, conflict_div, heat_index,
                                                                                  swapping_room,
                                                                                  placed_sing[swapping_room].index(contestant),
                                                                                  instructors_in_heat,
                                                                                  singles_in_heat, contestant,
                                                                                  conflict,
                                                                                  [])
                                    resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index,
                                          swapping_room, placed_sing[swapping_room].index(contestant), "contestant",
                                          contestant)
                            for j, instructors in enumerate(heat.getInstructors()):
                                if inst in instructors:
                                    dup = True
                                    nconflict_index = instructors.index(inst)
                                    nconflict_room = j
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    # Conflict to check og heat of nth conflict
                                    nconflict_counter += 1
                                    resolverconflict = ResolverConflictItemSingle(3, nconflict_div, -1, nconflict_room, nconflict_index, placed_inst[swapping_room], placed_sing[swapping_room], inst, conflict, [])
                                    resolverLog_s.addConflict(resolverconflict)
                                    print(nconflict_counter, "Swappee conflict in heat,room,index", -1,
                                          swapping_room, nconflict_index, "instructor", inst)
                                    # To check prev heat with nth conflict
                                    nconflict_counter += 1
                                    resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index,
                                                                                  swapping_room,
                                                                                  placed_inst[swapping_room].index(inst),
                                                                                  instructors_in_heat,
                                                                                  singles_in_heat, inst, conflict,
                                                                                  [])
                                    resolverLog_s.addConflict(resolverconflict, con_num, nconflict_counter)
                                    print(nconflict_counter, "Swappee conflict in heat,room,index", heat_index,
                                          swapping_room, placed_inst[swapping_room].index(inst), "instructor", inst)
                            for j, couples in enumerate(heat.getCouples()):
                                if contestant in couples:
                                    dup = True
                                    nconflict_index = couples.index(contestant)
                                    nconflict_room = j
                                    nconflict_div = heat.getDiv()[nconflict_room]
                                    nconflict_counter += 1
                                    # Conflict to check og heat of nth conflict
                                    resolverconflict = ResolverConflictItemCouple(2, nconflict_div, -1,
                                                                                  nconflict_room, nconflict_index,
                                                                                  couples_in_heat[nconflict_room],
                                                                                  singles_in_heat[nconflict_room],
                                                                                  contestant, conflict,
                                                                                  [])
                                    resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                                    # Check Prev heat conflict
                                    nconflict_counter += 1
                                    resolverconflict = ResolverConflictItemCouple(2, conflict_div, heat_index,
                                                                                  swapping_room, placed_sing[swapping_room].index(contestant),
                                                                                  couples_in_heat,
                                                                                  singles_in_heat,
                                                                                  contestant, conflict,
                                                                                  [])
                                    resolverLog_c.addConflict(resolverconflict, con_num, nconflict_counter)
                                if inst in couples:
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
                    if tmp.loc[0, "type id"] == "L":
                        inst_col = "Follow Dancer #"
                    elif tmp.loc[0, "type id"] == "F":
                        inst_col = "Lead Dancer #"
                    # Remove instructor swapped in
                    if tmp.loc[0, inst_col] in instructors_available_for_heat[conflict_room]:
                        instructors_available_for_heat[conflict_room].remove(tmp.loc[0, inst_col])
                    log_s.clearConflict(heat.getInstructors()[conflict_room][conflict_index], -1)
                    log_c.clearConflict(-1, [conflict_lead,conflict_follow])
                    print("Resolved Conflict by swapping out", conflict_lead, conflict_follow, "and in",
                          heat.getCouples()[conflict_room][conflict_index*2],
                          heat.getCouples()[conflict_room][(conflict_index*2)+1], "from heat", heat_index)
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
        # # Try to solve N order singles with singles
        # resolve = ResolveNOrderAllSS(log, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        # if resolve != -1:
        #     nordersolved = True
        #     resolverLog.clearConflicts()
        #     resolverLog_c.clearConflicts()
        # # If there are N order couples conflicts try to solve them with couples
        # elif len(resolverLog_c.getRoomlog()["conf_list"]) > 0:
        #     resolve = ResolveNOrderAllCC(log, resolverLog_c, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #     if resolve != -1:
        #         nordersolved = True
        #         resolverLog.clearConflicts()
        #         resolverLog_c.clearConflicts()
        #     # If there are N order singles conflicts try to solve them with couples
        #     else:
        #         resolve = ResolveNOrderAllSC(log, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #         if resolve != -1:
        #             nordersolved = True
        #             resolverLog.clearConflicts()
        #             resolverLog_c.clearConflicts()
        #         # If there are N order Couples conflicts try to solve them with Singles
        #         elif len(resolverLog_c.getRoomlog()["conf_list"]) > 0:
        #             resolve = ResolveNOrderAllCS(log, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #             if resolve != -1:
        #                 nordersolved = True
        #                 resolverLog.clearConflicts()
        #                 resolverLog_c.clearConflicts()
        #             else:
        #                 return -1
        #         else:
        #             return -1
        # # If there are N order singles conflicts try to solve them with couples
        # else:
        #     resolve = ResolveNOrderAllSC(log, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
        #     if resolve != -1:
        #         nordersolved = True
        #         resolverLog.clearConflicts()
        #         resolverLog_c.clearConflicts()
        #     else:
        #         return -1
        # dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])  # Update dance_df from a potential nth change
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
        return -1