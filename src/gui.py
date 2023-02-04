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
from methods import partitionData


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
        self.runbutton.bind(on_press=partitionData)
        self.buttons.add_widget(self.runbutton)
        self.runbutton.disabled = True

        self.window.add_widget(self.buttons)
        # Create error display tabs
        self.tb_panel = TabbedPanel(do_default_tab=False, pos_hint={"center_x":.5})

        # self.tb_panel.TabbedPanelHeader.default_tab = ""
        self.settings = TabbedPanelHeader(text="Settings")
        self.event = TabbedPanelHeader(text="Event Cat.")
        self.singles = TabbedPanelHeader(text="Singles")
        self.couples = TabbedPanelHeader(text="Couples")
        self.pro = TabbedPanelHeader(text="Pro")
        self.instructors = TabbedPanelHeader(text="Instructors")

        # use a scroll view as content of tab
        # self.singles.content = BoxLayout(pos_hint={'center_x': .5})

        # Update Singles Error Tab
        file = os.getcwd().replace('\src', "") + '\\text.txt'
        with open(file) as f:
            filecontent = f.read()

        scroll = ScrollView(size_hint=(None, None), scroll_y=1)
        scroll.size = (self.singles.width, self.singles.height)
        text = Label(text=filecontent, size_hint_y=None, padding=(10, 5))
        text.text_size = (self.singles.width, self.singles.height)
        text.halign = 'left'
        text.valign = 'top'
        text.height = text.texture_size[1]
        scroll.add_widget(text)
        self.singles.content = scroll

        self.couples.content = ScrollView(size_hint=(1, None), size=(self.couples.width, self.couples.height))
        self.settings.content = ScrollView(size_hint=(1, None), size=(self.settings.width, self.settings.height*2))
        self.event.content = ScrollView(size_hint=(1, None), size=(self.event.width, self.event.height))
        self.instructors.content = ScrollView(size_hint=(1, None), size=(self.instructors.width, self.instructors.height))

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
        file = os.getcwd().replace('\src', "") + '\FreestyleEventPlannerInput.xlsm'

        self.runbutton.disabled = True
        wb = xw.Book(file)
        macro = wb.macro("Module1.Validate")
        macro()

        errors = [0]*5

        # Update Singles Error Tab
        file = os.getcwd().replace('\src', "") + '\SinglesErrors.txt'
        with open(file) as f:
            filecontent = f.read()

        if self.ran is True:
            self.singles.content.remove_widget()
        scroll = ScrollView()
        scroll.add_widget(Label(text=filecontent))
        self.singles.content = scroll

        # view = ScrollView(size_hint=(self.singles.width, None), size=(self.tb_panel.width, self.tb_panel.height),
        #            do_scroll_y=True, pos_hint={'left': 1})
        # view.add_widget(Label(text=filecontent, size_hint=(None,None), size=self.singles.texture_size))
        # self.singles.content.add_widget(view)

        self.singles.background_normal = ''
        if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
            self.singles.background_color = [.5, 0, 0, 1]  # red
            errors[0] = 1
        elif filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.singles.background_color = [.95, .9, 0, .77]  # Yellow
            errors[0] = 0
        else:
            self.singles.background_color = [0, .5, 0, 1]  # green
            errors[0] = 0

        # Update Couples Error Tab
        file = os.getcwd().replace('\src', "") + '\CouplesErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.couples.content.ScrollView.Label(text=filecontent)

        self.couples.background_normal = ''
        if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
            self.couples.background_color = [.5, 0, 0, 1]  # red
            errors[1] = 1
        elif filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.couples.background_color = [.95, .9, 0, .77]  # Yellow
            errors[1] = 0
        else:
            self.couples.background_color = [0, .5, 0, 1]  # green
            errors[1] = 0

        # Update Instructors Error Tab
        file = os.getcwd().replace('\src', "") + '\InstructorsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.instructors.content.add_widget(Label(text=filecontent))

        self.instructors.background_normal = ''
        if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
            self.instructors.background_color = [.5, 0, 0, 1]  # red
            errors[2] = 1
        elif filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.instructors.background_color = [.95, .9, 0, .77]  # Yellow
            errors[2] = 0
        else:
            self.instructors.background_color = [0, .5, 0, 1]  # green
            errors[2] = 0

        # Update Settings Error Tab
        file = os.getcwd().replace('\src', "") + '\SettingsErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.settings.content.add_widget(Label(text=filecontent))

        self.settings.background_normal = ''
        if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
            self.settings.background_color = [.5, 0, 0, 1]  # red
            errors[3] = 1
        elif filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
            self.settings.background_color = [.95, .9, 0, .77]  # Yellow
            errors[3] = 0
        else:
            self.settings.background_color = [0, .5, 0, 1]  # green
            errors[3] = 0

        # Update Event Error Tab
        file = os.getcwd().replace('\src', "") + '\EventErrors.txt'
        with open(file) as f:
            filecontent = f.readlines()
        self.event.content.add_widget(Label(text=filecontent))

        self.event.background_normal = ''
        if filecontent != "" or filecontent.find("Errors: (Heats will not be built while errors present)") > -1:
            self.event.background_color = [.5, 0, 0, 1]  # red
            errors[4] = 1
        elif filecontent.find("Warnings: (Heats can be built while warnings present)") > -1:
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
