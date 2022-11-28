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
                              103,
                              104],
                 'First Name': ['Dalton',
                                "Marin",
                                "Kevin",
                                "Kayla"],
                 'Last Name': ['Dabney',
                               "Walters",
                               "Donahue",
                               "Dabney"],
                 'Age': [25,
                         24,
                         32,
                         23],
                 'Lead/Follow': ['Lead',
                                 "Follow",
                                 'Lead',
                                 "Follow"],
                 'Level': ["B1", "B1", "B3", "B4"],
                 "Instructor Dancer #'s": [[205,206],
                                        [206,205],
                                           [205, 206],
                                           [206]],
                 'School': ['Richmond',
                            'Richmond',
                            'Richmond',
                            'Richmond'],
                 'Open Foxtrot': [1,
                                  1,
                                  2,
                                  2],
                 'Closed ChaCha': [2,
                                   4,
                                   0,
                                   0],
                 'Showdown': [1,
                              3,
                              0,
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
    couples_per_ballroom = int(max_dance_couples / ballrooms)  # Number of Couples on a singular ballroom

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

    tot_current_heats = 0  # Current total heats made
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
                unideal_heats = [] # Holds metadata on unideal heat to be filled by a level +- 1 if possible
                instructor_dict = {}  # Track instructors in levels to know when to delete them from the available list
                dance_heat_count = 0  # current Heat count for this dance event
                tot_holes = []  # number of open spaces in the heats made to reach the maximum number per heat
                # Percent Trackers and variables
                lev_percent_s = []
                percent_left_s = []
                lev_percent_c = []
                percent_left_c = []
                total_entries_s = 0
                total_contestants_s = 0
                total_entries_c = 0
                total_contestants_c = 0
                # Tracking which level has most contestants at a given time
                decend_level_s = []  # Stores levels highest contestant to lowest contestant counts [[level,count]...]
                decend_level_c = []
                goto_next_dance = False  # Flag to set for moving to next dance event,
                                         # if all dfs are empty or too many conflicts with little data left
# ------------------------------------------ Build dfs for Selection ---------------------------------------------------
                # Slice dfs based on participation in dance event 'ev'
                # Add identifier column Couple dfs and reformat to be ready for heat sheet print, Singles done later
                for Single, Couple, roomlvl in zip(contestant_data['Single'], contestant_data['Couple'], keys):
                    # Slice dfs based on event 'ev'
                    Couple = Couple[Couple[ev] > 0]
                    Single = Single[Single[ev] > 0]
                    instructors_in_lev = []
                    level_entries = 0
                    # Couple df operations
                    if not Couple.empty:
                        total_contestants_c = total_contestants_c + Couple.shape[0]
                        total_entries_c = total_entries_c + Couple[ev].sum()
                        for i, lev in enumerate(decend_level_c):
                            if lev[1] <= Couple.shape[0]:
                                added = True
                                decend_level_c.insert(i-1, [roomlvl, Single.shape[0]])
                                # decend_level_c.append([roomlvl, Couple.shape[0]]) for testing
                                break
                        if not added:
                            decend_level_c.append([roomlvl, Couple.shape[0]])
                        Couple['type id'] = 'C'
                        Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name',
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School',
                                         ev]]
                    else:
                        Couple = pd.DataFrame()

                    # Each entry in dict is a level range i.e. AB, FB etc
                    dance_dfs_dict_c[roomlvl] = Couple

                    # Get Unique instructors in this level
                    if not Single.empty:
                        instructor_dict[roomlvl] = {}
                        for row, data in Single.iterrows():  # Iterate down all rows of Single df
                            for num in data["Instructor Dancer #'s"]:  # Iterate through all instructor lists
                                if instructors_in_lev.count(num) == 0:
                                    instructors_in_lev.append(num)
                                    instructor_dict[roomlvl][num] = 1
                                else:
                                    instructor_dict[roomlvl][num] += 1

                    df = pd.DataFrame()
                    # Single df operations both for lead and follow
                    if not Single.empty:
                        # Find totals for this Singles level
                        total_contestants_s = total_contestants_s + Single.shape[0]
                        total_entries_s = total_entries_s + Single[ev].sum()
                        # Track Levels largest to smallest
                        added = False
                        for i, lev in enumerate(decend_level_s):
                            if lev[1] <= Single.shape[0]:
                                added = True
                                decend_level_s.insert(i-1, [roomlvl, Single.shape[0]])
                                # decend_level_s.append([roomlvl, Single.shape[0]]) for testing
                                break
                        if not added:
                            decend_level_s.append([roomlvl, Single.shape[0]])

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
                    dance_dfs_dict_s[roomlvl] = df
                    instructors_available_in_lev.append(instructors_in_lev)
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

                # Set Holes
                for key in keys:
                    if dance_dfs_dict_s[key].empty:
                        tot_holes.append(-1)
                    else:
                        tot_holes.append(0)

                # Check if current dfs are empty, and remove them
                # TODO: need a way to flag if a df is not there for couples vs singles, I could be assuming there are couples where they may be none
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
                # TODO: may have to make 2 conflict resolvers/holders one for singles and one for couples
                heat_list = HeatList([], 0)  # list of individual heats for the current dance 'ev'
                singles_done = False  # True when all singles are in heats for this event 'ev'
                couples_done = False  # True when all couples are in heats for this event 'ev'
                while len(dance_dfs_dict_s) > 0 and len(dance_dfs_dict_c) > 0: # while there are contestants in the dfs still
                    heat_roster = []  # holds full contestant data for a heat, each element is a list for a dance floor
                    fin_rooms = []  # marks a room as finished with a 1
                    instructors_in_heat = []  # Holds instructor numbers for quick reference
                    singles_in_heat = []  # Holds contestant number for quick reference
                    couples_in_heat = [] # Holds Couples number for quick ref.
                    # couples_in_heat format [[1 Lead #,1 Follow #,...,N Follow #],...[1 Lead #,1 Follow #,..., N Follow #]]
                    for rooms in range(ballrooms):
                        heat_roster.append([])
                        instructors_in_heat.append([])
                        singles_in_heat.append([])
                        couples_in_heat.append([])
                        fin_rooms.append(0)
                    heat_finished = False
                # ---------------------------------------------- Singles -------------------------------------------
                    while len(dance_dfs_dict_s) > 0 or single_empty:  # Match all singles/instructors first
                        # Add the soft level assignment to the rooms, this is based on instructors and students in the level
                        heat_room_levs = []  # holds the levels of each room len <= ballrooms
                        level_mode = 0  # indicator for when levels are lower than rooms
                        lev_mode_selection = False # Indicate if/when a level mode selection is happening
                        # Check how many levels there are
                        level_count = 0
                        for lev in keys_in_s:
                            if lev > -1:
                                level_count += 1
                        # if levels > rooms assign based on ratio of instructor to student
                        # TODO: finish and Test levels > ballrooms
                        #  selected first based on % then based on instructor overlap
                        if level_count > ballrooms:
                            # heat_room_levs.append(decend_level_s[0][0]) # Add largest level to the heat list
                            overlap_data = calculateOverlap(instructors_available_in_lev, ballrooms)
                            looped = False
                            # While rooms are not filled
                            while len(heat_room_levs) < ballrooms:
                                # Go down list of largest rooms and if they fit fill them
                                for i, lev in enumerate(decend_level_s):
                                    lev = lev[0]
                                    if heat_room_levs.count(lev) > 0:
                                        continue
                                    if overlap_data[lev]['level total'] >= couples_per_ballroom*.5:
                                        if overlap_data[lev]['avg'] >= .45:
                                            heat_room_levs.append(lev)
                                            continue
                                    if looped:
                                        heat_room_levs.append(lev)
                                    if len(heat_room_levs) == ballrooms:
                                        break
                                looped = True

                        # if levels < rooms assign all the levels then come back after full or conflicts
                        elif level_count < ballrooms:
                            level_mode = 1
                            level_mode_selection_lev = []
                            for lev in keys_in_s:
                                if lev > -1:
                                    heat_room_levs.append(lev)
                            vacant_rooms = len(heat_roster) - len(heat_room_levs)
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
                        heat_holes = []
                        for place in heat_room_levs:
                            heat_holes.append(0)
                        # Make Instructors for heat list that will change based on placed contestants and instructors
                        instructors_available_for_heat = []
                        for data in instructors_available_in_lev:
                            instructors_available_for_heat.append(data[:])
                        # TODO: will now infite loop need to set conditions for heat_finished
                        key = each + '-' + every + '-' + ev + '-' + str(len(heat_list.getRostersList()))
                        while not heat_finished:
                            selection_finished = False
                            # Selection is before
                            while not selection_finished:
                                # TODO: try to get as many instructors in the heat as possible
                                # TODO: track count conflict between matches, conflict type
                                #  internal: no free contestant for inst save contestants who are dupe
                                #  external: instructor not free
                                #
                                for roomid, roomlvl in enumerate(heat_room_levs):  # For each ballroom make 1 instructor/single pair
                                    if fin_rooms[roomid] > 0:  # if room is filled or declared full, continue on
                                        continue

                                    placed = False  # Set when a valid instructor/single pair is placed
                                    curr_lev = roomlvl  # Set curr_lev to room's assigned level
                                    attempted = []  # holds instructors attempted for this search
                                    consecutive = 0  # Stops infinite loops on failed attempts to add candidate to the heat
                                    solved = 0  # counts how many resolveConflict() calls for this pair search
                                    while (not placed) and fin_rooms[roomid] != 1:  # Find a viable single/inst match
                                        # TODO: test instructor conflict
                                        contestantconflicts = []
                                        inst = random.choice(instructors_available_for_heat[curr_lev])  # get random instructor, will throw error if list at index is empty
                                        # if attempted.count(inst) == 0:  # Check if instructor has been tried before
                                        #     attempted.append(inst)
                                        # else:
                                        #     consecutive += 1
                                        instructor_taken = False
                                        for selection in instructors_in_heat:
                                            if instructor_taken:
                                                break
                                            if selection.count(inst) > 0:  # Check if instructor is being used in heat
                                                instructor_taken = True
                                                break
                                        if instructor_taken:
                                            cons = getContestantConflictList(dance_dfs_dict_s[curr_lev], inst, singles_in_heat)
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
                                        found = False
                                        # Loop over each row in the df for this level
                                        df_shuffled = dance_dfs_dict_s[curr_lev].sample(frac=1)
                                        for row, entry in df_shuffled.iterrows():
                                            next_contestant = False
                                            if found:
                                                break
                                            # Set column variables based on single type
                                            if entry["type id"] == "L":
                                                contestant_col = "Lead Dancer #"
                                                inst_col = "Follow Dancer #"
                                                inst_fname = "Follow First Name"
                                                inst_lname = "Follow Last Name"
                                            elif entry["type id"] == "F":
                                                contestant_col = "Follow Dancer #"
                                                inst_col = "Lead Dancer #"
                                                inst_fname = "Lead First Name"
                                                inst_lname = "Lead Last Name"
                                            else:
                                                raise Exception("Type id for " + entry + " is invalid")
                                            # Loop over the instructor list for the contestant row
                                            for num in entry["Instructor Dancer #'s"]:
                                                if num == inst:
                                                    for rost in singles_in_heat:
                                                        if rost.count(entry[contestant_col]) > 0:
                                                            contestantconflicts.append(entry[contestant_col])
                                                            next_contestant = True
                                                    if not next_contestant:
                                                        # Set candidate to this single/inst match
                                                        candidate = entry.to_frame().T
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
                                            singles_in_heat[roomid].append(candidate.loc[:, contestant_col][0])
                                            heat_roster[roomid].append(candidate)
                                            instructors_available_for_heat[curr_lev].remove(inst)
                                            for num in candidate.loc[:, "Instructor Dancer #'s"][0]:
                                                if instructor_dict[curr_lev][num] == 1:
                                                    del instructor_dict[curr_lev][num]
                                                    instructors_available_in_lev[curr_lev].remove(num)
                                                else:
                                                    instructor_dict[curr_lev][num] -= 1
                                            # Remove the placed candidate from the df, or -1 if multi-entry
                                            if candidate.loc[:, ev][0] == 1:
                                                dance_dfs_dict_s[curr_lev] = dance_dfs_dict_s[curr_lev][
                                                    dance_dfs_dict_s[curr_lev].loc[:, contestant_col] != candidate.loc[
                                                        0, contestant_col]]
                                                # Change the largest level tracker if needed
                                                for i, lev in enumerate(decend_level_s):
                                                    # Find current level in the list
                                                    if lev[0] == curr_lev:
                                                        lev[1] = lev[1] - 1
                                                        # If contestants are gone then remove the level
                                                        if lev[1] == 0:
                                                            decend_level_s.remove(lev)
                                                            break
                                                        # If it is not the smallest level already
                                                        if i < len(decend_level_s) - 1:
                                                            # If level is now smaller than adjacent level, swap them
                                                            if lev[1] < decend_level_s[i + 1][1]:
                                                                tmp = decend_level_s[i + 1]
                                                                decend_level_s[i + 1] = lev
                                                                decend_level_s[i] = tmp
                                                        break
                                            else:
                                                dance_dfs_dict_s[curr_lev].loc[
                                                    dance_dfs_dict_s[curr_lev].loc[:, contestant_col] ==
                                                    candidate.loc[:, contestant_col][0], [ev]] = candidate.loc[:, ev][0] - 1
                                            placed = True
                                            # Check if current level df is empty after a placed candidate
                                            if dance_dfs_dict_s[curr_lev].empty:
                                                # TODO: Decide if I want to finish room if list is empty or start filling it with level +- 1
                                                #  Here a should check the holes and if < couples just move on, if not start filling in +- 1
                                                fin_rooms[roomid] = 1
                                                del dance_dfs_dict_s[curr_lev]  # Delete df
                                                keys_in_s[curr_lev] = -1  # Make key location -1 to show level is empty
                                                if keys_in_s.count(-1) == 6:
                                                    single_empty = True
                                            # Determine if room is finished
                                            if single_empty:
                                                for i in enumerate(heat_room_levs):
                                                    fin_rooms[i] = 1
                                            if len(heat_roster[roomid]) == couples_per_ballroom:
                                                fin_rooms[roomid] = 1
                                            if len(instructors_available_for_heat[roomlvl]) == 0:
                                                fin_rooms[roomid] = 1
                                            if solved == 1000 and len(heat_roster[roomid]) != couples_per_ballroom:
                                                fin_rooms[roomid] = 2  # Forced finish
                                            if consecutive == 1000 and (heat_list.getLevelHeatCount(roomlvl) == 0): # if conflicts and no previous heats
                                                fin_rooms[roomid] = 2  # Forced finish
                                            ''' Not sure I'll use this here will maybe use later after all is finished
                                            # Check if levels above or below are empty as well
                                            if dance_dfs_dict_s[curr_lev].empty:
                                                if curr_lev == AB and curr_lev-1 in dance_dfs_dict_s:
                                                    if dance_dfs_dict_s[curr_lev+1].empty:
                                                        fin_rooms[roomid] = 1
                                                if curr_lev > AB and dance_dfs_dict_s[curr_lev-1].empty:
                                                    fin_rooms[roomid] = 1
                                            '''
                                            # Determine if heat finished
                                            if (fin_rooms.count(1) + fin_rooms.count(2)) == len(heat_room_levs):
                                                selection_finished = True
                                                if not level_mode:
                                                    heat_finished = False
                                                if lev_mode_selection:
                                                    heat_finished = True
                                            print("Candidate placed: ")
                                            print(candidate)
                                        else:
                                            log.addConflict(ConflictItemSingle(2, contestantconflicts, inst, 'i'), roomlvl, roomid)
                                            consecutive += 1
                            # Selection finished
                            # Update Holes metadata
                            if not lev_mode_selection:
                                # Add number of holes before a level mode selection
                                for i, lvl in enumerate(heat_room_levs):
                                    tot_holes[lvl] += couples_per_ballroom - len(heat_roster[i])
                                    heat_holes[i] = couples_per_ballroom - len(heat_roster[i])
                            else:
                                # Add holes after level mode selection but only to newly filled room
                                i = vacant_rooms # Start of the vacant rooms
                                for lvl in level_mode_selection_lev:
                                    tot_holes[lvl] += (couples_per_ballroom - len(heat_roster[i]))
                                    heat_holes[i] = (couples_per_ballroom - len(heat_roster[i]))
                                    i += 1
                            # If levels < ballrooms, figure out if the current selection pool can be put into open room(s)
                            if level_mode:
                                # Loop over all rooms in heat
                                for vacant in heat_roster:
                                    if len(vacant) > 0:  # If room is already in use, continue loop
                                        continue
                                    if not_possible:
                                        print(key + "level mode assigning or splitting not possible")
                                        heat_finished = True
                                        break
                                    assigned = False
                                    looped = False
                                    i = 0
                                    # Choose the highest level whose holes will not exceed Couples pool for that level
                                    while not assigned:
                                        # if looped fully, consider splitting a level now
                                        if i > len(decend_level_c):
                                            if looped:
                                                not_possible = True
                                                break
                                            i = 0
                                            looped = True
                                        possible_largest = decend_level_c[i][0]
                                        couples_for_lev = dance_dfs_dict_c[possible_largest]
                                        placeable_couples = len(instructors_available_for_heat[possible_largest])
                                        if placeable_couples >= couples_per_ballroom:
                                            pot_added_holes = 0
                                        else:
                                            pot_added_holes = couples_per_ballroom - placeable_couples
                                        # Sanity check for level to work at all
                                        if (tot_holes[possible_largest] + pot_added_holes) <= (couples_for_lev + 3):
                                            # If level is being used consider other levels first
                                            if heat_room_levs.count(possible_largest) > 0 and (not looped):
                                                i += 1
                                                continue
                                            # TODO: add a check here to internal vs external conflict if too high external then instructors will likely not get a match
                                            assigned = True
                                            # Metadata for filling in holes metadata
                                            level_mode_selection_lev.append(possible_largest)
                                            heat_room_levs.append(possible_largest)
                                            # If there are Instructors left and the room was not forced to end
                                            if placeable_couples > 0:
                                                if fin_rooms[heat_room_levs.index(possible_largest)] == 1:
                                                    fin_rooms.append(0)
                                                elif fin_rooms[heat_room_levs.index(possible_largest)] == 2:
                                                    fin_rooms.append(2)
                                                    heat_finished = True
                                            else:
                                                heat_finished = True
                        # Heat fully complete Construct key for the new heat
                        # Fill the unused room data if needed
                        if len(heat_room_levs) < ballrooms:
                            for i in range(ballrooms-len(heat_room_levs)):
                                heat_room_levs.append(-1)
                                heat_holes.append(couples_per_ballroom)
                        # Create heat obj
                        heat = Heat(key, heat_room_levs, heat_roster, heat_holes, singles_in_heat, instructors_in_heat, [])
                        heat_list.appendList(heat)  # add completed heat to the HeatList obj
                        dance_heat_count += 1
                        tot_current_heats += 1
                        if tot_current_heats > max_heats:
                            print("Exceeded max heats for event time metrics")
                    # ---------------------------------------------- Couples -------------------------------------------
                    # TODO: while loop the ends when couples df is empty
                    #  first loop over heatlist and fill the holes currently there, making any swaps with the conflict resolver
                    #  then start making couple only heats, much of the code can be reused for couples but much less complicated
                    singles_index = 0  # Iterator, tracks location in the previously built heats
                    backfill_mode = True  # Indicates when all backfilling is complete
                    while len(dance_dfs_dict_c) > 0 or couple_empty: # While couples still have contestants
                        heat_finished = False
                        while not heat_finished: # TODO: Don't think this while loop is needed
                            # Check if all backfill-ed heats are completed
                            if singles_index >= heat_list.getHeatCount():
                                backfill_mode = False
                            # backfill mode pre-selection processing, get all tracking metadata from preexisting heat
                            if backfill_mode:
                                # Check if heat has holes from Singles Selection to backfill
                                heat_to_fill = heat_list.getRostersList()[singles_index]
                                if heat_to_fill.getHoles().count(0) == ballrooms:
                                    singles_index += 1
                                    continue
                                # get levels that need to be backfilled and add them to heat room levels
                                for lev, holes in zip(heat_to_fill.getLevels(), heat_to_fill.getHoles()):
                                    # Fill in metadata about preexisting heat
                                    heat_room_levs.append(lev)
                                    for instruts in heat_to_fill.getInstructors():
                                        instructors_in_heat.append(instruts[:])
                                    for dancers in heat_to_fill.getSingles():
                                        singles_in_heat.append(dancers[:])
                                    for entry in heat_to_fill.getRoster():
                                        heat_roster.append(entry[:])
                                    # Check if there are holes in the room declare if room is finished or not
                                    if holes > 0:
                                        fin_rooms.append(0)
                                    else:
                                        fin_rooms.append(1)
                            else: # backfill completed
                                # TODO: count levels left in dance dfs c use singles code as a copy to assign levels to rooms
                            # Loop rooms, backfill or filling new room to completion before moving to the next room
                            for roomid, roomlvl in enumerate(heat_room_levs):
                                # If room finished
                                if fin_rooms[roomid] > 0:
                                    continue
                                # Make list to hold a placed contestant entry data
                                if backfill_mode: # get the existing roster for this heat to backfill
                                    curr_heat = heat_roster[roomid]
                                else: # If a new heat make a blank list
                                    curr_heat = []
                                curr_lev = roomlvl # Set roomlvl as current (because I don't want to change var name)
                                consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                                solved = 0  # counts how many resolveConflict() calls for this heat
                                done = False  # Used when a heat conflict cannot be resolved and stops selection for that heat
                                # Get suitable candidates from the df of the current level (AB, FB, etc)
                                while (len(curr_heat) < max_dance_couples) | (not goto_next_dance) | (not done):

                                    # if consecutive > 1000:
                                    #     if solved < 1000:
                                    #         #if resolveConflict(curr_heat, dance_dfs_dict_c, conflcitlist, heat_roster, solved):
                                    #          #   solved += 1
                                    #     else:
                                    #         pass
                                            # TODO: compare what is left to max heat size, if much greater re-roll or done and continue if it happens again this category may be doinked, if much less there are some options: 'done' the heat continue building,
                                            #  add the pool to next level df and build from there,

                                    # TODO: Add Conflict resolution code check notebook for concepts, much less robust than before with single and couple split
                                    candidate = dance_dfs_dict_c[curr_lev].sample() # Pick out random entry from df, may need to have try catch
                                    added = False
                                    # Check candidate has no one already in heat
                                    dup_sing = False
                                    dup_inst = False
                                    dup_coup = False
                                    if candidate.loc[:, 'type id'][0] == 'C':
                                        number = candidate.loc[:, 'Lead Dancer #'][0]
                                        fnumber = candidate.loc[:, 'Follow Dancer #'][0]
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
                                        # Check Instructors in heat
                                        for selection in couples_in_heat:
                                            if dup_coup:
                                                break
                                            if selection.count(number) > 0:  # Check if Lead is being used in heat
                                                dup_coup = True
                                                break
                                            if selection.count(fnumber) > 0:  # Check if Follow is being used in heat
                                                dup_coup = True
                                                break
                                    # TODO: add the conflict resolver/log, need to brainstorm couple conflicts
                                    # TODO: how to handle a multi conflict?
                                    if dup_sing or dup_inst or dup_coup:
                                        # conflcitlist.addConflict(ConflictItem(1, number))
                                        consecutive += 1  # stop infinite looping when list has no candidate to add to this heat
                                        # Add to the conflict log
                                        if dup_sing:
                                            pass
                                        if dup_coup:
                                            pass
                                        if dup_inst:
                                            pass
                                        continue
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
                                    #         # TODO: this will be removed and greedy will work fine as if there is a later conflict I can simply swap the inst in the heat or just remove it.
                                    #         for lev in instructors_in_heat:
                                    #             if lev.count(inst) != 0:
                                    #                 found = True
                                    #                 break
                                    #         if not found:
                                    #             instructors_in_heat[roomlvl].append(inst)
                                    #             added = True
                                    #             break
                                    # instructors_in_heat[roomlvl].append(-1)

                                    added = True
                                    # if candidate possible add to the roster,remove that entry from the query
                                    curr_heat.append(candidate)
                                    col = "Lead Dancer #"
                                    fcol = "Follow Dancer #"
                                    # if last or only entry remove it from query_df
                                    if candidate.loc[:, ev][0] == 1:
                                        dance_dfs_dict_c[curr_lev] = dance_dfs_dict_c[curr_lev][dance_dfs_dict_c[curr_lev].loc[:,col] != candidate.loc[0, col]]
                                    else:
                                        dance_dfs_dict_c[curr_lev].loc[dance_dfs_dict_c[curr_lev].loc[:, col] == candidate.loc[:, col][0], [ev]] = candidate.loc[:, ev][0] - 1
                                    # Add candidate data to tracker lists
                                    couples_in_heat[roomid].append(candidate.loc[:, col][0])
                                    couples_in_heat[roomid].append(candidate.loc[:, fcol][0])
                                    # Check if current df is empty after adding the candidate
                                    if dance_dfs_dict_c[curr_lev].empty:
                                        del dance_dfs_dict_c[curr_lev]  # Delete df
                                        keys_in_c[curr_lev] = -1  # Make key location -1 to show level is empty
                                        if keys_in_c.count(-1) == 6:
                                            couple_empty = True
                                        # TODO: change current level to that level, but make sure to update the meta data correctly
                                        # Check if current room is full, if not, see if adjacent levels are viable
                                        if len(heat_roster[roomid]) < couples_per_ballroom and not mixed_heat:
                                            # Decided if Lower level is valid
                                            holes = couples_per_ballroom - len(heat_roster[roomid]) # Calculate holes
                                            if curr_lev != AB and keys_in_c[curr_lev-1] != -1: # If lower level exists
                                                wait_longer = True
                                                # If lower level pool can fit inside this hole, and can still fill it's lev's holes
                                                remaining = dance_dfs_dict_c[curr_lev - 1].shape[0]
                                                lultimate_leftover = remaining - tot_holes[curr_lev - 1]
                                                if couples_per_ballroom > remaining >= holes and lultimate_leftover > 0:
                                                    # If lower level is not being selected for, or is finished selecting
                                                    if heat_room_levs.count(curr_lev-1) == 0 or fin_rooms[heat_room_levs.index(curr_lev-1)] > 0:
                                                        lower_valid = True
                                            # Decide if upper level is valid
                                            if curr_lev != FG and keys_in_c[curr_lev+1] != -1:
                                                wait_longer = True
                                                # If lower level pool can fit inside this hole, and can still fill it's lev's holes
                                                remaining = dance_dfs_dict_c[curr_lev+1].shape[0]
                                                uultimate_leftover = remaining - tot_holes[curr_lev+1]
                                                if couples_per_ballroom > remaining >= holes and uultimate_leftover > 0:
                                                    # If lower level is not being selected for, or is finished selecting
                                                    if heat_room_levs.count(curr_lev+1) == 0 or fin_rooms[heat_room_levs.index(curr_lev+1)] > 0:
                                                        upper_valid = True
                                            # If both can work, must choose between levels
                                            # TODO: may need to note this is a mixed level somehow, for the conflict resolver
                                            if upper_valid and lower_valid:
                                                mixed_heat = True
                                                if lultimate_leftover == holes:
                                                    curr_lev = curr_lev-1
                                                elif uultimate_leftover == holes:
                                                    curr_lev = curr_lev+1
                                                else: # Choose the level that fills the most holes
                                                    if  holes - lultimate_leftover <= holes - uultimate_leftover:
                                                        curr_lev = curr_lev - 1
                                                    else:
                                                        curr_lev = curr_lev + 1
                                            elif upper_valid:
                                                mixed_heat = True
                                                curr_lev = curr_lev + 1
                                            elif lower_valid:
                                                mixed_heat = True
                                                curr_lev = curr_lev - 1
                                            else:
                                                if wait_longer:
                                                    if backfill_mode:
                                                        heatid = singles_index
                                                    else:
                                                        heatid = dance_heat_count
                                                    unideal_heats.append([heatid, roomlvl, holes])
                                                else: # if neither are valid nor is there enough to wait longer
                                                    fin_rooms[roomid] = 1
                                            # Determine if room is finished
                                            if couple_empty:
                                                for i in enumerate(heat_room_levs):
                                                    fin_rooms[i] = 1
                                            if len(heat_roster[roomid]) == couples_per_ballroom:
                                                fin_rooms[roomid] = 1
                                                # TODO: add check here to see if unideal heats has a valid option only if leftover < couples_per_ballroom
                                                if dance_dfs_dict_c[curr_lev].shape[0] < couples_per_ballroom:
                                                    for heat in unideal_heats:
                                                        if heat[1] == curr_heat+1 or heat[1] == curr_heat-1:
                                                            if heat[2] <= dance_dfs_dict_c.shape[0]:
                                                                # TODO: run a method here, to fill in the preexisting heat?
                                            if solved == 1000 and len(heat_roster[roomid]) != couples_per_ballroom:
                                                fin_rooms[roomid] = 2  # Forced finish
                                            # if consecutive == 1000 and (heat_list.getLevelHeatCount(roomlvl) == 0):  # if conflicts and no previous heats
                                            #     fin_rooms[roomid] = 2  # Forced finish
                                            # Check if levels above or below are empty as well
                                            if dance_dfs_dict_s[curr_lev].empty:
                                                if curr_lev == AB and curr_lev-1 in dance_dfs_dict_s:
                                                    if dance_dfs_dict_s[curr_lev+1].empty:
                                                        fin_rooms[roomid] = 1
                                                if curr_lev > AB and dance_dfs_dict_s[curr_lev-1].empty:
                                                    fin_rooms[roomid] = 1
                                            # Determine if heat finished
                                            if (fin_rooms.count(1) + fin_rooms.count(2)) == len(heat_room_levs):
                                                selection_finished = True
                                                if not level_mode:
                                                    heat_finished = False
                                                if lev_mode_selection:
                                                    heat_finished = True
                            heat_roster.append(curr_heat)  # add this individual heat to roster list
                        # TODO: make the df suited for printing on the excel output, and add the single and couple dfs together
                    key = each + '-' + every + '-' + ev + '-' + len(rosters)
                    heat = Heat(key, 0, heat_roster, instructors_in_heat)
                    rosters.append(heat)
                    tot_current_heats += 1
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

def getContestantConflictList(dance_df,inst,contestants):
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

def getContestantFreeList(dance_df,inst,contestants):
    """Finds the all contestants that are free for the current heat roster given the instructor inst

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
           a list of Dancer #'s that are free with the current heat roster
       """
    # TODO: Find all the possible contestants that will not work with this invalid inst
    # TODO: optimize here by slicing the df based on inst in the list
    free_con = []
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
                    if each.count(singles[contestant_col]) == 0:
                        free_con.append(each)
    return free_con

def calculateOverlap(decend_level_s, instructors_available_in_lev):
    overlap_data = {}
    total = 0
    heat_room_levels = decend_level_s
    # Find total # of instructors
    for each in heat_room_levels:
        overlap_data[each]["lev total"] = len(instructors_available_in_lev[each])
        total = total + len(instructors_available_in_lev[each])
    # find overlap for each level compared to the other
    total_count = 0
    for each in heat_room_levels:
        # Loop over every level besides 'each', find percentage of instructor overlap between them
        for every in decend_level_s[decend_level_s.index(each):]:
            paired_count = 0
            total = len(instructors_available_in_lev[each])+len(instructors_available_in_lev[every])
            for instructor in instructors_available_in_lev[each]:
                if instructors_available_in_lev[every].count(instructor) > 0:
                    total_count += 1
                    paired_count += 1

            overlap_data[each][every] = (overlap_data[each]["lev total"] + overlap_data[every]["lev total"]) - paired_count
            overlap_data[every][each] = (overlap_data[each]["lev total"] + overlap_data[every]["lev total"]) - paired_count

    # find the average overlap for each level compared to the over levels
    for each in overlap_data:
        avg = 0
        for every in overlap_data[each]:
            if every == 'lev total':
                continue
            avg = avg + every
        overlap_data[each]["avg"] = avg/len(decend_level_s)
    overlap_data["total"] = total_count / total
    return overlap_data