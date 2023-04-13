import init
from init import *
import random
from Structures import ConflictItemCouple
from conflictCouples import resolveConflictCouples
from conflict import resetSolutionLogic
from debug import countInstances, checkheat
from methods import backfill


def selectionCouples(heat, heat_list, singles_index, c_floors, cfin_rooms, instructors_available_for_heat, log, couples_per_floor, acceptablecouples):
    print("Selecting Couples")
    singles_in_heat = heat.getSingles()
    couples_in_heat = heat.getCouples()
    instructors_in_heat = heat.getInstructors()
    heat_roster = heat.getRoster()
    heat_key = heat.getKey()
    # Loop rooms, backfill or filling new room to completion before moving to the next room
    for roomid, room_info in enumerate(c_floors):
        # If room finished
        if cfin_rooms[roomid] > 0:
            continue
        print('Selecting for room', roomid, room_info)
        dance_df = getNode(init.dance_dfs, room_info)
        consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
        # Get suitable candidates from the df of the current division
        while len(heat_roster[roomid + singles_index]) < couples_per_floor and cfin_rooms[roomid] == 0:
            candidate = dance_df.sample(ignore_index=True)  # Pick out random entry from df, may need to have try catch
            # Check candidate has no one already in heat
            dup_sing = False
            dup_inst = False
            dup_coup = False
            number = candidate.loc[0, 'Lead Dancer #']
            fnumber = candidate.loc[0, 'Follow Dancer #']
            # TODO copy this section to 'A' as well
            # Check contestants in heat
            for selection in singles_in_heat:
                if dup_sing:
                    break
                if selection.count(number) > 0:  # Check if Lead is being used in heat
                    dup_sing = True
                    break
                if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                    dup_sing = True
                    break
            # Check Instructors in heat
            for selection in instructors_in_heat:
                if dup_inst:
                    break
                if selection.count(number) > 0:  # Check if Lead is being used in heat
                    dup_inst = True
                    break
                if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                    dup_inst = True
                    break
            # Check couples in heat
            for selection in couples_in_heat:
                if dup_coup:
                    break
                if selection.count(number) > 0:  # Check if Lead is being used in heat
                    dup_coup = True
                    break
                if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                    dup_coup = True
                    break
            if dup_sing or dup_inst or dup_coup:
                consecutive += 1  # stop infinite looping when list has no candidate to add to this heat
                # Add to the conflict log
                if dup_sing:
                    conflict = ConflictItemCouple(2, number, fnumber)
                    log.addConflict(conflict, roomid + singles_index)
                if dup_coup:
                    conflict = ConflictItemCouple(1, number, fnumber)
                    log.addConflict(conflict, roomid + singles_index)
                if dup_inst:
                    raise Exception("Couple in Instructor list", number, fnumber)
            # # Check if instructor inside heat, only for Singles
            # if candidate.loc[:, 'type id'][0] != "C":  # if not a couple entry
            #     # Set which column will be used based on Leader or Follower single
            #     if candidate.loc[:, 'type id'][0] == 'F':
            #         inst_col = 'Lead Dancer #'
            #     else:
            #         inst_col = 'Follow Dancer #'
            #
            #     potential_instructors = candidate[inst_col].tolist()[0]
            #     # loop through potential_instructors list,
            #     # if not in heat already, keep the list in case of a later swap
            #     # add to heat roster and instructors_in_heat
            #     for inst in potential_instructors:
            #         found = False
            #
            #         for lev in instructors_in_heat:
            #         for lev in instructors_in_heat:
            #             if lev.count(inst) != 0:
            #                 found = True
            #                 break
            #         if not found:
            #             instructors_in_heat[roomlvl].append(inst)
            #             added = True
            #             break
            # instructors_in_heat[roomlvl].append(-1)
            else:  # Else = there are no conflicts
                # if candidate possible add to the roster, remove that entry from the pool
                heat.addEntry(candidate, roomid + singles_index)
                resetSolutionLogic()
                print()
                print("Candidate placed: ")
                print("Lead", number, "Follow", fnumber, 'room', roomid + singles_index, room_info, heat_key)
                col = "Lead Dancer #"
                fcol = "Follow Dancer #"
                # if last or only entry remove it from query_df
                if candidate.loc[0, init.ev] == 1:
                    dance_df = dance_df.reset_index(drop=True)
                    dance_df = dance_df.drop(dance_df[(dance_df[col] == candidate.loc[0, col]) & (dance_df[fcol] == candidate.loc[0, fcol])].index)
                    updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                else:
                    dance_df.loc[(dance_df.loc[:, col] == candidate.loc[0, col]) & (dance_df.loc[:, fcol] == candidate.loc[0, fcol]), init.ev] = candidate.loc[0, init.ev] - 1
                # Add candidate data to tracker lists
                heat_roster = heat.getRoster()
                couples_in_heat = heat.getCouples()
                # Check if current df is empty after adding the candidate
                if dance_df.empty:
                    print("Division Empty", room_info)
                    cfin_rooms[roomid] = 1
                    updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                    deleteEmpty(init.dance_dfs)  # Clean up parent levels if needed
            # Resolve Conflicts
            if consecutive > init.max_conflicts:
                resolve = resolveConflictCouples(roomid, log, heat, heat_list, instructors_available_for_heat, init.ev)
                dance_df = getNode(init.dance_dfs, room_info)
                if init.debug:
                    countInstances(heat, heat_list)
                    for check in heat_list.getRostersList():
                        checkheat(check)
                    checkheat(heat)
                if resolve == 1:
                    consecutive = 0
                else:  # If failed to resolve
                    cfin_rooms[roomid] = 2  # force a finish
                    print("Failed to resolve conflict, forcing finish", room_info)
            if len(heat_roster[roomid + singles_index]) == couples_per_floor:
                cfin_rooms[roomid] = 1
            # Determine if backfill needed
            if cfin_rooms[roomid] > 0 and dance_df[init.ev].sum() < acceptablecouples:
                if dance_df.shape[0] != 0 and heat_list.getDivisionHoleCount(room_info) > 0:
                    backfill(dance_df, room_info, heat_list, couples_per_floor, init.ev)
                    updateDanceDfs(init.dance_dfs, dance_df, room_info, room_info)
                    deleteEmpty(init.dance_dfs)
                else:
                    print("Not enough heats to backfill")
            if init.dance_dfs.get("C") is None:
                couples_empty = True
                for i, info in enumerate(cfin_rooms):
                    if cfin_rooms[i] == 0:
                        cfin_rooms[i] = 1
        # Determine if heat finished
        if (cfin_rooms.count(1) + cfin_rooms.count(2)) == len(c_floors):
            break