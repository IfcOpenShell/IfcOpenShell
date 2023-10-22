from lark import Lark, Transformer

# Grammar to retrieve the following structure: YYYY-MM-DDThh:mm:ss
grammar = """
 
    datetime_value: year "-" month "-" day "T" hour ":" minute ":" second ["." millisecond]

    hour: DIGIT DIGIT
    minute: DIGIT DIGIT
    second: DIGIT DIGIT
    millisecond: DIGIT DIGIT DIGIT*

    day: DIGIT DIGIT
    month: DIGIT DIGIT
    year: MINUS? DIGIT DIGIT DIGIT DIGIT DIGIT*

    MINUS: "-"
    DIGIT: "0".."9"

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start='datetime_value')


class DatetimeTransformer(Transformer):
    def year(self, items):
        return int(''.join(token.value for token in items))

    def month(self, items):
        return int(''.join(token.value for token in items))

    def month(self, items):
        return int(''.join(token.value for token in items))

    def day(self, items):
        return int(''.join(token.value for token in items))

    def hour(self, items):
        return int(''.join(token.value for token in items))

    def minute(self, items):
        return int(''.join(token.value for token in items))

    def second(self, items):
        return ''.join(token.value for token in items)

    def millisecond(self, items):
        if items:
            return ''.join(token.value for token in items)
        else:
            return None

    def datetime_value(self, items):

        year, month, day, hour, minute, second, millisecond = items
        
        return {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": float(second + f".{millisecond if millisecond else ''}")
        }


def parse_datetime(datetime_value):
    try:
        tree = parser.parse(datetime_value)
        transformer = DatetimeTransformer()
        parsed_datetime = transformer.transform(tree)
        return {"status": 1, "msg": parsed_datetime}
    except Exception as e:
        return {"status": -1, "msg": e}


def validate_datetime(parsed_datetime):
    if parsed_datetime == -1:
        return "Syntax error"
    else:
        # Year
        if parsed_datetime["year"] == "0000":
            return "invalid year value"
   
        # Month
        if not (parsed_datetime["month"] > 0 and parsed_datetime["month"] < 13):
            return "invalid month value"

        # Day
        if not (parsed_datetime["day"] > 0 and parsed_datetime["day"] < 32):
            return "invalid day value"

        # Check February and Leap year case
        if parsed_datetime["month"] == 2:
            if int(parsed_datetime["year"]) % 4 == 0:
                if not (parsed_datetime["day"] < 30):
                    return "invalid day value"
            else:
                if not (parsed_datetime["day"] < 29):
                    return "invalid day value"

        # Hour
        if not (parsed_datetime["hour"] > -1 and parsed_datetime["hour"] < 24):
            return "invalid hour value"

        # Minute
        if not (parsed_datetime["minute"] > -1 and parsed_datetime["minute"] < 60):
            return "invalid minute value"

        # Second
        if not (parsed_datetime["second"] > -1 and parsed_datetime["second"] < 60):
            return "invalid second value"

        return 1


def validate(d):
    parsing = parse_datetime(d)
    if parsing["status"] != -1:
        if validate_datetime(parsing["msg"]) != 1:
            print(validate_datetime(parsing["msg"]))
    else:
        print("syntax error")


if __name__ == '__main__':

    valid = ["2008-12-27T18:00:04",
             "2018-12-27T15:00:04.000054",
             "-2018-12-27T15:00:04.02",
             "0480-08-03T00:00:00",
             "-0480-08-03T00:00:00",
             "-12000-01-02T00:00:00"]

    not_valid = ["2008-12-27_18:00:04",
                 "80-8-03T00:00:00",
                 "0000-8-03T00:00:00",
                 "-2018-26-12T15:04:02"]

    for d in valid:
        validate(d)

    for d in not_valid:
        validate(d)
