import pandas as pd
from pandas import ExcelWriter
import os
import random
import openpyxl
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle
'''FIle with all methods used to create the Freestyle itenerary

'''

'''



'''
def partitionData():
    # Define base column lengths
    baseSingleCols = 8
    baseCoupleCols = 10
    baseInstructorCols = 4
    baseSettingsRows = 8
    """
    # DF's to make debugging faster
    data_set = {'Event Days'
                'Freestyle Time for Day 1 (in Hrs)':
                'Freestyle Time for Day 2 (in Hrs)':
                'Freestyle Time for Day 3 (in Hrs)':
                'Number of Judges':
                'Couples per Judge':
                'Number of Ballrooms':
                'Judges per Ballroom':
                'Heat Duration (Min)':
                'Heat Intermission (Min)':
                'Number of Age Brackets':
                'Age Bracket 1':
                'Age Bracket 2':
                'Age Bracket 3':
                'Event Name':
                'Data': 3,
                        4,
                        8,
                        10,
                        8,
                        4,
                        2,
                        4,
                        1.5,
                        1,
                        3,
                        35,
                        55,
                        56,
                        Hello World
                }
    
    df_set = pd.DataFrame(data=data_set)
    """
    data_cat = {'Dance': ['Foxtrot',
                          'ChaCha',
                          'Bachata',
                          'Showdown'],
                'Genre': ['Smooth',
                          'Rhythm',
                          'Specialty',
                          'Event'],
                'Price': [35,
                          35,
                          35,
                          75]
                }
    df_cat = pd.DataFrame.from_dict(data_cat)
    data_inst = {'Dancer #': [205,
                              206],
                'First Name': ['Ashley',
                               'Jennifer'],
                'Last Name': ['Kipps',
                              'Howard'],
                'School': ['Richmond',
                           'Richmond']
                 }
    df_inst = pd.DataFrame.from_dict(data_inst)
    data_sing = {'Dancer #': [101,
                              102,
                              103],
                 'First Name': ['Dalton',
                                "Marin",
                                "Kevin"],
                 'Last Name': ['Dabney',
                               "Walters",
                               "Donahue"],
                 'Age': [25,
                         24,
                         32],
                 'Lead/Follow': ['Lead',
                                 "Follow",
                                 'Lead'],
                 'Level': ["B3", "B3", "B3"],
                 "Instructor Dancer #'s": [[205,206],
                                        [206,205],
                                           [205,206]],
                 'School': ['Richmond',
                            'Richmond',
                            'Richmond'],
                 'Open Foxtrot': [1,
                                  1,
                                  2],
                 'Closed ChaCha': [2,
                                   4,
                                   0],
                 'Showdown': [1,
                              3,
                              0]
                 }
    df_sing = pd.DataFrame.from_dict(data_sing)
    data_coup = {'Lead Dancer #': [425],
                 'Lead First Name': ['Bill'],
                 'Lead Last Name': ['Richardson'],
                 'Lead Age': [54],
                 'Follow Dancer #': [426],
                 'Follow First Name': ['Suzi'],
                 'Follow Last Name': ['Richardson'],
                 'Follow Age': [52],
                 'Level': ["S4"],
                 'School': ['Richmond'],
                 'Open Foxtrot': [3],
                 'Closed ChaCha': [1],
                 'Closed Bachata': [2],
                 'Showdown': [1]
                 }
    df_coup = pd.DataFrame.from_dict(data_coup)

    # Import all input Sheets independently
    file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
    df_set = pd.read_excel(file, sheet_name='Settings', index_col=0)
    df_cat = pd.read_excel(file, sheet_name='Event Categories')

    # Make list of Genres
    genrelist = list(df_cat['Genre'].unique())
    # Make list of Dances/Events
    dancelist = list(df_cat['Dance'].unique())

    heats = makeHeatDict(genrelist, df_cat)

    """ Commented Out for faster debugging
        # Stops pandas from reading useless blank columns
        cols = []
        for i in range(len(dancelist)+baseSingleCols):
            cols.append(i)

        df_sing = pd.read_excel(file, sheet_name='Singles', usecols=cols)
        df_sing['id'] = ''
        # Stops pandas from reading useless blank columns
        cols = []
        for i in range(len(dancelist) + baseCoupleCols):
            cols.append(i)

        df_coup = pd.read_excel(file, sheet_name='Couples', usecols=cols)

        df_inst = pd.read_excel(file, sheet_name='Instructors')
    """
    # Get all settings data partitioned and saved
    days = int(df_set['Data']['Event Days'])
    hours_p_day = []
    # create list holding hours of heat time per day
    for each in range(days):
        hours_p_day.append(int(df_set['Data'][each + 1]))

    judges = int(df_set['Data']['Number of Judges'])
    judge_ratio = int(df_set['Data']['Couples per Judge'])
    ballrooms = int(df_set['Data']["Number of Ballrooms"])
    ballroom_judges = int(df_set['Data']['Judges per Ballroom'])
    heat_duration = df_set['Data']['Heat Duration (Min)']
    heat_intermission = df_set['Data']['Heat Intermission (Min)']
    bracket_count = int(df_set['Data']['Age Brackets'])
    eventName = df_set['Data']['Event Name']

    age_brackets = []
    for each in range(bracket_count):
        age_brackets.append(int(df_set['Data'][each + 1 + days + 3]))


    # Max number of couples on the floor for a dance assume even # of judges per ballroom
    max_dance_couples = judges * judge_ratio
    couples_per_ballroom = max_dance_couples / ballrooms  # Number of Couples on a singular ballroom

    heats_p_day = []  # Holds # of heats per day
    # Calculations based on Settings data
    for count, each in enumerate(hours_p_day):
        heat_time = heat_duration + heat_intermission
        heats_p_day.append((60 / heat_time) * each)

    max_heats = sum(heats_p_day)  # Max number of heats for entire event due to time settings
    heats_p_hour = max_heats / sum(hours_p_day)

    # Find # of heats per event i.e. per entry in dancelist
    ''' 
    loop through the dance list count the entrance numbers for that event
    need to account for multi entries, when I find the sum compare that to the # of contestansts and you know how many multi entries you have.
    Use that number to find

    or 

    going line by line and making a nominal heat to be sure there are no duplicate entries

    or

    don't worry about putting a heat inside a day until after they are all made.

    For each in dancelist:
        total_heat_p_dance = (df_sing.loc[each].sum() + df_coup.loc[each].sum()) / max_dance_couples
    '''
    '''
    df_list = [df_coup, df_sing]
    for each in df_list:
        each.Level = each.Level.astype(str)
    '''
    # Slice Contestant dfs based on levels
    contestant_data = sliceDfs(df_sing, df_coup)

    '''
    Loop through all dances in the heats dictionary depth first create all heats and store them 
    inside a list at the the lowest order dictionary 
    ex: {'Rhythm': {'Closed': {"Closed ChaCha" : [Heat1, Heat2, ..., Heatn]
                               "Closed East Coast Swing" : [Heat1, Heat2, ..., Heatn]}
                    .
                    .
                    .
                  }
        }
    '''
    # Used for easy access to dfs sliced by level
    AB = 0
    FB = 1
    AS = 2
    FS = 3
    AG = 4
    FG = 5

    current_heats = 0  # Current total heats made
    # For each genre
    for each in heats:
        # For each syllabus in genre
        for every in heats[each]:
            # For each event in that syllabus event
            for ev in heats[each][every]:
                # TODO: add age prio option, break up level dfs based on age then set up iterator variables
                dance_dfs_dict_c = {}
                dance_dfs_dict_s = {}
                keys = [AB, FB, AS, FS, AG, FG]
                keys_in_s = [AB, FB, AS, FS, AG, FG]
                keys_in_c = [AB, FB, AS, FS, AG, FG]
                instructors_available_in_lev = []
                dance_heat_count = 0  # current Heat count for this dance event
                # Percent Trackers and variables
                lev_percent_s = []
                percent_left_s = []
                lev_percent_c = []
                percent_left_c = []
                total_entries_s = 0
                total_contestants_s = 0
                total_entries_c = 0
                total_contestants_c = 0
                goto_next_dance = False  # Flag to set for moving to next dance event,
                                         # if all dfs are empty or too many conflicts with little data left
# ------------------------------------------ Build dfs for Selection ---------------------------------------------------
                # Slice dfs based on participation in dance event 'ev'
                # Add identifier column Couple dfs and reformat to be ready for heat sheet print, Singles done later
                for Single, Couple, roomid in zip(contestant_data['Single'], contestant_data['Couple'], keys):
                    # Slice dfs based on event 'ev'
                    Couple = Couple[Couple[ev] > 0]
                    Single = Single[Single[ev] > 0]
                    instructors_in_lev = []

                    # Couple df operations
                    if not Couple.empty:
                        total_contestants_c = total_contestants_c + Couple.shape[0]
                        total_entries_c = total_entries_c + Couple[ev].sum()
                        Couple['type id'] = 'C'
                        Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name',
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School',
                                         ev]]
                    else:
                        Couple = pd.DataFrame()

                    # Each entry in dict is a level range i.e. AB, FB etc
                    dance_dfs_dict_c[roomid] = Couple

                    # Get Unique instructors in this level
                    if not Single.empty:
                        for row, data in Single.iterrows():  # Iterate down all rows of Single df
                            for num in data["Instructor Dancer #'s"]:  # Iterate through all instructor lists
                                if instructors_in_lev.count(num) == 0:
                                    instructors_in_lev.append(num)

                    df = pd.DataFrame()
                    # Single df operations both for lead and follow
                    if not Single.empty:
                        # Find totals for this Singles level
                        total_contestants_s = total_contestants_s + Single.shape[0]
                        total_entries_s = total_entries_s + Single[ev].sum()

                        if not Single[Single['Lead/Follow'] == 'Lead'].empty:
                            df = Single[Single['Lead/Follow'] == 'Lead']
                            df['type id'] = 'L'
                            df = df.rename(columns={'First Name': 'Lead First Name', 'Last Name': 'Lead Last Name',
                                                    'Dancer #': 'Lead Dancer #'})
                            df['Follow First Name'] = ''
                            df['Follow Last Name'] = ''
                            df['Follow Dancer #'] = ''
                            df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Instructor Dancer #'s",
                                     'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]
                            # Get unique instructors available in this level
                            inst_col = "Follow Dancer #"

                        if not Single[Single['Lead/Follow'] == 'Follow'].empty:
                            df2 = Single[Single['Lead/Follow'] == 'Follow']
                            df2['type id'] = 'F'
                            df2 = df2.rename(columns={'First Name': 'Follow First Name', 'Last Name': 'Follow Last Name',
                                                'Dancer #': 'Follow Dancer #'})
                            df2['Lead First Name'] = ''
                            df2['Lead Last Name'] = ''
                            df2['Lead Dancer #'] = ''
                            df2 = df2[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Instructor Dancer #'s",
                                     'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]
                            '''
                            # Get unique instructors available in this level
                            inst_col = "Lead Dancer #"
                            for row, data in df2.iterrows():  # Iterate down all rows of Follows
                                for num in data[inst_col]:  # Iterate through all instructors for that Follow
                                    if instructors_in_lev.count(num) == 0:
                                        instructors_in_lev.append(num)
                            '''
                            df = pd.concat([df, df2])  # Concat Lead and Follow Singles
                        
                    # Each entry in dict is a level range i.e. AB, FB etc
                    #dance_dfs_dict[i] = pd.concat([df, Couple]) This line will concat singles and couples, not needed as of now.
                    #dance_dfs_dict_s[i] = Single
                    dance_dfs_dict_s[roomid] = df
                    instructors_available_in_lev.append(instructors_in_lev) # TODO: Here need to also get the count of instructor inside the level to know when to remove from the list entirely
                # Assume lowest level will change based on empty dfs
                coup_start_lev = keys[AB]
                sing_start_lev = keys[AB]

                # Set up Percent trackers
                for key in keys:
                    if dance_dfs_dict_s[key].empty:
                        lev_percent_s.append(-1)
                        percent_left_s.append(-1)
                    else:
                        lev_percent_s.append(dance_dfs_dict_s[key][ev].sum() / total_entries_s)
                        percent_left_s.append(1.0)

                    if dance_dfs_dict_c[key].empty:
                        lev_percent_c.append(-1)
                        percent_left_c.append(-1)
                    else:
                        lev_percent_c.append(dance_dfs_dict_c[key][ev].sum() / total_entries_c)
                        percent_left_c.append(1.0)

                # Check if current dfs are empty, and remove them
                single_empty = False
                single_first = True  # Used to set new lowest level for single dfs
                couple_empty = False
                couple_first = True  # Used to set new lowest level for couple dfs
                for key in keys:
                    # Single
                    if dance_dfs_dict_s[key].empty:
                        del dance_dfs_dict_s[key]
                        keys_in_s[key] = -1
                    elif single_first:
                        if key < FG:
                            sing_start_lev = keys[key]
                            single_first = False
                        else:
                            single_empty = True
                    # Couple
                    if dance_dfs_dict_c[key].empty:
                        lev_percent_c.append(-1)
                        percent_left_c.append(-1)
                        del dance_dfs_dict_c[key]
                        keys_in_c[key] = -1
                        couple_first = True
                    elif couple_first:
                        if key < FG:
                            coup_start_lev = keys[key]
                            couple_first = False
                        else:
                            couple_empty = True
                
                # if both Pools are totally empty continue
                # In this case it would only happen if there were no entries to current dance 'ev'
                if single_empty and couple_empty:
                    continue

                # Set current lev
                curr_lev = sing_start_lev
# ---------------------------------------------- Selection Process -----------------------------------------------------
                # TODO: Loop singles until all singles are in the various heats, then come back with couples
                # TODO: start with getting matching single and instructor pairs go one at a time and don't fill a level all at once
                # TODO: may have to make 2 conflict resolvers/holders one for singles and one for couples
                rosters = []  # list of individual heats for the current dance 'ev'
                singles_done = False  # True when all singles are in heats for this event 'ev'
                couples_done = False  # True when all couples are in heats for this event 'ev'
                while len(dance_dfs_dict_s) > 0 and len(dance_dfs_dict_c) > 0: # while there are contestants in the dfs still
                    heat_roster = []  # holds full contestant data for a heat, each element is a list for a dance floor
                    fin_rooms = []  # marks a room as finished with a 1
                    instructors_in_heat = []  # Holds instructor numbers for quick reference
                    contestants_in_heat = []  # Holds contestant number for quick reference
                    for rooms in range(ballrooms):
                        heat_roster.append([])
                        instructors_in_heat.append([])
                        contestants_in_heat.append([])
                        fin_rooms.append(0)
                    heat_finished = False
                # ---------------------------------------------- Singles -------------------------------------------
                    # TODO: add code that will create a df of singles that will be added to the couples df this
                    #  will happen when the last remaining singles cannot be easily matched or swapped.
                    while len(dance_dfs_dict_s) > 0 or single_empty:  # Match all singles/instructors first
                        # Add the soft level assignment to the rooms, this is based on instructors and students in the level
                        heat_room_levs = []  # holds the levels of each room len <= ballrooms
                        level_mode = 0  # indicator for when levels are lower than rooms
                        # Check how many levels there are
                        level_count = 0
                        for lev in keys_in_s:
                            if lev > -1:
                                level_count += 1
                        # if levels > rooms assign based on ratio of instructor to student
                        # TODO: finish and Test levels > ballrooms
                        if level_count > ballrooms:
                            for lev in keys_in_s:
                                if lev > -1:
                                    len(dance_dfs_dict_s[lev].index)/len(instructors_available_in_lev[lev])
                        # if levels < rooms assign all the levels then come back after full or conflicts
                        elif level_count < ballrooms:
                            level_mode = 1
                            for lev in keys_in_s:
                                if lev > -1:
                                    heat_room_levs.append(lev)

                            ''' For now disregard this, may come back to this part if i have a good idea for it
                        elif level_count < rooms:
                            # Get counts of instructors
                            inst_counts = []
                            contest_counts = []
                            for lev in keys:
                                if lev > -1:
                                    inst_counts.append(len(instructors_available_in_lev[lev]))
                                    contest_counts.append(len(dance_dfs_dict_s[lev].index))
                                else:
                                    inst_counts.append(-1)
                                    contest_counts.append(-1)
                            # assign based on count of instructors
                            while len(heat_room_levs) < ballrooms:
                                for inst_num, contest_num in zip(inst_counts, contest_counts):
                                    if inst_num >= max_dance_couples and contest_num :
                                        for i in range(int(inst_num/max_dance_couples)):
                                            if len(heat_room_levs) < ballrooms:
                                                heat_room_levs.append(keys[inst])
                            '''
                        else:
                            for lev in keys_in_s:
                                if lev > -1:
                                    heat_room_levs.append(lev)
                        log = ConflictLog(heat_room_levs)  # make conflict log for this heat
                        # TODO: will now infite loop need to set conditions for heat_finished
                        while not heat_finished:
                            # TODO: try to get as many instructors in the heat as possible
                            # TODO: track count conflict between matches, conflict type
                            #  internal: no free contestant for inst save contestants who are dupe
                            #  external: instructor not free
                            #
                            for roomid, roomlvl in enumerate(heat_room_levs):  # For each ballroom make 1 instructor/single pair
                                if fin_rooms[roomid] == 1:  # if room is filled or declared full, continue on
                                    continue
                                placed = False  # Set when a valid instructor/single pair is placed
                                consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                                solved = 0  # counts how many resolveConflict() calls for this instructor/single pair search
                                curr_lev = roomlvl  # Set curr_lev to rooms assigned level
                                while (not placed) and fin_rooms[roomid] != 1:  # Find a viable single/inst match
                                    # TODO: test instructor conflict
                                    contestantconflicts = []
                                    inst = random.choice(instructors_available_in_lev[curr_lev])  # get random instructor, will throw error if list at index is empty
                                    instructor_taken = False
                                    for selection in instructors_in_heat:
                                        if instructor_taken:
                                            break
                                        if selection.count(inst) > 0:  # Check if instructor is being used in heat so far
                                            instructor_taken = True
                                            break
                                    if instructor_taken:
                                        cons = getContestantList(dance_dfs_dict_s[curr_lev], inst, contestants_in_heat)
                                        log.addConflict(ConflictItemSingle(1, cons, inst, 'e'), roomlvl, roomid)
                                        consecutive += 1
                                        continue
                                # Find a single to pair with this instructor
                                    '''
                                    possible_singles = dance_dfs_dict_s[curr_lev]
                                    for row, contestant in possible_singles.iterows():
                                        for _list in contestant["Instructor Dancer #'s"]:
                                            found = False
                                            for num in _list:
                                                if num == inst:
                                                    found = True
                                                    break
                                            if not found:
                                                possible_singles.drop(possible_singles.index[row])
                                    possible_singles = dance_dfs_dict_s[curr_lev][dance_dfs_dict_s[curr_lev].loc[:,"Instructor Dancer #'s"].count(inst) > 0]
                                    '''
                                    # TODO: figure out best way to find a single match with inst by searching the df but have to interact with the list inside the col
                                    found = False
                                    # Loop over each row in the df for this level
                                    df_shuffled = dance_dfs_dict_s[curr_lev].sample(frac=1)
                                    for row, singles in df_shuffled.iterrows():
                                        next_contestant = False
                                        if found:
                                            break
                                        # Set column variables based on single type
                                        if singles["type id"] == "L":
                                            contestant_col = "Lead Dancer #"
                                            inst_col = "Follow Dancer #"
                                            inst_fname = "Follow First Name"
                                            inst_lname = "Follow Last Name"
                                        elif singles["type id"] == "F":
                                            contestant_col = "Follow Dancer #"
                                            inst_col = "Lead Dancer #"
                                            inst_fname = "Lead First Name"
                                            inst_lname = "Lead Last Name"
                                        else:
                                            raise Exception("Type id for " + singles + " is invalid")
                                        # Loop over the instructor list for the contestant row
                                        for num in singles["Instructor Dancer #'s"]:
                                            # TODO: test the scanning of the ballrooms, add check for internal or external conflict
                                            if num == inst:
                                                for rost in contestants_in_heat:
                                                    if rost.count(singles[contestant_col]) > 0:
                                                        contestantconflicts.append(singles[contestant_col])
                                                        next_contestant = True
                                                if not next_contestant:
                                                    # Set candidate to this single/inst match
                                                    candidate = singles.to_frame().T
                                                    candidate = candidate.reset_index(drop=True)
                                                    instructor_data = df_inst[df_inst["Dancer #"] == inst].reset_index(drop=True)
                                                    candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                                                    candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                                                    candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                                                    found = True
                                                    break
                                    if found:
                                        # Remove/add to tracking data structs
                                        instructors_in_heat[roomid].append(inst)
                                        contestants_in_heat[roomid].append(candidate.loc[:, contestant_col][0])
                                        heat_roster[roomid].append(candidate)
                                        instructors_available_in_lev[curr_lev].remove(inst)
                                        # Remove the placed candidate from the df
                                        if candidate.loc[:, ev][0] == 1:
                                            dance_dfs_dict_s[curr_lev] = dance_dfs_dict_s[curr_lev][
                                                dance_dfs_dict_s[curr_lev].loc[:, contestant_col] != candidate.loc[
                                                    0, contestant_col]]
                                        else:
                                            dance_dfs_dict_s[curr_lev].loc[
                                                dance_dfs_dict_s[curr_lev].loc[:, contestant_col] ==
                                                candidate.loc[:, contestant_col][0], [ev]] = candidate.loc[:, ev][0] - 1
                                        placed = True
                                        # Check if current level df is empty after a placed candidate
                                        if dance_dfs_dict_s[curr_lev].empty:
                                            del dance_dfs_dict_s[curr_lev]  # Delete df
                                            keys_in_s[curr_lev] = -1  # Make key location -1 to show level is empty
                                            if keys_in_s.count(-1) == 6:
                                                single_empty = True
                                        # TODO: may change this to tuple (finished (True, False), initial level(AB, FB,...))
                                        # Determine if room is finished
                                        if len(heat_roster[roomid]) == max_dance_couples:
                                            fin_rooms[roomid] = 1
                                        if len(instructors_available_in_lev[roomlvl]) == 0:
                                            fin_rooms[roomid] = 1
                                        if dance_dfs_dict_s[curr_lev].empty:
                                            if curr_lev == AB and dance_dfs_dict_s[curr_lev+1].empty: # TODO: since I am deleting from the df_dict this will give error if there is no df + or - 1
                                                fin_rooms[roomid] = 1
                                            if curr_lev > AB and dance_dfs_dict_s[curr_lev-1].empty:
                                                fin_rooms[roomid] = 1
                                        # Determine if heat finished
                                        if fin_rooms.count(1) == len(heat_room_levs):
                                            heat_finished = True
                                        print("Candidate placed: ")
                                        print(candidate)
                                    else:
                                        consecutive += 1
                        if level_mode:
                            pass
                            # TODO: Determine rooms left
                            # TODO: Determine which levels are full with leftovers or vacant with conflicts
                            # TODO: of those left start with largest level and least conflicts for that room, then do same selection as before.
                            # TODO: if none left leave room open for couples to come in and fill.



                    # ---------------------------------------------- Couples -------------------------------------------
                    for roomlvl in range(ballrooms): # for each ballroom create a heat, stops instructor duplication
                        curr_heat = []
                        instructors_in_heat.append([])
                        # Get suitable candidates from the df of the current level (AB, FB, etc)
                        # When a df is depleted remove it from the dictionary, update variables for tracking
                        # don't forget to track the instructors in the roster
                        consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                        solved = 0  # counts how many resolveConflict() calls for this heat
                        done = False  # Used when a heat conflict cannot be resolved and stops selection for that heat
                        while (len(curr_heat) < max_dance_couples) | (not goto_next_dance) | (not done):

                            # if consecutive > 1000:
                            #     if solved < 1000:
                            #         #if resolveConflict(curr_heat, dance_dfs_dict_c, conflcitlist, heat_roster, solved):
                            #          #   solved += 1
                            #     else:
                            #         pass
                                    # TODO: compare what is left to max heat size, if much greater re-roll or done and continue if it happens again this category may be doinked, if much less there are some options: 'done' the heat continue building,
                                    #  add the pool to next level df and build from there,

                             # TODO: Figure out what sample() output is when empty, should never happen
                             # TODO: Add Conflict resolution code check notebook for concepts, much less robust than before with single and couple split
                            candidate = dance_dfs_dict_c[curr_lev].sample() # Pick out random entry from df, may need to have try catch
                            added = False
                            # Check not already in heat
                            dup = False
                            # TODO: If I go to list of lists in contestants in heat I'll need to check previous level heats too jic
                            if candidate.loc[:, 'type id'][0] == 'C':
                                number = candidate.loc[:, 'Lead Dancer #'][0]
                                if contestants_in_heat.count(number) > 0 or contestants_in_heat.count(candidate.loc[:, 'Follow Dancer #'][0]) > 0:
                                    dup = True
                            elif candidate.loc[:, 'type id'][0] == 'L':
                                number = candidate.loc[:, 'Lead Dancer #'][0]
                                if contestants_in_heat.count(number) > 0:
                                    dup = True
                            else:
                                number = candidate.loc[:, 'Follow Dancer #'][0]
                                if contestants_in_heat.count(number) > 0:
                                    dup = True
                            if dup:
                                # conflcitlist.addConflict(ConflictItem(1, number))
                                consecutive += 1  # stop infinite looping when list has no candidate to add to this heat
                                continue
                            # Check if instructor inside heat, only for Singles
                            if candidate.loc[:, 'type id'][0] != "C":  # if not a couple entry
                                # Set which column will be used based on Leader or Follower single
                                if candidate.loc[:, 'type id'][0] == 'F':
                                    inst_col = 'Lead Dancer #'
                                else:
                                    inst_col = 'Follow Dancer #'

                                potential_instructors = candidate[inst_col].tolist()[0]
                                # loop through potential_instructors list,
                                # if not in heat already, keep the list in case of a later swap
                                # add to heat roster and instructors_in_heat
                                for inst in potential_instructors:
                                    found = False
                                    # TODO: this will be removed and greedy will work fine as if there is a later conflict I can simply swap the inst in the heat or just remove it.
                                    for lev in instructors_in_heat:
                                        if lev.count(inst) != 0:
                                            found = True
                                            break
                                    if not found:
                                        instructors_in_heat[roomlvl].append(inst)
                                        added = True
                                        break

                            else:  # Else meaning a 'couples' entry
                                added = True
                                instructors_in_heat[roomlvl].append(-1)

                            # if candidate was found possible add to the roster and remove that entry from the query
                            if added:
                                if candidate.loc[:, 'type id'][0] == 'F':
                                    col = "Follow Dancer #"
                                    contestants_in_heat.append(candidate.loc[0, 'Follow Dancer #'])
                                else:
                                    col = "Lead Dancer #"
                                    contestants_in_heat.append(candidate.loc[0, 'Lead Dancer #'])
                                    if candidate.loc[:, 'type id'][0] == 'C':
                                        contestants_in_heat.append(candidate.loc[0, 'Follow Dancer #'])

                                # if last or only entry remove it from query_df
                                if candidate.loc[:, ev][0] == 1:
                                    dance_dfs_dict_c[curr_lev] = dance_dfs_dict_c[curr_lev][dance_dfs_dict_c[curr_lev].loc[:,col] != candidate.loc[0, col]]
                                else:
                                    dance_dfs_dict_c[curr_lev].loc[dance_dfs_dict_c[curr_lev].loc[:, col] == candidate.loc[:, col][0], [ev]] = candidate.loc[:, ev][0] - 1
                                # Add candidate data to tracker lists
                                curr_heat.append(candidate.drop(labels=ev, axis=1))
                                # Check if current df is empty after adding the candidate
                                while dance_dfs_dict_c[curr_lev].empty:
                                    del dance_dfs_dict_c[curr_lev]  # Take out empty df
                                    # level_bp[curr_lev] = dance_heat_count  # Mark the BP for the level
                                    if curr_lev < FG:
                                        curr_lev.remove(curr_lev)  # TODO this may not work
                                        curr_lev = keys[curr_lev+1]
                                    elif keys != []:
                                        curr_lev = keys[0]
                                    else:
                                        goto_next_dance = True

                            else:
                                consecutive += 1
                                # conflcitlist.addConflict(ConflictItem(2, number))
                                continue
                        heat_roster.append(curr_heat)  # add this individual heat to roster list
                        # TODO: make the df suited for printing on the excel output, and add the single and couple dfs together
                    key = each + '-' + every + '-' + ev + '-' + len(rosters)
                    heat = Heat(key, 0, heat_roster, instructors_in_heat)
                    rosters.append(heat)
                    current_heats += 1
                    dance_heat_count += 1
            # Once all heats for an Event/Dance are made create a HeatList object
            heatlist = HeatList(rosters, len(rosters))
            heats[each][every][ev] = heatlist
    buildEvent()
    print("Hello World")

def makeHeatDict(genrelist, df_cat):
    heats = {}
    syllabus = ['Open', 'Closed']
    # For each genre, fill a dictionary key'd with genre, with a sub dict key'd by dance name with that genre
    # This will be used to hold all heats for that dance
    for each in genrelist:
        heats[each] = {}
        for every in syllabus:
            df_genre = df_cat[(df_cat.Genre == each) & (df_cat.Syllabus == every)]
            heats[each][every] = {}
            while not df_genre.empty:
                subdict = heats[each][every]
                subdict.update({df_genre["Dance"].iloc[0]: []})
                #heats.update(subdict.update({df_genre["Dance"].iloc[0]: []}))
                df_genre = df_genre.iloc[1:]
    return heats

def sliceDfs(df_sing, df_coup):
    # Slice Contestant dfs based on levels
    df_sing_AB = df_sing[(df_sing.Level == 'NC') | (df_sing.Level == 'B1') | (df_sing.Level == 'B2')]
    df_sing_FB = df_sing[(df_sing.Level == 'B3') | (df_sing.Level == 'B4')]
    df_sing_AS = df_sing[(df_sing.Level == 'S1') | (df_sing.Level == 'S2')]
    df_sing_FS = df_sing[(df_sing.Level == 'S3') | (df_sing.Level == 'S4')]
    df_sing_AG = df_sing[(df_sing.Level == 'G1') | (df_sing.Level == 'G2')]
    df_sing_FG = df_sing[(df_sing.Level == 'G3') | (df_sing.Level == 'G4') | (df_sing.Level == 'GB')]

    df_coup_AB = df_coup[(df_coup.Level == 'NC') | (df_coup.Level == 'B1') | (df_coup.Level == 'B2')]
    df_coup_FB = df_coup[(df_coup.Level == 'B3') | (df_coup.Level == 'B4')]
    df_coup_AS = df_coup[(df_coup.Level == 'S1') | (df_coup.Level == 'S2')]
    df_coup_FS = df_coup[(df_coup.Level == 'S3') | (df_coup.Level == 'S4')]
    df_coup_AG = df_coup[(df_coup.Level == 'G1') | (df_coup.Level == 'G2')]
    df_coup_FG = df_coup[(df_coup.Level == 'G3') | (df_coup.Level == 'G4') | (df_coup.Level == 'GB')]

    df_contestants = {'Single': [df_sing_AB, df_sing_FB, df_sing_AS, df_sing_FS, df_sing_AG, df_sing_FG],
                      'Couple': [df_coup_AB, df_coup_FB, df_coup_AS, df_coup_FS, df_coup_AG, df_coup_FG]
                     }

    return df_contestants
''' If I go back to saving singles and couples dances in list format each index is a different level

                    while dance_dfs_dict[iterator].empty:
                        dance_dfs_dict.remove(0)
                        df_list = dance_couples_list
                        query_df = df_list[iterator] # new df to be selecting from 
                    while dance_couples_list[couples_iterator].empty:
                        dance_couples_list.remove(0)
                        df_list = dance_dfs_dict
                        query_df = df_list[iterator] # new df to be selecting from
                        level_bp.append(dance_heat_count)
'''

def buildEvent(heats, ballrooms, eventName):
    wb = openpyxl.Workbook()
    wb.save(eventName + '.xlsx')
    rowindex = 1
    file = os.getcwd() + eventName + '.xlsx'
    for each in heats: # For each genre
        for every in heats[each]: # For every syllabus category
            wb.create_sheet(title=every+''+each)
            rowindex = 1
            keys = heats[each][every].keys() # Create list of keys
            while heats[each][every] != "": # While open or closed is not empty
                key = keys[0] # Print all heats for that key,TODO can make this random in future for day planning
                iterator = 0
                rosters = heats[each][every][key].getRostersList()
                level_bp = heats[each][every][key].getLevelBreakPoints()
                count = heats[each][every][key].getHeatCount()
                for rooms in range(ballrooms): # For each ballroom print out a heat, TODO: may need a -1
                    sheet = wb.get_sheet_by_name(every+''+each)
                    sheet['A'+str(rowindex)] = 'Ballroom' + str(rooms+65)
                    rowindex += 1
                    # Start at the lowest level and iterate until all rooms filed
                    # if highest level reached start at lowest again
                    with ExcelWriter(file, mode='a') as writer:
                        pass

def resolveConflict(curr_heat, dance_dfs_dict, conflcitlist, heat_roster, solved):
    if solved < 1000:
        pass

def getContestantList(dance_df,inst,contestants):
    """Finds the all contestants that will conflict for the current heat roster given the instructor inst

       Parameters
       ----------
       dance_df : Pandas DataFrame
           Current pool of single contestants
       inst : int
           Instructor Randomly picked from list of instructors possible for the level
       contestants : list[[int]]
           List of 6 lists holding all contestants that are placed in current heat
           List of 6 lists holding all contestants that are placed in current heat

       Returns
       -------
       list[int]
           a list of Dancer #'s that will conflict with the current heat roster
       """
    # TODO: Find all the possible contestants that will not work with this invalid inst
    # TODO: optimize here by slicing the df based on inst in the list
    dupe_con = []
    for row, singles in dance_df.iterrows():
        # Set column variables based on single type
        if singles["type id"] == "L":
            contestant_col = "Lead Dancer #"
            inst_col = "Follow Dancer #"
            inst_fname = "Follow First Name"
            inst_lname = "Follow Last Name"
        elif singles["type id"] == "F":
            contestant_col = "Follow Dancer #"
            inst_col = "Lead Dancer #"
            inst_fname = "Lead First Name"
            inst_lname = "Lead Last Name"
        else:
            raise Exception("Type id for " + singles + " is invalid")
        for num in singles["Instructor Dancer #'s"]:
            if num == inst:
                for each in contestants:
                    if each.count(singles[contestant_col]) > 0:
                        dupe_con.append(each)
    return dupe_con