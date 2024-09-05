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
            th.style.position = "relative";
            tr.appendChild(th);

            if (i < columnHeaders.length - 1) {
                const resizer = document.createElement("div");
                resizer.classList.add("resizer");
                th.appendChild(resizer);
                CostUI.addResizer(resizer);
            }
        }

        tbody.appendChild(tr);
        table.appendChild(tbody);
        document.getElementById("cost-items").appendChild(table);

        CostUI.addTableStyles(id);
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
        const contextMenu = document.createElement("div");
        contextMenu.id = "context-menu";
        contextMenu.classList.add("context-menu");
        contextMenu.innerHTML = `
            <button id="edit-cost-values-button">Edit Cost Values</button>
            <button id="add-cost-item-button">Add sub-cost</button>
            <button id="duplicate-button">Duplicate</button>
            <button id="delete-button">Delete</button>
        `;
        document.body.appendChild(contextMenu);

        document.addEventListener("contextmenu", function(event) {
            event.preventDefault();
            const targetRow = event.target.closest("tr");
            const targetCell = event.target.closest("td");
            if (targetRow && targetRow.parentElement.id === "cost-items") {
                const contextMenu = document.getElementById("context-menu");
                contextMenu.style.display = "block";
                contextMenu.style.left = `${event.pageX}px`;
                contextMenu.style.top = `${event.pageY}px`;

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

        const deleteButton = document.getElementById("delete-button");
        if (deleteButton && !deleteButton.hasListener) {
            deleteButton.addEventListener("click", function() {
                const targetRow = document.getElementById("context-menu").targetRow;
                if (targetRow) {
                    const costItemId = parseInt(targetRow.getAttribute("id"));
                    let expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
                    expandedState = CostUI.deleteRow(targetRow, expandedState)
                    localStorage.setItem('expandedState', JSON.stringify(expandedState));
                    callbacks.deleteCostItem(costItemId);
                }
            });
            deleteButton.hasListener = true;
        }

        const duplicateButton = document.getElementById("duplicate-button");
        if (duplicateButton && !duplicateButton.hasListener) {
            duplicateButton.addEventListener("click", function() {
                const targetRow = document.getElementById("context-menu").targetRow;
                if (targetRow) {
                    const costItemId = parseInt(targetRow.getAttribute("id"));
                    callbacks.duplicateCostItem(costItemId);
                }
            });
            duplicateButton.hasListener = true;
        }
    }

    static deleteRow(targetRow, expandedState) {
        if (!targetRow) {
            return
        }
        delete expandedState[targetRow.id]
        targetRow.remove()
        const subRows = document.querySelectorAll(`[parent-id='${targetRow.id}']`);
        subRows.forEach(subRow => {
            CostUI.deleteRow(subRow, expandedState)
        });
        return expandedState
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
        const levels = 10;
        const colorScheme = [];
        for (let i = 0; i < levels; i++) {
            colorScheme.push(CostUI.lightenColor(baseColor, i * 5));
        }
        return colorScheme;
    }
    
    static lightenColor(color, percent) {
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
            const level = index % colorScheme.length;
            row.style.backgroundColor = colorScheme[level];
        });
    }
    

    static createColorPicker() {
        const colorPicker = document.createElement("input");
        colorPicker.type = "color";
        colorPicker.id = "color-picker";
        colorPicker.value = "#ff0000";
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
        data.forEach(costItem => {
            const row = CostUI.createRow(costItem, nestingLevel, parentID, callbacks);
            container.appendChild(row);

            if (costItem.is_nested_by && costItem.is_nested_by.length > 0) {
                CostUI.createCostItem(costItem.is_nested_by, container, nestingLevel + 1, costItem.id, callbacks);
            }
        });
    }

    static createRow(costItem, nestingLevel, parentID, callbacks = {}) {
        const totalQuantity = costItem.TotalCostQuantity ? parseFloat(costItem.TotalCostQuantity).toFixed(2) : '-';
        const row = CostUI.createTableRow(costItem, nestingLevel, parentID);
        const expandButton = CostUI.createExpandButton(costItem);
        const nameCell = CostUI.createNameCell(costItem, nestingLevel, expandButton, callbacks);
        const totalCostQuantityCell = CostUI.createTableCell(totalQuantity);
        const unitSymbolCell = CostUI.createTableCell(costItem.UnitSymbol);
        const totalAppliedValueCell = CostUI.createTableCell(costItem.TotalAppliedValue);
        const totalCostCell = CostUI.createTotalCostCell(costItem);
        const flexContainerCell = CostUI.createFlexContainerCell(costItem, callbacks);
    
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
    
    static createTableRow(costItem, nestingLevel, parentID) {
        const row = document.createElement("tr");
        row.setAttribute("id", costItem.id);
        row.setAttribute("parent-id", parentID);
        if (nestingLevel > 0) {
            row.classList.add(`level-${nestingLevel}`);
        }
        return row;
    }

    static createExpandButton(row) {
        const expandButton = document.createElement("i");
        expandButton.classList.add("action-button");
        expandButton.classList.add("fa-solid");
        expandButton.classList.add("fa-angle-right");
    
        if (row.is_nested_by && row.is_nested_by.length > 0) {
            expandButton.classList.add('fa-angle-right');
        } else {
            expandButton.style.visibility = "hidden";
        }
    
        expandButton.addEventListener("click", function(event) {
            event.stopPropagation(); 
            let isExpanded = CostUI.isRowExpanded(row.id);
            console.log("Row is expanded", isExpanded);
            if (event.shiftKey) {
                if (isExpanded) {
                    CostUI.contractRow(row.id);
                    CostUI.updateExpandedState(row.id, false, true);
                } else {
                    CostUI.expandRow(row.id);
                    CostUI.updateExpandedState(row.id, true, true);
                }
            } else {
                if (isExpanded) {
                    CostUI.contractRow(row.id);
                    CostUI.updateExpandedState(row.id, false);
                }
                else {
                    CostUI.expandRow(row.id);
                    CostUI.updateExpandedState(row.id, true);
                }
            }
            CostUI.applyExpandedState();
        });
    
        return expandButton;
    }
    

    static hideRow(id) {
        const row = document.getElementById(id);
        if (row) {
            row.classList.add("nested");
        }
        
    }

    static contractRow(parentId, recursive=false) {
        CostUI.updateToggleButton(parentId, 'contract');
        const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
        rows.forEach(row => {
            const childId = row.getAttribute('id');
            CostUI.hideRow(childId);
            if (recursive || (childId && CostUI.isRowExpanded(childId))) {
                CostUI.contractRow(childId, recursive)
            }
            // CostUI.contractRow(childId);
        });
    }

    static showRow(id) {
        const row = document.getElementById(id);
        if (row) {
            row.classList.remove("nested");
        }
    }

    static updateToggleButton(id, type='contract') {
        const toggleButton = document.querySelector(`[id='${id}'] .action-button`);
        if (!toggleButton) {
            return;
        }
        if (type === 'expand') {
            toggleButton.classList.remove("fa-angle-right");
            toggleButton.classList.add("fa-angle-up");
        }
        else {
            toggleButton.classList.remove("fa-angle-up");
            toggleButton.classList.add("fa-angle-right");
        }
    }

    static expandRow(parentId, recursive=false) {
        CostUI.updateExpandedState(parentId, true);
        CostUI.updateToggleButton(parentId, 'expand');
        const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
        rows.forEach(row => {
            const childId = row.getAttribute('id');
            CostUI.showRow(childId);
            if (recursive || (childId && CostUI.isRowExpanded(childId))) {
                CostUI.expandRow(childId, recursive);
            }
        });
    }

    static updateExpandedState(id, isExpanded, recursive=false) {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
        expandedState[id] = isExpanded;
        localStorage.setItem('expandedState', JSON.stringify(expandedState));
        if (recursive) {
            const rows = document.querySelectorAll(`[parent-id='${id}']`);
            rows.forEach(row => {
                CostUI.updateExpandedState(row.id, isExpanded, recursive);
            });
        }
    }

    static applyExpandedState() {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || CostUI.getAllCostItemsIds().reduce((acc, id) => {
            acc[id] = true;
            return acc;
        }, {});

        console.log("Expanded state", expandedState);

        Object.keys(expandedState).forEach(id => {
            if (expandedState[id]) {
                CostUI.expandRow(id);
            } else {
                CostUI.contractRow(id);
            }
        });
    }

    static isRowExpanded(id) {
        const expandedState = JSON.parse(localStorage.getItem('expandedState')) || {};
        return expandedState[id] || false;
    }
    
    static createNameCell(costItem, nestingLevel, expandButton, callbacks) {
        const nameCell = document.createElement("td");
        const nameInput = document.createElement("input");
        nameInput.value = costItem.name ? costItem.name : "Unnamed";
    
        nameInput.addEventListener("change", function() {
            callbacks.editCostItemName ? callbacks.editCostItemName(costItem.id, this.value) : null;
        });
    
        nameInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                callbacks.editCostItemName ? callbacks.editCostItemName(costItem.id, this.value) : null;
            }
        });
    
        nameCell.style.paddingLeft = nestingLevel * 20 + "px";
        nameCell.appendChild(expandButton);
        nameCell.appendChild(nameInput);
        const widthButton = 20;
        nameInput.style.width = "calc(100% - " + widthButton + "%)";
        return nameCell;
    }
    
    static createTableCell(content) {
        const cell = document.createElement("td");
        cell.textContent = content;
        return cell;
    }
    
    static createTotalCostCell(costItem) {
        const totalCostCell = document.createElement("td");
        const totalCost = parseFloat(costItem.TotalCost).toFixed(2);
        totalCostCell.textContent = costItem.is_sum ? totalCost + " (Σ)" : totalCost;
        return totalCostCell;
    }
    
    static createFlexContainerCell(costItem, callbacks) {
        const divFlex = document.createElement("div");
        divFlex.classList.add("flex-container");
    
        const addButton = CostUI.createAddButton(costItem, callbacks);
        const selectButton = CostUI.createSelectButton(costItem, callbacks);
    
        divFlex.appendChild(addButton);
        divFlex.appendChild(selectButton);
    
        const flexContainerCell = document.createElement("td");
        flexContainerCell.appendChild(divFlex);
        return flexContainerCell;
    }
    
    static createAddButton(costItem, callbacks) {
        const addButton = document.createElement("button");
        addButton.textContent = "+";
        addButton.classList.add("add-button");
        addButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.addCostItem ? callbacks.addCostItem(costItem.id) : null;
        });
        return addButton;
    }
    
    static createSelectButton(costItem, callbacks) {
        const selectButton = document.createElement("button");
        selectButton.classList.add("action-button");
        selectButton.textContent = "Select";
        selectButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.selectAssignedElements ? callbacks.selectAssignedElements(costItem.id) : null;
        });
        return selectButton;
    }

    static highlightCostItem(id) {
        const row = document.getElementById(id);
        if (row) {
            row.classList.add("highlighted");
        }
    }

    static unhighlightCostItem(id) {
        const row = document.getElementById(id);
        if (row) {
            row.classList.remove("highlighted");
        }   
    }

    static getAllCostItemsIds() {
        const rows = document.querySelectorAll("#cost-items tr");
        const ids = [];
        rows.forEach(row => {
            ids.push(row.id);
        });
        return ids;
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
        cardButton.classList.add("action-button");
        cardButton.textContent = "Load";
        cardButton.addEventListener("click", callback);

        cardBody.appendChild(cardTitle);
        cardBody.appendChild(mainContainer);
        cardBody.appendChild(cardButton);
        card.appendChild(cardBody);

        return card;
    }

    static getRowNameCell(costItemId) {
        return document.getElementById(costItemId).querySelector("td input");
    }

    static getCostItemName(costItemId) {
        return CostUI.getRowNameCell(costItemId).value;
    }

    static createCostValuesForm({ costItemId, costValues, callbacks }) {
        const formId = "cost-values-form-" + costItemId;
        let existingForm = document.getElementById(formId);
        if (existingForm) {
            existingForm.remove();
        }
    
        const form = CostUI.createFormElement(formId, "cost-values-form");
        const costItemName = CostUI.getCostItemName(costItemId);
        const header = CostUI.createHeader("Cost Values Form for " + costItemName);
        form.appendChild(header);
        
        const table = CostUI.createCostValuesTable(costItemId, ["Type", "Category", "Value", ""]);
        
        costValues.forEach(costValue => {
            const tr = CostUI.createCostvaluesRow(costItemId, costValue, callbacks);
            table.appendChild(tr);
        });
        
        form.appendChild(table);
    
        const addButton = CostUI.createAddCostValueButton(costItemId, callbacks);
        form.appendChild(addButton);
        
        const closeButton = CostUI.createCloseButton(form);
        form.appendChild(closeButton);
        
        CostUI.makeHeaderDraggable(header, form);
        
        document.body.appendChild(form);
        
        return form;
    }
    

    static getCostValuesTable(costItemId) {
        return document.getElementById("cost-values-table-" + costItemId);
    }

    static addNewCostValueRow(costItemId, costValueId, costValueCallbacks) {
        const table = CostUI.getCostValuesTable(costItemId);
        if (!table) {
            console.log("Cost values table not found for cost item ID:", costItemId);
            return;
        }
        console.log("Adding new cost value row", costValueId);
        console.log(table)
        const tr = CostUI.createCostvaluesRow(costItemId, {"category": "", "name": "", "applied_value": 0, "id": costValueId, "parent": costItemId}, costValueCallbacks);
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

    static createCostvaluesRow(costItemId,costValue, costValueCallbacks) {
        function cleanLabel(value) {
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
        
            if (selectedType === "SUM") {
                const costValueId = parseInt(this.closest("tr").getAttribute("id"));
                const appliedValue = parseFloat(valueCell1.querySelector("input").value);
                const costCategory = categoryCell.querySelector("input").value;
        
                if (costValueCallbacks.editCostValues) {
                    costValueCallbacks.editCostValues(costItemId, [
                        {
                            costType: selectedType,
                            costCategory: costCategory,
                            appliedValue: appliedValue,
                            id: costValueId,
                            costItemId: costItemId
                        }
                    ]);
                }
            }
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

        const inputValue = valueCell1.querySelector("input");
        function handleCostValueChange(costItemId) {
            const costValueData = {
                costType: typeCell.querySelector("select").value,
                costCategory: categoryCell.querySelector("input").value,
                appliedValue: parseFloat(this.value),
                id: costValue.id,
                costItemId: costItemId
            }
            if (costValueCallbacks.editCostValues) {
                costValueCallbacks.editCostValues(costItemId, [costValueData]);
            }
        }
        
        inputValue.addEventListener("change", handleCostValueChange.bind(inputValue, costItemId));
        
        inputValue.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                handleCostValueChange.call(this, costItemId);
            }
        });
        const deleteCell = document.createElement("td");
        tr.appendChild(deleteCell);
        const deleteButton = document.createElement("button");
        deleteButton.classList.add("action-button");
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", function() {
            costValueCallbacks.deleteCostValue(costItemId, costValue.id);
            tr.remove();
        });
        deleteCell.appendChild(deleteButton);
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
        addButton.classList.add("action-button");
        addButton.textContent = " + Add Cost Value";
        addButton.addEventListener("click", function(e) {
            e.preventDefault();
            callbacks.addCostValue ? callbacks.addCostValue(costItemId) : null;
        });
        return addButton;
    }
    
    static createFormElement(id, className) {
        const form = document.createElement("form");
        form.id = id;
        form.classList.add(className);
        form.style.position = "absolute";
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
            const costItemId = form.id.split("-")[3];
            CostUI.unhighlightCostItem(costItemId);
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
