'''
File with all objects and structures used to create Free Style Itenerary
'''

class Heat:

    def __init__(self, key='', levels=[], roster=[], holes=[], singles=[], instructors=[], couples=[]):
        # key = Genre-Syllabus-Dance-index
        self.key = key
        self.levels = levels
        self.holes = holes
        self.roster = roster
        self.singles = singles
        self.instructors = instructors
        self.couples = couples

    def getRoster(self):
        return self.roster

    def getLevels(self):
        return self.levels

    def getInstructors(self):
        return self.instructors

    def getHoles(self):
        return self.holes

    def getKey(self):
        return self.key

    def getSingles(self):
        return self.singles

    def getCouples(self):
        return self.couples

    def addEntry(self, entry, roomid):
        # Append to the roster[roomid]
        self.roster[roomid].append(entry)
        #  Check the type and add to respective list
        if entry["type id"] == "L":
            self.singles.append(entry.loc[:, "Lead Dancer #"][0])
            self.instructors.append(entry.loc[:, "Follow Dancer #"][0])
        elif entry["type id"] == "F":
            self.singles.append(entry.loc[:, "Follow Dancer #"][0])
            self.instructors.append(entry.loc[:, "Lead Dancer #"][0])
        elif entry["type id"] == "C":
            self.couples.append(entry.loc[:, "Lead Dancer #"][0])
            self.couples.append(entry.loc[:, "Follow Dancer #"][0])
        # Subtract from the holes[roomid]
        self.holes[roomid] -= 1

    def replaceContestant(self, roomid, roster_index, replacement_couple):
        tmp = self.roster[roomid][roster_index]
        self.roster[roomid][roster_index] = replacement_couple
        return tmp


class HeatList:
    def __init__(self, rosters=[], heat_count=0):
        self.rosters = rosters
        # self.level_bp = level_bp
        self.heat_count = heat_count

    def getRostersList(self):
        return self.rosters

    '''
    def getLevelBreakPoints(self):
        return self.level_bp
    '''

    def getHeatCount(self):
        return self.heat_count

    def appendList(self, heat):
        self.rosters.append(heat)
        self.heat_count += 1


class ConflictList:

    def __init__(self, itemlist=[], counts=[]):
        self.itemlist = itemlist
        self.counts = counts

    def addConflict(self, conflictItem):
        dup = False  # flag for finding a duplicate conflict
        for i, each in enumerate(self.itemlist):
            if (each.getCode() == conflictItem.getCode()) and (each.getCandidate() == conflictItem.getCandidate()):
                dup = True
                self.counts[i] = self.counts[i] + 1

        if not dup:
            self.itemlist.append(conflictItem)
            self.counts.append(1)

    def clearConflicts(self):
        self.itemlist = []
        self.counts = []


class ConflictItemSingle:

    def __init__(self, code=0, contestants=[], inst=000, loc='n'):
        # code table
        # 1: No free Instructor assumes contestant free must be at a different level, external only
        # 2: No free contestant, internal only contestant can't be in 2 levels for the same dance.
        self.code = code
        self.contestants = contestants
        self.inst = inst
        # Loc table
        # i: internal conflict
        # e: external conflict
        self.loc = loc

    def getCode(self):
        return self.code

    def getContestant(self):
        return self.contestant

    def getInstructor(self):
        return self.inst

    def getLocation(self):
        return self.loc


class ConflictLog:

    def __init__(self, lvls=[]):
        self.lvls = lvls
        self.rooms = len(lvls)
        self.roomlog = {}

        for roomid, lvl in enumerate(lvls):
            self.roomlog[roomid] = {}
            self.roomlog[roomid]["list"] = []
            self.roomlog[roomid]["lvl"] = lvl
            self.roomlog[roomid]["total"] = 0
            self.roomlog[roomid]["mode_con"] = (0, 0)
            self.roomlog[roomid]["mode_inst"] = 0
            self.roomlog[roomid]["mode_code"] = 0
            self.roomlog[roomid]["mode_loc"] = 0

    def addConflict(self, conflict, lvl, roomid):
        self.roomlog[roomid]["list"].append(conflict)
        self.roomlog[roomid]["total"] += 1
        # if conflict.getLocation() == 'e':
        #     self.roomlog[roomid][]
        # TODO: decided if I need to make all these mode calcs
        # if self.roomlog[room]["mode_con"][1] <