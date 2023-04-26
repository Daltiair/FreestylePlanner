import init
import pandas as pd


def createParticipantSheets():
    # Loop over each data set and create an empty df where there specific heat data will be added
    # only add one if not already there

    for row, data in init.df_sing.iterrows():
        dancer = data.loc["Dancer #"]
        if init.participantsheets.get(dancer) is None:
            init.participantsheets[dancer] = {}
            init.participantsheets[dancer]["Data"] = pd.DataFrame(init.participantsheetcols)
            init.participantsheets[dancer]["Count"] = 0

    for row, data in init.df_inst.iterrows():
        dancer = data.loc["Dancer #"]
        if init.participantsheets.get(dancer) is None:
            init.participantsheets[dancer] = {}
            init.participantsheets[dancer]["Data"] = pd.DataFrame(init.participantsheetcols)
            init.participantsheets[dancer]["Count"] = 0

    for row, data in init.df_coup.iterrows():
        dancer = data.loc["Lead Dancer #"]
        if init.participantsheets.get(dancer) is None:
            init.participantsheets[dancer] = {}
            init.participantsheets[dancer]["Data"] = pd.DataFrame(init.participantsheetcols)
            init.participantsheets[dancer]["Count"] = 0
        dancer = data.loc["Follow Dancer #"]
        if init.participantsheets.get(dancer) is None:
            init.participantsheets[dancer] = {}
            init.participantsheets[dancer]["Data"] = pd.DataFrame(init.participantsheetcols)
            init.participantsheets[dancer]["Count"] = 0


def clearParticipantSheetCounts():
    # Loop over each data set and clear the number of times it shows up in the sorted heats
    # If not equal to prints to console TODO print to a file or raise exception
    print("Counting Instances", init.ev)
    if init.ev in init.df_sing.columns:
        Single = init.df_sing[init.df_sing[init.ev] > 0]
        for row, data in init.df_sing.iterrows():
            dancer = data.loc["Dancer #"]
            if init.participantsheets.get(dancer) is not None:  # If the entry is present
                rawcount = getUnsortedCount(dancer)
                if (init.participantsheets[dancer]["Count"]) != rawcount:  # If not equal to the input form
                    print(dancer, "input entry count", init.participantsheets[dancer]["Count"], "!= output sorted count", rawcount, "in event", init.ev)
                # Drop the entry from the DF
                # Single = Single.reset_index(drop=True)
                Single = Single.drop(Single[Single["Dancer #"] == dancer].index)
        # If there are some left they were not sorted into the output
        if not Single.empty:
            print(Single[['Dancer #']], "input entry is not present in sorted event output", init.ev)

    if init.ev in init.df_coup.columns:
        Couple = init.df_coup[init.df_coup[init.ev] > 0]

        for row, data in init.df_coup.iterrows():
            dancer = data.loc["Lead Dancer #"]
            dancerf = data.loc["Follow Dancer #"]

            if init.participantsheets.get(dancer) is not None:
                rawcount = getUnsortedCount(dancer)
                if (init.participantsheets[dancer]["Count"]) != rawcount:  # If not equal to the input form
                    print(dancer, "input entry count", init.participantsheets[dancer]["Count"], "!= output sorted count", rawcount, "in event", init.ev)

            if init.participantsheets.get(dancerf) is not None:
                rawcount = getUnsortedCount(dancerf)
                if (init.participantsheets[dancerf]["Count"]) != rawcount:  # If not equal to the input form
                    print(dancerf, "input entry count", init.participantsheets[dancerf]["Count"], "!= output sorted count", rawcount, "in event", init.ev)
            # Drop the entry from the DF
            # Couple = Couple.reset_index(drop=True)
            Couple = Couple.drop(Couple[(Couple["Lead Dancer #"] == dancer) & (Couple["Follow Dancer #"] == dancerf)].index)
            # If there are some left they were not sorted into the output
        if not Couple.empty:
            print(Couple[["Lead Dancer #", "Follow Dancer #"]], "input entry is not present in sorted event output", init.ev)

    # Clear the sheet count after counting them
    if init.ev in init.df_sing.columns:
        for row, data in init.df_sing.iterrows():
            dancer = data.loc["Dancer #"]
            if init.participantsheets.get(dancer) is not None:  # If the entry is present
                init.participantsheets[dancer]["Count"] = 0

    if init.ev in init.df_coup.columns:
        for row, data in init.df_coup.iterrows():
            dancer = data.loc["Lead Dancer #"]
            dancerf = data.loc["Follow Dancer #"]

            if init.participantsheets.get(dancer) is not None:
                init.participantsheets[dancer]["Count"] = 0

            if init.participantsheets.get(dancerf) is not None:
                init.participantsheets[dancerf]["Count"] = 0


def getUnsortedCount(dancer):
    unsorted_data_s = init.df_sing[init.df_sing[init.ev] > 0]
    unsorted_data_c = init.df_coup[init.df_coup[init.ev] > 0]

    unsorted_entry_s = unsorted_data_s[unsorted_data_s["Dancer #"] == dancer].reset_index(drop=True)
    if unsorted_entry_s.empty:
        rawsing = 0
    else:
        rawsing = unsorted_entry_s.loc[0, init.ev].sum()

    unsorted_entry_c = unsorted_data_c[(unsorted_data_c["Lead Dancer #"] == dancer) | (unsorted_data_c["Follow Dancer #"] == dancer)].reset_index(drop=True)
    if unsorted_entry_c.empty:
        rawcoup = 0
    else:
        rawcoup = unsorted_entry_c.loc[0, init.ev].sum()
    return rawcoup + rawsing


def appendParticipantSheet(div, syllabus, ev, roomid, roster_entry, heat, heatslist):

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

    if div[0] == "S":
        eventlvls = heatslist.getEventLvlSingles()
        eventages = heatslist.getEventAgesSingles()
    # elif div[0] == "C":
    else:
        eventlvls = heatslist.getEventLvlCouples()
        eventages = heatslist.getEventAgesCouples()

    if syllabus != "":  # TODO for debug run
        for lev in init.lvl_conversion:
            if lev in div:
                div[div.index(lev)] = eventlvls[lev]
        for age in eventages:
            if age in div:
                printagelist = eventages.copy()
                printagelist.insert(0, 17)
                age_index = printagelist.index(div[div.index(age)])
                if age_index == printagelist[-1]:  # If the last bracket make it '86+'
                    div[div.index(age)] = str(printagelist[age_index - 1] + 1) + "+"
                else:
                    div[div.index(age)] = str(printagelist[age_index - 1] + 1) + "-" + str(printagelist[age_index])
        printstr = ""
        for d in div:
            printstr = printstr + str(d) + ", "
    else:
        printstr = div

    # Set Participant df data
    dancer = roster_entry.loc[0, lead_col]
    partner = roster_entry.loc[0, follow_col]
    partner_n = roster_entry.loc[0, "Follow First Name"] + " " + roster_entry.loc[0, "Follow Last Name"]
    participantsheetentry = {"Day": [1], "Heat #": [heat.getKey()], "Floor": [roomid+1], "Partner #": [partner],
                             "Partner Name": [partner_n], "Event": [ev], "Syllabus": [syllabus], "Division": [printstr[:-2]]}
    participantsheetentry = pd.DataFrame(participantsheetentry)
    # participantsheetentry = participantsheetentry.astype({"Day": int, "Heat #": int, "Floor": int, "Partner #": int})
    participantsheetentry = participantsheetentry.astype({"Day": int, "Floor": int, "Partner #": int})
    # if not init.participantsheets[dancer].empty:
    #     pass
    init.participantsheets[dancer]["Data"] = pd.concat([init.participantsheets[dancer]["Data"], participantsheetentry])
    # init.participantsheets[dancer]["Data"] = init.participantsheets[dancer]["Data"].astype({"Day": int, "Heat #": int, "Floor": int, "Partner #": int})
    init.participantsheets[dancer]["Data"] = init.participantsheets[dancer]["Data"].astype({"Day": int, "Floor": int, "Partner #": int})
    init.participantsheets[dancer]["Count"] += 1
    # init.participantsheets[dancer]["div"] = div
    # init.participantsheets[dancer]["tid"] = "L"

    # Set Participant df data
    dancer = roster_entry.loc[0, follow_col]
    partner = roster_entry.loc[0, lead_col]
    partner_n = roster_entry.loc[0, "Lead First Name"] + " " + roster_entry.loc[0, "Lead Last Name"]
    participantsheetentry = {"Day": [1], "Heat #": [heat.getKey()], "Floor": [roomid+1], "Partner #": [partner],
                             "Partner Name": [partner_n], "Event": [ev],
                             "Syllabus": [syllabus], "Division": [printstr[:-2]]}
    participantsheetentry = pd.DataFrame(participantsheetentry)
    # participantsheetentry = participantsheetentry.astype({"Day": int, "Heat #": int, "Floor": int, "Partner #": int})
    participantsheetentry = participantsheetentry.astype({"Day": int, "Floor": int, "Partner #": int})
    # if not init.participantsheets[dancer]["Data"].empty:
    #     pass
    init.participantsheets[dancer]["Data"] = pd.concat([init.participantsheets[dancer]["Data"], participantsheetentry])
    # init.participantsheets[dancer]["Data"] = init.participantsheets[dancer]["Data"].astype({"Day": int, "Heat #": int, "Floor": int, "Partner #": int})
    init.participantsheets[dancer]["Data"] = init.participantsheets[dancer]["Data"].astype({"Day": int, "Floor": int, "Partner #": int})
    init.participantsheets[dancer]["Count"] += 1
    # init.participantsheets[dancer]["div"] = div
    # init.participantsheets[dancer]["tid"] = "F"