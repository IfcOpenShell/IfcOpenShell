import ifcopenshell
import ifcopenshell.api
from datetime import time


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"recurrence_type": 'WEEKLY'}
        for key, value in settings.items():
            self.settings[key] = value
    
    def execute(self):
        
        recurrence = self.file.createIfcRecurrencePattern(self.settings['recurrence_type'])
        #recurrence.WeekdayComponent = [self.file.createIfcDayInWeekNumber(1),self.file.createIfcDayInWeekNumber(2)]
        recurrence.TimePeriods = [
            self.file.createIfcTimePeriod(time(8).isoformat(),time(12).isoformat()),
            self.file.createIfcTimePeriod(time(13).isoformat(),time(17).isoformat())
        ]
        return recurrence