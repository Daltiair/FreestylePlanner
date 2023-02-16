'''File to house global variables and helper methods'''

df_inst = 0
dance_dfs = 0
inst2sing_tree = 0

def getNode(dance_dfs, div):
    for i, key in enumerate(div):
        if i == 0:
            tmp = dance_dfs[key]
        elif type(tmp) is dict:
            tmp = tmp[key]
    return tmp


def updateDanceDfs(dance_dfs, df_for_heat, floor_info):

    if type(dance_dfs[floor_info[0]]) is dict:
        updateDanceDfs(dance_dfs[floor_info[0]], df_for_heat, floor_info[1:])
    else:
        dance_dfs[floor_info[0]] = df_for_heat
    return dance_dfs