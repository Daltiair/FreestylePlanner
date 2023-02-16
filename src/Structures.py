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
        self.singles_index = len(self.singles)

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
        tmp = self.roster[roomid][roster_index]
        if tmp.loc[0, "type id"] == "L":
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.singles[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
        elif tmp.loc[0, "type id"] == "F":
            self.singles[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.singles[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.instructors[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])
        elif tmp.loc[0, "type id"] == "C":
            self.couples[roomid].insert(roster_index, replacement_couple.loc[:, "Lead Dancer #"][0])
            self.couples[roomid].insert(roster_index, replacement_couple.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Follow Dancer #"][0])
            self.couples[roomid].remove(tmp.loc[:, "Lead Dancer #"][0])

        self.roster[roomid].insert(roster_index, replacement_couple)
        self.roster[roomid].pop(roster_index+1)
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
    def __init__(self, code=0, div=[], heat_index=0, nconflict_room=0, nconflict_index=0, contestants=[], free_inst=[], conflict_num=000, prev_conflict=0):
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
        self.free_inst = free_inst  # The instructor that is free but has not free contesants
        self.prev_conflict = prev_conflict  # The instructor that is free but has not free contesants
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

    def getContestants(self):
        return self.contestants

    def getConflictNumber(self):
        return self.conflict_num

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
            # self.roomlog[roomid]["mode_code"] = 0
            # # self.roomlog[roomid]["mode_loc"] = 0
            # self.roomlog[roomid]["codeCount"] = [0, 0]  # Code 1 Count, Codde 2 Count


    def getRoomlog(self):
        return self.roomlog

    def getDivision(self):
        return self.div

    def addConflict(self, conflict, roomid):
        dup = False
        for i, each in enumerate(self.roomlog[roomid]["conf_list"]):
            if conflict.getType() == "S":
                if each.getCode() == conflict.getCode():
                    if each.getInstructor() == conflict.getInstructor():
                        self.roomlog[roomid]["conf_count"][i] += 1
                        # self.roomlog[roomid]["conf_list"][i].updateContestants(conflict.getContestants())
                        new_num = self.roomlog[roomid]["conf_count"][i]
                        dup = True
            else:  # a Couples Conflict
                if each.getContestant() == conflict.getContestant():
                    pass

        if not dup:
            self.roomlog[roomid]["conf_list"].append(conflict)
            self.roomlog[roomid]["conf_count"].append(1)
            new_num = self.roomlog[roomid]["conf_count"][-1]

        self.roomlog[roomid]["total"] += 1

        # Update Mode
        if conflict.getType() == "S":
            # # Update code and Mode
            # if conflict.getCode() == 1:
            #     self.roomlog[roomid]["codeCount"][0] += 1
            #     if self.roomlog[roomid]["codeCount"][0] > self.roomlog[roomid]["codeCount"][1]:
            #         self.roomlog[roomid]["mode_code"] = 1
            # if conflict.getCode() == 2:
            #     self.roomlog[roomid]["codeCount"][1] += 1
            #     if self.roomlog[roomid]["codeCount"][1] > self.roomlog[roomid]["codeCount"][0]:
            #         self.roomlog[roomid]["mode_code"] = 2
            # Update Inst mode
            if new_num > self.roomlog[roomid]["mode_inst"][1]:
                self.roomlog[roomid]["mode_inst"][0] = conflict.getInstructor()
                self.roomlog[roomid]["mode_inst"][1] += 1

    def clearConflict(self, inst, contestants):
        # If an instructor is involved in the solution
        if inst != -1:
            # Delete conflict from every room involving instructor inst
            for each in self.roomlog:
                for i, every in enumerate(reversed(self.roomlog[each]["conf_list"])):
                    index = len(self.roomlog[each]["conf_list"]) - i - 1
                    if every.getInstructor() == inst:
                        # Reduce the count by the number of conflicts
                        # if every.getCode() == 1:
                        #     self.roomlog[each]["codeCount"][0] -= self.roomlog[each]["conf_count"][i]
                        #     # Update mode code
                        #     if self.roomlog[each]["codeCount"][0] > self.roomlog[each]["codeCount"][1]:
                        #         self.roomlog[each]["mode_code"] = 1
                        # else:
                        #     self.roomlog[each]["codeCount"][1] -= self.roomlog[each]["conf_count"][i]
                        #     # Update mode code
                        #     if self.roomlog[each]["codeCount"][1] > self.roomlog[each]["codeCount"][0]:
                        #         self.roomlog[each]["mode_code"] = 1
                        # Remove from total
                        self.roomlog[each]["total"] -= self.roomlog[each]["conf_count"][index]
                        del self.roomlog[each]["conf_count"][index]  # delete the count with it as well
                        del self.roomlog[each]["conf_list"][index]
                        if self.roomlog[each]["mode_inst"][0] == inst:
                            self.roomlog[each]["mode_inst"][0] = 0
                            self.roomlog[each]["mode_inst"][1] = 0


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

    def addConflict(self, conflict):

        if conflict.getType() == "S":
            self.roomlog["conf_list"].append(conflict)
            self.roomlog['roomid'].append(conflict.getNConflictRoom())
            self.roomlog['heat_index'].append(conflict.getHeatIndex())
            self.roomlog['div'].append(conflict.getDiv())
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

    # TODO probably not needed
    def clearConflict(self, inst, contestants):
        # If an instructor is involved in the solution
        if inst != -1:
            # Delete conflict from every room involving instructor inst
            for each in self.roomlog:
                for i, every in enumerate(self.roomlog[each]["conf_list"]):
                    if every.getInstructor() == inst:
                        del every
                        # Reduce the count by the number of conflicts
                        if every.getCode() == 1:
                            self.roomlog[each]["codeCount"][0] -= self.roomlog[each]["conf_count"][i]
                            # Update mode code
                            if self.roomlog[each]["codeCount"][0] > self.roomlog[each]["codeCount"][1]:
                                self.roomlog[each]["mode_code"] = 1
                        else:
                            self.roomlog[each]["codeCount"][1] -= self.roomlog[each]["conf_count"][i]
                            # Update mode code
                            if self.roomlog[each]["codeCount"][1] > self.roomlog[each]["codeCount"][0]:
                                self.roomlog[each]["mode_code"] = 1
                        # Remove from total
                        self.roomlog[each]["total"] -= self.roomlog[each]["conf_count"][i]
                        del self.roomlog[each]["conf_count"][i]  # delete the count with it as well