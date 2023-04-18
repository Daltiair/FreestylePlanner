
class Heat:

    # def __init__(self, key='', div=[], roster=[], holes=[], singles=[], instructors=[], couples=[]):
    def __init__(self, key='', div=[], roster=[], holes=[], singles=[], instructors=[], couples=[]):
        # key = Genre-Syllabus-Dance-index
        self.key = key
        self.div = div
        # self.holes = holes
        self.roster = roster
        self.holes = holes
        self.singles = singles
        self.instructors = instructors
        self.couples = couples
        self.singles_index = len(self.singles)

    def getRoster(self):
        return self.roster

    def getDiv(self):
        return self.div

    def setDiv(self, newdivs):
        self.div = newdivs

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
        if entry.loc[0, "type id"] == "L":
            self.singles[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].append(entry.loc[:, "Follow Dancer #"][0])
            if self.div[roomid][0] == "A":  # If an all type room, add the -1 to note this index is takeb
                self.couples[roomid].append(-1)
                self.couples[roomid].append(-1)
        elif entry.loc[0, "type id"] == "F":
            self.singles[roomid].append(entry.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            if self.div[roomid][0] == "A":  # If and all type room, add the-1 to note this index is taken
                self.couples[roomid].append(-1)
                self.couples[roomid].append(-1)
        elif entry.loc[0, "type id"] == "C":
            self.couples[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            self.couples[roomid].append(entry.loc[:, "Follow Dancer #"][0])
            if self.div[roomid][0] == "A":  # If and all type room, add the-1 to note this index is taken
                self.singles[roomid].append(-1)
                self.instructors[roomid].append(-1)
        # Subtract from the holes[roomid]
        # self.holes[roomid] -= 1

    def replaceContestant(self, roomid, roster_index, replacement_couple):
        tmp = self.roster[roomid][roster_index].copy(True)
        # print(tmp[['type id', "Lead Dancer #", "Follow Dancer #"]])
        # Insert the replacement
        if replacement_couple.loc[0, 'type id'] == "L":
            print("adding", replacement_couple['Lead Dancer #'][0], replacement_couple["Follow Dancer #"][0])
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
        elif replacement_couple.loc[0, "type id"] == "F":
            print("adding", replacement_couple["Follow Dancer #"][0], replacement_couple['Lead Dancer #'][0], )
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
        elif replacement_couple.loc[0, "type id"] == "C":
            self.couples[roomid].insert(roster_index * 2, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].insert(roster_index * 2, replacement_couple.loc[:, "Lead Dancer #"][0])

        # print(tmp[['type id', "Lead Dancer #", "Follow Dancer #"]])
        # Remove the Old Entry
        if tmp.loc[0, "type id"] == "L":
            print("removing", tmp['Lead Dancer #'][0], tmp["Follow Dancer #"][0], "Room", roomid, "Index", roster_index)
            # print(self.singles[roomid], self.instructors[roomid])
            self.singles[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            # print(self.singles[roomid], self.instructors[roomid])
        elif tmp.loc[0, "type id"] == "F":
            print("removing", tmp["Follow Dancer #"][0], tmp['Lead Dancer #'][0], "Room", roomid, "Index", roster_index)
            # print(self.instructors[roomid], self.singles[roomid])
            self.singles[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            # print(self.instructors[roomid], self.singles[roomid])
        elif tmp.loc[0, "type id"] == "C":
            self.couples[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])

        # Roster Index
        self.roster[roomid].insert(roster_index, replacement_couple)
        self.roster[roomid].pop(roster_index+1)
        return tmp

    def stealEntry(self, roomid, roster_index):
        tmp = self.roster[roomid][roster_index]
        # print("Stealing", tmp['Lead Dancer #'][0], tmp["Follow Dancer #"][0])
        del self.roster[roomid][roster_index]
        self.holes[roomid] += 1
        if tmp.loc[0, "type id"] == "L":
            self.singles[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            if self.div[roomid][0] == "A":  # If and all type room, remove the -1
                del self.couples[roomid][roster_index*2]  # Remove Lead -1
                del self.couples[roomid][roster_index*2+1]  # Remove Follow -1
                self.couples[roomid].append(-1)
        elif tmp.loc[0, "type id"] == "F":
            self.singles[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            if self.div[roomid][0] == "A":  # If and all type room, remove the -1 noting this index was taken
                del self.couples[roomid][roster_index*2]  # Remove Lead -1
                del self.couples[roomid][roster_index*2+1]  # Remove Follow -1
        elif tmp.loc[0, "type id"] == "C":
            self.couples[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            if self.div[roomid][0] == "A":  # If and all type room, remove the -1
                del self.singles[roomid][roster_index]  # Remove Lead -1
                del self.instructors[roomid][roster_index]  # Remove Follow -1
        # print(len(self.roster))
        return tmp

    def calculateHoles(self, couples_per_floor):
        # add the holes into heat obj
        for i, room in enumerate(self.roster):
            self.holes[i] = couples_per_floor - len(room)
            if couples_per_floor - len(room) != 0:
                pass

    def printHeat(self):
        for i, each in enumerate(self.singles):
            print("Room " + str(i) + " singles")
            print(each, self.div[i])
            # print("instructors")
            print(self.instructors[i], self.div[i])
        # for i, each in enumerate(self.instructors):
        #     print("Room" + str(i) + "instructors")
        #     print(each)

    def fillDivision(self, floor_info):
        if [] not in self.div:
            raise Exception("Heat Divisions already full", self.key)

        self.div = floor_info
        floors = len(self.roster)
        divlen = len(self.div)

        if divlen < floors:
            for i in range(floors-divlen):
                self.div.append([])

class HeatList:
    def __init__(self, rosters=[], floors=1, couples_p_floor=0, eventages_s=[], eventages_c=[], eventlvlnames_s=[], eventlvlnames_c=[]):
        self.rosters = rosters
        self.floors = floors
        self.couples_p_floor = couples_p_floor
        self.divs = []
        self.divcounts = []
        self.eventages_s = eventages_s
        self.eventages_c = eventages_c
        self.eventlvlnames_s = eventlvlnames_s
        self.eventlvlnames_c = eventlvlnames_c
        # self.level_bp = level_bp
        self.heat_count = 0
        self.hole_count = []

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

    def getDivisionHoleCount(self, div):
        try:
            index = self.divs.index(div)
        except:
            return 0

        return self.hole_count[index]

    def getHeatCount(self):
        return self.heat_count

    def getEventAgesSingles(self):
        return self.eventages_s

    def getEventAgesCouples(self):
        return self.eventages_c

    def getEventLvlSingles(self):
        return self.eventlvlnames_s

    def getEventLvlCouples(self):
        return self.eventlvlnames_c

    def getCouplesPerFloor(self):
        return self.couples_p_floor

    def appendList(self, heat):
        self.rosters.append(heat)
        self.heat_count += 1
        # Check the divs, if new add it, if exists increment the count of heats
        for i, each in enumerate(heat.getDiv()):
            try:
                index = self.divs.index(each)
            except:
                self.divs.append(each)
                self.divcounts.append(1)
                self.hole_count.append(heat.getHoles()[i])
                continue
            self.divcounts[index] += 1
            self.hole_count[index] += heat.getHoles()[i]