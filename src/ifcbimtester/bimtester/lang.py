import gettext

translation = None

def _(message):
    if translation:
        return translation(message)
    return message


def switch_locale(locale_dir, locale_id):
    global translation
    domain = "messages"
    # https://docs.python.org/3/library/gettext.html
    mo_file = gettext.find(domain, localedir=locale_dir, languages=[locale_id])
    if mo_file is not None:
        print(
            "Locale will be switched to language '{}'. Translation file found {}"
            .format(locale_id, mo_file)
        )
        newlang = gettext.translation(domain, localedir=locale_dir, languages=[locale_id])
        newlang.install()
        translation = newlang.gettext
    else:
        print(
            "Locale can not be switched to '{}'. Translation file (*.mo) not found in {}"
            .format(locale_id, locale_dir)
        )
