'''
File with all objects and structures used to create Free Style Itenerary
'''

class Heat:

    # def __init__(self, key='', div=[], roster=[], holes=[], singles=[], instructors=[], couples=[]):
    def __init__(self, key='', div=[], roster=[], singles=[], instructors=[], couples=[]):
        # key = Genre-Syllabus-Dance-index
        self.key = key
        self.div = div
        # self.holes = holes
        self.roster = roster
        self.singles = singles
        self.instructors = instructors
        self.couples = couples

    def getRoster(self):
        return self.roster

    def getDiv(self):
        return self.div

    def getInstructors(self):
        return self.instructors

    def getHoles(self):
        pass
        # return self.holes

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
            self.singles[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].append(entry.loc[:, "Follow Dancer #"][0])
        elif entry["type id"] == "F":
            self.singles[roomid].append(entry.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].append(entry.loc[:, "Lead Dancer #"][0])
        elif entry["type id"] == "C":
            self.couples[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            self.couples[roomid].append(entry.loc[:, "Follow Dancer #"][0])
        # Subtract from the holes[roomid]
        # self.holes[roomid] -= 1

    def replaceContestant(self, roomid, roster_index, replacement_couple):
        tmp = self.roster[roomid][roster_index]
        if tmp["type id"] == "L":
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.singles[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
        elif tmp["type id"] == "F":
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.singles[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
        elif tmp["type id"] == "C":  # TODO finish replace meta data 
            self.couples[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.couples[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
        self.roster[roomid].insert(roster_index, replacement_couple)
        self.roster[roomid].remove(tmp)
        return tmp


class HeatList:
    def __init__(self, rosters=[], floors=1, heat_count=0):
        self.rosters = rosters
        self.floors = floors
        self.divs = []
        self.divcounts = []
        # self.level_bp = level_bp
        self.heat_count = heat_count

    def getRostersList(self):
        return self.rosters

    def getFloors(self):
        return self.floors

    def getDivisionHeatCount(self, div):
        try:
            index = self.divs.index(div)
        except:
            return 0

        return self.divcounts[index]

    def getHeatCount(self):
        return self.heat_count

    def appendList(self, heat):
        self.rosters.append(heat)
        self.heat_count += 1
        # Check the divs, if new add it, if exists increment the count of heats
        for each in heat.getDiv():
            try:
                index = self.divs.index(each)
            except:
                self.divs.append(each)
                self.divcounts.append(1)
                continue
            self.divcounts[index] += 1




class ConflictList:

    def __init__(self, itemlist=[], counts=[]):
        self.itemlist = itemlist
        self.counts = counts

    def getCounts(self):
        return sum(self.counts)

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

    def __init__(self, code=0, contestants=[], inst=000, loc='n', type="n"):
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
        self.type = type

    def getCode(self):
        return self.code

    def getType(self):
        return self.type

    def getContestant(self):
        return self.contestant

    def getInstructor(self):
        return self.inst

    def getLocation(self):
        return self.loc


class ConflictLog:

    def __init__(self, div=[]):
        self.div = div
        self.rooms = len(div)
        self.roomlog = {}
        self.codeCount = [0,0]  # Code 1 Count, Codde 2 Count


        for roomid, info in enumerate(div):
            self.roomlog[roomid] = {}
            self.roomlog[roomid]["con_list"] = []
            self.roomlog[roomid]["con_count"] = []
            self.roomlog[roomid]["div"] = info
            self.roomlog[roomid]["total"] = 0
            self.roomlog[roomid]["mode_con"] = (0, 0)
            self.roomlog[roomid]["mode_inst"] = [0,0]
            self.roomlog[roomid]["mode_code"] = 0
            self.roomlog[roomid]["mode_loc"] = 0

    def addConflict(self, conflict, roomid):

        # TODO check inst and code to see if this conflict is present already
        #  if there increment and save the number, check if it is the new mode
        #  check if the code is the new mode as well
        #  if not there add a new conflict to the list and new number to count list
        dup = False
        for i, each in enumerate(self.roomlog[roomid]["list"]):
            if conflict.getType() == "S":
                if each.getCode() == conflict.getCode():
                    if each.getInstructor() == conflict.getInstructor():
                        self.roomlog[roomid]["con_count"][i] += 1
                        new_num = self.roomlog[roomid]["con_count"][i]
                        dup = True
            else: # a Couples Conflict
                if each.getContestant() == conflict.getContestant():

        if not dup:
            self.roomlog[roomid]["list"].append(conflict)
            self.roomlog[roomid]["con_count"].append(1)

        self.roomlog[roomid]["total"] += 1

        # Update Inst Mode
        if conflict.getType() == "S":
            # Update code and Mode
            if conflict.getCode() == 1:
                self.codeCount[0] += 1
                if self.codeCount[0] > self.codeCount[1]:
                    self.roomlog[roomid]["mode_code"] = 1
            if conflict.getCode() == 2:
                self.codeCount[1] += 1
                if self.codeCount[1] > self.codeCount[0]:
                    self.roomlog[roomid]["mode_code"] = 2
            # Update Inst
            if new_num > self.roomlog[roomid]["mode_inst"][1]:
                self.roomlog[roomid]["mode_inst"][0] += 1


        # if conflict.getLocation() == 'e':
        #     self.roomlog[roomid][]
