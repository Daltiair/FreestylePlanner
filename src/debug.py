import pandas as pd

import init
from init import getNode


def checkheat(heat):

    for i, room in enumerate(heat.getRoster()):
        if len(room) > heat.getCouplesPerFloor():
            if init.debug:
                raise Exception("Roster count exceeds max number room", i, heat.getKey())
            else:
                init.logString += "\n"
                init.logString += "Roster count exceeds max number room" + str(i) + heat.getKey()

    for sing_room in heat.getSingles():
        for sing in sing_room:
            if sing == -1:
                continue
            counter = 0
            for each in heat.getSingles():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    if init.debug:
                        raise Exception("Multiple persons in this heat", sing, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(sing) + heat.getKey()

            for each in heat.getInstructors():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", sing, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(sing) + heat.getKey()

            for each in heat.getCouples():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", sing, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(sing) + heat.getKey()

            if counter > 1:
                if init.debug:
                    raise Exception(" Multiple persons in this heat", sing, heat.getKey())
                else:
                    init.logString += "\n"
                    init.logString += "Multiple persons in this heat" + str(sing) + heat.getKey()

    for inst_room in heat.getInstructors():
        for inst in inst_room:
            if inst == -1:
                continue
            counter = 0

            for each in heat.getSingles():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", inst, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(inst) + heat.getKey()

            for each in heat.getInstructors():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", inst, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(inst) + heat.getKey()

            for each in heat.getCouples():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", inst, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(inst) + heat.getKey()

            if counter > 1:
                if init.debug:
                    raise Exception(" Multiple persons in this heat", inst, heat.getKey())
                else:
                    init.logString += "\n"
                    init.logString += "Multiple persons in this heat" + str(inst) + heat.getKey()

    for coup_room in heat.getCouples():
        for coup in coup_room:
            if coup == -1:
                continue
            counter = 0

            for each in heat.getSingles():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", coup, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(coup) + heat.getKey()

            for each in heat.getInstructors():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", coup, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(coup) + heat.getKey()

            for each in heat.getCouples():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    if init.debug:
                        raise Exception(" Multiple persons in this heat", coup, heat.getKey())
                    else:
                        init.logString += "\n"
                        init.logString += "Multiple persons in this heat" + str(coup) + heat.getKey()

            if counter > 1:
                if init.debug:
                    raise Exception(" Multiple persons in this heat", coup, heat.getKey())
                else:
                    init.logString += "\n"
                    init.logString += "Multiple persons in this heat" + str(coup) + heat.getKey()


def countInstances(heat, heat_list):
    # Loop over heat list, feeding each entry to the counter dict
    # make sure the addition of the placed DB and the DF = 2 if not pause the algo
    print("Counting instances")
    unsorted_data_s = init.df_sing[init.df_sing[init.ev] > 0]
    unsorted_data_c = init.df_coup[init.df_coup[init.ev] > 0]

    for prevheat in heat_list.getRostersList():
        for i, roster in enumerate(prevheat.getRoster()):
            for entry in roster:
                appendParticipantSheetdebug(prevheat.getDiv()[i], "", init.ev, i, entry, heat, heat_list)
    for i, roster in enumerate(heat.getRoster()):
        for entry in roster:
            appendParticipantSheetdebug(heat.getDiv()[i], "", init.ev, i, entry, heat, heat_list)

    for prevheat in heat_list.getRostersList():
        for i, roster in enumerate(prevheat.getRoster()):
            for entry in roster:
                if entry.loc[0, "type id"] == "L":
                    contestant_col = "Lead Dancer #"
                    dancer = entry.loc[0, contestant_col]
                elif entry.loc[0, "type id"] == "F":
                    contestant_col = "Follow Dancer #"
                    dancer = entry.loc[0, contestant_col]
                elif entry.loc[0, "type id"] == "C":
                    contestant_col = "Lead Dancer #"
                    dancer = entry.loc[0, contestant_col]
                    fcontestant_col = "Follow Dancer #"
                    dancerf = entry.loc[0, fcontestant_col]

                if init.participantsheets.get(dancer) is not None:  # If the entry is present
                    pool_count = getPoolCount(heat_list, dancer)
                    rawcount = getUnsortedCount(dancer, unsorted_data_s, unsorted_data_c)
                    if (init.participantsheets[dancer]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                        print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

                if entry.loc[0, "type id"] == "C":
                    if init.participantsheets.get(dancerf) is not None:  # If the entry is present
                        pool_count = getPoolCount(heat_list, dancerf)
                        rawcount = getUnsortedCount(dancerf, unsorted_data_s, unsorted_data_c)
                        if (init.participantsheets[dancerf]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                            print(dancerf, "input entry count", init.participantsheets[dancerf]["Count"], pool_count,"!= output sorted count", rawcount, "in event", init.ev)

    for i, roster in enumerate(heat.getRoster()):
        for entry in roster:
            if entry.loc[0, "type id"] == "L":
                contestant_col = "Lead Dancer #"
                dancer = entry.loc[0, contestant_col]
            elif entry.loc[0, "type id"] == "F":
                contestant_col = "Follow Dancer #"
                dancer = entry.loc[0, contestant_col]
            elif entry.loc[0, "type id"] == "C":
                contestant_col = "Lead Dancer #"
                dancer = entry.loc[0, contestant_col]
                fcontestant_col = "Follow Dancer #"
                dancerf = entry.loc[0, fcontestant_col]

            if init.participantsheets.get(dancer) is not None:  # If the entry is present
                pool_count = getPoolCount(heat_list, dancer)
                rawcount = getUnsortedCount(dancer, unsorted_data_s, unsorted_data_c)
                if (init.participantsheets[dancer]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                    print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

            if entry.loc[0, "type id"] == "C":
                if init.participantsheets.get(dancerf) is not None:  # If the entry is present
                    pool_count = getPoolCount(heat_list, dancerf)
                    rawcount = getUnsortedCount(dancerf, unsorted_data_s, unsorted_data_c)
                    if (init.participantsheets[dancerf]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                        print(dancerf, "input entry count", init.participantsheets[dancerf]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

    # Clear dictionary for next time
    for key in list(init.participantsheets.keys()):
        init.participantsheets[key]["Count"] = 0


def appendParticipantSheetdebug(div, syllabus, ev, roomid, roster_entry, heat, heatslist):

    typeid = roster_entry.loc[0, "type id"]
    # if typeid == "C":
    #     leads_df = init.df_coup
    #     follows_df = init.df_coup
    # elif typeid == "L":
    #     leads_df = init.df_sing
    #     follows_df = init.df_inst
    # elif typeid == "F":
    #     leads_df = init.df_inst
    #     follows_df = init.df_sing

    lead_col = "Lead Dancer #"
    follow_col = "Follow Dancer #"

    # Set Participant df data
    dancer = roster_entry.loc[0, lead_col]
    # partner = roster_entry.loc[0, follow_col]
    # partner_n = roster_entry.loc[0, "Follow First Name"] + " " + roster_entry.loc[0, "Follow Last Name"]
    init.participantsheets[dancer]["Count"] += 1

    # Set Participant df data
    dancer = roster_entry.loc[0, follow_col]
    # partner = roster_entry.loc[0, lead_col]
    # partner_n = roster_entry.loc[0, "Lead First Name"] + " " + roster_entry.loc[0, "Lead Last Name"]
    init.participantsheets[dancer]["Count"] += 1


def getPoolCount(heatlist, dancernum):
    # Set up the fake key builder lists
    if "l" in init.eventdiv or "L" in init.eventdiv:
        lvls = heatlist.getEventLvlSingles()
    else:
        lvls = [-1]

    if "a" in init.eventdiv or "A" in init.eventdiv:
        ages = heatlist.getEventAgesSingles()
    else:
        ages = [-1]

    if "s" in init.eventdiv or "S" in init.eventdiv:
        singles = ["Lead", "Follow"]
    else:
        singles = [-1]

    if "t" in init.eventdiv or "T" in init.eventdiv:
        types = ["S", "C"]
    else:
        types = ["A"]
    print("Counting", dancernum)
    pool_count = 0
    for ty in types:
        fake = [ty]
        for single in singles:
            if single != -1:
                fake.append(single)
            for lvl in lvls:
                if lvl != -1:
                    fake.append(lvl)
                for age in ages:
                    if age != -1:
                        fake.append(age)
                    print(fake)
                    node = getNode(init.dance_dfs, fake)
                    if isinstance(node, pd.DataFrame):
                        unit = node[(node["Lead Dancer #"] == dancernum) | (node["Follow Dancer #"] == dancernum)].reset_index(drop=True)
                    else:
                        unit = pd.DataFrame()

                    if unit.empty:
                        pool_count = pool_count + 0
                    else:
                        pool_count = pool_count + unit.loc[:, init.ev].sum()
                    print(pool_count)
                    if age != -1:
                        del fake[-1]
                if lvl != -1:
                    del fake[-1]
            if single != -1:
                del fake[-1]
        del fake[-1]


    # fake[0] = "C"
    # node = getNode(init.dance_dfs, fake)
    # if isinstance(node, pd.DataFrame):
    #     unit = node[(node["Lead Dancer #"] == dancer) | (node["Follow Dancer #"] == dancer)].reset_index(drop=True)
    # else:
    #     unit = pd.DataFrame()
    # if unit.empty:
    #     pool_count = pool_count + 0
    # else:
    #     pool_count = pool_count + unit.loc[0, init.ev].sum()
    #
    # fake[0] = "A"
    # node = getNode(init.dance_dfs, fake)
    # if isinstance(node, pd.DataFrame):
    #     unit = node[(node["Lead Dancer #"] == dancer) | (node["Follow Dancer #"] == dancer)].reset_index(drop=True)
    # else:
    #     unit = pd.DataFrame()
    # if unit.empty:
    #     pool_count = pool_count + 0
    # else:
    #     pool_count = pool_count + unit[init.ev].sum()

    return pool_count


def getUnsortedCount(dancer, unsorted_data_s, unsorted_data_c):

    unsorted_entry_s = unsorted_data_s[unsorted_data_s["Dancer #"] == dancer].reset_index(drop=True)
    if unsorted_entry_s.empty:
        rawsing = 0
    else:
        rawsing = unsorted_entry_s.loc[0, init.ev]

    unsorted_entry_c = unsorted_data_c[(unsorted_data_c["Lead Dancer #"] == dancer) | (unsorted_data_c["Follow Dancer #"] == dancer)].reset_index(drop=True)
    if unsorted_entry_c.empty:
        rawcoup = 0
    else:
        rawcoup = unsorted_entry_c.loc[0, init.ev]
    return rawcoup + rawsing