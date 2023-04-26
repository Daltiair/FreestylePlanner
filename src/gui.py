import kivy
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
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
from FreestlyePlannerMain import startProcess


class freestylePlannerGuiApp(App):

    def build(self):
        self.ran = False
        self.window = BoxLayout(spacing=10, orientation='vertical', size_hint=(0.8, 0.8) )
        self.window.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.buttons = GridLayout(spacing=10)
        self.buttons.cols = 1
        self.buttons.size_hint = (0.6, 0.7)
        self.buttons.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # Create Make Cells Button
        self.makeCells = Button(text="Make Cells", height=40, width=65)
        self.makeCells.bind(on_press=self.makeCellsFunc)
        self.buttons.add_widget(self.makeCells)

        # Create Validate Button
        self.validate = Button(text="Validate Data", height=40, width=65)
        self.validate.bind(on_press=self.validateData)
        self.buttons.add_widget(self.validate)

        # Create Run Button
        self.runbutton = Button(text="Run", height=40, width=65)
        self.runbutton.bind(on_press=startProcess)
        self.buttons.add_widget(self.runbutton)
        # self.runbutton.disabled = True

        self.window.add_widget(self.buttons)
        # Create error display tabs
        self.tb_panel = TabbedPanel(do_default_tab=False, pos_hint={"center_x": .5})

        # self.tb_panel.TabbedPanelHeader.default_tab = ""
        self.settings = TabbedPanelHeader(text="Settings")
        self.settingslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.settingslayout.bind(minimum_height=self.settingslayout.setter('height'))
        self.settingscroll = ScrollView(size_hint=(1, 1), size=(self.settings.width, 100))
        self.settingscroll.add_widget(self.settingslayout)
        self.settings.content = self.settingscroll

        self.event = TabbedPanelHeader(text="Event Cat.")
        self.eventlayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.eventlayout.bind(minimum_height=self.eventlayout.setter('height'))
        self.eventscroll = ScrollView(size_hint=(1, 1), size=(self.event.width, 100))
        self.eventscroll.add_widget(self.eventlayout)
        self.event.content = self.eventscroll
        
        self.singles = TabbedPanelHeader(text="Singles")
        self.singleslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.singleslayout.bind(minimum_height=self.singleslayout.setter('height'))
        self.singlescroll = ScrollView(size_hint=(1, 1), size=(self.singles.width, 100))
        self.singlescroll.add_widget(self.singleslayout)
        self.singles.content = self.singlescroll
        
        self.couples = TabbedPanelHeader(text="Couples")
        self.coupleslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.coupleslayout.bind(minimum_height=self.coupleslayout.setter('height'))
        self.couplescroll = ScrollView(size_hint=(1, 1), size=(self.couples.width, 100))
        self.couplescroll.add_widget(self.coupleslayout)
        self.couples.content = self.couplescroll
        
        self.pro = TabbedPanelHeader(text="Pro")
        self.prolayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.prolayout.bind(minimum_height=self.prolayout.setter('height'))
        self.proscroll = ScrollView(size_hint=(1, 1), size=(self.pro.width, 100))
        self.proscroll.add_widget(self.prolayout)
        self.pro.content = self.proscroll
        
        self.instructors = TabbedPanelHeader(text="Instructors")
        self.instructorslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.instructorslayout.bind(minimum_height=self.instructorslayout.setter('height'))
        self.instructorscroll = ScrollView(size_hint=(1, 1), size=(self.instructors.width, 100))
        self.instructorscroll.add_widget(self.instructorslayout)
        self.instructors.content = self.instructorscroll

        # use a scroll view as content of tab
        # self.singles.content = BoxLayout(pos_hint={'center_x': .5})

        # Update Singles Error Tab
        # file = os.getcwd().replace('\src', "") + '\\text.txt'
        # with open(file) as f:
        #     filecontent = f.read()

        # scroll = ScrollView(size_hint=(None, None), scroll_y=1)
        # scroll.size = (self.singles.width, self.singles.height)
        # text = Label(text=filecontent, size_hint_y=None, padding=(10, 5))
        # text.text_size = (self.singles.width, self.singles.height)
        # text.halign = 'left'
        # text.valign = 'top'
        # text.height = text.texture_size[1]
        # scroll.add_widget(text)
        # self.singles.content = scroll

        # self.couples.content = ScrollView(size_hint=(1, None), size=(self.couples.width, self.couples.height))
        # self.settings.content = ScrollView(size_hint=(1, None), size=(self.settings.width, self.settings.height*2))
        # self.event.content = ScrollView(size_hint=(1, None), size=(self.event.width, self.event.height))
        # self.instructors.content = ScrollView(size_hint=(1, None), size=(self.instructors.width, self.instructors.height))

        self.tb_panel.add_widget(self.settings)
        self.tb_panel.add_widget(self.event)
        self.tb_panel.add_widget(self.singles)
        self.tb_panel.add_widget(self.couples)
        self.tb_panel.add_widget(self.pro)
        self.tb_panel.add_widget(self.instructors)

        self.window.add_widget(self.tb_panel)

        # Create Version and License text
        self.softwareData = AnchorLayout(anchor_x='right', anchor_y='bottom')
        self.softwareData.size_hint = (-2.3, 0.001)

        self.version = Label(text="Version: " + "\n" + "License Date: ", text_size=(100, 75), font_size=(9), color=(.5,.5,.5,1))
        # self.version.size_hint = (0.01, 0.01)
        self.softwareData.add_widget(self.version)

        self.window.add_widget(self.softwareData)
        # self.license = Label(text="License Date: ")
        # self.softwareData.add_widget(self.license)

        return self.window

    def makeCellsFunc(self, instance):
        """Runs the Excel macro CreateCells() in excel document FreeStylePlannerInput.xlsm
        CreateCells() makes the appropriate entry rows for the Event Days and Age Brackets
        based on the value in each cell
        """

        self.runbutton.disabled = True

        # Open excel wb, run the macro, and save the wb
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
        wb = xw.Book(file)
        macro = wb.macro("Module1.CreateCells")
        macro()
        wb.save()

        # Close the wb
        # if(len(wb.app.books) == 1):
        #     wb.app.quit()
        # else:
        #     wb.close()

    def validateData(self, instance):
        """Runs the Excel macro Validate() in excel document FreeStylePlannerInput.xlsm
        Validate() will go over all entered data and make sure there are no
        """
        # Open excel wb, run the macro, and save the wb
        # self.removelines()

        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'

        self.runbutton.disabled = True
        wb = xw.Book(file)
        macro = wb.macro("Module1.Validate")
        macro()

        errors = [0]*5

        # Update Singles Error Tab
        file = os.getcwd().replace('\src', "") + '\SinglesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()

        # if self.ran is True:
        #     self.singles.content.remove_widget()
        # scroll = ScrollView()
        # scroll.add_widget(Label(text=filecontent))
        # self.singles.content = scroll
        self.addlines(file, self.singleslayout)

        # view = ScrollView(size_hint=(self.singles.width, None), size=(self.tb_panel.width, self.tb_panel.height),
        #            do_scroll_y=True, pos_hint={'left': 1})
        # view.add_widget(Label(text=filecontent, size_hint=(None,None), size=self.singles.texture_size))
        # self.singles.content.add_widget(view)

        self.singles.background_normal = ''
        # if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
        if filecontent[0] == "Errors: (Heats will not be built while errors present)\n":
            self.singles.background_color = [.5, 0, 0, 1]  # red
            errors[0] = 1
        elif filecontent[0] == "Warnings: (Heats can be built while warnings present)\n":
            self.singles.background_color = [.95, .9, 0, .77]  # Yellow
            errors[0] = 0
        else:
            self.singles.background_color = [0, .5, 0, 1]  # green
            errors[0] = 0

        # Update Couples Error Tab
        file = os.getcwd().replace('\src', "") + '\CouplesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        # self.couples.content.ScrollView.Label(text=filecontent)

        self.addlines(file, self.coupleslayout)

        self.couples.background_normal = ''
        if filecontent[0] == "Errors: (Heats will not be built while errors present)\n":
            self.couples.background_color = [.5, 0, 0, 1]  # red
            errors[1] = 1
        elif filecontent[0] == "Warnings: (Heats can be built while warnings present)\n":
            self.couples.background_color = [.95, .9, 0, .77]  # Yellow
            errors[1] = 0
        else:
            self.couples.background_color = [0, .5, 0, 1]  # green
            errors[1] = 0

        # Update Instructors Error Tab
        file = os.getcwd().replace('\src', "") + '\InstructorsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        # self.instructors.content.add_widget(Label(text=filecontent))
        self.addlines(file, self.instructorslayout)
        self.instructors.background_normal = ''
        if filecontent[0] == "Errors: (Heats will not be built while errors present)\n":
            self.instructors.background_color = [.5, 0, 0, 1]  # red
            errors[2] = 1
        elif filecontent[0] == "Warnings: (Heats can be built while warnings present)\n":
            self.instructors.background_color = [.95, .9, 0, .77]  # Yellow
            errors[2] = 0
        else:
            self.instructors.background_color = [0, .5, 0, 1]  # green
            errors[2] = 0

        # Update Settings Error Tab
        file = os.getcwd().replace('\src', "") + '\SettingsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        # self.settings.content.add_widget(Label(text=filecontent))
        self.addlines(file, self.settingslayout)
        self.settings.background_normal = ''
        if filecontent[0] == "Errors: (Heats will not be built while errors present)\n":
            self.settings.background_color = [.5, 0, 0, 1]  # red
            errors[3] = 1
        elif filecontent[0] == "Warnings: (Heats can be built while warnings present)\n":
            self.settings.background_color = [.95, .9, 0, .77]  # Yellow
            errors[3] = 0
        else:
            self.settings.background_color = [0, .5, 0, 1]  # green
            errors[3] = 0

        # Update Event Error Tab
        file = os.getcwd().replace('\src', "") + '\EventErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        # self.event.content.add_widget(Label(text=filecontent))
        self.addlines(file, self.eventlayout)
        self.event.background_normal = ''
        if filecontent[0] == "Errors: (Heats will not be built while errors present)\n":
            self.event.background_color = [.5, 0, 0, 1]  # red
            errors[4] = 1
        elif filecontent[0] == "Warnings: (Heats can be built while warnings present)\n":
            self.event.background_color = [.95, .9, 0, .77]  # Yellow
            errors[4] = 0
        else:
            self.event.background_color = [0, .5, 0, 1]  # green
            errors[4] = 0

        # Disable the run button if there are errors
        if errors.count(1) > 0:
            self.runbutton.disabled = True
        else:
            self.runbutton.disabled = False

    def resetCells(self, instance):
        """Runs the Excel macro ResetSettings() in excel document FreeStylePlannerInput.xlsm
        ResetSettings() will reset settings page to have no data
        """
        # Disable to
        self.runbutton.disabled = True

        # Open excel wb, run the macro, and save the wb
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'
        self.runbutton.disabled = True
        wb = xw.Book(file)
        macro = wb.macro("Module1.ResetSettings")
        macro()

    def addlines(self, file, layout, *args):
        with open(file) as f:
            # filecontent = f.read()
            filecontent = f.readlines()

        for x in filecontent:
            # text align as per: https://stackoverflow.com/questions/47335100/text-align-in-left-in-boxlayout
            single_error = Label(text=x.strip('\n'), size_hint_y=None, height=20, halign="left", valign="middle",
                                 padding_x=5)  # .strip('\n')
            # print("size ", self.layout.size, single_error.size, single_error.texture_size)
            single_error.text_size = self.settingslayout.size
            layout.add_widget(single_error)

    def removelines(self):

        self.settings.remove_widget(self.settingslayout)
        self.settingslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.settingslayout.bind(minimum_height=self.settingslayout.setter('height'))
        self.settingscroll = ScrollView(size_hint=(1, 1), size=(self.settings.width, 100))
        self.settingscroll.add_widget(self.settingslayout)
        self.settings.content = self.settingscroll

        # self.settingscroll.remove_widget(self.settingslayout)
        # self.settingscroll = ScrollView(size_hint=(1, 1), size=(self.settings.width, 100))
        # self.settingscroll.add_widget(self.settingslayout)
        # self.settings.content = self.settingscroll

        self.event.remove_widget(self.eventlayout)
        self.eventlayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.eventlayout.bind(minimum_height=self.eventlayout.setter('height'))
        self.eventscroll = ScrollView(size_hint=(1, 1), size=(self.event.width, 100))
        self.eventscroll.add_widget(self.eventlayout)
        self.event.content = self.eventscroll

        self.singles.remove_widget(self.singleslayout)
        self.singles = TabbedPanelHeader(text="Singles")
        self.singleslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.singleslayout.bind(minimum_height=self.singleslayout.setter('height'))
        self.singlescroll = ScrollView(size_hint=(1, 1), size=(self.singles.width, 100))
        self.singlescroll.add_widget(self.singleslayout)
        self.singles.content = self.singlescroll

        self.couples.remove_widget(self.coupleslayout)
        self.couples = TabbedPanelHeader(text="Couples")
        self.coupleslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.coupleslayout.bind(minimum_height=self.coupleslayout.setter('height'))
        self.couplescroll = ScrollView(size_hint=(1, 1), size=(self.couples.width, 100))
        self.couplescroll.add_widget(self.coupleslayout)
        self.couples.content = self.couplescroll

        self.prolayout.remove_widget(self.prolayout)
        self.pro = TabbedPanelHeader(text="Pro")
        self.prolayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.prolayout.bind(minimum_height=self.prolayout.setter('height'))
        self.proscroll = ScrollView(size_hint=(1, 1), size=(self.pro.width, 100))
        self.proscroll.add_widget(self.prolayout)
        self.pro.content = self.proscroll

        self.instructors.remove_widget(self.instructorslayout)
        self.instructors = TabbedPanelHeader(text="Instructors")
        self.instructorslayout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.instructorslayout.bind(minimum_height=self.instructorslayout.setter('height'))
        instructorscroll = ScrollView(size_hint=(1, 1), size=(self.instructors.width, 100))
        instructorscroll.add_widget(self.instructorslayout)
        self.instructors.content = instructorscroll