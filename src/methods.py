import pandas as pd
from pandas import ExcelWriter
import os
import openpyxl
from Structures import Heat, HeatList
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
                        56
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
    data_sing = {'Dancer #': [101],
                 'First Name': ['Dalton'],
                 'Last Name': ['Dabney'],
                 'Age': [25],
                 'Lead/Follow': ['Lead'],
                 'Level': ["B3"],
                 'Instructor Dancer #':[[205,206]],
                 'School': ['Richmond'],
                 'Open Foxtrot': [1],
                 'Closed ChaCha': [2],
                 'Showdown': [1]
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
                 'Level': ["B3"],
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

    current_heats = 0 # Current total heats made
    # For each genre
    for each in heats:
        # For each syllabus in genre
        for every in heats[each]:
            # For each event in that syllabus event
            for ev in heats[each][every]:
                # TODO: add age prio option, change to dict for easier tracking first break up level dfs based on age then set up iterator variables
                dance_dfs_dict = {}
                keys = [AB, FB, AS, FS, AG, FG]
                goto_next_dance = False  # Flag to set for moving to next dance event,
                                         # if all dfs are empty or too many conflicts
# ------------------------------------------ Build dfs for Selection ---------------------------------------------------
                # Slice dfs based on participation in dance event 'ev' concatenate single and couple df
                for Single, Couple, i in zip(contestant_data['Single'], contestant_data['Couple'], keys):
                    # Slice dfs based on event 'ev'
                    Couple = Couple[Couple[ev] > 0]
                    Single = Single[Single[ev] > 0]

                    dance_dfs_dict[i] = Couple
                    # Add identifier column to Single and Couple dfs and reformat them to concat together
                    # Couple df operations
                    if not Couple.empty:
                        Couple['type id'] = 'C'
                        Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name',
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School',
                                         ev]]
                        dance_dfs_dict[i] = Couple

                    if not Single.empty:
                        # Single df operations both for lead and follow
                        if not Single[Single['Lead/Follow'] == 'Lead'].empty:
                            df = Single[Single['Lead/Follow'] == 'Lead']
                            df['type id'] = 'L'
                            df = df.rename(columns={'First Name': 'Lead First Name', 'Last Name': 'Lead Last Name',
                                                    'Dancer #': 'Lead Dancer #', 'Instructor Dancer #': 'Follow Dancer #'})
                            df['Follow First Name'] = ''
                            df['Follow Last Name'] = ''
                            df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Follow Dancer #',
                                     'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]

                        if not Single[Single['Lead/Follow'] == 'Follow'].empty:
                            df2 = Single[Single['Lead/Follow'] == 'Follow']
                            df2['type id'] = 'F'
                            df2['Lead First Name'] = ''
                            df2['Lead Last Name'] = ''
                            df2.rename(columns={'First Name': 'Follow First Name', 'Last Name': 'Follow Last Name',
                                                'Dancer #': 'Follow Dancer #', 'Instructor Dancer #': 'Lead Dancer #'})
                            df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Follow Dancer #',
                                     'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]
                            df = pd.concat([df, df2])

                            df = df[['type  id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Follow Dancer #',
                                     'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]

                        # Each entry in dict is a level range i.e. AB, FB etc
                        dance_dfs_dict[i] = pd.concat([df, Couple])

                curr_selection_list = dance_dfs_dict[0]  # Start with lowest level first
                curr_lev = keys[AB]
                # TODO: add age prio option, change to dict for easier tracking first break up level dfs based on age then set up iterator variables
                iterator = 0
                dance_heat_count = 0
                
                # Check if current df is empty
                while dance_dfs_dict[curr_lev].empty:
                    del dance_dfs_dict[curr_lev]
                    if curr_lev < FG:
                        curr_lev = keys[curr_lev+1]
                    else:
                        goto_next_dance = True

                # if next dance flag is set continue loop
                # In this case it would only happen if there were no entries to current dance 'ev'
                if goto_next_dance:
                    continue

# ---------------------------------------------- Selection Process -----------------------------------------------------

                rosters = []  # list of individual heats for the current dance 'ev'
                level_bp = []  # holds the breakpoint of where in heat list a new level starts
                # Index Guide: 0 = AB, 1 = FB, ... , 5 = FG,
                # Ff element is 0 there are no heats of that level
                # while there are contestants in the dfs still
                while len(dance_dfs_dict) > 0:
                    # Check if current df is empty
                    while dance_dfs_dict[curr_lev].empty:
                        del dance_dfs_dict[curr_lev]  # Take out empty df
                        level_bp[curr_lev] = dance_heat_count  # Mark the BP for the level
                        if curr_lev < FG:
                            curr_lev = keys[curr_lev + 1]
                        else:
                            goto_next_dance = True
                    heat_roster = []  # holds contestant data for a heat
                    for rooms in enumerate(ballrooms): # for each ballroom create a heat, stops instructor duplication
                        curr_heat = []
                        # Get suitable candidates from the df of the current level (AB, FB, etc)
                        # When a df is depleted remove it from the dictionary, update variables for tracking
                        # don't forget to track the instructors in the roster
                        consecutive = 0  # Stop from infitely looping continual failed attempts to add candidate to the heat
                        instructors_in_heat = [] # -1 if that index is a couple entry
                        done = False  # Used when a heat conflict cannot be resolved and stops selection for that heat
                        while (len(curr_heat) < max_dance_couples) | (not goto_next_dance) | (not done):
                             # TODO: Figure out what sample() output is when empty
                             # TODO: Figure out best way to store the heats while in selection, Dancer # or store the df sinlge entry in a list and then concat them together when printing
                             # TODO: Add Conflict resolution code check notebook for concepts
                            candidate = dance_dfs_dict[curr_lev].sample() # Pick out random entry from df, may need to have try catch
                            # Check not already in heat
                             # TODO: Check this will stop when a candidate is already in the heat
                            if heat_roster.count(candidate) > 0:
                                consecutive += 1 # stop from infitely looping when list has no candidate to add to this heat
                                continue
                            # Check if instructor inside heat, only for Singles
                            if not candidate['type id'] == "C":  # if not a couple entry
                                # Set which column will be used based on Leader or Follower single
                                if candidate['type id'] == 'F':
                                    inst_col = 'Lead Dancer #'
                                else:
                                    inst_col = 'Follow Dancer #'

                                potential_instructors = candidate[inst_col].tolist()
                                # loop through potential_instructors list,
                                # if not in heat already, remove other instructors from candidate
                                # add to heat roster and instructors_in_heat
                                for inst in potential_instructors:
                                    # TODO: Determine what else can be considered other than greedy approach
                                    if instructors_in_heat.count(inst) == 0:
                                        candidate[inst_col] = inst
                                        instructors_in_heat.append(inst)
                                        added = True
                                        break
                            else: # Else meaning a 'couples' entry
                                added = True
                                instructors_in_heat.append(-1)
                            # if candidate was found possible add to the roster and remove that entry from the query
                            if added:
                                # if last or only entry remove it from query_df
                                if candidate.loc[every] == 1:
                                    dance_dfs_dict = dance_dfs_dict.drop(candidate)
                                else:
                                    dance_dfs_dict.loc[dance_dfs_dict["Dancer #"] == candidate["Dancer #"], every] = candidate["Dancer #"] - 1
                                curr_heat.append(candidate)
                                # Check if current df is empty after adding the candidate
                                while dance_dfs_dict[curr_lev].empty:
                                    del dance_dfs_dict[curr_lev]  # Take out empty df
                                    level_bp[curr_lev] = dance_heat_count  # Mark the BP for the level
                                    if curr_lev < FG:
                                        curr_lev.remove(curr_lev) #TODO this may not work
                                        curr_lev = keys[curr_lev+1]
                                    elif keys != []:
                                        curr_lev = keys[0]
                                    else:
                                        goto_next_dance = True

                            else:
                                consecutive += 1
                        heat_roster.append(curr_heat) # add this individual heat to roster list
                        # TODO: make the df suited for printing on the excel output, and add the single and couple dfs together
                    key = each + '-' + every + '-' + ev + '-' + len(rosters)
                    heat = Heat(key, 0, heat_roster, instructors_in_heat)
                    rosters.append(heat)
                    current_heats =+ 1
                    dance_heat_count += 1
            # Once all heats for an Event/Dance are made create a HeatList object
            heatlist = HeatList(rosters, level_bp, len(rosters))
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




