import init
import math

def PoachPrevHeatsSingles(roomid, div, heat, heatlist, acceptablecouples):
    if heatlist.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this event's settings")
        return
    heatlen = len(heat.getRoster()[roomid])
    couples_per_floor = heatlist.getCouplesPerFloor()

    poachlist = []
    heatnums = []
    potentials = 0
    poachsingles = []
    poachinst = []
    runcounter = 0
    # While current heat's selection room is less than half the size of a full room
    while heatlen < acceptablecouples:
        heatnums.clear()
        if runcounter > 5:  # If poacher runs for 15 iterations and no fill then break out
            print("forcing out poaching", div)
            break
        print("Gather entries to Poach", div)
        for heat_index, each in enumerate(heatlist.getRostersList()):
            # Check if heat has division
            if div not in each.getDiv():
                continue
            # Find an entry in the previous heat room that has no conflicts with current heat
            if each.getDiv().count(div) > 1:
                past_heat_iter = each.getDiv().count(div)
            else:
                past_heat_iter = 1
            start_at = 0
            for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                swapping_room = each.getDiv().index(div, 0)
                if not len(each.getRoster()[swapping_room]) > acceptablecouples:
                    continue
                start_at = swapping_room
                index_iter = 0
                index_2_swap = -1
                dup = False
                for contestant, inst in zip(each.getSingles()[swapping_room], each.getInstructors()[swapping_room]):
                    for i, singles in enumerate(heat.getSingles()):
                        if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                            dup = True
                            break
                    for i, instructors in enumerate(heat.getInstructors()):
                        if contestant in instructors:  # make sure the conflict is not because it has some inst trying to be freed
                            raise Exception(contestant, "in Singles Instructor list")
                            # conflict to check the previous heat entry nth conflict
                            # resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index,swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee])
                            # resolverLog.addConflict(resolverconflict, con_num)
                            # print("Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), 'inst', inst)
                        if inst in instructors:
                            dup = True
                            break
                    for i, couples in enumerate(heat.getCouples()):
                        if contestant in couples:
                            dup = True
                            break
                    if not dup:
                        index_2_swap = index_iter
                        # if (contestant in poachsingles) or (inst in poachinstructors):
                        if contestant not in poachsingles and inst not in poachinst and heat_index not in heatnums:
                            # Check this single/inst is not in the list already
                            poachlist.append([heat_index, swapping_room, index_2_swap])
                            heatnums.append(heat_index)
                            poachsingles.append(contestant)
                            poachinst.append(inst)
                        else:
                            potentials += 1
                    dup = False
                    index_iter += 1
        instructors_list = []
        for i, each in enumerate(heat.getInstructors()):
            for every in each:
                instructors_list.append(every)
        singles_list = []
        for i, each in enumerate(heat.getSingles()):
            for every in each:
                singles_list.append(every)
        print("Poaching from heats", div, poachlist)
        counter = 0
        while counter < 2:
            for poach in reversed(poachlist):
                if heatlen == acceptablecouples:
                    return
                # poach = random.choice(poachlist)
                heat2poach = heatlist.getRostersList()[poach[0]]
                # Check if either are in Heat already
                if heat2poach.getSingles()[poach[1]][poach[2]] in singles_list:
                    continue
                if heat2poach.getInstructors()[poach[1]][poach[2]] in instructors_list:
                    continue
                if len(heat2poach.getRoster()[poach[1]]) >= couples_per_floor and counter == 0:
                    print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                    singles_list.append(heat.getSingles()[roomid][-1])
                    instructors_list.append(heat.getInstructors()[roomid][-1])
                elif counter >= 1 and len(heat2poach.getRoster()[poach[1]]) > acceptablecouples:
                    print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], poach[2])
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                    singles_list.append(heat.getSingles()[roomid][-1])
                    instructors_list.append(heat.getInstructors()[roomid][-1])
            counter += 1
        poachlist.clear()
        runcounter += 1


def PoachPrevHeatsCouples(roomid, div, heat, heatlist, acceptablecouples):
    if heatlist.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this event's settings")
        return
    couples_per_floor = heatlist.getCouplesPerFloor()
    heatlen = len(heat.getRoster()[roomid])
    poachlist = []
    poachcouples = []
    runcounter = 0
    heatnums = []
    pastpoach = []
    # While current heat's selection room is less than half the size of a full room
    while heatlen < acceptablecouples:
        heatnums.clear()
        poachlist.clear()
        if runcounter > 5:  # If poacher runs for 15 iterations and no fill then break out
            print("forcing out poaching", div)
            break
        print("Gather entries to Poach", div)
        # While current heat's selection room is less than half the size of a full room
        for heat_index, each in enumerate(heatlist.getRostersList()):
            # Check if heat has division
            if div not in each.getDiv():
                continue
            # Find an entry in the previous heat room that has no conflicts with current heat
            if each.getDiv().count(div) > 1:
                past_heat_iter = each.getDiv().count(div)
            else:
                past_heat_iter = 1
            start_at = 0
            for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                swapping_room = each.getDiv().index(div, start_at)
                start_at = swapping_room
                index_iter = 0
                index_2_swap = -1
                lookin = each.getCouples()[swapping_room]
                dup = False
                for contestant in lookin:
                    for i, singles in enumerate(heat.getSingles()):
                        if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                            dup = True
                            break
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
                            break
                    # if no conflicts with both lead and follow, make the swap with entry index i
                    if math.fmod(index_iter, 2) == 1:
                        if not dup:
                            index_2_swap = int(index_iter-1)
                            f = contestant
                            if (l not in poachcouples) and (f not in poachcouples) and heat_index not in heatnums: # Check this couple is not in the list already
                                if [heat_index, swapping_room, index_2_swap] not in pastpoach:
                                    poachlist.append([heat_index, swapping_room, index_2_swap])
                                    poachcouples.append(l)
                                    poachcouples.append(f)
                                    heatnums.append(heat_index)
                        dup = False
                    else:
                        if not dup:
                            l = contestant
                    index_iter += 1

        couples_list = []
        for i, each in enumerate(heat.getCouples()):
            for every in each:
                couples_list.append(every)
        print("Poaching from heats", div, poachlist)
        counter = 0
        while counter < 2:
            for poach in reversed(poachlist):
                if heatlen == acceptablecouples:
                    return
                # poach = random.choice(poachlist)
                heat2poach = heatlist.getRostersList()[poach[0]]
                # Check if either are in Heat already
                if heat2poach.getCouples()[poach[1]][poach[2]] in couples_list:
                    continue
                if heat2poach.getCouples()[poach[1]][poach[2] + 1] in couples_list:
                    continue
                if len(heat2poach.getRoster()[poach[1]]) >= couples_per_floor and counter == 0:
                    print("Contestants", heat2poach.getCouples()[poach[1]][poach[2]], heat2poach.getCouples()[poach[1]][poach[2]+1], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], int(poach[2]/2))
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                    print(heat.getCouples()[roomid][-2], heat.getCouples()[roomid][-1])
                    couples_list.append(heat.getCouples()[roomid][-2])
                    couples_list.append(heat.getCouples()[roomid][-1])
                elif counter >= 1 and len(heat2poach.getRoster()[poach[1]]) >= acceptablecouples:
                    # Check if either are in Heat already
                    print("Contestants", heat2poach.getCouples()[poach[1]][poach[2]], heat2poach.getCouples()[poach[1]][poach[2]+1], "stolen from heat, room", poach[0], poach[1])
                    tmp = heat2poach.stealEntry(poach[1], int(poach[2]/2))
                    heat.addEntry(tmp, roomid)
                    heatlen += 1
                    print(heat.getCouples()[roomid][-2], heat.getCouples()[roomid][-1])
                    couples_list.append(heat.getCouples()[roomid][-2])
                    couples_list.append(heat.getCouples()[roomid][-1])
            counter += 1
        pastpoach.extend(poachlist)
        runcounter += 1


def PoachPrevHeatsAll(roomid, div, heat, heatlist, acceptablecouples):
    """Poach Entries from previous heats to make the heat have acceptable # of contestants.
    Searches the Heat List for a heat with that Division will note a Single and a Couple from that heat (if possible).
    1 of each for each heat/room with that division.
    Then will Poach 1 at a time alternating between Couple and Single until the heat length is acceptable or end of Poachlists
    Repeat until fail or acceptable #

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
    if heatlist.getDivisionHeatCount(div) == 0:
        print(div, "Not enough contestants to make a heat in", init.ev, "Recommend editing this event's settings")
        return
    couples_per_floor = heatlist.getCouplesPerFloor()
    heatlen = len(heat.getRoster()[roomid])
    poachlist_c = []
    poachlist_s = []
    poachcouples = []
    poachsingles = []
    poachinst = []
    runcounter = 0
    heatnums = []
    pastpoach_c = []
    pastpoach_s = []
    # While current heat's selection room is less than half the size of a full room
    while heatlen < acceptablecouples:
        heatnums.clear()
        poachlist_c.clear()
        poachlist_s.clear()
        if runcounter > 5:  # If poacher runs for 15 iterations and no fill then break out
            print("forcing out poaching", div)
            break
        print("Gather entries to Poach", div)
        # While current heat's selection room is less than half the size of a full room
        for heat_index, each in enumerate(heatlist.getRostersList()):
            # Check if heat has division
            if div not in each.getDiv():
                continue
            # Find an entry in the previous heat room that has no conflicts with current heat
            if each.getDiv().count(div) > 1:
                past_heat_iter = each.getDiv().count(div)
            else:
                past_heat_iter = 1
            start_at = 0
            for j in range(past_heat_iter):  # Catches any heat that has multi same division floors
                swapping_room = each.getDiv().index(div, start_at)
                start_at = swapping_room
                index_iter = 0
                index_2_swap = -1
                lookin = each.getCouples()[swapping_room]
                dup = False
                for contestant in lookin:
                    if contestant == -1:
                        index_iter += 1
                        continue
                    for i, singles in enumerate(heat.getSingles()):
                        if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                            dup = True
                            break
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
                            break
                    # if no conflicts with both lead and follow, make the swap with entry index i
                    if math.fmod(index_iter, 2) == 1:
                        if not dup:
                            index_2_swap = int(index_iter - 1)
                            f = contestant
                            if (l not in poachcouples) and (f not in poachcouples) and heat_index not in heatnums:  # Check this couple is not in the list already
                                if [heat_index, swapping_room, index_2_swap] not in pastpoach_c:
                                    poachlist_c.append([heat_index, swapping_room, index_2_swap])
                                    poachcouples.append(l)
                                    poachcouples.append(f)
                                    heatnums.append(heat_index)
                        dup = False
                    else:
                        if not dup:
                            l = contestant
                    index_iter += 1
                # Look for Singles to Poach
                heatnums.clear()
                index_iter = 0
                index_2_swap = -1
                dup = False
                for contestant, inst in zip(each.getSingles()[swapping_room], each.getInstructors()[swapping_room]):
                    if contestant == -1 and inst == -1:
                        index_iter += 1
                        continue
                    for i, singles in enumerate(heat.getSingles()):
                        if contestant in singles:  # make sure the conflict is not because it has some inst trying to be freed
                            dup = True
                            break
                    for i, instructors in enumerate(heat.getInstructors()):
                        if contestant in instructors:  # make sure the conflict is not because it has some inst trying to be freed
                            raise Exception(contestant, "in Singles Instructor list")
                            # conflict to check the previous heat entry nth conflict
                            # resolverconflict = ResolverConflictItemSingle(3, conflict_div, heat_index,swapping_room, placed_inst[swapping_room].index(inst), instructors_in_heat, singles_in_heat, inst, conflict, [swapper, swappee])
                            # resolverLog.addConflict(resolverconflict, con_num)
                            # print("Swappee conflict in heat,room,index", heat_index, swapping_room, placed_inst[swapping_room].index(inst), 'inst', inst)
                        if inst in instructors:
                            dup = True
                            break
                    for i, couples in enumerate(heat.getCouples()):
                        if contestant in couples:
                            dup = True
                            break
                    if not dup:
                        index_2_swap = index_iter
                        # if (contestant in poachsingles) or (inst in poachinstructors):
                        if contestant not in poachsingles and inst not in poachinst and heat_index not in heatnums:
                            if [heat_index, swapping_room, index_2_swap] not in pastpoach_s:
                                # Check this single/inst is not in the list already
                                poachlist_s.append([heat_index, swapping_room, index_2_swap])
                                heatnums.append(heat_index)
                                poachsingles.append(contestant)
                                poachinst.append(inst)
                    dup = False
                    index_iter += 1
            # if poachlist_s[-1] == poachlist_c[-1]:
            #     pass
        # Make lists for easy reference
        instructors_list = []
        for i, each in enumerate(heat.getInstructors()):
            for every in each:
                instructors_list.append(every)
        singles_list = []
        for i, each in enumerate(heat.getSingles()):
            for every in each:
                singles_list.append(every)
        couples_list = []
        for i, each in enumerate(heat.getCouples()):
            for every in each:
                couples_list.append(every)
        print("Poaching Couples in heats", div, poachlist_c)
        print("Poaching Singles in heats", div, poachlist_s)
        counter = 0
        while counter < 2:
            poach_c = len(poachlist_c) - 1
            poach_s = len(poachlist_s)
            # if there are no poachable entries break the loop
            if poach_c == -1 and poach_s == 0:
                break
            couple = False
            while poach_c >= 0 or poach_s >= 0:
                # Indexing and Couple/Single switching
                if couple and poach_c >= 0:
                    if poach_s >= 0:
                        couple = False
                    poach_c -= 1
                elif poach_s >= 0:
                    if poach_c >= 0:
                        couple = True
                    poach_s -= 1
                if heatlen == acceptablecouples:
                    return
                if couple:
                    poach = poachlist_c[poach_c]
                else:
                    poach = poachlist_s[poach_s]
                heat2poach = heatlist.getRostersList()[poach[0]]
                print(poach)
                # Check if either are in Heat already
                if couple:
                    # The other type has poached from this heat before
                    if len(heat2poach.getRoster()[poach[1]])-1 < (poach[2]/2):
                        poach[2] -= 2  # Decrement the index to get the right index
                    # print(heat2poach.getCouples()[poach[1]])
                    if heat2poach.getCouples()[poach[1]][poach[2]] in couples_list or heat2poach.getCouples()[poach[1]][poach[2]] in singles_list:
                        continue
                    if heat2poach.getCouples()[poach[1]][poach[2] + 1] in couples_list or heat2poach.getCouples()[poach[1]][poach[2] + 1] in singles_list:
                        continue
                else:
                    # The other type has poached from this heat before
                    if len(heat2poach.getRoster()[poach[1]])-1 < poach[2]:
                        poach[2] -= 1  # Decrement the index to get the right index
                    # print(heat2poach.getSingles()[poach[1]])
                    # print(heat2poach.getInstructors()[poach[1]])
                    if heat2poach.getSingles()[poach[1]][poach[2]] in singles_list or heat2poach.getSingles()[poach[1]][poach[2]] in couples_list:
                        continue
                    if heat2poach.getInstructors()[poach[1]][poach[2]] in instructors_list:
                        continue
                if len(heat2poach.getRoster()[poach[1]]) >= couples_per_floor and counter == 0:
                    if couple:
                        print("Contestants", heat2poach.getCouples()[poach[1]][poach[2]], heat2poach.getCouples()[poach[1]][poach[2] + 1], "stolen from heat, room", poach[0], poach[1])
                        tmp = heat2poach.stealEntry(poach[1], int(poach[2] / 2))
                        heat.addEntry(tmp, roomid)
                        heatlen += 1
                        couples_list.append(heat.getCouples()[roomid][-2])
                        couples_list.append(heat.getCouples()[roomid][-1])
                    else:
                        print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                        tmp = heat2poach.stealEntry(poach[1], poach[2])
                        heat.addEntry(tmp, roomid)
                        heatlen += 1
                        singles_list.append(heat.getSingles()[roomid][-1])
                        instructors_list.append(heat.getInstructors()[roomid][-1])
                elif counter >= 1 and len(heat2poach.getRoster()[poach[1]]) >= acceptablecouples:
                    if couple:
                        print("Contestants", heat2poach.getCouples()[poach[1]][poach[2]], heat2poach.getCouples()[poach[1]][poach[2] + 1], "stolen from heat, room", poach[0], poach[1])
                        tmp = heat2poach.stealEntry(poach[1], int(poach[2] / 2))
                        heat.addEntry(tmp, roomid)
                        heatlen += 1
                        couples_list.append(heat.getCouples()[roomid][-2])
                        couples_list.append(heat.getCouples()[roomid][-1])
                    else:
                        print("Contestant", heat2poach.getSingles()[poach[1]][poach[2]], 'Instructor', heat2poach.getInstructors()[poach[1]][poach[2]], "stolen from heat, room", poach[0], poach[1])
                        tmp = heat2poach.stealEntry(poach[1], poach[2])
                        heat.addEntry(tmp, roomid)
                        heatlen += 1
                        singles_list.append(heat.getSingles()[roomid][-1])
                        instructors_list.append(heat.getInstructors()[roomid][-1])

            counter += 1
        pastpoach_c.extend(poachlist_c)
        pastpoach_s.extend(poachlist_s)
        runcounter += 1