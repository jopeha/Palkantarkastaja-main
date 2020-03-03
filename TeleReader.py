from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import calendar
import datetime
import os
import json


class BaseReader:

    def __init__(self,headless=False,url="",x=0,y=0,width=1920,height=1080):
        options=Options()
        if headless:
            options.add_argument("-headless")
        self.driver = webdriver.Firefox(firefox_options=options)
        self.url=url
        self.driver.get(url)
        self.driver.set_window_rect(x=x, y=y, width=width, height=height)

    def quit(self):
        self.driver.quit()

class TeleReader(BaseReader):

    months = ["January", "February", "March",
                   "April", "May", "June",
                   "July", "August", "September",
                   "October", "November", "December"]

    months_short = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    timeout=10
    def __init__(self,year,month,headless=False):

        self.fill_amount=0
        self.fill_pos=0
        self._alive=False
        BaseReader.__init__(self,
                            headless=headless,
                            url='teleopti/mytime/path',
                            width=1920,
                            x=0,
                            y=0
                            )

        for _ in range(3):
                try:
                    WebDriverWait(self.driver,self.timeout).until(EC.visibility_of_element_located((By.XPATH,"/html/body/div/div[1]/div[2]/div/div[3]/div/div/form/a[2]")))
                    break
                except TimeoutError:
                    self.driver.get(self.url)


        self.driver.find_element_by_xpath("/html/body/div/div[1]/div[2]/div/div[3]/div/div/form/a[2]").click()

        self.wait_for_element("//*[@id='Username-input']")
        self.driver.find_element_by_xpath("//*[@id='Username-input']").send_keys("username")
        self.driver.find_element_by_xpath('//*[@id="Password-input"]').send_keys("password")
        self.driver.find_element_by_xpath('//*[@id="Signin-button"]').click()
        self.time=datetime.datetime(year=year,month=month,day=1)
        self._alive=True
    @property
    def timestring(self):
        return self._datetime.strftime("%d.%m.-%y")

    @property
    def time(self):
        return self._datetime

    def wait_for_element(self,XPATH):
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(
                (By.XPATH, XPATH)))

        except TimeoutError:
            pass
    def wait_for_element_by_class(self,CLASS_NAME):
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(
                (By.CLASS_NAME, CLASS_NAME)))

        except TimeoutError:
            pass
    @time.setter
    def time(self,DATETIME):
        self._datetime=DATETIME
        self.wait_for_element("/html/body/section/article/div/div[2]/div[2]/div[3]/div[3]/div[5]/div/div[5]")
        self.driver.find_element_by_xpath('/html/body/section/article/div/div[1]/div/ul/li[1]/span/span[2]/button[1]').click()
        self.wait_for_element('/html/body/div[4]/div[1]/table/thead/tr[1]/th[2]')
        self.driver.find_element_by_xpath('/html/body/div[4]/div[1]/table/thead/tr[1]/th[2]').click()
        self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/thead/tr/th[2]').click()
        year = DATETIME.year
        month = DATETIME.month
        day = DATETIME.day

        year = str(year)
        month = self.months_short[month - 1].capitalize()
        day = str(day)

        elements = self.driver.find_elements_by_class_name("year")
        for i in elements:
            if i.text == year:
                i.click()
                break

        elements = self.driver.find_elements_by_class_name("month")

        for i in elements:
            if i.text == month:
                i.click()
                break

        old_elements = self.driver.find_elements_by_class_name("old")
        new_elements = self.driver.find_elements_by_class_name("new")
        elements = self.driver.find_elements_by_class_name("day")
        for i in old_elements + new_elements:
            if i in elements:
                elements.remove(i)

        for i in elements:
            if i.text == day:

                i.click()
                break
        else:
            raise Exception


    def read(self):

        def read_weeks(starting_location):
            self.wait_for_element_by_class("weekview-day-schedule-layer")

            d = driver.find_elements_by_class_name("weekview-day-dayofmonth")
            locations_to_days = {}
            for i in d:
                if i.location["x"] >= starting_location:
                    locations_to_days[i.location["x"] + i.size["width"]] = i.text
                    days[i.text] = []
                    if days_in_month==int(i.text):
                        break
            elements = driver.find_elements_by_class_name("weekview-day-schedule-layer")
            timeline=driver.find_element_by_class_name("weekview-timeline")
            timeline_images.append((timeline.screenshot_as_png,timeline.location["y"]))

            for day_pos in locations_to_days:

                for box in driver.find_elements_by_class_name("weekview-day-schedule"):
                    if abs(day_pos - box.location["x"]+box.size["width"]) < 10:
                        day_box_images[locations_to_days[day_pos]]=(box.screenshot_as_png,box.location["y"])
                for ele in elements:
                    ele_pos = ele.location["x"] + ele.size["width"]

                    if abs(day_pos - ele_pos) < 10:

                        if len(ele.text.split("\n"))==2:
                            days[locations_to_days[day_pos]].append(ele.text)
                            continue

                        style=ele.get_attribute("style").split(";")[0:-1]

                        style=[i.split(":") for i in style]

                        style=dict([(i[0].strip(),i[1].strip()) for i in style])

                        color=style["background-color"].replace("rgb(","").replace(")","")
                        color=[int(i) for i in color.split(",")]

                        coffee_break_red=[255,0,0]
                        lunch_break_yellow=[255,255,0]

                        if color == coffee_break_red:
                            days[locations_to_days[day_pos]].append("Tauko")
                        elif color== lunch_break_yellow:
                            days[locations_to_days[day_pos]].append("Ruokatauko")
                        else:
                            action = ActionChains(driver)
                            action.move_to_element(ele).perform()
                            action.move_to_element(ele).perform()

                            tip=driver.find_element_by_class_name("tooltip").text

                            days[locations_to_days[day_pos]].append(tip)

                if days_in_month == int(locations_to_days[day_pos]):

                    break
            else:
                driver.find_element_by_xpath('//*[@id="btnNextWeek"]').click()
                read_weeks(0)

        self.wait_for_element_by_class("weekview-day-month")
        driver=self.driver
        months = driver.find_elements_by_class_name("weekview-day-month")
        print(self.months[self.time.month - 1])
        for i in months:
            print(i.text)
            if i.text == self.months[self.time.month-1]:
                starting_location=i.location["x"]
                break
        else:
            print("starting day not found")
            input()

        days = {}
        day_box_images = {}
        timeline_images =[]

        days_in_month=calendar.monthrange(self.time.year, self.time.month)[1]

        read_weeks(starting_location)

        dayson=[]

        month = self.time.month
        year = self.time.year

        for day in days:

            d={"day":[int(day),month,year],
               "elements":days[day]}

            dayson.append(d)

        if not os.path.exists("Telereader"):
            os.makedirs("Telereader")
        with open(f"Telereader/{len(os.listdir('Telereader'))}-{month}-{year}.json","w") as file:
            json.dump(dayson,file)


reader=TeleReader(2019,1)###,headless=True)
reader.read()
print("Reddie")
reader.quit()
