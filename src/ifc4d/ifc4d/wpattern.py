"""
This class parses the calendar work pattern and retruns a list
The list returned has a key DayOfWeek which takes a value Sunday to Saturday
for each day as a key there is a list of working times with the format 
{"Start": datetime.time, "Finish": datetime.time}

"""

import re
from datetime import time, datetime
from typing import Any
from ifc4d.common import WorkSlot


class AstaCalendarWorkPattern:
    def get_keys(self, s: str) -> list[str]:
        regex = r"\<(\".+?\")\>(\w|\d|)+?"

        matches = re.finditer(regex, s)
        matcs = []
        for matchNum, match in enumerate(matches, start=1):
            matcs.append(match.group(1))
        return matcs

    def get_values(self, s: str) -> list[str]:
        rx2 = r"<\"[^<>]+\">"  # TODO: unused?
        data = re.split("<[^<>]+>", s)
        return data

    # Used the list of Blender supported languages as a reference.
    # Method to generate names for other language:
    # def get_day_names(lang):
    #     from babel.dates import get_day_names
    #     from babel import Locale
    #     locale = Locale(lang)
    #     return [i.capitalize() for i in get_day_names(locale=locale, width="wide").values()]
    Days = {
        "am": ("እሑድ", "ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ"),
        "ar": ("الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"),
        "be": ("Нядзеля", "Панядзелак", "Аўторак", "Серада", "Чацвер", "Пятніца", "Субота"),
        "bg": ("Неделя", "Понеделник", "Вторник", "Сряда", "Четвъртък", "Петък", "Събота"),
        "ca": ("Diumenge", "Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte"),
        "cs": ("Neděle", "Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota"),
        "da": ("Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"),
        "de": ("Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"),
        "el": ("Κυριακή", "Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο"),
        "en": ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"),
        "eo": ("Dimanĉo", "Lundo", "Mardo", "Merkredo", "Ĵaŭdo", "Vendredo", "Sabato"),
        "es": ("Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"),
        "et": ("Pühapäev", "Esmaspäev", "Teisipäev", "Kolmapäev", "Neljapäev", "Reede", "Laupäev"),
        "eu": ("Igandea", "Astelehena", "Asteartea", "Asteazkena", "Osteguna", "Ostirala", "Larunbata"),
        "fa": ("یکشنبه", "دوشنبه", "سه\u200cشنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"),
        "fi": ("Sunnuntaina", "Maanantaina", "Tiistaina", "Keskiviikkona", "Torstaina", "Perjantaina", "Lauantaina"),
        "fr": ("Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"),
        "ha": ("Lahadi", "Litinin", "Talata", "Laraba", "Alhamis", "Jummaʼa", "Asabar"),
        "he": ("יום ראשון", "יום שני", "יום שלישי", "יום רביעי", "יום חמישי", "יום שישי", "יום שבת"),
        "hi": ("रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"),
        "hr": ("Nedjelja", "Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak", "Subota"),
        "hu": ("Vasárnap", "Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat"),
        "id": ("Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"),
        "it": ("Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"),
        "ja": ("日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"),
        "ka": ("კვირა", "ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი"),
        "kk": ("Жексенбі", "Дүйсенбі", "Сейсенбі", "Сәрсенбі", "Бейсенбі", "Жұма", "Сенбі"),
        "km": ("អាទិត្យ", "ច័ន្ទ", "អង្គារ", "ពុធ", "ព្រហស្បតិ៍", "សុក្រ", "សៅរ៍"),
        "ko": ("일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"),
        "ky": ("Жекшемби", "Дүйшөмбү", "Шейшемби", "Шаршемби", "Бейшемби", "Жума", "Ишемби"),
        "ne": ("आइतबार", "सोमबार", "मङ्गलबार", "बुधबार", "बिहिबार", "शुक्रबार", "शनिबार"),
        "nl": ("Zondag", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag"),
        "pl": ("Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota"),
        "pt": ("Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"),
        "ro": ("Duminică", "Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă"),
        "ru": ("Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"),
        "sk": ("Nedeľa", "Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota"),
        "sl": ("Nedelja", "Ponedeljek", "Torek", "Sreda", "Četrtek", "Petek", "Sobota"),
        "sr": ("Недеља", "Понедељак", "Уторак", "Среда", "Четвртак", "Петак", "Субота"),
        "sv": ("Söndag", "Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag"),
        "sw": ("Jumapili", "Jumatatu", "Jumanne", "Jumatano", "Alhamisi", "Ijumaa", "Jumamosi"),
        "ta": ("ஞாயிறு", "திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி"),
        "th": ("วันอาทิตย์", "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์"),
        "tr": ("Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"),
        "uk": ("Неділя", "Понеділок", "Вівторок", "Середа", "Четвер", "Пʼятниця", "Субота"),
        "ur": ("اتوار", "پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ"),
        "vi": ("Chủ nhật", "Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy"),
    }

    def get_day_names(self, string: str) -> None:
        """Parse day names from string and translate them to English.

        :raises Exception: If language is not yet supported.
        """
        # Parse day names.
        day_names = [day_name.strip('"') for day_name in self.get_keys(string)]
        # Identify language.
        day_names_set = set(day_names)
        for lang in self.Days:
            lang_day_names = self.Days[lang]
            if day_names_set.issubset(lang_day_names):
                en_day_names = self.Days["en"]
                self.lang = lang
                # Translate day names to English.
                self.day_names = [en_day_names[lang_day_names.index(d)] for d in day_names]
                return

        msg = (
            "Could not identify language for work patterns, need to update Days dictionary."
            "Please report it to IfcOpenShell Github issues"
            f"\nDay names provided: {day_names}."
            "\nAvailable languages:"
        )
        for lang in self.Days:
            msg += f"\n - {lang}: {self.Days[lang]}"
        raise Exception(msg)

    lang: str
    day_names: list[str]

    def __init__(self, string: str, work_type_ids: list[int]):
        self.get_day_names(string)
        self.values = self.get_values(string)
        self.dict_wp: list[WorkSlot] = []

        for value, day_name in zip(self.values[1:], self.day_names, strict=True):
            splt_data = value.strip().split(",")
            workhours: list[dict[str, Any]] = []
            if len(splt_data) >= 7:
                number_of_work_slots = splt_data[1]
                for i in range(int(number_of_work_slots)):
                    work_slot_data = splt_data[2 + i * 3 :][:3]
                    work_type_id, start_time, end_time = work_slot_data
                    if int(work_type_id) in work_type_ids:
                        st1_1 = datetime.strptime(start_time.ljust(5, "0"), "%H%M%S")
                        st1_2 = datetime.strptime(end_time.ljust(5, "0"), "%H%M%S")
                        st = {
                            "Start": time(st1_1.hour, st1_1.minute),
                            "Finish": time(st1_2.hour, st1_2.minute),
                            "ifc": None,
                        }
                        workhours.append(st)

            self.dict_wp.append(WorkSlot(DayOfWeek=day_name, WorkTimes=workhours, ifc=None))

        # Add empty work times for missing week days.
        missing_week_days = set(self.Days[self.lang]) - set(self.day_names)
        for day_name in missing_week_days:
            self.dict_wp.append(WorkSlot(DayOfWeek=day_name, WorkTimes=[], ifc=None))
