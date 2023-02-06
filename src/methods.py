import pandas as pd
from pandas import ExcelWriter
import os
import random
import openpyxl
from openpyxl import workbook
from openpyxl.styles import PatternFill
import socket
from Structures import Heat, HeatList, ConflictLog, ConflictItemSingle
from uuid import getnode as gma

'''
FIle with all methods used to create the Freestyle itenerary
'''
IP = ""
port = 8989

max_conflicts = 1000
def run():
    # Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO encrypt the file with the ip addr, add read and decryption here
    client.connect((IP, port))

    # Import all input Sheets independently
    file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'

    # get file and size
    bytestr = open(file, "rb")
    # fileSize = os.path.getsize(file)

    # Make file name the Event name in the server
    df_set = pd.read_excel(file, sheet_name='Settings', index_col=0)
    eventName = df_set['Data']['Event Name']

    # Get mac address, if not faked send all the data
    mac1 = gma()
    if mac1 == gma():
        # Send all info
        client.send((eventName + ".xlsm").encode())
        client.send(gma())
        # client.send(str(fileSize).encode())

        data = bytestr.read()
        client.sendall(data)
        client.send(b"<Terminate>")

    # TODO continually run until a message comes from the server, depending on the message execute differently
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
    """
    # Import all input Sheets independently
    file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
    df_set = pd.read_excel(file, sheet_name='Settings', index_col=0)
    df_cat = pd.read_excel(file, sheet_name='Event Categories')

    # Make list of Genres
    genrelist = list(df_cat['Genre'].unique())
    # Make list of Dances/Events
    dancelist = list(df_cat['Dance'].unique())

    heats = makeHeatDict(genrelist, df_cat)

    # Stops pandas from reading useless blank columns
    cols = []
    for i in range(len(dancelist)+baseSingleCols):
        cols.append(i)

    df_sing = pd.read_excel(file, sheet_name='Singles', usecols=cols)
    df_sing['id'] = ''
    df_sing["Dancer #"] = df_sing['Dancer #'].astype(int)
    df_sing["Age"] = df_sing['Age'].astype(int)
    # for row, entry in df_sing.iterrows():
    #     # Retrofit the instructor list data
    #     if type(entry["Instructor Dancer #'s"]) == int:
    #         tmp = [entry["Instructor Dancer #'s"]]
    #     else:
    #         tmp = [int(x) for x in entry["Instructor Dancer #'s"].split(";")]
    #     entry["Instructor Dancer #'s"] = tmp
    #     del tmp

    # Stops pandas from reading useless blank columns
    cols = []
    for i in range(len(dancelist) + baseCoupleCols):
        cols.append(i)

    df_coup = pd.read_excel(file, sheet_name='Couples', usecols=cols)
    df_coup["Lead Dancer #"] = df_coup['Lead Dancer #'].astype(int)
    df_coup["Follow Dancer #"] = df_coup['Follow Dancer #'].astype(int)
    df_coup["Lead Age"] = df_coup['Lead Age'].astype(int)
    df_coup["Follow Age"] = df_coup['Follow Age'].astype(int)

    df_inst = pd.read_excel(file, sheet_name='Instructors')
    df_inst["Dancer #"] = df_inst['Dancer #'].astype(int)

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
    for each in range(bracket_count-1):
        age_brackets.append(int(df_set['Data'][each + days + 2]))
    age_brackets.append(1000)  # Append to make sure to get the last age bracket

    # Max number of couples on the floor for a dance assume even # of judges per ballroom
    max_dance_couples = judges * judge_ratio
    # couples_per_ballroom = int(max_dance_couples / ballrooms)  # Number of Couples on a singular ballroom
    couples_per_ballroom = 7  # Number of Couples on a singular ballroom

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
                dance_dfs = {"C": {}, "S": {"Lead": {}, "Follow": {}}}
                l_keys = [AB, FB, AS, FS, AG, FG]
                keys_in_s = [AB, FB, AS, FS, AG, FG]
                keys_in_c = [AB, FB, AS, FS, AG, FG]
                # instructors_available_in_lev = []
                unideal_heats = []  # Holds metadata on unideal heat to be filled by a level +- 1 if possible
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
                # Slice dfs based on participation in dance event 'ev', level, type, age
                # Add identifier column Couple dfs and reformat to be ready for heat sheet print, Singles done later
                # TODO: Get event division from event df
                #  then break down each dvision to its smallest parts then combine where needed based on the division data
                eventrow = df_cat.loc[df_cat['Dance'] == ev].reset_index(drop=True)
                div = eventrow.loc[:, 'Event Divisions'][0].split(";")

                # Build Couples df for this event broken down by all metrics
                shell_c = {}
                for Couple, lvl in zip(contestant_data['Couple'], l_keys):
                    Couple = Couple[Couple[ev] > 0]
                    dance_dfs["C"][lvl] = {}
                    shell_c[lvl] = {}
                    if not Couple.empty:  # Couple df operations
                        Couple['type id'] = 'C'
                        Couple = Couple[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', 'Lead Age',
                                         'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age',
                                         'Level', 'School', ev]]
                        if div.count('t') == 0 or div.count("T") == 0:
                            Couple["Instructor Dancer #'s"] = ''
                        for i, age in enumerate(age_brackets):
                            # Slice Couple so that it is inside age bracket
                            if i == 0:  # Set bounds of age bracket
                                lower = 18
                                upper = age
                            else:
                                lower = age_brackets[i - 1] + 1
                                upper = age
                            # Split the df based on which age is lower and then add them together at the end
                            sliced_f = Couple[Couple["Lead Age"] >= Couple["Follow Age"]]
                            sliced_f = sliced_f[(lower <= sliced_f["Follow Age"]) & (sliced_f["Follow Age"] <= upper)]
                            sliced_l = Couple[Couple["Lead Age"] < Couple["Follow Age"]]
                            sliced_l = sliced_l[(lower <= sliced_l["Lead Age"]) & (sliced_l["Lead Age"] <= upper)]
                            shell_c[lvl][age] = pd.concat([sliced_l, sliced_f])
                    else:
                        for i, age in enumerate(age_brackets):
                            dance_dfs["C"][lvl][age] = pd.DataFrame()
                            shell_c[lvl][age] = pd.DataFrame()


                # if not Couple.empty:
                #     pass
                #     # total_contestants_c = total_contestants_c + Couple.shape[0]
                #     # total_entries_c = total_entries_c + Couple[ev].sum()
                #     # added = False
                #     # for i, lev in enumerate(decend_level_c):
                #     #     if lev[1] <= Couple.shape[0]:
                #     #         added = True
                #     #         decend_level_c.insert(i-1, [lvl, Single.shape[0]])
                #     #         # decend_level_c.append([lvl, Couple.shape[0]]) for testing
                #     #         break
                #     # if not added:
                #     #     decend_level_c.append([lvl, Couple.shape[0]])
                shell_s = {"Lead": {}, "Follow": {}}
                shell_i = {"Lead": {}, "Follow": {}}
                for Single, lvl in zip(contestant_data['Single'], l_keys):
                    Single = Single[Single[ev] > 0]
                    dance_dfs["S"]["Lead"][lvl] = {}
                    dance_dfs["S"]["Follow"][lvl] = {}
                    shell_s["Lead"][lvl] = {}
                    shell_i["Lead"][lvl] = {}
                    shell_s["Follow"][lvl] = {}
                    shell_i["Follow"][lvl] = {}
                    if not Single.empty:
                        if not Single[Single['Lead/Follow'] == 'Lead'].empty:
                            df = Single[(Single['Lead/Follow'] == 'Lead') | (Single['Lead/Follow'] == 'L')]
                            df['type id'] = 'L'
                            df = df.rename(columns={'First Name': 'Lead First Name', 'Last Name': 'Lead Last Name',
                                                    'Dancer #': 'Lead Dancer #', "Age": "Lead Age"})
                            df['Follow First Name'] = ''
                            df['Follow Last Name'] = ''
                            df['Follow Age'] = ''
                            df['Follow Dancer #'] = ''
                            df = df[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age", "Follow Age", "Instructor Dancer #'s",
                                     'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School', ev]]
                            for i, age in enumerate(age_brackets):
                                # SLice so that it is inside age bracket
                                if i == 0:  # Set bounds of age bracket
                                    lower = 18
                                    upper = age
                                else:
                                    lower = age_brackets[i - 1] + 1
                                    upper = age
                                # Split the df based on which age is lower and then add them together at the end
                                sliced_l = df[(lower <= df["Lead Age"]) & (df["Lead Age"] <= upper)]
                                shell_s["Lead"][lvl][age] = sliced_l
                                shell_i["Lead"][lvl][age] = {}
                                # Find unique instructors for this division
                                # TODO: test this and then copy to follows
                                for row, data in sliced_l.iterrows():  # Iterate down all rows of Single df
                                    if type(data["Instructor Dancer #'s"]) == int:
                                        tmp = [data["Instructor Dancer #'s"]]
                                    else:
                                        tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
                                    data["Instructor Dancer #'s"] = tmp
                                    del tmp
                                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                                        if num in shell_i["Lead"][lvl][age].keys():
                                            shell_i["Lead"][lvl][age][num] += 1
                                        else:
                                            shell_i["Lead"][lvl][age][num] = 1
                        else:
                            for i, age in enumerate(age_brackets):
                                dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                                shell_s["Lead"][lvl][age] = pd.DataFrame()
                                shell_i["Lead"][lvl][age] = pd.DataFrame()

                        if not Single[Single['Lead/Follow'] == 'Follow'].empty:

                            df2 = Single[Single['Lead/Follow'] == 'Follow']
                            df2['type id'] = 'F'
                            df2 = df2.rename(columns={'First Name': 'Follow First Name', 'Last Name': 'Follow Last Name',
                                                'Dancer #': 'Follow Dancer #', "Age": "Follow Age"})
                            df2['Lead First Name'] = ''
                            df2['Lead Last Name'] = ''
                            df2['Lead Age'] = ''
                            df2['Lead Dancer #'] = ''
                            df2 = df2[['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name', "Lead Age" , "Instructor Dancer #'s",
                                     'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Follow Age', 'Level', 'School', ev]]
                            for i, age in enumerate(age_brackets):
                                # SLice Couple so that it is inside age bracket
                                if i == 0:  # Set bounds of age bracket
                                    lower = 18
                                    upper = age
                                else:
                                    lower = age_brackets[i - 1] + 1
                                    upper = age
                                # Split the df based on which age is lower and then add them together at the end
                                sliced_f = df2[(lower <= df2["Follow Age"]) & (df2["Follow Age"] <= upper)]
                                shell_s["Follow"][lvl][age] = sliced_f
                                shell_i["Follow"][lvl][age] = {}

                        else:
                            for i, age in enumerate(age_brackets):
                                dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                                shell_s["Follow"][lvl][age] = pd.DataFrame()
                                shell_i["Follow"][lvl][age] = pd.DataFrame()
                    else:
                        for i, age in enumerate(age_brackets):
                            dance_dfs["S"]["Lead"][lvl][age] = pd.DataFrame()
                            dance_dfs["S"]["Follow"][lvl][age] = pd.DataFrame()
                            shell_s["Follow"][lvl][age] = pd.DataFrame()
                            shell_s["Lead"][lvl][age] = pd.DataFrame()
                            shell_i["Lead"][lvl][age] = pd.DataFrame()
                            shell_i["Follow"][lvl][age] = pd.DataFrame()

                # Add together dfs based on the division metrics of this event
                if div.count('A') == 0 and div.count('a') == 0:
                    # Lead concat
                    for lvl in shell_s["Lead"].keys():
                        for i, key in enumerate(shell_s["Lead"][lvl].keys()):
                            if i == 0:
                                tmp = shell_s["Lead"][lvl][key]
                                continue
                            tmp = pd.concat([tmp, shell_s["Lead"][lvl][key]])
                        shell_s["Lead"][lvl] = tmp
                    # Combine Instructor data
                    for lvl in shell_i["Lead"].keys():
                        for i, key in enumerate(shell_i["Lead"][lvl].keys()):
                            if i == 0:
                                tmp = shell_i["Lead"][lvl][key]
                                continue
                            tmp = tmp.update(shell_i["Lead"][lvl][key])
                        shell_s["Lead"][lvl] = tmp


                    # Follow Concat
                    for lvl in shell_s["Follow"].keys():
                        for i, key in enumerate(shell_s["Follow"][lvl].keys()):
                            if i == 0:
                                tmp = shell_s["Follow"][lvl][key]
                                continue
                            tmp = pd.concat([tmp, shell_s["Follow"][lvl][key]])
                        shell_s["Follow"][lvl] = tmp

                    # Couple Concat
                    for lvl in shell_c.keys():
                        for i, key in enumerate(shell_c[lvl].keys()):
                            if i == 0:
                                tmp = shell_c[lvl][key]
                                continue
                            tmp = pd.concat([tmp, shell_c[lvl][key]])
                        shell_c[lvl] = tmp

                # Combine all levels if needed
                if div.count('L') == 0 and div.count('l') == 0:
                    # Lead Concat
                    for i, lvl in enumerate(shell_s["Lead"].keys()):
                        if i == 0:
                            tmp = shell_s["Lead"][lvl]
                            continue
                        if type(tmp) is dict:
                            for subkey in tmp.keys():
                                tmp[subkey] = pd.concat([tmp[subkey], shell_s["Lead"][lvl][subkey]])
                        else:
                            tmp = pd.concat([tmp, shell_s["Lead"][lvl]])
                    shell_s["Lead"] = tmp

                    # Follow Concat
                    for i, lvl in enumerate(shell_s["Follow"].keys()):
                        if i == 0:
                            tmp = shell_s["Follow"][lvl]
                            continue
                        if type(tmp) is dict:
                            for subkey in tmp.keys():
                                tmp[subkey] = pd.concat([tmp[subkey], shell_s["Follow"][lvl][subkey]])
                        else:
                            tmp = pd.concat([tmp, shell_s["Follow"][lvl]])
                    shell_s["Follow"] = tmp

                    for i, key in enumerate(shell_c.keys()):
                        if i == 0:
                            tmp = shell_c[key]
                            continue
                        if type(tmp) is dict:
                            for subkey in tmp.keys():
                                tmp[subkey] = pd.concat([tmp[subkey], shell_c[key][subkey]])
                        else:
                            tmp = pd.concat([tmp, shell_c[key]])
                    shell_c = tmp

                # if event Singles should be combined
                if (div.count('S') == 0 and div.count('s') == 0) or (div.count('T') == 0 and div.count('t') == 0):
                    # Singles Lead/Follow Concat
                    for i, key in enumerate(shell_s.keys()):
                        if i == 0:
                            tmp = shell_s[key]
                            continue
                        if type(tmp) is dict: # Go down the tree and combine the corresponding N nodes
                            for subkey in tmp.keys():
                                if type(tmp[subkey]) is dict:
                                    for subkey2 in tmp[subkey].keys():
                                        tmp[subkey][subkey2] = pd.concat([tmp[subkey][subkey2], shell_s[key][subkey][subkey2]])
                                else:
                                    tmp[subkey] = pd.concat([tmp[subkey], shell_s[key][subkey]])
                        else:
                            tmp = pd.concat([tmp, shell_s[key]])
                    shell_s = tmp

                # put shells into df
                dance_dfs["S"] = shell_s
                dance_dfs["C"] = shell_c

                # If Couples and Singles need to be combined
                if div.count('T') == 0 and div.count('t') == 0:
                    for i, key in enumerate(dance_dfs.keys()):
                        if i == 0:
                            tmp = dance_dfs[key]
                            continue
                        if type(tmp) is dict:  # Go down the tree and combine the corresponding N nodes
                            for subkey in tmp.keys():
                                if type(tmp[subkey]) is dict:
                                    for subkey2 in tmp[subkey].keys():
                                        tmp[subkey][subkey2] = pd.concat([tmp[subkey][subkey2], dance_dfs[key][subkey][subkey2]])
                                else:
                                    tmp[subkey] = pd.concat([tmp[subkey], dance_dfs[key][subkey]])
                        else:
                            tmp = pd.concat([tmp, dance_dfs[key]])
                    dance_dfs["A"] = tmp
                    del dance_dfs["S"]
                    del dance_dfs["C"]

                    del shell_s
                    del shell_c

                # df = pd.DataFrame()
                # # Single df operations both for lead and follow
                # if not Single.empty:
                #     # Find totals for this Singles level
                #     total_contestants_s = total_contestants_s + Single.shape[0]
                #     total_entries_s = total_entries_s + Single[ev].sum()
                #     # Track Levels largest to smallest
                #     added = False
                #     for i, lev in enumerate(decend_level_s):
                #         if lev[1] <= Single.shape[0]:
                #             added = True
                #             decend_level_s.insert(i-1, [lvl, Single.shape[0]])
                #             # decend_level_s.append([lvl, Single.shape[0]]) for testing
                #             break
                #     if not added:
                #         decend_level_s.append([lvl, Single.shape[0]])

                # # Set up Percent trackers
                # for key in keys:
                #     if dance_dfs_dict_s[key].empty:
                #         lev_percent_s.append(-1)
                #         percent_left_s.append(-1)
                #     else:
                #         lev_percent_s.append(dance_dfs_dict_s[key][ev].sum() / total_entries_s)
                #         percent_left_s.append(1.0)
                #
                #     if dance_dfs_dict_c[key].empty:
                #         lev_percent_c.append(-1)
                #         percent_left_c.append(-1)
                #     else:
                #         lev_percent_c.append(dance_dfs_dict_c[key][ev].sum() / total_entries_c)
                #         percent_left_c.append(1.0)

                # # Set Holes
                # for key in keys:
                #     if dance_dfs_dict_s[key].empty:
                #         tot_holes.append(-1)
                #     else:
                #         tot_holes.append(0)

                # Check if current dfs are empty, and remove them
                deleteEmpty(dance_dfs)

                # if both Pools are totally empty continue
                # In this case it would only happen if there were no entries to current dance 'ev'
                if len(dance_dfs) == 0:
                    continue
                inst_tree = buildInstTree(dance_dfs, {}, ev)
                inst2sing_tree = buildInst2SingTree(dance_dfs, {}, ev)
                pre_inst_tree = inst_tree.copy()
# ---------------------------------------------- Selection Process -----------------------------------------------------
                # TODO: may have to make 2 conflict resolvers/holders one for singles and one for couples
                floors = eventrow.loc[:, 'Floors'][0]
                heat_list = HeatList([], floors, 0)  # list of individual heats for the current dance 'ev'
                singles_empty = False  # True when all singles are in heats for this event 'ev'
                couples_empty = False  # True when all couples are in heats for this event 'ev'
                while len(dance_dfs) > 0:  # while there are contestants in the dfs still
                    heat_roster = []  # holds full contestant data for a heat, each element is a list for a dance floor
                    fin_rooms = []  # marks a room as finished with a 1
                    instructors_in_heat = []  # Holds instructor numbers for quick reference
                    singles_in_heat = []  # Holds contestant number for quick reference
                    couples_in_heat = []  # Holds Couples number for quick ref.
                    # couples_in_heat format [[1 Lead #,1 Follow #,...,N Follow #],...[1 Lead #,1 Follow #,..., N Follow #]]
                    floor_info = pickDfs(ev, dance_dfs, inst_tree, floors, div, age_brackets, couples_per_ballroom)
                    if len(floor_info) < floors:
                        split_mode = 1
                        vacant_rooms = floors - len(floor_info)
                    for floor in range(floors):
                        heat_roster.append([])
                        instructors_in_heat.append([])
                        singles_in_heat.append([])
                        couples_in_heat.append([])
                        fin_rooms.append(0)
                    heat_finished = False
                    # selection_dfs = []
                    s_floors = []
                    sfin_rooms = []
                    c_floors = []
                    cfin_rooms = []
                    # Separate out singles and couple assigned floors
                    if 't' in div or 'T' in div:
                        for floor in floor_info:
                            if floor[0] == "S":
                                s_floors.append(floor)
                                sfin_rooms.append(0)
                            else:
                                c_floors.append(floor)
                                cfin_rooms.append(0)
                    heat_key = each + '-' + every + '-' + ev + '-' + str(len(heat_list.getRostersList()))
                    log = ConflictLog(floor_info)  # make conflict log for this heat
                    heat = Heat(heat_key, floor_info, heat_roster, singles_in_heat, instructors_in_heat, couples_in_heat)
                    while not heat_finished:
                        # ---------------------------------------------- Singles ---------------------------------------
                        lev_mode_selection = False  # Indicate if/when a level mode selection is happening
                        # TODO move some of this code to the pickDf function as that will provide answer to start to try and split up levels
                        # # Check how many levels there are
                        # level_count = 0
                        # for lev in keys_in_s:
                        #     if lev > -1:
                        #         level_count += 1
                        # # if levels > rooms assign based on ratio of instructor to student
                        # # TODO: finish and Test levels > ballrooms
                        # #  selected first based on % then based on instructor overlap
                        # #  Get all possible level combos overlap between all levels in heat select the lowest overlap
                        # #  Just go with largest number of instructors firstone
                        # if level_count > ballrooms:
                        #     # heat_room_levs.append(decend_level_s[0][0]) # Add largest level to the heat list
                        #     overlap_data = calculateOverlap(instructors_available_in_lev, ballrooms)
                        #     looped = False
                        #     # While rooms are not filled
                        #     while len(heat_room_levs) < ballrooms:
                        #         # Go down list of largest rooms and if they fit fill them
                        #         for i, lev in enumerate(decend_level_s):
                        #             lev = lev[0]
                        #             if heat_room_levs.count(lev) > 0:
                        #                 continue
                        #             if overlap_data[lev]['level total'] >= couples_per_ballroom*.5:
                        #                 if overlap_data[lev]['avg'] >= .45:
                        #                     heat_room_levs.append(lev)
                        #                     continue
                        #             if looped:
                        #                 heat_room_levs.append(lev)
                        #             if len(heat_room_levs) == ballrooms:
                        #                 break
                        #         looped = True

                        # if levels < rooms assign all the levels then come back after full or conflicts

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
                        heat_holes = []
                        for place in floor_info:
                            heat_holes.append(0)
                        # Make Instructors for heat list that will change based on placed contestants and instructors
                        dfs_for_heat = []
                        inst_tree_nodes = []
                        inst2sing_tree_nodes = []
                        instructors_available_for_heat = []
                        for roomid, info in enumerate(s_floors):
                            for i, key in enumerate(info):
                                if i == 0:
                                    tmp = dance_dfs[key]
                                    tmp2 = inst_tree[key]
                                    tmp3 = inst2sing_tree[key]
                                elif type(tmp) is dict:
                                    tmp = tmp[key]
                                    tmp2 = tmp2[key]
                                    tmp3 = tmp3[key]
                            dfs_for_heat.append(tmp)
                            inst_tree_nodes.append(tmp2)
                            inst2sing_tree_nodes.append(tmp3)
                            instructors_available_for_heat.append(list(tmp2.keys()))
                        selection_finished = False
                        print("Event " + ev + ", Heat number: " + str(heat_list.getHeatCount()))
                        print(floor_info)
                        print()
                        while not selection_finished:
                            if len(s_floors) == 0:  # If no singles move to couples selection
                                break
                            # Selection is before
                            # TODO: try to get as many instructors in the heat as possible
                            # TODO: track count conflict between matches, conflict type
                            #  internal: no free contestant for inst save contestants who are dupe
                            #  external: instructor not free
                            #
                            for roomid, room_info in enumerate(s_floors):  # For each ballroom make 1 instructor/single pair
                                if sfin_rooms[roomid] > 0:  # if room is filled or declared full, continue on
                                    continue
                                placed = False  # Set when a valid instructor/single pair is placed
                                attempted = []  # holds instructors attempted for this search
                                consecutive = 0  # Stops infinite loops on failed attempts to add candidate to the heat
                                solved = 0  # counts how many resolveConflict() calls for this pair search
                                while (not placed) and not (sfin_rooms[roomid] > 0):  # Find a viable single/inst match
                                    # TODO: test instructor conflict
                                    if consecutive > max_conflicts:
                                        resolveConflictSingles(roomid, dance_dfs, log, heat, heat_list, instructors_available_for_heat, solved, inst_tree, inst2single_tree, df_inst)
                                        print("max conflicts in ", room_info, "df size", dfs_for_heat[roomid].shape[0], " heat index ", dance_heat_count)
                                        print(" ")
                                    contestantconflicts = []

                                    inst = random.choice(instructors_available_for_heat[roomid])  # get random instructor, will throw error if list at index is empty
                                    instructor_taken = False
                                    for selection in instructors_in_heat:
                                        if instructor_taken:
                                            break
                                        if selection.count(inst) > 0:  # Check if instructor is being used in heat
                                            instructor_taken = True
                                            break
                                    if instructor_taken:
                                        cons = getContestantConflictList(dfs_for_heat[roomid], inst, singles_in_heat)
                                        log.addConflict(ConflictItemSingle(1, cons, inst, 'e'), roomid)
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
                                    df_shuffled = dfs_for_heat[roomid].sample(frac=1)
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
                                        # Retrofit the instructor list entry
                                        if type(entry["Instructor Dancer #'s"]) == int:
                                            tmp = [entry["Instructor Dancer #'s"]]
                                        else:
                                            tmp = [int(x) for x in entry["Instructor Dancer #'s"].split(";")]
                                        entry["Instructor Dancer #'s"] = tmp
                                        del tmp
                                        # Loop over the instructor list for the contestant row
                                        for num in entry["Instructor Dancer #'s"]:
                                            if num == inst:
                                                for i, rost in enumerate(singles_in_heat):
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
                                        heat.addEntry(candidate, roomid)
                                        heat_roster = heat.getRoster()
                                        instructors_in_heat = heat.getInstructors()
                                        singles_in_heat = heat.getSingles()
                                        instructors_available_for_heat[roomid].remove(inst)
                                        print("Candidate placed: ")
                                        print(candidate.loc[0, contestant_col])
                                        print(roomid, floor_info)
                                        print("Deleting from inst tree")
                                        for num in candidate.loc[:, "Instructor Dancer #'s"][0]:
                                            if inst_tree_nodes[roomid][num] == 1:
                                                del inst_tree_nodes[roomid][num]
                                                if num in instructors_available_for_heat[roomid]:
                                                    instructors_available_for_heat[roomid].remove(num)
                                            else:
                                                inst_tree_nodes[roomid][num] -= 1
                                        # Remove the placed candidate from the df, or -1 if multi-entry
                                        print("Deleting from dancer df")
                                        print()
                                        if candidate.loc[:, ev][0] == 1:
                                            dfs_for_heat[roomid] = dfs_for_heat[roomid].drop(dfs_for_heat[roomid][dfs_for_heat[roomid][contestant_col] == candidate.loc[0, contestant_col]].index)
                                        else:
                                            dfs_for_heat[roomid].loc[dfs_for_heat[roomid].loc[:, contestant_col] == candidate.loc[0, contestant_col], ev] = candidate.loc[0, ev] - 1
                                        placed = True
                                        # Check if current level df is empty after a placed candidate
                                        if dfs_for_heat[roomid].empty:
                                            sfin_rooms[roomid] = 1
                                            del dfs_for_heat[roomid]  # Delete df
                                            deleteEmpty(dance_dfs)  # Remove the keys from the tree that are empty
                                            if dance_dfs.get("S") is None:
                                                singles_empty = True
                                    else:
                                        log.addConflict(ConflictItemSingle(2, contestantconflicts, inst, 'i'), roomid)
                                        consecutive += 1
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        pass
                                    # Determine if room is finished
                                    if len(heat_roster[roomid]) == couples_per_ballroom:
                                        sfin_rooms[roomid] = 1
                                        if dfs_for_heat[roomid].shape[0] < int(couples_per_ballroom / 2):
                                            if dfs_for_heat[roomid][ev].sum() < heat_list.getDivisionHeatCount(room_info) * 2:
                                                backfill(dfs_for_heat[roomid], room_info, heat_list, df_inst)
                                                deleteEmpty(dfs_for_heat)
                                                if dance_dfs.get("S") is None:
                                                    singles_empty = True
                                            else:
                                                print("Not enough heats to backfill")
                                    if singles_empty:
                                        for i in enumerate(sfin_rooms):
                                            if sfin_rooms[i] == 0:
                                                sfin_rooms[i] = 1
                                    if len(instructors_available_for_heat[roomid]) == 0:
                                        sfin_rooms[roomid] = 1
                                    if solved == 1000 and len(heat_roster[roomid]) != couples_per_ballroom:
                                        sfin_rooms[roomid] = 2  # Forced finish
                                    # TODO change the heat list class to track based on all keys not just lvl
                                    if consecutive > max_conflicts and (heat_list.getDivisionHeatCount(room_info) == 0):  # if conflicts and no previous heats
                                        print("Initial Heat for ", room_info, " forced finish")
                                        print("df size:", dfs_for_heat[roomid].shape[0])
                                        print("roster:", heat_roster[roomid])
                                        sfin_rooms[roomid] = 2  # Forced finish
                                    # Determine if heat finished
                                    if (sfin_rooms.count(1) + sfin_rooms.count(2)) == len(s_floors):
                                        selection_finished = True
                                        # if not split_mode:
                                        #     heat_finished = False
                                        # if lev_mode_selection:
                                        #     heat_finished = True

                        # selection_dfs.append(dfs_for_heat[:])
                            # Selection finished
                            # # Update Holes metadata
                            # if not lev_mode_selection:
                            #     pass
                            #     # # Add number of holes before a level mode selection
                            #     # for i, lvl in enumerate(heat_room_levs):
                            #     #     tot_holes[lvl] += couples_per_ballroom - len(heat_roster[i])
                            #     #     heat_holes[i] = couples_per_ballroom - len(heat_roster[i])
                            # else:
                            #     # Add holes after level mode selection but only to newly filled room
                            #     i = vacant_rooms  # Start of the vacant rooms
                            #     for lvl in level_mode_selection_lev:
                            #         tot_holes[lvl] += (couples_per_ballroom - len(heat_roster[i]))
                            #         heat_holes[i] = (couples_per_ballroom - len(heat_roster[i]))
                            #         i += 1

                        # Heat fully complete Construct key for the new heat
                        # Fill the unused room data if needed
                        # if len(heat_room_levs) < ballrooms:
                        #     for i in range(ballrooms-len(heat_room_levs)):
                        #         heat_room_levs.append(-1)
                        #         heat_holes.append(couples_per_ballroom)
                        # Update Dance dfs with all placements
                        for df, info in zip(dfs_for_heat, s_floors):
                            dance_dfs = updateDanceDfs(dance_dfs, df, info)
                        # ---------------------------------------------- Couples ---------------------------------------
                        # TODO: while loop the ends when couples df is empty
                        #  first loop over heatlist and fill the holes currently there, making any swaps with the conflict resolver
                        #  then start making couple only heats, much of the code can be reused for couples but much less complicated
                        # backfill_mode = True  # Indicates when all backfilling is complete
                        if len(c_floors) > 0:  # if a couples key has been picked
                            dfs_for_heat = []
                            for roomid, info in enumerate(c_floors):
                                for i, key in enumerate(info):
                                    if i == 0:
                                        tmp = dance_dfs[key]
                                        continue
                                    if type(tmp) is dict:
                                        tmp = tmp[key]
                                dfs_for_heat.append(tmp)
                            # Loop rooms, backfill or filling new room to completion before moving to the next room
                            for roomid, room_info in enumerate(c_floors):
                                # If room finished
                                if cfin_rooms[roomid] > 0:
                                    continue
                                consecutive = 0  # Stops infinite looping continual failed attempts to add candidate to the heat
                                solved = 0  # counts how many resolveConflict() calls for this heat
                                done = False  # Used when a heat conflict cannot be resolved and stops selection for that heat
                                # Get suitable candidates from the df of the current division
                                if len(s_floors) > 0:
                                    singles_index = len(s_floors)-1
                                else:
                                    singles_index = 0
                                while len(heat_roster[roomid+singles_index]) < max_dance_couples and (not done):
                                    if consecutive > max_conflicts:
                                        print(info, dfs_for_heat[roomid].shape[0], dance_heat_count)
                                        break
                                        # if solved < 1000:
                                        #      if resolveConflict(curr_heat, dance_dfs_dict_c, conflcitlist, heat_roster, solved):
                                        #         solved += 1
                                        # else:
                                        #     pass
                                            # TODO: compare what is left to max heat size, if much greater re-roll or done and continue if it happens again this category may be doinked,
                                            #  if much less there are some options: 'done' the heat continue building,
                                            #  add the pool to next level df and build from there,

                                    # TODO: Add Conflict resolution code check notebook for concepts, much less robust than before with single and couple split
                                    candidate = dfs_for_heat[roomid].sample(ignore_index=True)  # Pick out random entry from df, may need to have try catch
                                    added = False
                                    # Check candidate has no one already in heat
                                    dup_sing = False
                                    dup_inst = False
                                    dup_coup = False
                                    if candidate.loc[0, 'type id'] == 'C':
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
                                    # TODO move to 'A' code
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
                                    #             if lev.count(inst) != 0:
                                    #                 found = True
                                    #                 break
                                    #         if not found:
                                    #             instructors_in_heat[roomlvl].append(inst)
                                    #             added = True
                                    #             break
                                    # instructors_in_heat[roomlvl].append(-1)
                                    else:  # Else = there are no conflicts
                                        added = True
                                        # if candidate possible add to the roster,remove that entry from the query
                                        heat.addEntry(candidate, roomid+singles_index)
                                        col = "Lead Dancer #"
                                        fcol = "Follow Dancer #"
                                        # if last or only entry remove it from query_df
                                        if candidate.loc[0, ev] == 1:
                                            dfs_for_heat[roomid+singles_index] = dfs_for_heat[roomid+singles_index][dfs_for_heat[roomid+singles_index].loc[:,col] != candidate.loc[0, col]]
                                        else:
                                            dfs_for_heat[roomid+singles_index].loc[dfs_for_heat[roomid+singles_index].loc[:, col] == candidate.loc[0, col], [ev]] = candidate.loc[0, ev] - 1
                                        # Add candidate data to tracker lists
                                        heat_roster = heat.getRoster()
                                        couples_in_heat = heat.getCouples()
                                        # Check if current df is empty after adding the candidate
                                        if dfs_for_heat[roomid+singles_index].empty:
                                            del dfs_for_heat[roomid+singles_index]  # Delete df
                                            deleteEmpty(dance_dfs) # Clean up parent levels if needed
                                            # keys_in_c[curr_lev] = -1  # Make key location -1 to show level is empty
                                            if dance_dfs.get("C") is None:
                                                couples_empty = True
                                    if couples_empty:
                                        for i in enumerate(cfin_rooms):
                                            if cfin_rooms[i] == 0:
                                                cfin_rooms[i] = 1
                                    if solved == 1000 and len(heat_roster[roomid+singles_index]) != couples_per_ballroom:
                                        cfin_rooms[roomid] = 2  # Forced finish
                                    if consecutive == max_conflicts and (heat_list.getDivisionHeatCount(room_info) == 0):  # if conflicts and no previous heats
                                        cfin_rooms[roomid] = 2  # Forced finish
                                    # Determine if heat finished
                                    if len(heat_roster[roomid+singles_index]) == couples_per_ballroom:
                                        cfin_rooms[roomid] = 1
                                        if dfs_for_heat[roomid].shape[0] < int(couples_per_ballroom/2):
                                            if dfs_for_heat[roomid][ev].sum() < heat_list.getDivisionHeatCount(room_info)*2:
                                                backfill(dfs_for_heat[roomid], room_info, heat_list, df_inst)
                                                deleteEmpty(dfs_for_heat)
                                            else:
                                                print("Not enough heats to backfill")
                                        break
                                    if (cfin_rooms.count(1) + cfin_rooms.count(2)) == len(c_floors):
                                        break
                            for df, info in zip(dfs_for_heat, c_floors):
                                dance_dfs = updateDanceDfs(dance_dfs, df, info)
    # ------------------------------------------------- Double up on unused rooms --------------------------------------
                        # If levels < ballrooms and not in split mode already, figure out if the current selection pool can be put into open room(s)
                        if len(floor_info) < floors and not split_mode:
                            # Sanity Check all the current floors
                            splits = []
                            for i, info in enumerate(room_info):
                                # Find meta data for singles list
                                if info[0] == "S":
                                    unique = findUnique(pre_inst_tree, s_floors, [])
                                    if not unique > couples_per_ballroom*2:  # If room cannot be split due to instructor constraints
                                        continue
                                    count = findContestantCount(dance_dfs, info)
                                    # if len(leftover_inst) < count:
                                    #     count = len(leftover_inst)
                                else:
                                    count = findContestantCount(dance_dfs, info)
                                for i, split in enumerate(splits):  # order largest to smallest count
                                    if split[1] > count:
                                        continue
                                    else:
                                        splits.insert(i, [info, count])
                            # Loop over all rooms in heat
                            for vacant in heat_roster:
                                if len(vacant) > 0:  # If room is already in use, continue loop
                                    continue
                                if len(splits) == 0:
                                    print(key + "level mode assigning or splitting not possible")
                                    heat_finished = True
                                    break
                                assigned = False
                                looped = False
                                i = 0
                                # Choose the highest level whose holes will not exceed Couples pool for that level
                                floor_info.append(info)
                                if 't' in div or 'T' in div:
                                    if floor_info[-1] == "S":
                                        s_floors.append(floor_info[-1])
                                        sfin_rooms.append(0)
                                    else:
                                        c_floors.append(floor_info[-1])
                                        cfin_rooms.append(0)
                                split = True
                            if not split:
                                heat_finished = True
                            else:
                                split_mode = True
                        else:
                            heat_finished = True
                            # # TODO Check each of the current divisions use find unique if it is a single and find contestant count
                            # #  if it is a couple figure out the numer of unique couples and how many are left
                            # #  pick the largest of those until full, add them to room info and then loop back to beginning of selection
                            # #  if cannot make it work then move on
                            # while not assigned:
                            #     # if looped fully, consider splitting a level now
                            #     if i > len(decend_level_c):
                            #         if looped:
                            #             not_possible = True
                            #             break
                            #         i = 0
                            #         looped = True
                            #     possible_largest = decend_level_c[i][0]
                            #     couples_for_lev = dance_dfs_dict_c[possible_largest]
                            #     placeable_couples = len(instructors_available_for_heat[possible_largest])
                            #     if placeable_couples >= couples_per_ballroom:
                            #         pot_added_holes = 0
                            #     else:
                            #         pot_added_holes = couples_per_ballroom - placeable_couples
                            #     # Sanity check for level to work at all
                            #     if (tot_holes[possible_largest] + pot_added_holes) <= (couples_for_lev + 3):
                            #         # If level is being used consider other levels first
                            #         if heat_room_levs.count(possible_largest) > 0 and (not looped):
                            #             i += 1
                            #             continue
                            #         # TODO: add a check here to internal vs external conflict if too high external then instructors will likely not get a match
                            #         assigned = True
                            #         # Metadata for filling in holes metadata
                            #         level_mode_selection_lev.append(possible_largest)
                            #         heat_room_levs.append(possible_largest)
                            #         # If there are Instructors left and the room was not forced to end
                            #         if placeable_couples > 0:
                            #             if fin_rooms[heat_room_levs.index(possible_largest)] == 1:
                            #                 fin_rooms.append(0)
                            #             elif fin_rooms[heat_room_levs.index(possible_largest)] == 2:
                            #                 fin_rooms.append(2)
                            #                 heat_finished = True
                            #         else:
                            #             heat_finished = True

                    heat_list.appendList(heat)  # add completed heat to the HeatList obj
                    split_mode = False
                    dance_heat_count += 1
                    tot_current_heats += 1
                    if tot_current_heats > max_heats:
                        print("Exceeded max heats for event time metrics")
            heats[each][every][ev] = heat_list
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

    rowindex = 1
    # file = os.getcwd() + eventName + '.xlsx'
    for each in heats:  # For each genre
        # Create a new directory
        try:
            filepath = os.getcwd().replace('\src', "") + "\Output" + "\\" + each
            os.mkdir(filepath)
            wb = openpyxl.Workbook()
            excelfile = eventName + '_' + each + '.xlsx'
            wb.save(eventName + '_' + each + '.xlsx')
        except:
            pass
        for every in heats[each]:  # For every syllabus category
            rowindex = 1
            keys = heats[each][every].keys()  # Create list of keys
            wb.create_sheet(title=keys[0])
            while heats[each][every] != "":  # While open or closed is not empty
                heatslist = heats[each][every][keys[0]] # Print all heats for that key,TODO can make this random in future for day planning
                iterator = 0
                rosters = heatslist.getRostersList()
                couples_per_floor = heatslist
                # level_bp = heats[each][every][key].getLevelBreakPoints()
                count = heatslist.getHeatCount()
                for room in range(heatslist.getFloors()):  # For each ballroom print out a heat, TODO: may need a -1
                    sheet = wb.get_sheet_by_name(keys[0])
                    sheet['A'+str(rowindex)] = 'Ballroom ' + chr(room)
                    rowindex += 1
                    startingrow = rowindex
                    # print out each contestant, formatting df to relevant columns
                    with ExcelWriter(filepath + excelfile, mode='a') as writer:
                        cols = ['type id', 'Lead Dancer #', 'Lead First Name', 'Lead Last Name',
                                'Follow Dancer #', 'Follow First Name', 'Follow Last Name', 'Level', 'School']
                        for contestant in rosters[room]:
                            contestant.to_excel(writer, sheet_name=keys[0], startrow=rowindex, columns=cols, index=False)
                            rowindex += 1
                    # go over the printed rows and highlight cells for easy identify
                        for i in range(rowindex-startingrow):
                            index = i+startingrow
                            idcol = 'A'
                            if sheet[idcol+str(index)] == "L":
                                sheet.cell[idcol+str(index)].fill = PatternFill(bgColor="00FF8080")
                            elif sheet[idcol+str(index)] == "F":
                                sheet.cell[idcol+str(index)].fill = PatternFill(bgColor="00FFFF00")
                            # level color code
                            levcol = "H"
                            # Bronze/NC
                            if sheet[levcol+str(index)][1] == "B" or sheet[levcol+str(index)][1] == "N":
                                if sheet[levcol+str(index)][2] == "1" or sheet[levcol+str(index)][2] == "2" or sheet[levcol+str(index)][2] == "C":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00993300")
                                if sheet[levcol+str(index)][2] == "3" or sheet[levcol+str(index)][2] == "4":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00800000")
                            # Silver
                            if sheet[levcol+str(index)][1] == "S":
                                if sheet[levcol+str(index)][2] == "1" or sheet[levcol+str(index)][2] == "2":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00C0C0C0")
                                if sheet[levcol+str(index)][2] == "3" or sheet[levcol+str(index)][2] == "4":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00808080")
                            # Gold
                            if sheet[levcol+str(index)][1] == "G":
                                if sheet[levcol+str(index)][2] == "1" or sheet[levcol+str(index)][2] == "2":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00FFFF99")
                                if sheet[levcol+str(index)][2] == "3" or sheet[levcol+str(index)][2] == "4" or sheet[levcol+str(index)][2] == "B":
                                    sheet.cell[levcol+str(index)].fill = PatternFill(bgColor="00FFCC00")

                    # add in blank rows if data < couples-per-floor
                    if len(rosters[room]) < couples_per_floor:
                        for i in range(len(rosters[room])-couples_per_floor):
                            rowindex += 1
def resolveConflictSingles(roomid, dance_dfs, log, heat, heat_list, instructors_available_for_heat, solved, inst_tree, inst2single_tree, df_inst):
    # TODo start with the mode instructor
    #  the instructor is not free see if it can be freed by a simple swap of the instructor for that single
    #  if not can that single be traded for a different one (check instructors for that heat for another inst)
    singles_in_heat = heat.getSingles()
    instructors_in_heat = heat.getInstructors()
    presolved = solved

    roomlog = log.getRoomlog()
    conflict_inst = roomlog[roomid]["mode_inst"][0]
    mode_code = roomlog[roomid]["mode_code"]
    roomdiv = roomlog[roomid]["div"]
    conflicts = []
    # get all conflicts with this instructor
    for each in roomlog[roomid]["conf_list"]:
        if each.getInstructor() == conflict_inst:
            conflicts.append(each)

    # if the instructor is not free
    if conflicts[0].getCode() == 1:
        instructors_list = []
        # Locate where instructor taken and whom with
        for i, each in enumerate(instructors_in_heat):
            if conflict_inst in each:
                conflict_room = i
                conflict_index = each.index(conflict_inst)
                conflict_div = heat.getdiv()[conflict_room]
                conflict_contestant = singles_in_heat[conflict_room][conflict_index]
            for every in each:
                instructors_list.append(every)

        # See if that contestant has another free instructor
        conflict_entry = heat.getRoster()[conflict_room][conflict_index]
        # Set column variables based on single type
        if conflict_entry.loc[0, "type id"] == "L":
            contestant_col = "Lead Dancer #"
            inst_col = "Follow Dancer #"
            inst_fname = "Follow First Name"
            inst_lname = "Follow Last Name"
        elif conflict_entry.loc[0, "type id"] == "F":
            contestant_col = "Follow Dancer #"
            inst_col = "Lead Dancer #"
            inst_fname = "Lead First Name"
            inst_lname = "Lead Last Name"
        else:
            raise Exception("Type id for " + conflict_entry + " is invalid")
        conflict_entry_single = conflict_entry.loc[0, contestant_col]
        # Retrofit the instructor list entry
        # if type(conflict_entry.loc[0, "Instructor Dancer #'s"]) == int:
        #     tmp = [conflict_entry["Instructor Dancer #'s"]]
        # else:
        #     tmp = [int(x) for x in conflict_entry.loc[0, "Instructor Dancer #'s"].split(";")]
        # conflict_entry.loc[0, "Instructor Dancer #'s"] = tmp
        # del tmp
        # Loop over the instructor list for the contestant row
        for num in conflict_entry.loc[0, "Instructor Dancer #'s"]:
            # if instructor is not conflict instructor and not being used in heat
            if num != conflict_inst and num not in instructors_list:
                solved += 1
                instructors_in_heat[conflict_room][conflict_index] = num
                instructor_data = df_inst[df_inst["Dancer #"] == num].reset_index(drop=True)
                conflict_entry.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                conflict_entry.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                conflict_entry.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                heat.replaceContestant(conflict_room, conflict_index, conflict_entry)

    # Check if conflict can be swapped with an entry in a previous heat
    # loop heat_list and check metadata
    possible_matches = inst2single_tree[conflict_room][num].copy()
    for each in heat_list:
        # Check if heat has division
        if conflict_div not in each.getDiv():
            continue
        # TODO there will be an unchecked room if there are duplicate divisions in heat 'each'
        swapping_room = each.getDiv().index(conflict_div)
        # Check this heat's instructors
        placed_inst = each.getInstructors()
        dup = False
        for every in placed_inst:
            if conflict_contestant in every:
                dup = True
            if conflict_inst in every:
                dup = True
        if dup:
            continue
        # Check this heats singles
        placed_sing = each.getSingles()
        dup = False
        for every in placed_sing:
            if conflict_contestant in every:
                dup = True
            if conflict_inst in every:
                dup = True
        if dup:
            continue
        # Check this heats singles
        placed_coup = each.getCouples()
        dup = False
        for every in placed_coup:
            if conflict_contestant in every:
                dup = True
            if conflict_inst in every:
                dup = True
        if dup:
            continue
        # Find an entry in the previous heat room that has no conflicts with current heat
        i = 0
        index_to_swap = -1
        for contestant, inst in zip(placed_sing[swapping_room], placed_inst[swapping_room]):
            for singles in heat.getSingles():
                if contestant in singles:
                    dup = True
            for instructors in heat.getInstructors():
                if inst in instructors:
                    dup = True
            for couples in heat.getCouples():
                if contestant in couples:
                    dup = True
                if inst in couples:
                    dup = True
            # if no conflicts make the swap with entry index i
            if not dup:
                index_2_swap = i
                break
            i += 1
        # if no suitable entry found, continue to another heat
        if index_2_swap == -1:
            continue
        # if there are no duplicates, swap
        solved += 1
        tmp = each.replaceContestant(swapping_room, index_2_swap, conflict_entry)
        heat.replaceContestant(conflict_room, conflict_index, tmp)

    # TODO if needed go over these steps again but with another layer of swapping
    if presolved == solved:
        print("Solution not found, need to build out more in resolver")
    else:
        # TODO clear out the log with conflicts of the same inst and code
    # for contestant in inst2single_tree[conflict_room][num]:
    #     conflict_inst
    # TODO for couples see if the mode couple can be swapped for another couple in the heat list already
    #  check the divs of the each heat list if matching check the meta data for any of the swapping numbers.
    #  if meta data is good then run swap candidate, make sure to add the returned entry after resolveConflict is returned


def getContestantConflictList(dance_df, inst, contestants):
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
        # Retrofit the instructor list data
        if type(singles["Instructor Dancer #'s"]) == int:
            tmp = [singles["Instructor Dancer #'s"]]
        else:
            tmp = [int(x) for x in singles["Instructor Dancer #'s"].split(";")]
        singles["Instructor Dancer #'s"] = tmp
        del tmp
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

def deleteEmpty(dance_dfs):
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            deleteEmpty(dance_dfs[each])
            if len(dance_dfs[each]) == 0:  # If dict is now empty, delete it
                del dance_dfs[each]
        elif dance_dfs[each].empty:
            del dance_dfs[each]
    return dance_dfs

def buildInstTree(dance_dfs, inst_tree, ev):
    """Builds the dictionary tree of all instructors and thier count in that division

           Parameters
           ----------
           dance_df : Pandas DataFrame
               Current pool of single contestants
           inst_tree : Python Dictionary
               Tree of dictionaries key'd by the division metrics

           Returns
           -------
           dict
              tree of all instructor counts key'd by thier division
           """
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            inst_tree[each] = {}
            buildInstTree(dance_dfs[each], inst_tree[each], ev)
        else:
            singles_only = dance_dfs[each][(dance_dfs[each]['type id'] == 'L') | (dance_dfs[each]['type id'] == 'F')]
            if not singles_only.empty:
                inst_tree[each] = {}
                # Find unique instructors for this division
                for row, data in singles_only.iterrows():  # Iterate down all rows of Single df
                    if data["type id"] == "L":
                        contestant_col = "Lead Dancer #"
                        inst_col = "Follow Dancer #"
                        inst_fname = "Follow First Name"
                        inst_lname = "Follow Last Name"
                    elif data["type id"] == "F":
                        contestant_col = "Follow Dancer #"
                        inst_col = "Lead Dancer #"
                        inst_fname = "Lead First Name"
                        inst_lname = "Lead Last Name"
                    if type(data["Instructor Dancer #'s"]) == int:
                        tmp = [data["Instructor Dancer #'s"]]
                    else:
                        tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
                    data["Instructor Dancer #'s"] = tmp
                    del tmp
                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                        if num in inst_tree[each].keys():
                            inst_tree[each][num] += data[ev]  # Need to add this contestant's entry number for this event
                        else:
                            inst_tree[each][num] = data[ev]  # Need to add this contestant's entry number for this event
    return inst_tree

def buildInst2SingTree(dance_dfs, inst2sing_tree, ev):
    """Builds the dictionary tree of all instructors and thier count in that division

           Parameters
           ----------
           dance_df : Pandas DataFrame
               Current pool of single contestants
           inst_tree : Python Dictionary
               Tree of dictionaries key'd by the division metrics

           Returns
           -------
           dict
              tree of all instructor counts key'd by thier division
           """
    keylist = list(dance_dfs.keys())
    for each in keylist:
        if type(dance_dfs[each]) is dict:
            inst2sing_tree[each] = {}
            buildInst2SingTree(dance_dfs[each], inst2sing_tree[each], ev)
        else:
            singles_only = dance_dfs[each][(dance_dfs[each]['type id'] == 'L') | (dance_dfs[each]['type id'] == 'F')]
            if not singles_only.empty:
                inst2sing_tree[each] = {}
                # Find unique instructors for this division
                for row, data in singles_only.iterrows():  # Iterate down all rows of Single df
                    if data["type id"] == "L":
                        contestant_col = "Lead Dancer #"
                        inst_col = "Follow Dancer #"
                        inst_fname = "Follow First Name"
                        inst_lname = "Follow Last Name"
                    elif data["type id"] == "F":
                        contestant_col = "Follow Dancer #"
                        inst_col = "Lead Dancer #"
                        inst_fname = "Lead First Name"
                        inst_lname = "Lead Last Name"
                    if type(data["Instructor Dancer #'s"]) == int:
                        tmp = [data["Instructor Dancer #'s"]]
                    else:
                        tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
                    data["Instructor Dancer #'s"] = tmp
                    del tmp
                    for num in data["Instructor Dancer #'s"]:  # Iterate through all #'s in instructor lists
                        # singles for that instructor tree
                        if inst2sing_tree[each].get(num) is None:
                            inst2sing_tree[each][num] = [data[contestant_col]]
                        if data[contestant_col] not in inst2sing_tree[each][num]:
                            inst2sing_tree[each][num].append(data[contestant_col])

    return inst2sing_tree


def pickDfs(ev, dance_dfs, inst_tree, floors, div, age_brackets, couples_per_floor):
    l_keys = [0, 1, 2, 3, 4, 5]

    if div.count('T') == 0 and div.count('t') == 0:
        start = "A"
    elif "S" in dance_dfs:
        start = "S"
    else:
        start = "C"

    shell = dance_dfs[start]
    picked_keys = []
    picked_keys.append(start)
    # TODO how to handel lead and follow 3 or 4 split with singles
    while type(shell) is dict:
        # pick = random.choice(list(shell.keys()))  # random choice
        pick = list(shell.keys())[0]
        picked_keys.append(pick)
        shell = shell[pick]

    # If only one floor return the key
    if len([picked_keys]) == floors:
        return [picked_keys]
    unideal = []  # keys that do not meet initial conditions but if no other options will choose one of these
    # If picked df is a single
    if picked_keys[0] == "S":
        iter = 1  # Iterator to track key index
        # if divided by L and F, set labels
        if ("S" in div) or ("s" in div):
            same_s = "same_s"
            opp_s = "opp_s"
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_s = "Follow"
            opp_s = "Lead"

        # If divided by level set the same level
        if ("L" in div) or ("l" in div):
            same_l = picked_keys[iter]
            diff_l = "diff_l"
            lev_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_l = 0
            diff_l = 0

        # If divided by age set the same age bracket
        if ("A" in div) or ("a" in div):
            same_a = picked_keys[iter]
            diff_a = "diff_a"
            age_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_a = 0
            diff_a = 0

        #        Opposite Gender
        prio_s = [["S", opp_s, same_l, same_a], ["S", opp_s, same_l, diff_a], ["S", opp_s, diff_l, same_a],
                  ["S", opp_s, diff_l, diff_a],
        #         Same Gender
                  ["S", same_s, same_l, diff_a], ["S", same_s, diff_l, same_a], ["S", same_s, diff_l, diff_a],
        #         Couples
                  ["C", same_l, same_a], ["C", same_l, diff_a], ["C", diff_l, same_a], ["C", diff_l, diff_a]]
        all_poss = []  # holds all possible keys to be selected, used in the case of different level or age
        picked_keys = [picked_keys]
        prio = 0
        while prio < len(prio_s):
            poss_key = []
            iter = 1
            # Take out unused key slots
            if div.count('T') != 0 or div.count('t') != 0:
                poss_key.append(prio_s[prio][0])
            else:
                poss_key.append("A")
            if (div.count('s') != 0 or div.count('S') != 0) and poss_key[0] == "S":
                if prio_s[prio][1] == "opp_s":
                    if picked_keys[-1][iter] == "Lead":
                        poss_key.append("Follow")
                    else:
                        poss_key.append("Lead")
                else:
                    if picked_keys[-1][iter] == "Follow":
                        poss_key.append("Follow")
                    else:
                        poss_key.append("Lead")
                iter += 1
            if div.count('L') != 0 or div.count('l') != 0:
                if prio_s[prio][2] != "diff_l":
                    poss_key.append(prio_s[prio][2])
                    all_poss.append(poss_key)
                else:  # If different level make a key with all possible levels
                    for lev in l_keys:  # For all level keys
                        if lev != picked_keys[0][lev_index]:  # if not the same level, create a new possible key
                            poss_key.append(lev)
                            all_poss.append(poss_key)
                            poss_key = poss_key[:-1]
                iter += 1
            if div.count('A') != 0 or div.count('a') != 0:
                if len(all_poss) == 0:  # in case 'l' split is not part of this Event
                    all_poss.append(poss_key)
                if prio_s[prio][3] != "diff_a":
                    for key in all_poss:
                        key.append(prio_s[prio][3])
                else:  # If different age make a key with all possible ages
                    curr_all_poss = len(all_poss)
                    agelist = age_brackets.copy()
                    agelist.remove(picked_keys[0][age_index])
                    # iter = 0
                    for age in agelist:
                        for j in range(curr_all_poss):
                            poss_key = all_poss[j][:]
                            poss_key.append(age)
                            all_poss.append(poss_key)
                    # Remove the all_poss with no age
                    all_poss = all_poss[curr_all_poss:]
            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            for every in all_poss:
                for i, key in enumerate(every):
                    if i == 0:
                        tmp = dance_dfs[key]
                        continue
                    if key not in tmp:
                        break
                    if type(tmp[key]) is dict:
                        tmp = tmp[key]
                    elif every not in picked_keys:  # add to picked list only if that key combo is not in already
                        # if added is a single
                        if every[0] == "S":
                            cop = []
                            for key in picked_keys:
                                cop.append(key[:])
                            # Sanity check the levels in question
                            unique = findUnique(inst_tree, cop, every)
                            count = findInstCount(inst_tree, every)
                            # find # of 'singles' rooms
                            sfloors = 0
                            for room in picked_keys:
                                if room[0] == "S":
                                    sfloors += 1
                            if every[0] == "S":
                                sfloors += 1
                            # if (unique >= (len(picked_keys) * couples_per_floor)-3) and (count > (couples_per_floor-2)):
                            if unique >= (sfloors * couples_per_floor)-2:
                                picked_keys.append(every)
                                picked = True
                                break
                            else:
                                unideal.append([every, count])
                        else:  # if not a single
                            count = findContestantCount(dance_dfs, every, ev)
                            if count[0] >= couples_per_floor-2:
                                picked_keys.append(every)
                                picked = True
                            else:
                                unideal.append([every, count[1]])
                if picked:  # If picked break
                    picked = False
                    prio = 1  # So I don't skip other gender prio options
                    break
                if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                    prio += 1
            all_poss.clear()  # Once all possible keys in priority slot are not picked, clear the list
            if len(picked_keys) == floors:
                break
                
    # If picked df is a couple
    elif picked_keys[0] == "C" or picked_keys[0] == "A":
        iter = 1  # Iterator to track key index
        # If divided by level set the same level
        if ("L" in div) or ("l" in div):
            same_l = picked_keys[iter]
            diff_l = "diff_l"
            lev_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_l = 0
            diff_l = 0

        # If divided by age set the same age bracket
        if ("A" in div) or ("a" in div):
            same_a = picked_keys[iter]
            diff_a = "diff_a"
            age_index = iter
            iter += 1
        else:  # assignment means nothing for else case only to stop compile error, since this key DNE
            same_a = 0
            diff_a = 0

        # Pick priority list depending on starting key
        if picked_keys[0] == "C":
            #         Couples
            prio_c = [["C", same_l, diff_a], ["C", diff_l, same_a], ["C", diff_l, diff_a],
            #         Singles
                      ["S", "single", same_l, same_a], ["S", "single", same_l, diff_a], ["S", "single", diff_l, same_a],
                      ["S", "single", diff_l, diff_a]]
        elif picked_keys[0] == "A":
            prio_c = [["A", same_l, diff_a], ["A", diff_l, same_a], ["A", diff_l, diff_a]]

        all_poss = []  # holds all possible keys to be selected, used in the case of different level or age
        picked_keys = [picked_keys]
        prio = 0
        while prio < len(prio_c):
            poss_key = []
            iter = 1
            # Take out unused key slots
            if div.count('T') != 0 or div.count('t') != 0:
                poss_key.append(prio_c[prio][0])
            else:
                poss_key.append("A")
            if (div.count('s') != 0 or div.count('S') != 0) and poss_key[0] == "S":
                poss_key.append("Lead")
                all_poss.append(poss_key)
                poss_key = poss_key[:-1]
                poss_key.append("Follow")
                all_poss.append(poss_key)
                iter += 1
            if div.count('L') != 0 or div.count('l') != 0:
                if len(all_poss) == 0:  # in case 's' split is not part of this event
                    all_poss.append(poss_key)
                if prio_c[prio][1] != "diff_l":
                    for key in all_poss:
                        key.append(prio_c[prio][1])
                else:  # If different level make a key with all possible levels
                    curr_all_poss = len(all_poss)
                    for lev in l_keys:  # duplicate current all_poss per different level
                        if lev != picked_keys[0][lev_index]:
                            for j in range(curr_all_poss):
                                poss_key = all_poss[j][:]
                                poss_key.append(lev)
                                all_poss.append(poss_key)
                    # remove first 2 keys that have no age
                    all_poss = all_poss[curr_all_poss:]
                iter += 1
            if div.count('A') != 0 or div.count('a') != 0:
                if len(all_poss) == 0:  # In case 's' split is not part of this
                    all_poss.append(poss_key)
                if prio_c[prio][2] != "diff_a":
                    for key in all_poss:
                        key.append(prio_c[prio][2])
                else:  # If different age make a key with all existing key with all ages
                    curr_all_poss = len(all_poss)
                        # TODO do I make check all floors ages?
                    agelist = age_brackets.copy()
                    agelist.remove(picked_keys[0][age_index])
                    for age in agelist:
                        for j in range(curr_all_poss):
                            poss_key = all_poss[j][:]
                            poss_key.append(age)
                            all_poss.append(poss_key)
                    # Remove the all_poss with no age
                    all_poss = all_poss[curr_all_poss:]

            # Use all_poss to find out if that combo exists in the data tree
            picked = False
            for every in all_poss:
                for i, key in enumerate(every):
                    if i == 0:
                        tmp = dance_dfs[key]
                        continue
                    if key not in tmp:
                        break
                    if type(tmp[key]) is dict:
                        tmp = tmp[key]
                    elif every not in picked_keys:  # add to picked list only if that key combo is not in already
                        # if added is a single
                        if every[0] == "S":
                            cop = []
                            for key in picked_keys:
                                cop.append(key[:])
                            # Sanity check the levels in question
                            unique = findUnique(inst_tree, cop, every)
                            count = findInstCount(inst_tree, every)
                            # find # of 'singles' rooms
                            sfloors = 0
                            for room in picked_keys:
                                if room[0] == "S":
                                    sfloors += 1
                            if every[0] == "S":
                                sfloors += 1
                            # if (unique >= (len(picked_keys) * couples_per_floor)-3) and (count > (couples_per_floor-2)):
                            if unique >= (sfloors * couples_per_floor) - 2:
                                picked_keys.append(every)
                                picked = True
                                break
                            else:
                                unideal.append([every, count])
                        else:  # if not a single
                            count = findContestantCount(dance_dfs, every, ev)
                            if count[0] >= couples_per_floor - 2:
                                picked_keys.append(every)
                                picked = True
                            else:
                                unideal.append([every, count[1]])
                if picked:  # If picked break
                    picked = False
                    prio = 1  # So I don't skip other gender prio options
                    break
                if every == all_poss[-1]:  # If at the end of options for this priority bracket move to another
                    prio += 1
            all_poss.clear()  # Once all possible keys in priority slot are not picked, clear the list
            if len(picked_keys) == floors:
                break

        # If all possible keys are tried and not filled the floors try the unideal heats
        while len(picked_keys) != floors:
            if len(unideal) == 0:
                break
            largest = 0
            largest_index = 0
            for i, each in enumerate(unideal):
                if each[1] > largest:
                    largest = each[1]
                    largest_index = i
            picked_keys.append(unideal[largest_index])
            del unideal[largest_index]
    return picked_keys

def findUnique(inst_tree, picked_keys, newkey):

    instructors = []

    picked_keys.append(newkey)
    for each in picked_keys:
        if each[0] != "C":
            tmp = inst_tree[each[0]]
            i = 1
            while type(tmp) is dict and i < len(each):
                tmp = tmp[each[i]]
                i += 1
            instructors = list(tmp.keys()) + instructors

    return len(set(instructors))

def findInstCount(inst_tree, newkey):
    for i, each in enumerate(newkey):
        if i == 0:
            tmp = inst_tree[each]
            continue
        tmp = tmp[each]

    return len(tmp.keys())

def findContestantCount(dance_dfs, newkey, ev):
    for i, each in enumerate(newkey):
        if i == 0:
            tmp = dance_dfs[each]
            continue
        tmp = tmp[each]

    return [tmp.shape[0], tmp[ev].sum()]

def updateDanceDfs(dance_dfs, df_for_heat, floor_info):


    if type(dance_dfs[floor_info[0]]) is dict:
        updateDanceDfs(dance_dfs[floor_info[0]], df_for_heat, floor_info[1:])
    else:
        dance_dfs[floor_info[0]] = df_for_heat
    return dance_dfs

def backfill(dance_df, div, heat_list, df_inst):
    # Todo: while df has entries
    #  loop over the heat list and find a heat that is < max
    #  if found check the meta data,
    #  check if contestant(s) is alreay in the heat
    #  loop over the inst of single and strike it if it is there, if there are no inst left move on

    list_index = 0
    heats = heat_list.getRostersList()
    heats_count = len(heats)
    for row, data in dance_df.iterrows():
        # Set columns to check
        if data["type id"] == "L":
            con_col = ["Lead Dancer Number", "Lead Dancer Number"]
        elif data["type id"] == "F":
            con_col = ["Follow Dancer Number", "Follow Dancer Number"]
        else:
            con_col = ["Lead Dancer Number", "Follow Dancer Number"]
        # Search the list
        placed = False
        while (list_index < range(heats_count)):
            # Check if heat has this division
            try:
                heat_list[list_index].getDiv().index(div)
            except:
                list_index += 1
                break

            # Check if Dancer is already in heat
            found = False
            for each in heats[list_index].getSingles():
                if data[con_col[0]] in each or data[con_col[1]] in each:
                    found = True
                    break
            for each in heats[list_index].getInstructors():
                if data[con_col[0]] in each or data[con_col[1]] in each:
                    print("While in backfill() Instructor # matches with " + data)
                    found = True
                    break
            for each in heats[list_index].getCouples():
                if data[con_col[0]] in each or data[con_col[1]] in each:
                    found = True
                    break
            if found:
                list_index += 1
                break
            roomid = heat_list[list_index].getDiv().index(div)  # Note will only return
            # if couple place it
            if data["type id"] == "C":
                heat_list[list_index].addEntry(data, roomid)
                list_index += 1
                break
            
            # If single need to check the instructors
            if data["type id"] == "L":
                contestant_col = "Lead Dancer #"
                inst_col = "Follow Dancer #"
                inst_fname = "Follow First Name"
                inst_lname = "Follow Last Name"
            elif data["type id"] == "F":
                contestant_col = "Follow Dancer #"
                inst_col = "Lead Dancer #"
                inst_fname = "Lead First Name"
                inst_lname = "Lead Last Name"
            else:
                raise Exception("While running backfill() for " + div + " Type id for " + data + " is invalid")
            # Retrofit the instructor list data
            if type(data["Instructor Dancer #'s"]) == int:
                tmp = [data["Instructor Dancer #'s"]]
            else:
                tmp = [int(x) for x in data["Instructor Dancer #'s"].split(";")]
            data["Instructor Dancer #'s"] = tmp
            del tmp

            for inst in data["Instructor Dancer #'s"]:
                for each in heat_list[list_index].getInstructors():
                    if inst in each:
                        found = True
                        break
                for each in heat_list[list_index].getCouples():
                    if inst in each:
                        found = True
                        break
                for each in heat_list[list_index].Singles():
                    if inst in each:
                        found = True
                        break
                if not found:
                    # Set candidate to this single/inst match
                    candidate = data.to_frame().T
                    candidate = candidate.reset_index(drop=True)
                    instructor_data = df_inst[df_inst["Dancer #"] == inst].reset_index(drop=True)
                    candidate.loc[0, inst_col] = instructor_data.loc[0, "Dancer #"]
                    candidate.loc[0, inst_fname] = instructor_data.loc[0, "First Name"]
                    candidate.loc[0, inst_lname] = instructor_data.loc[0, "Last Name"]
                    heat_list[list_index].addEntry(candidate)
                    list_index += 1
                    break
            if not found:
                break
