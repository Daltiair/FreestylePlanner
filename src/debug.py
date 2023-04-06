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
    unsorted_data = init.df_sing[init.df_sing[init.ev] > 0]

    for prevheat in heat_list.getRostersList():
        for i, roster in enumerate(prevheat.getRoster()):
            for entry in roster:
                appendParticipantSheet(prevheat.getDiv()[i], "", init.ev, i, entry, heat, heat_list)
    for i, roster in enumerate(heat.getRoster()):
        for entry in roster:
            appendParticipantSheet(heat.getDiv()[i], "", init.ev, i, entry, heat, heat_list)

    try:
        for prevheat in heat_list.getRostersList():
            for i, roster in enumerate(prevheat.getRoster()):
                for entry in roster:
                    if entry.loc[0, "type id"] == "L":
                        contestant_col = "Lead Dancer #"
                    elif entry.loc[0, "type id"] == "F":
                        contestant_col = "Follow Dancer #"
                    dancer = entry.loc[0, contestant_col]
                    if init.participantsheets.get(dancer) is not None:  # If the entry is present
                        node = getNode(init.dance_dfs, prevheat.getDiv()[i])
                        if isinstance(node, pd.DataFrame):
                            unit = node[node[contestant_col] == dancer].reset_index(drop=True)
                        else:
                            unit = pd.DataFrame()
                        if unit.empty:
                            pool_count = 0
                        else:
                            pool_count = unit.loc[0, init.ev]
                        unsorted_entry = unsorted_data[unsorted_data["Dancer #"] == dancer].reset_index(drop=True)
                        if (init.participantsheets[dancer]["Count"] + pool_count) != unsorted_entry.loc[0, init.ev]:  # If not equal to the input form
                            print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", unsorted_entry.loc[0, init.ev], "in event", init.ev)
    except:
        pass

    for i, roster in enumerate(heat.getRoster()):
        for entry in roster:
            if entry.loc[0, "type id"] == "L":
                contestant_col = "Lead Dancer #"
            elif entry.loc[0, "type id"] == "F":
                contestant_col = "Follow Dancer #"
            dancer = entry.loc[0, contestant_col]
            if init.participantsheets.get(dancer) is not None:
                # If the entry is present
                node = getNode(init.dance_dfs, heat.getDiv()[i])
                if isinstance(node, pd.DataFrame):
                    unit = node[node[contestant_col] == dancer].reset_index(drop=True)
                else:
                    unit = pd.DataFrame()
                if unit.empty:
                    pool_count = 0
                else:
                    pool_count = unit.loc[0, init.ev]
                unsorted_entry = unsorted_data[unsorted_data["Dancer #"] == dancer].reset_index(drop=True)
                if (init.participantsheets[dancer]["Count"] + pool_count) != unsorted_entry.loc[0, init.ev]:  # If not equal to the input form
                    print(dancer, "input entry count", init.participantsheets[dancer]["Count"], pool_count, "!= output sorted count", unsorted_entry.loc[0,init.ev], "in event", init.ev)

    # Clear dictionary for next time
    for key in list(init.participantsheets.keys()):
        init.participantsheets[key]["Count"] = 0