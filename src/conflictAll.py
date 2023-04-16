import pandas as pd
import init
from conflict import solvedLogic
from conflictSingles import resolveConflictSingles
from conflictCouples import resolveConflictCouples
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import *
from conflictCouples import ResolveNOrderCouples
import traceback


def resolveConflictAll(roomid, log, log_c, heat, heat_list, instructors_available_for_heat, ev):
    resolverLog = ResolverConflictLog()
    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    i = 0
    for i in range(2):
        if init.debug:
            for level in instructors_available_for_heat:
                print(level)
        if init.solution == 0:
            init.solution[0] = 1  # start the solution logic
        if init.solved[0] == -1:  # Termination after solution number is 10
            return -1

        # Resolve Singles Conflicts
        dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
        if i == 0:
            resolve = resolveConflictSingles(roomid, dance_df, log, heat, heat_list, instructors_available_for_heat, ev)
            if resolve == 1:
                return 1
        else:
            resolve = resolveConflictCouples(roomid, log, heat, heat_list, instructors_available_for_heat, ev)
            if resolve == 1:
                return 1

        # Resolve Couples Conflicts
        dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
        if i == 0:
            resolve = resolveConflictCouples(roomid, log_c, heat, heat_list, instructors_available_for_heat, ev)
            if resolve == 1:
                return 1
        else:
            resolve = resolveConflictSingles(roomid, dance_df, log_c, heat, heat_list, instructors_available_for_heat, ev)
            if resolve == 1:
                return 1

    return -1