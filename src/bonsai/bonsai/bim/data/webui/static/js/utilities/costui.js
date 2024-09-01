export class CostUI {
    constructor() {}

    static isCostScheduleLoaded(id) {
        const existingTable = document.getElementById('cost-items-' + id);
        return existingTable !== null;
    }

    static removeCostSchedule(id) {
        document.getElementById("cost-items-" + id).remove();
    }
    static createTable(id, callbacks) {
        CostUI.isCostScheduleLoaded(id) ? CostUI.removeCostSchedule(id) : null;

        const table = document.createElement("table");
        table.id = 'cost-items-' + id;
        const tbody = document.createElement("tbody");
        tbody.setAttribute("id", "cost-items");

        const columnHeaders = ["Name", "Quantity", "Unit", "Cost", "Total Cost", "Action"];
        const tr = document.createElement("tr");

        for (let i = 0; i < columnHeaders.length; i++) {
            const th = document.createElement("th");
            th.textContent = columnHeaders[i];
            th.style.position = "relative"; // Required for the resizer handle
            tr.appendChild(th);

            // Add resizer handle
            if (i < columnHeaders.length - 1) { // No resizer for the last column
                const resizer = document.createElement("div");
                resizer.classList.add("resizer");
                th.appendChild(resizer);
                CostUI.addResizer(resizer);
            }
        }

        tbody.appendChild(tr);
        table.appendChild(tbody);
        document.getElementById("cost-items").appendChild(table);

        // Add CSS to set column widths, resizer styles, hover effect, and color scheme
        CostUI.addTableStyles(id);

        // Create context menu
        CostUI.createContextMenu(callbacks);

        table.get_blender_id = function() {
            return this.getAttribute("id").split("-")[2];
        };

        return [table, tbody];
    }

    static addTableStyles(id) {
        const style = document.createElement("style");
        style.textContent = `
            #cost-items-${id} th:nth-child(1),
            #cost-items-${id} td:nth-child(1) {
                width: auto;
            }
            #cost-items-${id} th:not(:nth-child(1)),
            #cost-items-${id} td:not(:nth-child(1)) {
                width: 100px; /* Set a fixed width for other columns */
            }

        `;
        document.head.appendChild(style);
    }

    static createContextMenu(callbacks) {
        // Create context menu
        const contextMenu = document.createElement("div");
        contextMenu.id = "context-menu";
        contextMenu.classList.add("context-menu");
        contextMenu.innerHTML = `
            <button id="add-cost-item-button">Add sub-cost</button>
            <button id="edit-cost-values-button">Edit</button>
            <button id="delete-button">Delete</button>
            <button id="duplicate-button">Duplicate</button>
        `;
        document.body.appendChild(contextMenu);

        // Add event listeners for context menu
        document.addEventListener("contextmenu", function(event) {
            event.preventDefault();
            const targetRow = event.target.closest("tr");
            const targetCell = event.target.closest("td");
            if (targetRow && targetRow.parentElement.id === "cost-items") {
                const contextMenu = document.getElementById("context-menu");
                contextMenu.style.display = "block";
                contextMenu.style.left = `${event.pageX}px`;
                contextMenu.style.top = `${event.pageY}px`;

                // Store the target row in the context menu for later use
                contextMenu.targetRow = targetRow;
                contextMenu.targetCell = targetCell;
            } else {
                document.getElementById("context-menu").style.display = "none";
            }
        });

        document.addEventListener("click", function(event) {
            const contextMenu = document.getElementById("context-menu");
            if (!contextMenu.contains(event.target)) {
                contextMenu.style.display = "none";
            }
        });

        const editCostValuesButton = document.getElementById("edit-cost-values-button");
        editCostValuesButton.addEventListener("click", function() {
            console.log("Edit cost values executed");
            const targetRow = document.getElementById("context-menu").targetRow;
            const targetCell = document.getElementById("context-menu").targetCell;
            if (targetRow) {
                const costItemId = parseInt(targetRow.getAttribute("id"));
                callbacks.enableEditingCostValues ? callbacks.enableEditingCostValues(costItemId) : null;
            }
        });

        const addButton = document.getElementById("add-cost-item-button");
        if (!addButton.dataset.listenerAdded) {
            function addCostItemHandler(e) {
                e.stopPropagation();
                const targetRow = document.getElementById("context-menu").targetRow;
                if (targetRow) {
                    const costItemId = parseInt(targetRow.getAttribute("id"));
                    callbacks.addCostItem ? callbacks.addCostItem(costItemId) : null;
                }
                document.getElementById("context-menu").style.display = "none";
            }
            addButton.addEventListener("click", addCostItemHandler);
            addButton.dataset.listenerAdded = "true";
        }

        document.getElementById("delete-button").addEventListener("click", function() {
            const targetRow = document.getElementById("context-menu").targetRow;
            if (targetRow) {
                // Implement your delete action here
                console.log("Delete row:", targetRow.getAttribute("id"));
                targetRow.remove();
            }
        });

        document.getElementById("duplicate-button").addEventListener("click", function() {
            const targetRow = document.getElementById("context-menu").targetRow;
            if (targetRow) {
                // Implement your duplicate action here
                console.log("Duplicate row:", targetRow.getAttribute("id"));
                const newRow = targetRow.cloneNode(true);
                targetRow.parentElement.appendChild(newRow);
            }
        });
    }
    
    static addResizer(resizer) {
        let startX, startWidth, th;
    
        resizer.addEventListener("mousedown", function(e) {
            th = e.target.parentElement;
            startX = e.pageX;
            startWidth = th.offsetWidth;
            document.addEventListener("mousemove", resizeColumn);
            document.addEventListener("mouseup", stopResize);
        });
    
        function resizeColumn(e) {
            const newWidth = startWidth + (e.pageX - startX);
            th.style.width = newWidth + "px";
        }
    
        function stopResize() {
            document.removeEventListener("mousemove", resizeColumn);
            document.removeEventListener("mouseup", stopResize);
        }
    }
    
    static generateColorScheme(baseColor) {
        // This function generates a color scheme based on the base color
        // For simplicity, we'll just lighten the base color for each level
        const levels = 7; // Number of levels of nesting
        const colorScheme = [];
        for (let i = 0; i < levels; i++) {
            colorScheme.push(CostUI.lightenColor(baseColor, i * 7));
        }
        return colorScheme;
    }
    
    static lightenColor(color, percent) {
        // This function lightens a color by a given percentage
        const num = parseInt(color.slice(1), 16),
            amt = Math.round(2.55 * percent),
            R = (num >> 16) + amt,
            G = (num >> 8 & 0x00FF) + amt,
            B = (num & 0x0000FF) + amt;
        return `#${(0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1).toUpperCase()}`;
    }
    
    static applyColorScheme(tableId, colorScheme) {
        const rows = document.querySelectorAll(`#${tableId} tbody tr`);
        rows.forEach((row, index) => {
            const level = index % colorScheme.length; // Assuming level is determined by index for simplicity
            row.style.backgroundColor = colorScheme[level];
        });
    }
    

    static createColorPicker() {
        const colorPicker = document.createElement("input");
        colorPicker.type = "color";
        colorPicker.id = "color-picker";
        colorPicker.value = "#ff0000"; // Default color
        const colorText = document.createElement("p");
        colorText.textContent = "Select a color to change row color:";
        document.getElementById("UI").appendChild(colorText);
        document.getElementById("UI").appendChild(colorPicker);

        colorPicker.addEventListener("input", function() {
            const baseColor = colorPicker.value;
            const colorScheme = CostUI.generateColorScheme(baseColor);
            CostUI.applyColorScheme("cost-items", colorScheme);
        });
        const colorScheme = CostUI.generateColorScheme("#000000");
        CostUI.applyColorScheme("cost-items", colorScheme);
    }
    
    static createCostSchedule({ data, blenderID, title, callbacks = {} }) {
        const [table, tbody] = CostUI.createTable(blenderID, callbacks);
        CostUI.createCostItem(data, tbody, 0, null, callbacks);
        CostUI.applyExpandedState();
    }

    static createCostItem(data, container, nestingLevel = 0, parentID = null, callbacks = {}) {
        data.forEach(obj => {
            const row = CostUI.createRow(obj, nestingLevel, parentID, callbacks);
            container.appendChild(row);

            if (obj.is_nested_by && obj.is_nested_by.length > 0) {
                CostUI.createCostItem(obj.is_nested_by, container, nestingLevel + 1, obj.id, callbacks);
            }
        });
    }

    static createRow(obj, nestingLevel, parentID, callbacks = {}) {
        const row = CostUI.createTableRow(obj, nestingLevel, parentID);
        const expandButton = CostUI.createExpandButton(obj);
        const nameCell = CostUI.createNameCell(obj, nestingLevel, expandButton, callbacks);
        const totalCostQuantityCell = CostUI.createTableCell(obj.TotalCostQuantity);
        const unitSymbolCell = CostUI.createTableCell(obj.UnitSymbol);
        const totalAppliedValueCell = CostUI.createTableCell(obj.TotalAppliedValue);
        const totalCostCell = CostUI.createTotalCostCell(obj);
        const flexContainerCell = CostUI.createFlexContainerCell(obj, callbacks);
    
        row.appendChild(nameCell);
        row.appendChild(totalCostQuantityCell);
        row.appendChild(unitSymbolCell);
        row.appendChild(totalAppliedValueCell);
        row.appendChild(totalCostCell);
        row.appendChild(flexContainerCell);
    
        row.get_id = function() {
            return this.getAttribute("id");
        };
    
        row.get_parent = function() {
            const parentId = this.getAttribute("parent-id");
            return parentId ? document.getElementById(parentId) : null;
        };
    
        return row;
    }
    
    static createTableRow(obj, nestingLevel, parentID) {
        const row = document.createElement("tr");
        row.setAttribute("id", obj.id);
        row.setAttribute("parent-id", parentID);
        if (nestingLevel > 0) {
            row.classList.add("nested");
            row.classList.add(`level-${nestingLevel}`);
        }
        return row;
    }
    
    static createExpandButton(obj) {
        const expandButton = document.createElement("button");
        expandButton.classList.add("toggle-button");
        if (obj.is_nested_by && obj.is_nested_by.length > 0) {
            expandButton.textContent = ">";
        } else {
            expandButton.style.visibility = "hidden";
        }
        expandButton.addEventListener("click", function() {
            CostUI.contractExpandRow.call(this, obj.id);
        });
        return expandButton;
    }
    
    static createNameCell(obj, nestingLevel, expandButton, callbacks) {
        const nameCell = document.createElement("td");
        const nameInput = document.createElement("input");
        nameInput.value = obj.name ? obj.name : "Unnamed";
    
        nameInput.addEventListener("change", function() {
            callbacks.editCostItemName ? callbacks.editCostItemName(obj.id, this.value) : null;
        });
    
        nameInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                callbacks.editCostItemName ? callbacks.editCostItemName(obj.id, this.value) : null;
            }
        });
    
        nameCell.style.paddingLeft = nestingLevel * 20 + "px";
        nameCell.appendChild(expandButton);
        nameCell.appendChild(nameInput);
        return nameCell;
    }
    
    static createTableCell(content) {
        const cell = document.createElement("td");
        cell.textContent = content;
        return cell;
    }
    
    static createTotalCostCell(obj) {
        const totalCostCell = document.createElement("td");
        const totalCost = parseFloat(obj.TotalCost).toFixed(2);
        totalCostCell.textContent = obj.is_sum ? totalCost + " (Σ)" : totalCost;
        return totalCostCell;
    }
    
    static createFlexContainerCell(obj, callbacks) {
        const divFlex = document.createElement("div");
        divFlex.classList.add("flex-container");
    
        const addButton = CostUI.createAddButton(obj, callbacks);
        const selectButton = CostUI.createSelectButton(obj, callbacks);
    
        divFlex.appendChild(addButton);
        divFlex.appendChild(selectButton);
    
        const flexContainerCell = document.createElement("td");
        flexContainerCell.appendChild(divFlex);
        return flexContainerCell;
    }
    
    static createAddButton(obj, callbacks) {
        const addButton = document.createElement("button");
        addButton.textContent = "+";
        addButton.classList.add("add-button");
        addButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.addCostItem ? callbacks.addCostItem(obj.id) : null;
        });
        return addButton;
    }
    
    static createSelectButton(obj, callbacks) {
        const selectButton = document.createElement("button");
        selectButton.textContent = "Select";
        selectButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.selectAssignedElements ? callbacks.selectAssignedElements(obj.id) : null;
        });
        return selectButton;
    }

    static hideNestedRows(parentId) {
        const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
        rows.forEach(row => {
            row.classList.add("nested");
            const childId = row.getAttribute('id');
            if (childId) {
                CostUI.hideNestedRows(childId);
            }
        });
    }

    static showNestedRows(parentId) {
        const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
        rows.forEach(row => {
            row.classList.remove("nested");
            const childId = row.getAttribute('id');
            if (childId && CostUI.isRowExpanded(childId)) {
                CostUI.showNestedRows(childId);
            }
        });
    }

    static contractExpandRow(id) {
        const rows = document.querySelectorAll(`[parent-id='${id}']`);
        if (rows.length === 0) {
            return;
        }

        let isVisible = false;
        rows.forEach(row => {
            if (!row.classList.contains("nested")) {
                isVisible = true;
            }
        });

        if (isVisible) {
            CostUI.hideNestedRows(id);
            this.textContent = ">";
            CostUI.updateExpandedState(id, false);
        } else {
            CostUI.showNestedRows(id);
            this.textContent = "^";
            CostUI.updateExpandedState(id, true);
        }
    }

    static updateExpandedState(id, isExpanded) {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
        expandedState[id] = isExpanded;
        localStorage.setItem('expandedState', JSON.stringify(expandedState));
    }

    static applyExpandedState() {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
        Object.keys(expandedState).forEach(id => {
            if (expandedState[id]) {
                CostUI.showNestedRows(id);
                const toggleButton = document.querySelector(`[id='${id}'] .toggle-button`);
                if (toggleButton) {
                    toggleButton.textContent = "^";
                }
            } else {
                CostUI.hideNestedRows(id);
                const toggleButton = document.querySelector(`[id='${id}'] .toggle-button`);
                if (toggleButton) {
                    toggleButton.textContent = ">";
                }
            }
        });
    }

    static isRowExpanded(id) {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
        return expandedState[id] || false;
    }

    static text(label) {
        const text = document.createElement("p");
        text.textContent = label;
        return text;
    }

    static createCard(title, mainContainer, callback) {
        const card = document.createElement("div");
        card.classList.add("card");

        const cardBody = document.createElement("div");
        cardBody.classList.add("card-body");

        const cardTitle = document.createElement("h5");
        cardTitle.classList.add("card-title");
        cardTitle.textContent = title;

        const cardButton = document.createElement("button");
        cardButton.classList.add("btn", "btn-primary");
        cardButton.textContent = "Load";
        cardButton.addEventListener("click", callback);

        cardBody.appendChild(cardTitle);
        cardBody.appendChild(mainContainer);
        cardBody.appendChild(cardButton);
        card.appendChild(cardBody);

        return card;
    }

    static createCostValuesForm({ costItemId, costValues, callbacks }) {
        // Check if the form already exists and remove it if it does
        const formId = "cost-values-form-" + costItemId;
        let existingForm = document.getElementById(formId);
        if (existingForm) {
            existingForm.remove();
        }
    
        const form = CostUI.createFormElement(formId, "cost-values-form");
        
        const header = CostUI.createHeader("Cost Values Form");
        form.appendChild(header);
        
        const table = CostUI.createCostValuesTable(costItemId, ["Type", "Category", "Value"]);
        
        costValues.forEach(costValue => {
            const tr = CostUI.createCostvaluesRow(costItemId, costValue);
            table.appendChild(tr);
        });
        
        form.appendChild(table);
    
        const addButton = CostUI.createAddCostValueButton(costItemId, callbacks);
        form.appendChild(addButton);
        
        const submitButton = CostUI.createSubmitButton(callbacks);
        form.appendChild(submitButton);
        
        const closeButton = CostUI.createCloseButton(form);
        form.appendChild(closeButton);
        
        CostUI.makeHeaderDraggable(header, form);
        
        document.body.appendChild(form);
        
        return form;
    }
    

    static getCostValuesTable(costItemId) {
        return document.getElementById("cost-values-table-" + costItemId);
    }

    static addNewCostValueRow(costItemId, costValueId) {
        const table = CostUI.getCostValuesTable(costItemId);
        // check if table exists
        if (!table) {
            console.log("Cost values table not found for cost item ID:", costItemId);
            return;
        }
        console.log("Adding new cost value row", costValueId);
        console.log(table)
        const tr = CostUI.createCostvaluesRow(costItemId, {"category": "", "name": "", "applied_value": 0, "id": costValueId, "parent": costItemId});
        table.appendChild(tr);
    }

    static createCostValuesTable(costItemId, headers) {
        const table = document.createElement("table");
        table.classList.add("cost-values-table");
        table.id = "cost-values-table-" + costItemId;
    
        const headerRow = document.createElement("tr");
        headers.forEach(headerText => {
            const th = document.createElement("th");
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
    
        return table;
    }

    static createCostvaluesRow(costItemId,costValue) {

        function cleanLabel(value) {
            // remove anything which is not a dot or a digit
            return value.replace(/[^0-9.]/g, '');
            
        }


        if (document.getElementById(costValue.id)) {
            return document.getElementById(costValue.id);
        }

        const tr = document.createElement("tr");
        tr.isCostValue = true;
        tr.parent = costItemId;
        tr.id = costValue.id;

        let costType = "FIXED";
        if (costValue.category === "*") {
            costType = "SUM";
        }
        else if (costValue.category && costValue.category !== "*") {
            costType = "CATEGORY";
        }
        else if (costValue.applied_value) {
            costType = "FIXED";
        }
    
        const typeCell = CostUI.createTableDropdown("type", costType);
        const dropdown = typeCell.querySelector("select");
        dropdown.addEventListener("change", function() {
            const selectedType = this.value;
            CostUI.updateRowBasedOnType(selectedType, categoryCell, valueCell1);
        });
        tr.appendChild(typeCell);
    
        const categoryCell = CostUI.createTableInput("text", "category", costValue.category);
        tr.appendChild(categoryCell);
        
        let value 

        if (costValue.category === "*"){
            value = cleanLabel(costValue.label)
        }
        else {
            value = costValue.applied_value
        }
        const valueCell1 = CostUI.createTableInput("number", "value", value);
        tr.appendChild(valueCell1);
        // Apply initial state based on costType
        CostUI.updateRowBasedOnType(costType, categoryCell, valueCell1);
    
        return tr;
    }
    
    static updateRowBasedOnType(type, categoryCell, valueCell1) {
        if (type === "FIXED") {
            categoryCell.querySelector("input").disabled = true;
            categoryCell.querySelector("input").style.backgroundColor = "lightgrey";
            valueCell1.querySelector("input").disabled = false;
            valueCell1.querySelector("input").style.backgroundColor = "";
        } else if (type === "CATEGORY") {
            categoryCell.querySelector("input").disabled = false;
            categoryCell.querySelector("input").style.backgroundColor = "";
            valueCell1.querySelector("input").disabled = false;
            valueCell1.querySelector("input").style.backgroundColor = "";
        } else if (type === "SUM") {
            categoryCell.querySelector("input").disabled = true;
            categoryCell.querySelector("input").style.backgroundColor = "lightgrey";
            valueCell1.querySelector("input").disabled = true;
            valueCell1.querySelector("input").style.backgroundColor = "lightgrey";
        }
    }
    
    static createTableDropdown(name, value="FIXED") {
        const cell = document.createElement("td");
        const dropdown = document.createElement("select");
        dropdown.name = name;
    
        const options = ["FIXED", "CATEGORY", "SUM"];
        options.forEach(optionValue => {
            const option = document.createElement("option");
            option.value = optionValue;
            option.textContent = optionValue;
            if (optionValue === value) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    
        cell.appendChild(dropdown);
        return cell;
    }
    
    static createTableInput(type, name, value) {
        const cell = document.createElement("td");
        const input = document.createElement("input");
        input.type = type;
        input.name = name;
        input.value = value;
        cell.appendChild(input);
        return cell;
    }
    
    static createAddCostValueButton(costItemId, callbacks) {
        const addButton = document.createElement("button");
        addButton.textContent = "+";
        addButton.classList.add("add-button");
        addButton.addEventListener("click", function(e) {
            e.preventDefault();
            callbacks.addCostValue ? callbacks.addCostValue(costItemId) : null;
        });
        return addButton;
    }
    
    static createSubmitButton(callbacks) {
        const submitButton = document.createElement("button");
        submitButton.type = "submit";
        submitButton.textContent = "Save";

        submitButton.addEventListener("click", function(e) {
            e.preventDefault();
            const form = this.closest("form");
            const costValues = [];
            const rows = Array.from(form.querySelectorAll("tr")).filter(row => row.isCostValue);

            rows.forEach(row => {
                const costCategory = row.querySelector("input[name='category']").value;
                const appliedValue = parseFloat(row.querySelector("input[name='value']").value);
                const costType = row.querySelector("select[name='type']").value;
                const id = parseInt(row.id);
                costValues.push({ costType, costCategory, appliedValue, id: id, costItemId: row.parent });
            });
            const costItemId = parseInt(form.id.split("-")[3]);
            console.log(form.id)
            console.log("Cost values to be saved:", costItemId);
            callbacks.editCostValues ? callbacks.editCostValues(costItemId, costValues) : null;
            form.remove();
        });
        return submitButton;
    }

    static createFormElement(id, className) {
        const form = document.createElement("form");
        form.id = id;
        form.classList.add(className);
        form.style.position = "absolute"; // Set initial position to absolute
        form.style.top = "50%";
        form.style.left = "50%";
        form.style.transform = "translate(-50%, -50%)";
        return form;
    }

    static createHeader(text) {
        const header = document.createElement("div");
        header.classList.add("form-header");
        header.textContent = text;
        return header;
    }

    static createCloseButton(form) {
        const closeButton = document.createElement("span");
        closeButton.classList.add("close-button");
        closeButton.innerHTML = "&times;";
        closeButton.addEventListener("click", function() {
            form.remove();
        });
        return closeButton;
    }
    
    static makeHeaderDraggable(header, form) {
        header.addEventListener("mousedown", function(e) {
            let offsetX = e.clientX - form.getBoundingClientRect().left;
            let offsetY = e.clientY - form.getBoundingClientRect().top;
    
            function mouseMoveHandler(e) {
                form.style.left = `${e.clientX - offsetX}px`;
                form.style.top = `${e.clientY - offsetY}px`;
            }
    
            function mouseUpHandler() {
                document.removeEventListener("mousemove", mouseMoveHandler);
                document.removeEventListener("mouseup", mouseUpHandler);
            }
    
            document.addEventListener("mousemove", mouseMoveHandler);
            document.addEventListener("mouseup", mouseUpHandler);
        });
    }
}
