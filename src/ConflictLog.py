

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
                    if self.roomlog[each]["conf_list"][index].getType() != "S":  # If this is a single conflict, move to next index
                        index -= 1
                        continue
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
                    if self.roomlog[each]["conf_list"][index].getType() != "C":  # If this is a single conflict, move to next index
                        index -= 1
                        continue
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