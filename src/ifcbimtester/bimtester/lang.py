# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

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
        print("Locale will be switched to language '{}'. Translation file found {}".format(locale_id, mo_file))
        newlang = gettext.translation(domain, localedir=locale_dir, languages=[locale_id])
        newlang.install()
        translation = newlang.gettext
    else:
        print(
            "Locale can not be switched to '{}'. Translation file (*.mo) not found in {}".format(locale_id, locale_dir)
        )
