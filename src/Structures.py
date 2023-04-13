'''
File with all objects and structures used to create Free Style Itenerary
'''

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
        elif entry.loc[0, "type id"] == "F":
            self.singles[roomid].append(entry.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].append(entry.loc[:, "Lead Dancer #"][0])
        elif entry.loc[0, "type id"] == "C":
            self.couples[roomid].append(entry.loc[:, "Lead Dancer #"][0])
            self.couples[roomid].append(entry.loc[:, "Follow Dancer #"][0])
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
        elif tmp.loc[0, "type id"] == "F":
            self.singles[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
        elif tmp.loc[0, "type id"] == "C":
            self.couples[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
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

class ConflictItemSingle:
    # def __init__(self, code=0, contestants=[], inst=000, loc='n'):
    def __init__(self, code=0, inst=000):
        # code table
        # 1: No free Instructor assumes contestant free must be at a different level, external only
        # 2: No free contestant, internal only contestant can't be in 2 levels for the same dance.
        self.code = code
        # self.contestants = contestants
        self.inst = inst
        # Loc table
        # i: internal conflict
        # e: external conflict
        # self.loc = loc
        self.type = "S"

    def getCode(self):
        return self.code

    def getType(self):
        return self.type

    # def getContestants(self):
    #     return self.contestants

    def getInstructor(self):
        return self.inst

    # def getLocation(self):
    #     return self.loc

    # def updateContestants(self, contestants):
    #     self.contestants = contestants

class ResolverConflictItemSingle:
    # def __init__(self, code=0, contestants=[], inst=000, loc='n'):
    def __init__(self, code=0, div=[], heat_index=0, nconflict_room=0, nconflict_index=0, instructors=[], contestants=[], conflict_num=000, prev_conflict=0, aux=[]):
        # code table
        # 1: Internal heat conflict, conflict entry in question cannot swap instructor for a different one
        # 2: Internal heat conflict, conflict entry in question cannot swap Contestant for a different one
        # 3: External Heat conflict, previous heat has an instructor conflict with conflict entry in question
        # 4: External Heat conflict, previous heat has a Contestant conflict with conflict entry in question
        # 5: External Heat conflict, previous heat has a Couples Contestant conflict with conflict entry in question, prevent a couple being swapped out or errors
        self.code = code
        self.div = div
        self.heat_index = heat_index
        self.nconflict_room = nconflict_room
        self.nconflict_index = nconflict_index
        self.contestants = contestants  # for Nth conflict while trying to solve a no contestant conflict, no solution can cause these numbers to swap into the og heat
        self.conflict_num = conflict_num  # The number that is causing the conflict
        self.instructors = instructors  # The instructor that is free but has not free contesants
        self.prev_conflict = prev_conflict  # The instructor that is free but has not free contesants
        self.aux = aux  # The extra instructors/Contestants the fix has to work with
        # Loc table
        # i: internal conflict
        # e: external conflict
        # self.loc = loc
        self.type = "S"

    def getCode(self):
        return self.code

    def getDiv(self):
        return self.div

    def getHeatIndex(self):
        return self.heat_index

    def getNConflictRoom(self):
        return self.nconflict_room

    def getNConflictIndex(self):
        return self.nconflict_index

    def getType(self):
        return self.type

    def getPrevConflict(self):
        return self.prev_conflict

    def getInstructors(self):
        return self.instructors

    def getContestants(self):
        return self.contestants

    def getConflictNumber(self):
        return self.conflict_num

    def getAux(self):
        return self.aux

    # def getLocation(self):
    #     return self.loc

    def updateContestants(self, contestants):
        self.contestants = contestants

class ConflictLog:

    def __init__(self, div=[]):
        self.div = div
        self.rooms = len(div)
        self.roomlog = {}
        self.codeCount = [0, 0]  # Code 1 Count, Codde 2 Count


        for roomid, info in enumerate(div):
            self.roomlog[roomid] = {}
            self.roomlog[roomid]["conf_list"] = []
            self.roomlog[roomid]["conf_count"] = []
            self.roomlog[roomid]["div"] = info
            self.roomlog[roomid]["total"] = 0
            # self.roomlog[roomid]["mode_con"] = [0, 0]
            self.roomlog[roomid]["mode_inst"] = [0, 0]
            self.roomlog[roomid]["mode_cont"] = [0, 0]
            self.roomlog[roomid]["inst_list"] = []
            # self.roomlog[roomid]["mode_code"] = 0
            # # self.roomlog[roomid]["mode_loc"] = 0
            # self.roomlog[roomid]["codeCount"] = [0, 0]  # Code 1 Count, Codde 2 Count


    def getRoomlog(self):
        return self.roomlog

    def getDivision(self):
        return self.div

    def getInstructorsList(self, roomid):
        return self.roomlog[roomid]["inst_list"]

    def addConflict(self, conflict, roomid):
        dup = False
        if conflict.getType() == "S":
            # if instructor is not in the list
            if conflict.getInstructor() not in self.roomlog[roomid]["inst_list"]:
                self.roomlog[roomid]["inst_list"].append(conflict.getInstructor())
        for i, each in enumerate(self.roomlog[roomid]["conf_list"]):
            if conflict.getType() == "S":
                if each.getCode() == conflict.getCode():
                    if each.getInstructor() == conflict.getInstructor():
                        self.roomlog[roomid]["conf_count"][i] += 1
                        # self.roomlog[roomid]["conf_list"][i].updateContestants(conflict.getContestants())
                        new_num = self.roomlog[roomid]["conf_count"][i]
                        dup = True
            else:  # a Couples Conflict
                if each.getLead() == conflict.getLead() and each.getFollow() == conflict.getFollow():
                    if each.getCode() == conflict.getCode():
                        self.roomlog[roomid]["conf_count"][i] += 1
                        new_num = self.roomlog[roomid]["conf_count"][i]
                        dup = True

        if not dup:
            self.roomlog[roomid]["conf_list"].append(conflict)
            self.roomlog[roomid]["conf_count"].append(1)
            new_num = self.roomlog[roomid]["conf_count"][-1]

        self.roomlog[roomid]["total"] += 1

        # Update Mode
        if conflict.getType() == "S":
            # Update Inst mode
            if new_num > self.roomlog[roomid]["mode_inst"][1]:
                self.roomlog[roomid]["mode_inst"][0] = conflict.getInstructor()
                self.roomlog[roomid]["mode_inst"][1] += 1

        # Update Mode
        if conflict.getType() == "C":
            # Update Contestant mode
            if new_num > self.roomlog[roomid]["mode_cont"][1]:
                self.roomlog[roomid]["mode_cont"][0] = conflict.getLead()
                self.roomlog[roomid]["mode_cont"][1] += 1

    def clearConflict(self, inst, contestants):
        # If an instructor is involved in the solution
        if inst != -1:
            # Delete conflict from every room involving instructor inst
            for each in self.roomlog:
                index = len(self.roomlog[each]["conf_list"]) - 1
                while index >= 0:  # reversed(self.roomlog[each]["conf_list"]):
                    if self.roomlog[each]["conf_list"][index].getInstructor() == inst:
                        # Remove from total
                        self.roomlog[each]["total"] -= self.roomlog[each]["conf_count"][index]
                        del self.roomlog[each]["conf_count"][index]  # delete the count with it as well
                        del self.roomlog[each]["conf_list"][index]
                        if inst in self.roomlog[each]["inst_list"]:
                            self.roomlog[each]["inst_list"].remove(inst)
                        if self.roomlog[each]["mode_inst"][0] == inst:
                            self.roomlog[each]["mode_inst"][0] = 0
                            self.roomlog[each]["mode_inst"][1] = 0
                    index -= 1
        else:
            for each in self.roomlog:
                index = len(self.roomlog[each]["conf_list"]) - 1
                while index >= 0:
                    if self.roomlog[each]["conf_list"][index].getLead() == contestants[0] and self.roomlog[each]["conf_list"][index].getFollow() == contestants[1]:
                        # Remove from total
                        self.roomlog[each]["total"] -= self.roomlog[each]["conf_count"][index]
                        del self.roomlog[each]["conf_count"][index]  # delete the count with it as well
                        del self.roomlog[each]["conf_list"][index]
                        if self.roomlog[each]["mode_cont"][0] == contestants[0]:
                            self.roomlog[each]["mode_cont"][0] = 0
                            self.roomlog[each]["mode_cont"][1] = 0
                    index -= 1

    def addRoom(self, newdiv):
        roomid = self.rooms
        self.rooms = len(self.div)
        self.roomlog[roomid] = {}
        self.roomlog[roomid]["conf_list"] = []
        self.roomlog[roomid]["conf_count"] = []
        self.roomlog[roomid]["inst_list"] = []
        self.roomlog[roomid]["div"] = newdiv
        self.roomlog[roomid]["total"] = 0
        # self.roomlog[roomid]["mode_con"] = [0, 0]
        self.roomlog[roomid]["mode_inst"] = [0, 0]
        self.roomlog[roomid]["mode_cont"] = [0, 0]

class ResolverConflictLog:
    # TODO rewrite this to serve needs
    def __init__(self):
        # self.rooms = len(div)
        self.roomlog = {}
        self.codeCount = [0, 0, 0, 0]  # Code 1 Count, Codde 2 Count
        self.roomlog["conf_list"] = []
        self.roomlog["conf_count"] = []
        self.roomlog["roomid"] = []  # holds which room in the heat the conflict is in
        self.roomlog["heat_index"] = []  # holds heat index where the conflict is (if external conflict)
        self.roomlog["conflict_index"] = []  # holds roster index where the conflict is
        self.roomlog["div"] = []
        self.roomlog["prev"] = 0
        self.roomlog["nminus"] = []
        self.roomlog["print_index"] = []
        # self.roomlog["total"] = 0
        # self.roomlog["mode_con"] = [0, 0]
        # self.roomlog["mode_inst"] = [0, 0]
        # self.roomlog["mode_code"] = 0
        # # self.roomlog["mode_loc"] = 0
        # self.roomlog["codeCount"] = [0, 0]  # Code 1 Count, Codde 2 Count

        # for roomid, info in enumerate(div):
        #     self.roomlog[roomid] = {}
        #     self.roomlog[roomid]["conf_list"] = []
        #     self.roomlog[roomid]["conf_count"] = []
        #     self.roomlog[roomid]["div"] = info
        #     self.roomlog[roomid]["total"] = 0
        #     self.roomlog[roomid]["mode_con"] = [0, 0]
        #     self.roomlog[roomid]["mode_inst"] = [0, 0]
        #     self.roomlog[roomid]["mode_code"] = 0
        #     # self.roomlog[roomid]["mode_loc"] = 0
        #     self.roomlog[roomid]["codeCount"] = [0, 0]  # Code 1 Count, Codde 2 Count


    def getRoomlog(self):
        return self.roomlog

    def addConflict(self, conflict, con_num, nconflict_counter):

        if conflict.getType() == "S":
            self.roomlog["conf_list"].append(conflict)
            self.roomlog['roomid'].append(conflict.getNConflictRoom())
            self.roomlog['heat_index'].append(conflict.getHeatIndex())
            self.roomlog['div'].append(conflict.getDiv())
            self.roomlog["nminus"].append(con_num)
            self.roomlog["print_index"].append(nconflict_counter)

        if conflict.getType() == "C":
            self.roomlog["conf_list"].append(conflict)
            self.roomlog['roomid'].append(conflict.getNConflictRoom())
            self.roomlog['heat_index'].append(conflict.getHeatIndex())
            self.roomlog['div'].append(conflict.getDiv())
            self.roomlog["nminus"].append(con_num)
            self.roomlog["print_index"].append(nconflict_counter)
        # for i, each in enumerate(self.roomlog["conf_list"]):
        #     if conflict.getType() == "S":
        #         if each.getCode() == conflict.getCode():
        #             if each.getInstructor() == conflict.getInstructor():
        #                 self.roomlog["conf_count"][i] += 1
        #                 self.roomlog["conf_list"][i].updateContestants(conflict.getContestants())
        #
        #                 new_num = self.roomlog["conf_count"][i]
        #                 dup = True
        #     else: # a Couples Conflict
        #         if each.getContestant() == conflict.getContestant():
        #             pass
        #
        # if not dup:
        #     self.roomlog["conf_list"].append(conflict)
        #     self.roomlog["conf_count"].append(1)
        #     new_num = self.roomlog["conf_count"][-1]
        #
        # self.roomlog["total"] += 1
        #
        # # Update Mode
        # if conflict.getType() == "S":
        #     # Update code and Mode
        #     if conflict.getCode() == 1:
        #         self.roomlog["codeCount"][0] += 1
        #         if self.roomlog["codeCount"][0] > self.roomlog["codeCount"][1]:
        #             self.roomlog["mode_code"] = 1
        #     if conflict.getCode() == 2:
        #         self.roomlog["codeCount"][1] += 1
        #         if self.roomlog["codeCount"][1] > self.roomlog["codeCount"][0]:
        #             self.roomlog["mode_code"] = 2
        #     # Update Inst mode
        #     if new_num > self.roomlog["mode_inst"][1]:
        #         self.roomlog["mode_inst"][0] = conflict.getInstructor()
        #         self.roomlog["mode_inst"][1] += 1

    def clearConflicts(self):
        self.roomlog = {}
        self.codeCount = [0, 0, 0, 0]  # Code 1 Count, Codde 2 Count
        self.roomlog["conf_list"] = []
        self.roomlog["conf_count"] = []
        self.roomlog["roomid"] = []  # holds which room in the heat the conflict is in
        self.roomlog["heat_index"] = []  # holds heat index where the conflict is (if external conflict)
        self.roomlog["conflict_index"] = []  # holds roster index where the conflict is
        self.roomlog["div"] = []
        self.roomlog["prev"] = 0
        self.roomlog["nminus"] = []
        self.roomlog["print_index"] = []


class ConflictItemCouple:
    # def __init__(self, code=0, contestants=[], inst=000, loc='n'):
    def __init__(self, code=0, L=000, F=000):
        # code table
        # 1: Contestant conflict, must be internal
        # 2: Singles Conflict, must be external
        self.code = code
        self.L = L
        self.F = F
        self.type = "C"

    def getCode(self):
        return self.code

    def getType(self):
        return self.type

    def getLead(self):
        return self.L

    def getFollow(self):
        return self.F


class ResolverConflictItemCouple:
    # def __init__(self, code=0, contestants=[], inst=000, loc='n'):
    def __init__(self, code=0, div=[], heat_index=0, nconflict_room=0, nconflict_index=0, couples=[], singles=[], conflict_nums=[0, 0], prev_conflict=0, aux=[]):
        # code table
        # 1: Internal heat conflict, cannot swap conflict contestant for a different one
        # 2: External Heat conflict, previous heat has a Couples conflict with conflict entry in question
        # 3: External Heat conflict, previous heat has an Instructor conflict with conflict entry in question
        # 4: External Heat conflict, previous heat has a Single Contestant conflict with conflict entry in question
        self.code = code
        self.div = div
        self.heat_index = heat_index
        self.nconflict_room = nconflict_room
        self.nconflict_index = nconflict_index
        self.couples = couples  # for Nth conflict while trying to solve a no contestant conflict, no solution can cause these numbers to swap into the og heat
        self.singles = singles  # for Nth conflict while trying to solve a no contestant conflict, no solution can cause these numbers to swap into the og heat
        self.conflict_nums = conflict_nums  # The number that is causing the conflict
        # self.instructors = instructors  # The instructor that is free but has not free contesants
        self.prev_conflict = prev_conflict  # The instructor that is free but has not free contesants
        self.aux = aux  # The extra instructors/Contestants the fix has to work with
        self.type = "C"

    def getCode(self):
        return self.code

    def getDiv(self):
        return self.div

    def getHeatIndex(self):
        return self.heat_index

    def getNConflictRoom(self):
        return self.nconflict_room

    def getNConflictIndex(self):
        return self.nconflict_index

    def getType(self):
        return self.type

    def getPrevConflict(self):
        return self.prev_conflict

    def getSingles(self):
        return self.getSingles

    def getCouples(self):
        return self.couples

    def getConflictNums(self):
        return self.conflict_nums

    def getAux(self):
        return self.aux

    # def getLocation(self):
    #     return self.loc

    def updateContestants(self, contestants):
        self.contestants = contestants