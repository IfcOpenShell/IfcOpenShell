export class CostUI {
    constructor() {}

    createButton() {
        console.log("Button created");
    }

    createInput() {
        console.log("Input created");
    }

    static isCostScheduleLoaded(id) {
        const existingTable = document.getElementById('cost-items-' + id);
        return existingTable !== null;
    }

    static removeCostSchedule(id) {
        document.getElementById("cost-items-" + id).remove();
    }
    static createTable(id) {
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
        CostUI.createContextMenu();

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
            th {
                position: relative;
            }
            .resizer {
                position: absolute;
                right: 0;
                top: 0;
                width: 5px;
                height: 100%;
                cursor: col-resize;
                user-select: none;
            }
            .context-menu {
                display: none;
                position: absolute;
                background-color: white;
                border: 1px solid #ccc;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                z-index: 1000;
            }
            .context-menu button {
                display: block;
                width: 100%;
                padding: 8px;
                border: none;
                background: none;
                text-align: left;
                cursor: pointer;
            }
            .context-menu button:hover {
                background-color: #f0f0f0;
            }
            #cost-items tr:hover {
                background-color: #f0f0f0; /* Change this color to your desired hover color */
            }
        `;
        document.head.appendChild(style);
    }

    static createContextMenu() {
        // Create context menu
        const contextMenu = document.createElement("div");
        contextMenu.id = "context-menu";
        contextMenu.classList.add("context-menu");
        contextMenu.innerHTML = `
            <button id="edit-button">Edit</button>
            <button id="delete-button">Delete</button>
            <button id="duplicate-button">Duplicate</button>
        `;
        document.body.appendChild(contextMenu);

        // Add event listeners for context menu
        document.addEventListener("contextmenu", function(event) {
            event.preventDefault();
            const targetRow = event.target.closest("tr");
            if (targetRow && targetRow.parentElement.id === "cost-items") {
                const contextMenu = document.getElementById("context-menu");
                contextMenu.style.display = "block";
                contextMenu.style.left = `${event.pageX}px`;
                contextMenu.style.top = `${event.pageY}px`;

                // Store the target row in the context menu for later use
                contextMenu.targetRow = targetRow;
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

        document.getElementById("edit-button").addEventListener("click", function() {
            const targetRow = document.getElementById("context-menu").targetRow;
            if (targetRow) {
                // Implement your edit action here
                console.log("Edit row:", targetRow.getAttribute("id"));
            }
        });

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
        const [table, tbody] = CostUI.createTable(blenderID);
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
        const row = document.createElement("tr");
        row.setAttribute("id", obj.id);
        row.setAttribute("parent-id", parentID);
        if (nestingLevel > 0) {
            row.classList.add("nested");
            row.classList.add(`level-${nestingLevel}`);
        }
        const expandButton = document.createElement("button");
        expandButton.classList.add("toggle-button");
        if (obj.is_nested_by && obj.is_nested_by.length > 0) {
            expandButton.textContent = ">";
        } else {
            expandButton.style.visibility = "hidden";
        }
        //row.appendChild(expandButton);

        expandButton.addEventListener("click", function() {
            CostUI.contractExpandRow.call(this, obj.id);
        });

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
        row.appendChild(nameCell);

        const totalCostQuantityCell = document.createElement("td");
        totalCostQuantityCell.textContent = obj.TotalCostQuantity;
        row.appendChild(totalCostQuantityCell);

        const unitSymbolCell = document.createElement("td");
        unitSymbolCell.textContent = obj.UnitSymbol;
        row.appendChild(unitSymbolCell);

        const totalAppliedValueCell = document.createElement("td");
        totalAppliedValueCell.textContent = obj.TotalAppliedValue;
        row.appendChild(totalAppliedValueCell);

        const totalCostCell = document.createElement("td");
        const totalCost = parseFloat(obj.TotalCost).toFixed(2);

        totalCostCell.textContent = obj.is_sum ? totalCost + " (Σ)" : totalCost;

        row.appendChild(totalCostCell);

        const divFlex = document.createElement("div");
        divFlex.classList.add("flex-container");
        const addButton = document.createElement("button");
        addButton.textContent = "+";
        addButton.classList.add("add-button");
        addButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.addCostItem ? callbacks.addCostItem(obj.id) : null;
        });

        const selectButton = document.createElement("button");
        selectButton.textContent = "Select";
        selectButton.addEventListener("click", function(e) {
            e.stopPropagation();
            callbacks.selectAssignedElements ? callbacks.selectAssignedElements(obj.id) : null;
        });

        divFlex.appendChild(addButton);
        divFlex.appendChild(selectButton);

        const flexContainerCell = document.createElement("td");
        flexContainerCell.appendChild(divFlex);
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
}
