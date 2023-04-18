'''
File with all objects and structures used to create Free Style Itenerary
'''


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