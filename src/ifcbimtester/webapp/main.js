/*
 * BIMTester - OpenBIM Auditing Tool
 * Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
 *
 * This file is part of BIMTester.
 *
 * BIMTester is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * BIMTester is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Hacky mockup */
let elements = document.getElementsByTagName('input');
for (let i=0; i<elements.length; i++) {
    console.log(elements[i]);
    elements[i].addEventListener('click', function() {
        let input = this;
        console.log(input);
        let li = input.parentNode.parentNode.parentNode.parentNode;
        if (input.checked) {
            li.classList.remove('excluded');
        } else {
            li.classList.add('excluded');
        }
    });
}
