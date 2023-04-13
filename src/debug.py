import pandas as pd

import init
from init import getNode
from output import appendParticipantSheet


def checkheat(heat):

    for sing_room in heat.getSingles():
        for sing in sing_room:
            counter = 0
            for each in heat.getSingles():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    raise Exception("Multiple persons in this heat", sing, heat.getKey())


            for each in heat.getInstructors():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    raise Exception(" Multiple persons in this heat", sing, heat.getKey())


            for each in heat.getCouples():
                if sing in each:
                    counter += 1
                if each.count(sing) > 1:
                    raise Exception(" Multiple persons in this heat", sing, heat.getKey())

            if counter > 1:
                raise Exception("Multiple Persons in this heat", sing, heat.getKey())

    for inst_room in heat.getInstructors():
        for inst in inst_room:
            counter = 0

            for each in heat.getSingles():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    raise Exception(" Multiple persons in this heat", inst, heat.getKey())

            for each in heat.getInstructors():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    raise Exception(" Multiple persons in this heat", inst, heat.getKey())

            for each in heat.getCouples():
                if inst in each:
                    counter += 1
                if each.count(inst) > 1:
                    raise Exception(" Multiple persons in this heat", inst, heat.getKey())

            if counter > 1:
                raise Exception("Multiple Persons in this heat", inst, heat.getKey())

    for coup_room in heat.getCouples():
        for coup in coup_room:
            counter = 0

            for each in heat.getSingles():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    raise Exception(" Multiple persons in this heat", coup, heat.getKey())
            for each in heat.getInstructors():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    raise Exception(" Multiple persons in this heat", coup, heat.getKey())
            for each in heat.getCouples():
                if coup in each:
                    counter += 1
                if each.count(coup) > 1:
                    raise Exception(" Multiple persons in this heat", coup, heat.getKey())

            if counter > 1:
                raise Exception("Multiple Persons in this heat", coup, heat.getKey())


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
                    pool_count = getPoolCount(prevheat, i, dancer, contestant_col)
                    rawcount = getUnsortedCount(dancer, unsorted_data_s, unsorted_data_c)
                    if (init.participantsheets[dancer]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                        print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

                if entry.loc[0, "type id"] == "C":
                    if init.participantsheets.get(dancerf) is not None:  # If the entry is present
                        pool_count = getPoolCount(prevheat, i, dancerf, fcontestant_col)
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
                pool_count = getPoolCount(heat, i, dancer, contestant_col)
                rawcount = getUnsortedCount(dancer, unsorted_data_s, unsorted_data_c)
                if (init.participantsheets[dancer]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                    print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

            if entry.loc[0, "type id"] == "C":
                if init.participantsheets.get(dancerf) is not None:  # If the entry is present
                    pool_count = getPoolCount(heat, i, dancerf, fcontestant_col)
                    rawcount = getUnsortedCount(dancerf, unsorted_data_s, unsorted_data_c)
                    if (init.participantsheets[dancerf]["Count"] + pool_count) != rawcount:  # If not equal to the input form
                        print(dancerf, "input entry count", init.participantsheets[dancerf]["Count"], pool_count, "!= output sorted count", rawcount, "in event", init.ev)

    # Clear dictionary for next time
    for key in list(init.participantsheets.keys()):
        init.participantsheets[key]["Count"] = 0


def appendParticipantSheetdebug(div, syllabus, ev, roomid, roster_entry, heat, heatslist):

    typeid = roster_entry.loc[0, "type id"]
    if typeid == "C":
        leads_df = init.df_coup
        follows_df = init.df_coup
    elif typeid == "L":
        leads_df = init.df_sing
        follows_df = init.df_inst
    elif typeid == "F":
        leads_df = init.df_inst
        follows_df = init.df_sing

    lead_col = "Lead Dancer #"
    follow_col = "Follow Dancer #"

    # Set Participant df data
    dancer = roster_entry.loc[0, lead_col]
    partner = roster_entry.loc[0, follow_col]
    partner_n = roster_entry.loc[0, "Follow First Name"] + " " + roster_entry.loc[0, "Follow Last Name"]
    init.participantsheets[dancer]["Count"] += 1

    # Set Participant df data
    dancer = roster_entry.loc[0, follow_col]
    partner = roster_entry.loc[0, lead_col]
    partner_n = roster_entry.loc[0, "Lead First Name"] + " " + roster_entry.loc[0, "Lead Last Name"]
    init.participantsheets[dancer]["Count"] += 1


def getPoolCount(heat, roomid, dancer, dancer_col):
    fake = heat.getDiv()[roomid].copy()
    fake[0] = "S"

    node = getNode(init.dance_dfs, fake)
    if isinstance(node, pd.DataFrame):
        unit = node[node[dancer_col] == dancer].reset_index(drop=True)
    else:
        unit = pd.DataFrame()
    if unit.empty:
        pool_count = 0
    else:
        pool_count = unit.loc[0, init.ev]

    fake[0] = "C"
    node = getNode(init.dance_dfs, fake)
    if isinstance(node, pd.DataFrame):
        unit = node[node[dancer_col] == dancer].reset_index(drop=True)
    else:
        unit = pd.DataFrame()
    if unit.empty:
        pool_count = pool_count + 0
    else:
        pool_count = pool_count + unit.loc[0, init.ev]

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