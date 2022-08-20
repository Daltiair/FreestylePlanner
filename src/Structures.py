'''
File with all objects and structures used to create Free Style Itenerary
'''


class Heat:

    def __init__(self, key='', number=0, roster=[], instructors=[]):
        # key = Genre-Syllabus-Dance-index
        self.key = key
        self.number = number
        self.roster = roster
        self.instructors = instructors

    def getRoster(self):
        return self.roster

    def getInstructors(self):
        return self.instructors

    def getNumber(self):
        return self.number

    def getKey(self):
        return self.key

    def replaceContestant(self, current_couple, replacement_couple):
        if self.roster.contains(current_couple):
            if self.instructors.Contains(replacement_couple):
                self.roster[self.roster.Index(current_couple)] = replacement_couple


class HeatList:
    def __init__(self, rosters=[], level_bp=[], heat_count=0):
        self.rosters = rosters
        self.level_bp = level_bp
        self.heats_count = heat_count

    def getRostersList(self):
        return self.rosters

    def getLevelBreakPoints(self):
        return self.level_bp

    def getHeatCount(self):
        return self.heats_count
