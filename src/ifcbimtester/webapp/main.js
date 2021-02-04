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
