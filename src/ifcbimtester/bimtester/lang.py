import gettext

translation = None

def _(message):
    if translation:
        return translation(message)
    return message


def switch_locale(locale_dir, locale_id="en"):
    global translation
    newlang = gettext.translation("messages", localedir=locale_dir, languages=[locale_id])
    newlang.install()
    translation = newlang.gettext
