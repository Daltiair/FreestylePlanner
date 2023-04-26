import pandas as pd
import init
from conflict import solvedLogic
from conflictAll_SS import resolveConflictAllSS
from conflictAll_CC import resolveConflictAllCC
from conflictAll_SC import resolveConflictAllSC
from conflictAll_CS import resolveConflictAllCS
from debug import countInstances, checkheat
from init import getNode, updateDanceDfs, buildInstTree
from Structures import *
from conflictCouples import ResolveNOrderCouples


def resolveConflictAll(roomid, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev):
    # i = 0
    # for i in range(2):
    if init.debug:
        if init.inst:
            for level in instructors_available_for_heat:
                print(level)
    if init.solution == 0:
        init.solution[0] = 1  # start the solution logic
    if init.solved[0] == -1:  # Termination after solution number is 10
        return -1

    # Resolve Singles Conflicts
    dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
    # if i == 0:
    resolve = resolveConflictAllSS(roomid, dance_df, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev)
    if resolve == 1:
        return 1
    # else:
    #     resolve = resolveConflictAllSC(roomid, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev)
    #     if resolve == 1:
    #         return 1

    # Resolve Couples Conflicts
    dance_df = getNode(init.dance_dfs, heat.getDiv()[roomid])
    # if i == 0:
    resolve = resolveConflictAllCC(roomid, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev)
    if resolve == 1:
        return 1
    # else:
    #     resolve = resolveConflictAllCS(roomid, dance_df, log_s, log_c, heat, heat_list, instructors_available_for_heat, ev)
    #     if resolve == 1:
    #         return 1

    return -1

# def resolveNOrderAll(roomid, log, log_c, heat, heat_list, instructors_available_for_heat, ev):
#     resolve = ResolveNOrderAll_SS(log, resolverLog, order + 1, heat, heat_list, roomid, instructors_available_for_heat, ev)
#
#     if resolve != -1:
#         nordersolved = True
#         resolverLog.clearConflicts()
#         resolverLog_c.clearConflicts()
#     else:
#         resolve = ResolveNOrderAll_CS(log, resolverLog_c, order + 1, heat, heat_list, roomid,
#                                       instructors_available_for_heat, ev)