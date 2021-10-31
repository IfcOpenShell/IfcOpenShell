"""
This class parses the calendar work pattern and retruns a list
The list returned has a key DayOfWeek which takes a value Sunday to Saturday
for each day as a key there is a list of working times with the format 
{"Start": datetime.time, "Finish": datetime.time}

"""

import re
from datetime import time, datetime



class AstaCalendarWorkPattern:
    def get_keys(self, s):
        regex = r"\<(\".+?\")\>(\w|\d|)+?"

        matches=re.finditer(regex, s)
        matcs = []
        for matchNum, match in enumerate(matches, start=1):
            matcs.append(match.group(1))
        return matcs            
            

    def get_values(self, s):
        rx2 = r"<\"[^<>]+\">"
        data = re.split('<[^<>]+>', s)
        return data

    def __init__(self, string):
        self.string = string
        self.Days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.keys = self.get_keys(string)
        self.values = self.get_values(string)
        self.dict_wp = {}
        self.dict_wp = []
        for d, m in zip(self.values[1:], self.keys):
            splt_data = d.strip().split(",")
            workhours = []
            if len(splt_data)>15:
                print(splt_data)
                st1_1 = datetime.strptime(splt_data[6], "%H%M%S")
                st1_2 = datetime.strptime(splt_data[7], "%H%M%S")
                st = {"Start":time(st1_1.hour, st1_1.minute), "Finish": time(st1_2.hour, st1_2.minute), "ifc": None}
                workhours.append(st)
                st2_1 = datetime.strptime(splt_data[12], "%H%M%S")
                st2_2 = datetime.strptime(splt_data[13], "%H%M%S")
                st2 = {"Start":time(st2_1.hour, st2_1.minute), "Finish": time(st2_2.hour, st2_2.minute), "ifc": None}
                workhours.append(st2)
            
            self.dict_wp.append({'DayOfWeek': m.replace("\"",""),
                                                'WorkTimes': workhours, "ifc": None})
                                                
        for day in self.Days:
            if not len(list(filter(lambda d: d['DayOfWeek']== day , self.dict_wp))) > 0:
                print("MISSING", day)
                self.dict_wp.append({'DayOfWeek': day,
                                     'WorkTimes': [], "ifc": None})
        print("final", self.dict_wp)
                

