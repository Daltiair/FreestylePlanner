'''File to house global variables and helper methods'''

df_inst = 0
dance_dfs = 0
inst_tree = 0
inst2sing_tree = 0

def getNode(dance_dfs, div):
    for i, key in enumerate(div):
        if i == 0:
            tmp = dance_dfs[key]
        elif type(tmp) is dict:
            tmp = tmp[key]
    return tmp


def updateDanceDfs(dance_dfs, df_for_heat, floor_info):
    try:
        if type(dance_dfs[floor_info[0]]) is dict:
            updateDanceDfs(dance_dfs[floor_info[0]], df_for_heat, floor_info[1:])
        else:
            dance_dfs[floor_info[0]] = df_for_heat
        return dance_dfs
    except:
        print("Df pool is already deleted for", floor_info)

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