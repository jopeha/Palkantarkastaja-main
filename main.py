from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.widget import Widget
import os
from functools import partial
from SlipReader import funcs
from kivy.animation import Animation
import calendar
from datetime import date


class TopMenuScreen(Screen):

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        print(filename,"NAM")
        full_path=os.path.join(filename[0])
        json_path=funcs["load_pdf"](full_path)
        analyzer=funcs["load_json"](json_path)
        AS=AnalyzerScreen(analyzer)
        self.manager.switch_to(AS)
        self.manager.top_menu=self




        self.dismiss_popup()

    def exit(self,*_):
        quit()

class AnalyzerButtons(BoxLayout):
    pass

class AnalyzerScreen(Screen):

    def __init__(self,analyzer):
        super().__init__()
        self.month_name=""
        self.mainbox=BoxLayout(padding=100,orientation='vertical',spacing=20)
        self.analyzer=Analyzer()
        self.analyzer.load(analyzer)
        self.mainbox.add_widget(Label(text=self.analyzer.month_name,size_hint_y=None,height=30, color=(.2,.5,.2,1),font_size=50))
        self.mainbox.add_widget(self.analyzer)

        self.buttons=AnalyzerButtons()
        self.mainbox.add_widget(self.buttons)
        self.buttons.next=partial(self.next_button,self)
        self.buttons.previous=partial(self.previous_button,self)
        self.buttons.exit=partial(self.exit_button,self)

        self.add_widget(self.mainbox)

    def click(self,workday):
        if isinstance(workday,int):
            pass
        else:
            content=DayView()
            content.load(workday)
            self._popup=Popup(title=workday.date,
                              content=content,
                              title_color=(0.3,.7,.3,1),
                              title_size=40,
                              separator_color=(1,1,1,0),
                              size_hint=(0.9, 0.9),
                              background_color=(.9,.9,.9,1),
                              background=""
                              )
            content.dismiss=self._popup.dismiss

            self._popup.open()

    def next_button(self,*args):
        pass
    def previous_button(self,*args):
        pass
    def exit_button(self,*args):
        self.manager.switch_to(self.manager.top_menu)
        del self



class Analyzer(GridLayout):

    def load(self,analyzer):
        weekdays=["Ma","Ti","Ke","To","Pe","La","Su"]
        for i in range(7):
            self.add_widget(Label(text=weekdays[i],height=30,size_hint_y=None))#,color=(.2,.5,.2,1)))

        year=analyzer.year
        month=analyzer.month
        self.month_name=["Tammikuu","Helmikuu","Maaliskuu","Huhtikuu","Toukokuu","Kesäkuu","Heinäkuu","Elokuu",
                         "Syyskuu","Lokakuu","Marraskuu","Joulukuu"][month-1]
        weekskip=date(year,month,1).weekday()

        if month==1:
            pastmonth=12
            pastyear=year-1
        else:
            pastmonth=month-1
            pastyear=year

        for i in range(weekskip):
            self.add_widget(Widget())

        included=[]

        for day in range(calendar.monthrange(year,month)[1]):
            for workday in analyzer.work_days:
                if workday.datetime.date()==date(year,month,day+1):
                    self.add_widget(MonthViewWorkDay(workday))
                    included.append(workday)
                    break
            else:
                self.add_widget(MonthViewWorkDay(day+1))

        for _ in range(6-date(year,month,calendar.monthrange(year,month)[1]).weekday()):
            self.add_widget(Label())

        if len(included)<len(analyzer.work_days):
            for _ in range(3):
                self.add_widget(Label(height=30,size_hint_y=None))
            self.add_widget(Label(text="Muut Lisät:",height=30,size_hint_y=None,font_size=30))#,color=(.2,.5,.2,1)))
            for _ in range(3):
                self.add_widget(Label(height=30,size_hint_y=None))

            for day in analyzer.work_days:
                if day not in included:
                    self.add_widget(MonthViewWorkDay(day,other=True))



class MonthViewWorkDay(Button):

    def __init__(self,workday,past=False,other=False):
        super().__init__()
        self.workday=workday
        if isinstance(workday,int):
            if past:
                self.work_type="Past"
            else:
                self.work_type="None"
            self.day=str(workday)
            self.data=self.work_type
        elif other:
            self.day=f"{workday.datetime.date():%d.%m}"
            self.data = f"{workday.start_time:%H:%M}-{workday.end_time:%H:%M}\n" \
                        f"{workday.total_hours}h\n" \
                        f"palkka: {workday.total_wage:.2f}"
            self.work_type=workday.work_type

        else:
            self.day = f"{workday.datetime.day}"
            self.data = f"{workday.start_time:%H:%M}-{workday.end_time:%H:%M}\n" \
                        f"{workday.total_hours}h\n" \
                        f"palkka: {workday.total_wage:.2f}"
            self.work_type=workday.work_type



    @property
    def work_type(self):
        return self._work_type

    @work_type.setter
    def work_type(self,value):
        self._work_type=value
        if value=="Past":
            self.background_color=(.75,.75,.7,1)
        elif value=="Work":
            self.background_color=(.3,.7,.3,1)
        elif value=="None":
            self.background_color=(.65,.65,.65,1)
        elif value=="Sick":
            self.background_color=(.7,.3,.7,1)
        elif value == "SickWork":
            self.background_color = (.7, .6, .6, 1)
        else:
            self.background_color = (.3, .3, 7, 1)
            self.data=f"{self.work_type}\nPalkka: {self.workday.total_wage}"


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class DayView(BoxLayout):
    orientation = "vertical"
    def load(self,workday):

        elements=sorted(workday.elements,key=lambda a: a.start_time)

        time_range=min(i.start_time for i in workday.elements),max(i.end_time for i in workday.elements)

        for element in elements:
            self.add_widget(DayViewElement(element))

        self.add_widget(DayPopExit())

class DayPopExit(Button):
    pass

class DayViewElement(Button):

    def __init__(self,element):
        super().__init__()
        name1=element.name
        name2=element.name2
        hourly_wage=element.hourly_wage
        total_wage=element.total_wage
        time=element.time
        st=element.start_time
        et=element.end_time
        self.size_hint_y=.1
        self.text=f"{name1} --" \
                  f"{name2}  :  " \
                  f"{st} - {et}, " \
                  f"{time}h - tuntipalkka {hourly_wage}€ - " \
                  f"palkka {total_wage}"
        if "Tuntipalkka" in name2:
            self.background_color=(.3,.7,.3,1)
        elif "Sairasloma" in name2:
            self.background_color=(.7,.3,.7,1)
        else:
            self.background_color=(.3,.3,.7,1)

class SlipCheckerApp(App):

    def build(self):

        self.sm=ScreenManager()
        self.sm.add_widget(TopMenuScreen())

        return self.sm


SlipCheckerApp().run()