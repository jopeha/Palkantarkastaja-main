from datetime import timedelta,datetime,date
import json


class WageMultiplier:

    def __init__(self, multiplier, days=None, weekdays=None, timeofday=None):

        self.timeofday = timeofday
        self.weekdays = weekdays
        self.multiplier = multiplier
        self.days = days

    def __call__(self, element):

        d=element.day.date

        multip = self.multiplier

        if self.days is not None:
            multip *= (element.day.date in self.days)

        if self.weekdays is not None:
            multip *= (element.day.date.weekday in self.weekdays)

        if self.timeofday is not None:
            start, end = (d+timedelta(hours=i[0],minutes=i[1]) for i in self.timeofday)
            if start <= element.start < element.end <= end:
                multip *= 1
            elif start <= element.start <= end <= element.end:
                multip *= (element.time - ((element.end - end) / timedelta(hours=1))) / element.time
            elif element.start <= start <= element.end <= end:
                multip *= (element.time - ((element.start - start) / timedelta(hours=1))) / element.time
            elif element.start <= start <= end <= element.end:
                mt = (end - start) / timedelta(hours=1)
                multip *= mt / element.time
            else:
                multip *= 0

        return multip


class TeleElement:

    unpaid=[
        "Ruokatauko",
        "Sairasvapaa"
    ]

    def __init__(self,string,day):
        self.wage=0

        self.day=day
        if string=="Tauko":
            self.name=string
            self.time=.25
            self.start,self.end=day.date,day.date
        elif string=="Ruokatauko":
            self.name=string
            self.time=.5
            self.start, self.end = day.date,day.date
        else:
            self.name,t=string.split("\n")
            s,e=t.split("+")[0].split("-")
            if e.strip().rstrip()=="0:00":
                e="24:00"
            sh,sm=(int(i) for i in s.split(":"))
            eh,em=(int(i) for i in e.split(":"))
            self.start=day.date+timedelta(hours=sh,minutes=sm)
            self.end=day.date+timedelta(hours=eh,minutes=em)
            self.time=(self.end-self.start)/timedelta(hours=1)

        if self.name in self.unpaid:
            self.paid=False
        else:
            self.paid=True





class TeleDay:

    holidays=[date(*reversed(i)) for i in [
        (1,1,2019),
        (6,1,2019),
        (19,4,2019),
        (22,4,2019),
        (1,5,2019),
        (12,5,2019),
        (30,5,2019),
        (9,6,2019),
        (21,6,2019),
        (2,11,2019),
        (6,12,2019),
        (24,12,2019),
    ]]
    great_holidays=[date(*reversed(i)) for i in [
        (25, 12, 2019),
        (26, 12, 2019)
    ]]

    multipliers=[


        # Suurjuhlapyhäkorvaukset
         [
             WageMultiplier(2, days=great_holidays),
             WageMultiplier(2, days=[i - timedelta(days=1) for i in great_holidays],  # aikaisemmasta päivästä 1800
                            timeofday=((18, 0), (24, 0))),  # alkaen maksettava korvaus
             WageMultiplier(.45, days=great_holidays,
                            timeofday=((18, 0), (22, 00))),  # iltakorvaus
             WageMultiplier(.45, days=[i - timedelta(days=1) for i in great_holidays],  # iltakorvaus aiemmalta illalta
                            timeofday=((18, 0), (22, 00))),
             WageMultiplier(.9, days=great_holidays, timeofday=((0, 0), (6, 00))),  # yökorvaus aamulta
             WageMultiplier(.9, days=great_holidays, timeofday=((22, 0), (24, 00))),  # yökorvaus yöltä
             WageMultiplier(.9, days=[i - timedelta(days=1) for i in great_holidays],  # iltakorvaus aiemmalta illalta
                            timeofday=((22, 0), (24, 00)))
         ],
        # Sunnuntaikorvaukset
        [
            WageMultiplier(1, weekdays=[6]), # Sunnuntaikorvaus
            WageMultiplier(1,weekdays=[5],timeofday=((18,0),(24,0))), # Lauantaista 1800 alkaen maksettava sunnuntaikorvaus
            WageMultiplier(.3, weekdays=[6], timeofday=((18, 0), (22, 00))), # sunnuntai-iltakorvaus
            WageMultiplier(.3, weekdays=[5], timeofday=((18, 0), (22, 00))), #sunnuntai-iltakorvaus lauantai-illasta
            WageMultiplier(.6, weekdays=[6], timeofday=((0, 0), (6, 00))), #sunnuntaiyökorvaus-aamu
            WageMultiplier(.6, weekdays=[6], timeofday=((22, 0), (24, 00))), #sunnuntaiyökorvaus-ilta
            WageMultiplier(.6, weekdays=[5], timeofday=((22, 0), (24, 00))) #yökorvaus lauantai-illalta
        ],
        #Pyhäkorvaukset
        [
            WageMultiplier(1, days=holidays),
            WageMultiplier(1, days=[i-timedelta(days=1) for i in holidays], #aikaisemmasta päivästä 1800
                           timeofday=((18, 0), (24, 0))),                   #alkaen maksettava korvaus
            WageMultiplier(.3, days=[i for i in holidays],
                           timeofday=((18, 0), (22, 00))),  #iltakorvaus
            WageMultiplier(.3, days=[i-timedelta(days=1) for i in holidays], #iltakorvaus aiemmalta illalta
                           timeofday=((18, 0), (22, 00))),
            WageMultiplier(.6, days=[i for i in holidays], timeofday=((0, 0), (6, 00))),  #yökorvaus aamulta
            WageMultiplier(.6, days=[i for i in holidays], timeofday=((22, 0), (24, 00))),  # yökorvaus yöltä
            WageMultiplier(.6, days=[i-timedelta(days=1) for i in holidays], # iltakorvaus aiemmalta illalta
                           timeofday=((22, 0), (24, 00)))
        ],

        #Tavalliset ilta- ja yökorvaukset
        [
            WageMultiplier(.15,timeofday=((18,00),(22,00))), #Ilta
            WageMultiplier(.3,timeofday=((22,00),(24,00))), #yö
            WageMultiplier(.3,timeofday=((00,00),(6,00)))   #aamuyö

        ],

    ]

    def __init__(self,base_dict):

        d,m,y=base_dict["day"]
        self.date=datetime(year=y,month=m,day=int(d))
        self.elements=[TeleElement(i,self) for i in base_dict["elements"]]

        if self.elements:

            self.time=sum(i.time for i in self.elements)
            self.start=min(i.start for i in self.elements)
            self.end=max(i.end for i in self.elements)

            self.count_wages(12.05,None)

        else:
            self.time=0
            self.start=0
            self.end=0


    def count_wages(self,hourly,bonuses):
        for element in self.elements:
            if element.paid:
                for category in self.multipliers:
                    multiplier = sum(i(element) for i in category)
                    if multiplier!=0:
                        break
                element.wage=hourly*element.time*(1+multiplier)
                if element.wage<0:
                    print("_----------_")
                    print(element.wage)
                    print(element.day.date)
                    print(element.time)
                    print(multiplier)

    @property
    def wage(self):
        if self.time==0:
            return 0
        else:
            return sum(i.wage for i in self.elements)



with open("Telereader/2-1-2019.json","r") as file:
    MONTH=json.load(file)

with open("MAINOUTPUT.txt","w") as file:
    lines=[]
    for day in MONTH:
        d=TeleDay(day)
        lines.append(f"{d.date.date()} - {d.wage:.2f}\n")
    file.writelines(lines)
