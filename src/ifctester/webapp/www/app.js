"use strict";

feather.replace()

var ns = 'http://standards.buildingsmart.org/IDS';
var xs = 'http://www.w3.org/2001/XMLSchema';

class IDSNew extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click(e) {
        var ifcTester = this.closest('ifc-tester');
        var template = ifcTester.getElementsByTagName('template')[0];
        console.log(template);
        ifcTester.appendChild(template.content.cloneNode(true));
        feather.replace();
    }
}

class IDSClose extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click(e) {
        var container = this.closest('ids-container');
        container.parentElement.removeChild(container);
    }
}

class IDSContainer extends HTMLElement {
    connectedCallback() {
        this.filename = 'specifications.ids';
        this.ids = null;
        this.containerId = crypto.randomUUID();
        this.isEditing = true;
    }
}

class IDSInfo extends HTMLElement {
    load(idsElement) {
        this.idsElement = idsElement;
        var idsInfoElements = this.getElementsByTagName('ids-info-element');
        for (var i=0; i<idsInfoElements.length; i++) {
            var name = idsInfoElements[i].attributes['name'].value;
            idsInfoElements[i].load(idsElement, idsElement.getElementsByTagNameNS(ns, name)[0]);
        }
    }
}

class IDSInfoElement extends HTMLElement {
    connectedCallback() {
        this.contentEditable = true;
        this.addEventListener('input', this.input);
        this.addEventListener('blur', this.blur);
        this.defaultValue = this.textContent;
        if (this.defaultValue == 'date()') {
            this.defaultValue = new Date().toISOString().split('T')[0];
            this.textContent = this.defaultValue;
        }
        this.title = this.attributes['name'].value.replace(/^\w/, (c) => c.toUpperCase());
    }

    load(idsParentElement, idsElement) {
        this.idsElement = idsElement;
        this.idsParentElement = idsParentElement;
        if (idsElement) {
            this.textContent = idsElement.textContent;
        }
        this.idsElement ? this.classList.remove('null') : this.classList.add('null');
        this.validate() ? this.classList.remove('error') : this.classList.add('error');
    }

    input(e) {
        if ( ! this.idsElement && this.textContent) {
            this.add();
        }
        this.idsElement ? this.idsElement.textContent = this.textContent : null;
        this.idsElement ? this.classList.remove('null') : this.classList.add('null');
        this.validate() ? this.classList.remove('error') : this.classList.add('error');
    }

    blur(e) {
        if (this.idsElement && ( ! this.textContent)) {
            this.remove();
        }
        if ( ! this.textContent) {
            this.textContent = this.defaultValue;
        }
        this.idsElement ? this.classList.remove('null') : this.classList.add('null');
        this.validate() ? this.classList.remove('error') : this.classList.add('error');
    }

    validate() {
        if (this.attributes['name'].value == 'author') {
            return this.textContent.match(new RegExp('[^@]+@[^\.]+\..+')) != null;
        } else if (this.attributes['name'].value == 'date') {
            return this.textContent.match(new RegExp('[0-9]{4}-[0-9]{2}-[0-9]{2}')) != null;
        }
        return true;
    }

    add() {
        var container = this.closest('ids-container');
        this.idsElement = container.ids.createElementNS(ns, this.attributes["name"].value);
        this.idsElement.textContent = this.textContent;
        this.idsParentElement.appendChild(this.idsElement);
    }

    remove() {
        this.idsParentElement.removeChild(this.idsElement);
        this.idsElement = null;
    }
}

class IDSSpecRemove extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click(e) {
        var specs = this.closest('ids-specs');
        var spec = this.closest('ids-spec');
        specs.idsElement.removeChild(spec.idsElement);
        specs.idsElement.dispatchEvent(new Event('ids-spec-remove'));
    }
}

class IDSSpecMove extends HTMLElement {
    connectedCallback() {
        this.direction = this.attributes['direction'].value;
        this.addEventListener('click', this.click);
    }

    load(idsElement) {
        var self = this;
        this.idsElement = idsElement;
        this.render();
    }

    render() {
        var index = Array.prototype.indexOf.call(this.idsElement.parentElement.children, this.idsElement);
        if (index == 0 && this.direction == 'up') {
            this.classList.add('hidden');
        } else if (index == this.idsElement.parentElement.children.length - 1 && this.direction == 'down') {
            this.classList.add('hidden');
        } else {
            this.classList.remove('hidden');
        }
    }

    click(e) {
        if (this.direction == "up") {
            this.idsElement.parentElement.insertBefore(this.idsElement, this.idsElement.previousElementSibling);
        } else if (this.direction == "down") {
            var nextNextSibling = this.idsElement.nextElementSibling.nextElementSibling;
            this.idsElement.parentElement.insertBefore(this.idsElement, nextNextSibling);
        }
        this.idsElement.parentElement.dispatchEvent(new Event('ids-spec-move'));
    }
}

class IDSSpecAdd extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click(e) {
        var specs = this.closest('ids-specs');
        var spec = this.closest('ids-spec');

        var container = this.closest('ids-container');
        var newSpec = container.ids.createElementNS(ns, "specification");
        var newApplicability = container.ids.createElementNS(ns, "applicability");
        var newRequirements = container.ids.createElementNS(ns, "requirements");

        specs.idsElement.insertBefore(newSpec, spec.idsElement.nextElementSibling);
        newSpec.appendChild(newApplicability);
        newSpec.appendChild(newRequirements);
        specs.idsElement.dispatchEvent(new Event('ids-spec-add'));
    }
}

class IDSSpecHandle extends HTMLElement {
    connectedCallback() {
        this.addEventListener('dragstart', this.dragstart);
        this.addEventListener('dragend', this.dragend);
    }

    dragstart(e) {
        var snippet = this.getElementsByClassName('snippet')[0];
        snippet.style.left = e.clientX + 'px';
        snippet.style.top = e.clientY + 'px';
        var dropzones = document.getElementsByTagName('ids-spec');
        for (var i=0; i<dropzones.length; i++) {
            dropzones[i].classList.add('dropzone');
        }
        snippet.classList.remove('hidden');
        this.closest('ids-spec').style.opacity = '0.3';
    }

    dragend(e) {
        var snippet = this.getElementsByClassName('snippet')[0];
        snippet.classList.add('hidden');
        this.closest('ids-spec').style.opacity = '1';
        var dropzones = document.getElementsByTagName('ids-spec');
        for (var i=0; i<dropzones.length; i++) {
            dropzones[i].classList.remove('dropzone');
            dropzones[i].classList.remove('dragover');
        }
    }
}

class IDSSpecCounter extends HTMLElement {
    connectedCallback() {
        var spec = this.closest('ids-spec');
        var index = Array.prototype.indexOf.call(spec.parentElement.children, spec);
        this.textContent = index;
    }
}

class IDSSpecAnchor extends HTMLElement {
    connectedCallback() {
        var spec = this.closest('ids-spec');
        var index = Array.prototype.indexOf.call(spec.parentElement.children, spec);
        var container = this.closest('ids-container');
        var a = this.getElementsByTagName('a')[0];
        a.setAttribute('href', '#' + container.containerId + '-' + index);
    }
}

class IDSSpecTarget extends HTMLElement {
    connectedCallback() {
        var spec = this.closest('ids-spec');
        var index = Array.prototype.indexOf.call(spec.parentElement.children, spec);
        var container = this.closest('ids-container');
        var a = document.createElement("a");
        a.setAttribute('id', container.containerId + '-' + index);
        this.appendChild(a);
    }
}

class IDSSpecAttribute extends HTMLElement {
    connectedCallback() {
        this.name = this.attributes['name'].value;
        if ( ! this.attributes['readonly']) {
            this.contentEditable = true;
            this.addEventListener('input', this.input);
            this.addEventListener('blur', this.blur);
        }
        this.defaultValue = this.textContent;
    }

    load(idsElement) {
        var self = this;
        this.idsElement = idsElement;
        this.idsElement.addEventListener('ids-spec-attribute-' + this.name, function() { self.render(); });
        this.render();
    }

    render() {
        this.idsAttribute = this.idsElement.attributes[this.name];
        if (this.idsAttribute) {
            if (this.textContent != this.idsAttribute.value) {
                this.textContent = this.idsAttribute.value;
            }
        }
        this.idsAttribute ? this.classList.remove('null') : this.classList.add('null');
        if ( ! this.textContent) {
            this.textContent = this.defaultValue;
        }
    }

    input(e) {
        if ( ! this.idsAttribute && this.textContent) {
            this.add();
        }
        if (this.idsAttribute && ! this.textContent) {
            this.remove();
        }
        if (this.idsAttribute) {
            this.idsAttribute.value = this.textContent;
        }
        this.idsElement.dispatchEvent(new Event('ids-spec-attribute-' + this.name));
    }

    blur(e) {
        if (this.idsAttribute && ! this.textContent) {
            this.remove();
            this.idsElement.dispatchEvent(new Event('ids-spec-attribute-' + this.name));
        }
    }

    add() {
        this.idsElement.setAttribute(this.attributes['name'].value, this.textContent);
        this.idsAttribute = this.idsElement.attributes[this.attributes['name'].value];
    }

    remove() {
        this.idsElement.attributes.removeNamedItem(this.attributes['name'].value);
        this.idsAttribute = null;
    }
}

class IDSFacets extends HTMLElement {
    load(idsElement) {
        var self = this;
        this.idsElement = idsElement;
        this.idsElement.addEventListener('ids-facet-remove', function() { self.render(); });
        this.render();
    }

    render() {
        var template = this.getElementsByTagName('template')[0];

        var children = [];
        for (var i=0; i<this.children.length; i++) {
            if (this.children[i] != template) {
                children.push(this.children[i]);
            }
        }

        for (var i=0; i<children.length; i++) {
            this.removeChild(children[i]);
        }

        var facets = this.idsElement.children;
        for (var i=0; i<facets.length; i++) {
            this.appendChild(template.content.cloneNode(true));
            var facet = this.children[this.children.length-1];
            var facetElements = facet.getElementsByTagName('ids-facet');
            for (var j=0; j<facetElements.length; j++) {
                facetElements[j].load(facets[i]);
            }
            var facetInstructionsElements = facet.getElementsByTagName('ids-facet-instructions');
            for (var j=0; j<facetInstructionsElements.length; j++) {
                facetInstructionsElements[j].load(facets[i]);
            }
        }
        feather.replace();
    }

    showResults(requirements) {
        var facetElements = this.getElementsByTagName('ids-facet');
        for (var i=0; i<facetElements.length; i++) {
            facetElements[i].showResults(requirements[i]);
        }
    }
}

class IDSFacetInstructions extends HTMLElement {
    connectedCallback() {
        this.contentEditable = true;
        this.defaultValue = this.textContent;
        this.addEventListener('input', this.input);
        this.addEventListener('blur', this.blur);
    }

    load(idsElement) {
        this.idsElement = idsElement;
        this.idsAttribute = this.idsElement.attributes['instructions']
        if (this.idsAttribute) {
            this.textContent = this.idsAttribute.value;
        }
        this.idsAttribute ? this.classList.remove('null') : this.classList.add('null');
    }

    input(e) {
        if ( ! this.idsAttribute && this.textContent) {
            this.add();
        }
        this.idsAttribute ? this.idsAttribute.value = this.textContent : null;
        this.idsAttribute ? this.classList.remove('null') : this.classList.add('null');
    }

    blur(e) {
        if (this.idsAttribute && ! this.textContent) {
            this.remove();
        }
        if ( ! this.textContent) {
            this.textContent = this.defaultValue;
        }
        this.idsAttribute ? this.classList.remove('null') : this.classList.add('null');
    }

    add() {
        this.idsElement.setAttribute('instructions', this.textContent);
        this.idsAttribute = this.idsElement.attributes['instructions'];
    }

    remove() {
        this.idsElement.attributes.removeNamedItem('instructions');
        this.idsAttribute = null;
    }
}

class IDSFacetRemove extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click(e) {
        var idsElement = this.closest('div').getElementsByTagName('ids-facet')[0].idsElement;
        var parentElement = idsElement.parentElement;
        parentElement.removeChild(idsElement);
        parentElement.dispatchEvent(new Event('ids-facet-remove'));
    }
}

class IDSFacet extends HTMLElement {
    load(idsElement) {
        this.idsElement = idsElement;
        this.type = this.attributes['type'].value;
        this.params = [];
        if (this.idsElement.localName == 'entity') {
            this.loadEntity();
        } else if (this.idsElement.localName == 'attribute') {
            this.loadAttribute()
        } else if (this.idsElement.localName == 'classification') {
            this.loadClassification();
        } else if (this.idsElement.localName == 'property') {
            this.loadProperty();
        } else if (this.idsElement.localName == 'material') {
            this.loadMaterial();
        } else if (this.idsElement.localName == 'partOf') {
            this.loadPartOf();
        }

        var paramElements = this.getElementsByTagName('ids-param');
        for (var i=0; i<paramElements.length; i++) {
            paramElements[i].load(this.params[i]);
        }
    }

    showResults(requirement) {
        var idsResultElements = this.parentElement.getElementsByTagName('ids-result');
        for (var i=0; i<idsResultElements.length; i++) {
            if (! idsResultElements[i].classList.contains('hidden')) {
                idsResultElements[i].classList.add('hidden');
            }
            if (requirement.status == true && idsResultElements[i].attributes['name'].value == 'pass') {
                idsResultElements[i].classList.remove('hidden');
            } else if (requirement.status == false && idsResultElements[i].attributes['name'].value == 'fail') {
                idsResultElements[i].classList.remove('hidden');
                idsResultElements[i].getElementsByTagName('span')[0].textContent = requirement.failed_entities.length;
            }
        }
    }

    renderTemplate(templates, parameters) {
        for (var i=0; i<templates.length; i++) {
            var hasKeys = true;
            for (var key in parameters) {
                if (templates[i].indexOf('{' + key + '}') == -1) {
                    hasKeys = false;
                    break;
                } else {
                    templates[i] = templates[i].replace('{' + key + '}', parameters[key]);
                }
            }
            if (hasKeys) {
                return templates[i];
            }
        }
    }

    loadEntity() {
        if (this.type == 'applicability') {
            var templates = [
                'All {name} data',
                'All {name} data of type {type}',
                'All {name} data having a type of either {typeEnumeration}',
            ];
        } else if (this.type == 'requirement') {
            var templates = [
                'Shall be {name} data',
                'Shall be {name} data of type {type}',
                'Shall be {name} data with a type of either {typeEnumeration}',
            ];
        }

        var parameters = {};
        this.parseEntityName(this.idsElement, parameters);
        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    parseEntityName(idsElement, parameters) {
        var name = this.idsElement.getElementsByTagNameNS(ns, 'name')[0];
        var value = this.getIdsValue(name);
        if (value.type == 'simpleValue' || value.type == 'enumeration') {
            var content = this.capitalise(value.content.toLowerCase().replaceAll('ifc', ''))
            parameters.name = '<ids-param filter="entityName">' + content + '</ids-param>';
            this.params.push(value.param);
        }
        var predefinedTypes = this.idsElement.getElementsByTagNameNS(ns, 'predefinedType');
        if (predefinedTypes.length) {
            value = this.getIdsValue(predefinedTypes[0]);
            if (value.type == 'simpleValue') {
                parameters.type = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'enumeration') {
                parameters.typeEnumeration = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }

    }

    loadAttribute() {
        if (this.type == 'applicability') {
            var templates = [
                'Data where the {name} is provided',
                'Data where the {name} is {value}',
                'Data where the {name} follows the convention of {valuePattern}',
                'Data where the {name} is either {valueEnumeration}',
            ];
        } else if (this.type == 'requirement') {
            var templates = [
                'The {name} shall be provided',
                'The {name} shall be {value}',
                'The {name} shall follow the convention of {valuePattern}',
                'The {name} shall be either {valueEnumeration}'
            ];
        }

        var parameters = {};

        var name = this.idsElement.getElementsByTagNameNS(ns, 'name')[0];
        var value = this.getIdsValue(name);
        if (value.type == 'simpleValue') {
            parameters.name = '<ids-param filter="attributeName">' + this.sentence(value.content) + '</ids-param>';
            this.params.push(value.param);
        }
        var values = this.idsElement.getElementsByTagNameNS(ns, 'value');
        if (values.length) {
            value = this.getIdsValue(values[0]);
            if (value.type == 'simpleValue') {
                parameters.value = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'pattern') {
                parameters.valuePattern = '<ids-param class="pattern">' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'enumeration') {
                parameters.valueEnumeration = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }

        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    loadClassification() {
        if (this.type == 'applicability') {
            var templates = [
                'Data classified using {system}',
                'Data classified as {reference}',
                'Data classified following the convention of {referencePattern}',
                'Data having a {system} reference of {reference}',
                'Data having a {system} reference following the convention of {referencePattern}',
            ];
        } else if (this.type == 'requirement') {
            var templates = [
                'Shall be classified using {system}',
                'Shall be classified as {reference}',
                'Shall be classified following the convention of {referencePattern}',
                'Shall have a {system} reference of {reference}',
                'Shall have a {system} reference following the convention of {referencePattern}',
            ];
        }

        var parameters = {};

        var value;
        var systems = this.idsElement.getElementsByTagNameNS(ns, 'system');
        if (systems.length) {
            value = this.getIdsValue(systems[0]);
            if (value.type == 'simpleValue') {
                parameters.system = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }
        var references = this.idsElement.getElementsByTagNameNS(ns, 'value');
        if (references.length) {
            value = this.getIdsValue(references[0]);
            if (value.type == 'simpleValue') {
                parameters.reference = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'pattern') {
                parameters.referencePattern = '<ids-param class="pattern">' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }

        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    loadProperty() {
        if (this.type == 'applicability') {
            var templates = [
                'Elements with {name} data in the dataset {pset}',
                'Elements with {name} data of {value} in the dataset {pset}',
                'Elements with {name} data following the convention of {valuePattern} in the dataset {pset}',
                'Elements with {name} data with either {valueEnumeration} in the dataset {pset}',
            ];
        } else if (this.type == 'requirement') {
            var templates = [
                '{name} data shall be provided in the dataset {pset}',
                '{name} data shall be {value} and in the dataset {pset}',
                '{name} data shall follow the convention of {valuePattern} and in the dataset {pset}',
                '{name} data shall be one of {valueEnumeration} and in the dataset {pset}',
            ];
        }

        var parameters = {};

        var name = this.idsElement.getElementsByTagNameNS(ns, 'baseName')[0];
        var value = this.getIdsValue(name);
        if (value.type == 'simpleValue') {
            parameters.name = '<ids-param filter="propertyName">' + this.sentence(value.content) + '</ids-param>';
            this.params.push(value.param);
        }

        var values = this.idsElement.getElementsByTagNameNS(ns, 'value');
        if (values.length) {
            value = this.getIdsValue(values[0]);
            if (value.type == 'simpleValue') {
                parameters.value = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'pattern') {
                parameters.valuePattern = '<ids-param class="pattern">' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'enumeration') {
                parameters.valueEnumeration = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }

        var propertySet = this.idsElement.getElementsByTagNameNS(ns, 'propertySet')[0];
        value = this.getIdsValue(propertySet);
        if (value.type == 'simpleValue') {
            parameters.pset = '<ids-param>' + value.content + '</ids-param>';
            this.params.push(value.param);
        }

        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    loadMaterial() {
        if (this.type == 'applicability') {
            var templates = [
                'All data with a {value} material',
                'All data with a material of either {valueEnumeration}',
                'All data with a material',
            ];
        } else if (this.type == 'requirement') {
            var templates = [
                'Shall shall have a material of {value}',
                'Shall have a material of either {valueEnumeration}',
                'Shall have a material',
            ];
        }

        var parameters = {};

        var value;
        var values = this.idsElement.getElementsByTagNameNS(ns, 'value');
        if (values.length) {
            value = this.getIdsValue(values[0]);
            if (value.type == 'simpleValue') {
                parameters.value = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'pattern') {
                parameters.valuePattern = '<ids-param class="pattern">' + value.content + '</ids-param>';
                this.params.push(value.param);
            } else if (value.type == 'enumeration') {
                parameters.valueEnumeration = '<ids-param>' + value.content + '</ids-param>';
                this.params.push(value.param);
            }
        }


        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    loadPartOf() {
        var templates = [
            'Must be part of a {relation} relationship',
            'Must be part of a {name} with a {relation} relationship',
            'Must be part of a {name} of type {type} with a {relation} relationship',
        ]

        var parameters = {};

        document.asdf = this.idsElement;
        parameters.relation = '<ids-param>' + this.sentence(this.idsElement.attributes['relation'].value.replace('Ifc', '').replace('Rel', '')) + '</ids-param>';
        this.parseEntityName(this.idsElement, parameters);

        this.innerHTML = this.renderTemplate(templates, parameters);
    }

    getIdsValue(element) {
        var simpleValues = element.getElementsByTagNameNS(ns, 'simpleValue');
        if (simpleValues.length) {
            return {type: 'simpleValue', param: simpleValues[0], content: simpleValues[0].textContent}
        }
        var restriction = element.getElementsByTagNameNS(xs, 'restriction')[0];
        var patterns = restriction.getElementsByTagNameNS(xs, 'pattern');
        if (patterns.length) {
            return {type: 'pattern', param: patterns[0], content: patterns[0].attributes['value'].value}
        }
        var enumerations = restriction.getElementsByTagNameNS(xs, 'enumeration');
        if (enumerations.length) {
            var values = [];
            for (var i=0; i<enumerations.length; i++) {
                values.push(enumerations[i].attributes['value'].value);
            }
            return {type: 'enumeration', param: restriction, content: values.join(' or ')}
        }
    }

    capitalise(text) {
        return text.toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
    }

    sentence(text) {
        // E.g. ElevationOfSSLRelative --> Elevation Of S S L Relative
        var words = text.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1);
        var mergedWords = [];
        var mergedWord = '';
        for (var i=0; i<words.length; i++) {
            if (words[i].length == 1) {
                mergedWord += words[i];
                if (i == words.length-1) {
                    mergedWords.push(mergedWord);
                }
            } else {
                if (mergedWord.length) {
                    mergedWords.push(mergedWord);
                    mergedWord = '';
                }
                mergedWords.push(words[i]);
            }
        }
        // E.g. Elevation Of S S L Relative --> Elevation Of SSL Relative
        return mergedWords.join(' ');
    }
}

class IDSParam extends HTMLElement {
    connectedCallback() {
        this.contentEditable = true;
        this.addEventListener('input', this.input);
        this.filter = this.attributes['filter'] ? this.attributes['filter'].value : null;
    }

    load(idsElement) {
        this.idsElement = idsElement;
    }

    input(e) {
        if (this.filter == 'entityName') {
            this.idsElement.textContent = 'IFC' + this.textContent.toUpperCase();
        } else if (this.filter == 'attributeName' || this.filter == 'propertyName') {
            this.idsElement.textContent = this.textContent.replace(/\s+/g, '');
        } else {
            this.idsElement.textContent = this.textContent;
        }
    }
}

class IDSSpecs extends HTMLElement {
    load(idsElement) {
        var self = this;
        this.idsElement = idsElement;
        this.idsElement.addEventListener('ids-spec-remove', function() { self.render(); });
        this.idsElement.addEventListener('ids-spec-add', function() { self.render(); });
        this.idsElement.addEventListener('ids-spec-move', function() { self.render(); });
        this.render();
    }

    render() {
        var template = this.getElementsByTagName('template')[0];

        var children = [];
        for (var i=0; i<this.children.length; i++) {
            if (this.children[i] != template) {
                children.push(this.children[i]);
            }
        }

        for (var i=0; i<children.length; i++) {
            this.removeChild(children[i]);
        }

        var idsSpecs = this.idsElement.getElementsByTagNameNS(ns, 'specification');
        for (var i=0; i<idsSpecs.length; i++) {
            this.appendChild(template.content.cloneNode(true));
            var spec = this.children[this.children.length-1];
            spec.load(idsSpecs[i]);
        }
        feather.replace();
    }

    showResults(specifications) {
        var specElements = this.getElementsByTagName('ids-spec');
        for (var i=0; i<specElements.length; i++) {
            specElements[i].showResults(specifications[i]);
        }
    }
}

class IDSSpec extends HTMLElement {
    connectedCallback() {
        this.addEventListener('dragenter', this.dragenter);
        this.addEventListener('dragover', this.dragover);
        this.addEventListener('drop', this.drop);
    }

    dragenter(e) {
        if (e.target.classList.contains('dropzone')) {
            var dropzones = document.getElementsByTagName('ids-spec');
            for (var i=0; i<dropzones.length; i++) {
                dropzones[i].classList.remove('dragover');
            }
            e.target.classList.add('dragover');
        }
    }

    load(idsElement) {
        var self = this;
        this.idsElement = idsElement;

        var children = this.getElementsByTagName('ids-spec-attribute');
        for (var i=0; i<children.length; i++) {
            children[i].load(idsElement);
        }

        var children = this.getElementsByTagName('ids-facets');
        for (var i=0; i<children.length; i++) {
            children[i].load(idsElement.getElementsByTagNameNS(ns, children[i].attributes['name'].value)[0]);
        }

        var children = this.getElementsByTagName('ids-spec-move');
        for (var i=0; i<children.length; i++) {
            children[i].load(idsElement);
        }
    }

    showResults(specification) {
        var facetsElements = this.getElementsByTagName('ids-facets');
        for (var i=0; i<facetsElements.length; i++) {
            if (facetsElements[i].attributes['name'].value == "requirements") {
                facetsElements[i].showResults(specification.requirements);
            }
        }
    }

    dragover(e) {
        // The HTML draggable API is terrible.
        e.preventDefault();
    }

    drop(e) {
        e.preventDefault();
    }
}

class IDSLoader extends HTMLElement {
    connectedCallback() {
        var self = this;
        this.addEventListener('click', this.launchFileBrowser);
    }

    launchFileBrowser(accept, callback) {
        var inputElement = document.createElement("input");
        inputElement.idsLoader = this;
        inputElement.type = "file";
        inputElement.accept = '.ids,.xml';
        inputElement.multiple = false;
        inputElement.addEventListener("change", this.loadFile)
        inputElement.dispatchEvent(new MouseEvent("click"));
    }

    loadFile(e) {
        var self = this.idsLoader;
        var container = self.closest('ids-container')
        container.filename = this.files[0].name;
        var read = new FileReader();
        read.readAsBinaryString(this.files[0]);
        read.onloadend = function() {
            var parser = new DOMParser();
            var xml = parser.parseFromString(read.result, "text/xml")
            var container = self.closest('ids-container')
            container.ids = xml;
            container.idsElement = xml;
            window.xxx = xml; // TODO
            self.loadSpecs(container);
        }
    }

    loadSpecs(container) {
        container.getElementsByTagName('ids-info')[0].load(container.ids.getElementsByTagNameNS(ns, 'info')[0]);
        var specsElements = container.getElementsByTagName('ids-specs');
        for (var i=0; i<specsElements.length; i++) {
            var specs = specsElements[i];
            specs.load(container.ids.getElementsByTagNameNS(ns, 'specifications')[0]);
        }
    }
}

class IDSSave extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.click);
    }

    click() {
        var container = this.closest('ids-container')
        var xmlString = new XMLSerializer().serializeToString(container.ids);
        this.download(container.filename, xmlString);
    }

    download(filename, text) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }
}


class IDSAudit extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.launchFileBrowser);
    }

    launchFileBrowser(accept, callback) {
        var inputElement = document.createElement("input");
        inputElement.idsAudit = this;
        inputElement.type = "file";
        inputElement.accept = '.ifc';
        inputElement.multiple = false;
        inputElement.addEventListener("change", this.loadFile)
        inputElement.dispatchEvent(new MouseEvent("click"));
    }

    loadFile(e) {
        var self = this.idsAudit;
        var container = self.closest('ids-container');
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() { self.processResponse(request); };
        request.open("POST", "audit");
        var data = new FormData();
        data.append('ifc', this.files[0]);
        data.append('ids', new Blob([new XMLSerializer().serializeToString(container.ids)], {type:'text/plain'}));
        request.send(data);
    }

    processResponse(request) {
        if (request.readyState != 4) {
            return;
        }
        var container = this.closest('ids-container');
        container.isEditing = false;
        var results = JSON.parse(request.responseText);
        var specsElements = container.getElementsByTagName('ids-specs');
        for (var i=0; i<specsElements.length; i++) {
            var specs = specsElements[i];
            specs.showResults(results.specifications);
        }
    }
}

window.customElements.define('ids-new', IDSNew);
window.customElements.define('ids-container', IDSContainer);
window.customElements.define('ids-loader', IDSLoader);
window.customElements.define('ids-save', IDSSave);
window.customElements.define('ids-close', IDSClose);
window.customElements.define('ids-audit', IDSAudit);
window.customElements.define('ids-info', IDSInfo);
window.customElements.define('ids-info-element', IDSInfoElement);
window.customElements.define('ids-specs', IDSSpecs);
window.customElements.define('ids-spec', IDSSpec);
window.customElements.define('ids-spec-handle', IDSSpecHandle);
window.customElements.define('ids-spec-remove', IDSSpecRemove);
window.customElements.define('ids-spec-move', IDSSpecMove);
window.customElements.define('ids-spec-add', IDSSpecAdd);
window.customElements.define('ids-spec-attribute', IDSSpecAttribute);
window.customElements.define('ids-spec-counter', IDSSpecCounter);
window.customElements.define('ids-spec-anchor', IDSSpecAnchor);
window.customElements.define('ids-spec-target', IDSSpecTarget);
window.customElements.define('ids-facets', IDSFacets);
window.customElements.define('ids-facet', IDSFacet);
window.customElements.define('ids-facet-remove', IDSFacetRemove);
window.customElements.define('ids-facet-instructions', IDSFacetInstructions);
window.customElements.define('ids-param', IDSParam);
