from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import os
import xlwings as xw
from methods import partitionData

'''
File with all objects and structures used to create Free Style Itenerary
'''


class freestylePlannerGui(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1

        # Create Version and License text
        self.softwareData = GridLayout(cols=1, row_default_height=20, spacing=1)

        self.version = Label(text="Version: ")
        self.softwareData.add_widget(self.version)

        self.license = Label(text="License Date: ")
        self.softwareData.add_widget(self.license)

        self.window.add_widget(self.softwareData)

        # Create Make Cells Button
        self.makeCells = Button(text="Make Cells", height=40, width=65)
        self.makeCells.bind(on_press=self.makeCells)
        self.window.add_widget(self.makeCells)

        # Create Validate Button
        self.validate = Button(text="Validate Data", height=40, width=65)
        self.validate.bind(on_press=self.validateData)
        self.window.add_widget(self.validate)

        # Create Run Button
        self.runbutton = Button(text="Run", height=40, width=65)
        self.runbutton.bind(on_press=partitionData())
        self.window.add_widget(self.runbutton)

        # Create error display tabs
        self.tb_panel = TabbedPanel()

        self.settings = TabbedPanelHeader(text="Settings")
        self.event = TabbedPanelHeader(text="Event Categories")
        self.singles = TabbedPanelHeader(text="Singles")
        self.couples = TabbedPanelHeader(text="Couples")
        self.instructors = TabbedPanelHeader(text="Instructors")

        # use a scroll view as content of tab
        self.singles.content = ScrollView(size_hint=(1, None), size=(self.singles.width, self.singles.height))
        self.couples.content = ScrollView(size_hint=(1, None), size=(self.couples.width, self.couples.height))
        self.settings.content = ScrollView(size_hint=(1, None), size=(self.settings.width, self.settings.height))
        self.event.content = ScrollView(size_hint=(1, None), size=(self.event.width, self.event.height))
        self.instructors.content = ScrollView(size_hint=(1, None), size=(self.instructors.width, self.instructors.height))

        self.tb_panel.add_widget(self.settings)
        self.tb_panel.add_widget(self.event)
        self.tb_panel.add_widget(self.singles)
        self.tb_panel.add_widget(self.couples)
        self.tb_panel.add_widget(self.instructors)

    def makeCells(self):
        """Runs the Excel macro CreateCells() in excel document FreeStylePlannerInput.xlsm
        CreatCells() makes the appropriate entry rows for the Event Days and Age Brackets
        based on the value in each cell
        """
        # Open excel wb, run the macro, and save the wb
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
        wb = xw.Book(file)
        wb.macro("Module1.CreateCells")
        wb.save()

        # Open excel wb, run the macro, and save the wb
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
        wb = xw.Book(file)
        wb.macro("Module1.Validate")

        errors = [0] * 5
        # Update Singles Error Tab
        file = os.getcwd().replace('\src', "") + '\SinglesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.singles.content.add_widget(Label(text=filecontent))

        if filecontent != "":
            self.singles.background_color(1, 0, 0, 1)  # red
            errors[0] = 1
        else:
            self.singles.background_color(0, 1, 0, 1)  # green
            errors[0] = 0

        # Close the wb
        # if(len(wb.app.books) == 1):
        #     wb.app.quit()
        # else:
        #     wb.close()

    def validateData(self):
        """Runs the Excel macro Validate() in excel document FreeStylePlannerInput.xlsm
        Validate() will go over all entered data and make sure there are no
        """
        # Open excel wb, run the macro, and save the wb
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
        wb = xw.Book(file)
        wb.macro("Module1.Validate")

        errors = [0]*5
        # Update Singles Error Tab
        file = os.getcwd().replace('\src', "") + '\SinglesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.singles.content.add_widget(Label(text=filecontent))

        if filecontent != "" or filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.singles.background_color(1, 0, 0, 1)  # red
            errors[0] = 1
        else:
            self.singles.background_color(0, 1, 0, 1)  # green
            errors[0] = 0

        # Update Couples Error Tab
        file = os.getcwd().replace('\src', "") + '\CouplesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.couples.content.add_widget(Label(text=filecontent))

        if filecontent != "" or filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.couples.background_color(1, 0, 0, 1)  # red
            errors[1] = 1
        else:
            self.couples.background_color(0, 1, 0, 1)  # green
            errors[1] = 0

        # Update Instructors Error Tab
        file = os.getcwd().replace('\src', "") + '\InstructorsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.instructors.content.add_widget(Label(text=filecontent))

        if filecontent != "" or filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.instructors.background_color(1, 0, 0, 1)  # red
            errors[2] = 1
        else:
            self.instructors.background_color(0, 1, 0, 1)  # green
            errors[2] = 0

        # Update Settings Error Tab
        file = os.getcwd().replace('\src', "") + '\SettingsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.settings.content.add_widget(Label(text=filecontent))

        if filecontent != "" or filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.settings.background_color(1, 0, 0, 1)  # red
            errors[3] = 1
        else:
            self.settings.background_color(0, 1, 0, 1)  # green
            errors[3] = 0

        # Update Event Error Tab
        file = os.getcwd().replace('\src', "") + '\EventErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.event.content.add_widget(Label(text=filecontent))

        if filecontent != "" or filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.event.background_color(1, 0, 0, 1)  # red
            errors[4] = 1
        else:
            self.event.background_color(0, 1, 0, 1)  # green
            errors[4] = 0

        # Disable the run button if there are errors
        if errors.count(1) > 0:
            self.runbutton.disabled = True
        else:
            self.runbutton.disabled = False

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