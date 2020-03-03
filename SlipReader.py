"""Lukija staffpointin pdf palkkalapuille"""

import tabula
import pprint
import json
import os
import datetime


pprint=pprint.pprint


class WorkElement:
    r = [
        ("02 ", "02"),
        ("KIKY ", "KIKY-"),
        ("yölisä ", "yölisä-"),
        ("ilisä ", "ilisä-"),
        ("alisä ", "alisä-"),
        ("lisät ", "lisät-"),
        (" 100%", "-100%"),
        ("juhlapyhäkorotus ", "juhlapyhäkorotus"),
        (" (", "("),
        (" /", "/"),
        ("Bonus henk.koht.","Bonus-henk.koht"),
        ("Sunnuntaityö ", "Sunnuntaityö")
    ]

    def __init__(self,name,data1):

        for i in self.r:
            name=name.replace(*i)

        namelist=name.split(" ")

        if len(namelist)==4:
            namelist.append("00.00")
        elif len(namelist)<4:
            namelist+=["None","None","None","None"]
        self.name,self.date,self.start_time,_,self.end_time,*_=namelist

        try:
            self.time=float(data1["Aika/Määrä  Tid/Antal"].replace(",","."))
        except:
            print(self.__dict__)
            print(name)
            print(data1)
            input()
        self.hourly_wage=float(data1["A-hinta  A-pris"].replace(",","."))
        self.total_wage=float(data1["Euro"].replace(",","."))
        self.name2=data1["Palkkalaji  Löneslag"]
        self.type="work"

class LoadedElement(WorkElement):

    def __init__(self,base):

        self.__dict__.update(base)

        if hasattr(self,"date"):
            if self.date=="" or self.date=="None":
                self.date="None"
        else:
            self.date="None"


        self.calculated_total_wage=self.time*self.hourly_wage

class SpecialElement(WorkElement):

    def __init__(self,data):
        self.name=data["Palkkalaji  Löneslag"]

        if data["Euro"].__class__.__name__=="float":
            data["Euro"]="0"
        self.total_wage=float(data["Euro"].replace(",","."))

        self.time=0
        self.type="special"
        self.hourly_wage=0

class WorkDay:

    def __init__(self,elements,date):
        self.elements=elements
        self.date=str(date)


        if date=="None":
            self.datetime=datetime.datetime(1,1,1)
        else:

            if len(date.split("."))<3:
                time=1,1,1
            else:
                try:
                    time=list(reversed([int(i) for i in date.split(".")]))
                except:
                    print("date not found - ",date)
                    input()
            self.datetime=datetime.datetime(*time)

        element_names=[i.name2 for i in self.elements]
        print("WORKDAY:")
        print(element_names)
        if any("Sairasloma" in i for i in element_names):
            if any("Tuntipalkka" in i for i in element_names):
                self.work_type="SickWork"
            else:
                self.work_type="Sick"
        elif any("Tuntipalkka" in i for i in element_names):
            self.work_type="Work"

        elif all(element_names[0]==i for i in element_names):
            self.work_type=element_names[0]
        else:
            self.work_type="Other"


        self.total_wage=sum(i.total_wage for i in elements)

        tp=list(filter(lambda a: "Tuntipalkka" in a.name2 or "Sairasloma" in a.name2,self.elements))

        self.total_hours=sum(i.time for i in tp)
        t = datetime.time
        if len(tp)!=0:

            st=[[int(a[0]),int(a[1])] for a in (i.start_time.split(".") for i in tp)]
            et=[[int(a[0]),int(a[1])] for a in (i.end_time.split(".") for i in tp)]

            self.start_time=min(t(*i) for i in st)
            self.end_time=max(t(*i) for i in et)
        else:
            self.start_time,self.end_time=t(0,0),t(0,0)

    def __repr__(self):
        _wd=["mon","tue","wed","thu","fri","sat","sun"]
        text=f"Day: {_wd[self.datetime.weekday()]} {self.date}  Total wage: {self.total_wage:.2f} Hours: {self.total_hours} At: {self.start_time.hour}:{self.start_time.minute:02d}-{self.end_time.hour}:{self.end_time.minute:02d}"

        return text

    def print_all(self):
        text=self.__repr__()

        for i in self.elements:
            text+="\n  "
            text+=f"{i.name} - time:{i.time} - hourly wage:{i.hourly_wage} - total wage:{i.total_wage}"

        print(text)

def get_page(page,first):

    end=int(len(page.index))-1

    elements=[]
    if first:
        toprow=dict(page.iloc[0])
    else:
        toprow=None

    i=1 if first else 0
    while True:
        if i>end:
            break

        print(i, "/", end)

        row1 = dict(page.iloc[i])
        print(row1)
        if "KIKY" in row1["Palkkalaji  Löneslag"]:
            elements.append(SpecialElement(row1).__dict__)
            i+=1
            print("KIKY")
            continue
        if "Loma" in row1["Palkkalaji  Löneslag"]:
            elements.append(SpecialElement(row1).__dict__)
            i+=1
            print("LOMA")
            continue

        if "901 " in row1["Palkkalaji  Löneslag"]:
            elements.append(SpecialElement(dict(page.iloc[i])).__dict__)
            elements.append(SpecialElement(dict(page.iloc[i + 1])).__dict__)
            elements.append(SpecialElement(dict(page.iloc[i + 2])).__dict__)
            print("END")
            i += 3
            continue
        if "902 " in row1["Palkkalaji  Löneslag"]:
            elements.append(SpecialElement(dict(page.iloc[i])).__dict__)
            elements.append(SpecialElement(dict(page.iloc[i + 1])).__dict__)
            print("END")
            i += 2
            continue

        try:
            row2_name = dict(page.iloc[i+1])["Palkkalaji  Löneslag"]
        except:
            print(row1)

        element=WorkElement(row2_name,row1)
        if len(element.date.split("."))==2 or len(element.date.split("."))==3 and element.date.split(".")[2]=="":
            print(element.date)
            t=0
            while True:
                t+=1
                print(f"No year, trying from behind {t}/100",)
                try:
                    year=elements[-t]["date"].split(".")[2]
                    break
                except:
                    if t==100:
                        year="1"
                        break

            if len(element.date.split(".")) == 3 and element.date.split(".")[2] == "":
                element.date+=year
            else:
                element.date+="."+year

        elements.append(element.__dict__)
        i+=2

    return elements, toprow


def _read_pdf(name,columns=None):

    print(f"Reading: {name}")

    def count_pdf_pages():
        cmd = f'pdfinfo {name}' + " | grep 'Pages' | awk '{print $2}'"
        return int(os.popen(cmd).read().strip())
    rows=[]
    for i in range(count_pdf_pages()):

        print("page -- ",i+1,"of", name)


        area=[270,0,490,575] if i+1==count_pdf_pages() else [270,0,795,575]
        if columns:
            page= tabula.read_pdf(name,area=area,pages=i+1,columns=columns)
        else:
            page = tabula.read_pdf(name,area=area,pages=i+1)
        data,top=get_page(page,i==0)

        if top:rows+=[top]
        rows+=data

    just_name=os.path.basename(name).split(".")[0]

    print(just_name)
    with open(f"palkat/elementit/{just_name}.json","w") as file:
        json.dump(rows,file)

    return f"palkat/elementit/{just_name}.json"

class Analyzer:

    def __init__(self):

        self.loaded_elements=[]
        self.top_row={}
        self.work_days=[]
        self.total_wage=0
        self.total_wage_hourly=0
        self.total_hours=0
        self.average_hourly_wage=0
        self.special_elements=[]


    def load(self, preset_choice=None,file=None):

        def load(name):
            with open(name) as file:
                data=json.load(file)
                self.top_row=data.pop(0)
                a=0
                for i in data:
                    #print(a)
                    #print(i)
                    a+=1
                    self.loaded_elements.append(LoadedElement(i))

        if file is not None:
            load(file)
        else:
            files=os.listdir("palkat/elementit")
            files=sorted(files)
            if len(files)==1:
                print("Loading ",files[0])
                choice=0
            else:
                for pos,i in enumerate(files):
                    print(f"#{pos}: {i}")
                choice=preset_choice if preset_choice != None else input("\nEnter a number corresponding to a file or 'A' to load all. 'X' to exit").upper()

            if choice=="A":
                for i in files:
                    load(i)
            elif choice=="X":
                return False
            else:
                load(f"palkat/elementit/{files[int(choice)]}")

        print("I'm loaded.")

        return True

    def lyze(self):

        elements_by_days={}
        specials=[]
        D=set()
        for i in self.loaded_elements:
            if i.type=="work":
                D.add(i.date)

        for i in D:
            elements_by_days[i]=[]

        for i in self.loaded_elements:
            if i.type == "work":
                elements_by_days[i.date].append(i)
            else:
                specials.append(i)

        self.special_elements=specials

        for day in elements_by_days:
            self.work_days.append(WorkDay(elements_by_days[day],day))

        self.total_wage=sum(i.total_wage for i in self.loaded_elements)
        self.daily_total_wage=sum(i.total_wage for i in self.work_days)

        self.total_wage_hourly=sum(i.calculated_total_wage for i in self.loaded_elements)
        self.total_hours=sum(i.total_hours for i in self.work_days)

        self.average_hourly_wage_net=self.total_wage/self.total_hours
        self.average_hourly_wage=self.total_wage_hourly/self.total_hours

        self.work_days=[*sorted(self.work_days,key=lambda a:a.datetime)]

        months=[i.datetime.month for i in self.work_days]
        years=[i.datetime.year for i in self.work_days]
        self.month=[*sorted(months,key=lambda a:months.count(a))][-1]
        self.year=[*sorted(years,key=lambda a:years.count(a))][-1]


    def print(self):
        print(len(self.work_days))

        days=sorted(self.work_days,key=lambda a : a.datetime)
        _wd=["mon","tue","wed","thu","fri","sat","sun"]

        for pos,i in enumerate(days):
            print(f"#{pos}-Day: {_wd[i.datetime.weekday()]} {i.date}  Total wage: {i.total_wage:.2f} Hours: {i.total_hours} At: {i.start_time.hour}:{i.start_time.minute:02d}-{i.end_time.hour}:{i.end_time.minute:02d} ")

        print("Other elements:")
        good,bad=[],[]
        for i in self.special_elements:
            if i.total_wage!=0:
                good.append(f"{i.name} Wage: {i.total_wage}")
            else:
                bad.append(f"{i.name} Wage: {i.total_wage}")
        for i in good:
            print(i)

        print(f"Total wage from all totals: {self.total_wage:.2f}")
        print(f"Total wage from hourly wages: {self.total_wage_hourly:.2f}")#+sum(i.total_wage for i in self.loaded_elements[-3:]):.2f}")
        print(f"Total wage from daily totals: {self.daily_total_wage:.2f}")
        print(f"Work hours: {self.total_hours}")
        print(f"Average hourly wage: {self.average_hourly_wage:.2f}")
        print(f"Average real hourly wage: {self.average_hourly_wage_net:.2f}")
        print("\nTotal wage as on strip:")
        print(self.top_row["Palkkalaji  Löneslag"],"-",self.top_row["Euro"])
        print(f"full wage {sum(i.total_wage for i in self.loaded_elements):.2f}")
        print()
        while True:
            day=input("Input number corresponding to the day you wish to examine or 'A' to expand all days 'X' to exit.").upper()
            if day=="X":
                break
            if day=="A":
                for i in days:
                    i.print_all()
            elif day=="E":
                for i in self.loaded_elements:
                    print(i.__dict__)
            elif day=="BAD":
                for i in bad:
                    print(i)
            else:
                try:
                    day=int(day)
                except:
                    exit(f"input must be int or 'A'. Input was {day}")
                days[day].print_all()

def analyze(file):
    a=Analyzer()
    if a.load(file=file):
        a.lyze()
        return a
    return False

def read_pdf(name):

    l=[
        [46,305,390,477],
        [36,294,379.5,466.5]
    ]
    for i in l:
        try:
            return _read_pdf(name,columns=i)
        except:
            pass
    print("Column things failed. trying without set columns")
    return _read_pdf(name)



funcs={"load_pdf":read_pdf,
       "load_json":analyze}

"""
Read_from_pdf=False
Analyze=True

if Read_from_pdf:
    for self in os.listdir("pdf"):
        read_pdf("pdf/" + self)
if Analyze:
    while True:
        Analyze = Analyzer()
        if not Analyze.load():
            break
        Analyze.lyze()"""


