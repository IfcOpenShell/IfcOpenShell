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
class DateError:
    pass

class DateErrorParsing(DateError):
    def __init__(self):
        self.type = "syntax"
        self.msg = "(syntax error)"

class DateErrorContent(DateError):
    def __init__(self):
        self.type = "content"
        self.msg = "(content error)"

def parse_datetime(datetime_value):
    try:
        tree = parser.parse(datetime_value)
        transformer = DatetimeTransformer()
        parsed_datetime = transformer.transform(tree)
        return {"status": 1, "msg": parsed_datetime}
    except Exception:
        return DateErrorParsing()


def validate_datetime(parsed_datetime):
    if parsed_datetime["year"] == 0:
        yield DateErrorContent()

    # Month
    if not (parsed_datetime["month"] > 0 and parsed_datetime["month"] < 13):
        yield DateErrorContent()

    # Day
    if not (parsed_datetime["day"] > 0 and parsed_datetime["day"] < 32):
        yield DateErrorContent()

    # Check February and Leap year case
    if parsed_datetime["month"] == 2:
        if int(parsed_datetime["year"]) % 4 == 0:
            if not (parsed_datetime["day"] < 30):
                yield DateErrorContent()
        else:
            if not (parsed_datetime["day"] < 29):
                yield DateErrorContent()

    # Hour
    if not (parsed_datetime["hour"] > -1 and parsed_datetime["hour"] < 24):
        yield DateErrorContent()
    # Minute
    if not (parsed_datetime["minute"] > -1 and parsed_datetime["minute"] < 60):
        yield DateErrorContent()
    # Second
    if not (parsed_datetime["second"] > -1 and parsed_datetime["second"] < 60):
        yield DateErrorContent()
