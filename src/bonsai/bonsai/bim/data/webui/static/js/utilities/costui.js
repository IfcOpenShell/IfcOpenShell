export class CostUI {
  constructor() {}

  static isCostScheduleLoaded(id) {
    const existingTable = document.getElementById("cost-items-" + id);
    return existingTable !== null;
  }

  static removeCostSchedule(id) {
    const table = document.getElementById("cost-items-" + id);
    table ? table.parentElement.remove() : null;
  }
  static createCostTable({ costSchedule, currency, callbacks }) {
    const isScheduleOfRates = costSchedule.PredefinedType === "SCHEDULEOFRATES";
    let tableWrapper;
    const id = costSchedule.id;
    if (CostUI.isCostScheduleLoaded(id)) {
      const table = document.getElementById("cost-items-" + id);
      tableWrapper = table.parentElement;
      table.remove();
    } else {
      tableWrapper = document.createElement("div");
      tableWrapper.classList.add("table-wrapper");
      document.getElementById("cost-items").appendChild(tableWrapper);
      const tableHeader = document.createElement("div");
      tableHeader.classList.add("form-header");
      const text = CostUI.Text(
        costSchedule.Name,
        "fa-solid fa-money-bill-wave",
        "x-large"
      );

      const callback = () => {
        tableWrapper.remove();
        CostUI.unhighlightElement("schedule-" + id);
      };
      let closeButton = CostUI.createCloseButton(callback);
      tableHeader.appendChild(text);
      tableHeader.appendChild(closeButton);
      tableWrapper.appendChild(tableHeader);
    }
    const table = document.createElement("table");
    table.id = "cost-items-" + id;
    const tbody = document.createElement("tbody");
    const columnHeaders = [
      "ID",
      "Name",
      "Quantity",
      "Unit",
      "Cost (" + currency + ")",
      "Total Cost (" + currency + ")",
      "Actions",
    ];
    if (isScheduleOfRates) {
      columnHeaders.splice(2, 1);
      columnHeaders[3] = "Rate (" + currency + ")";
      columnHeaders[4] = "Total Rate (" + currency + ")";
    }
    const thead = document.createElement("thead");
    const tr = document.createElement("tr");
    thead.appendChild(tr);

    for (let i = 0; i < columnHeaders.length; i++) {
      const th = document.createElement("th");
      th.textContent = columnHeaders[i];
      tr.appendChild(th);

      if (i < columnHeaders.length - 1) {
        const resizer = document.createElement("div");
        resizer.classList.add("resizer");
        th.appendChild(resizer);
        CostUI.addResizer(resizer);
      }
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    tableWrapper.appendChild(table);

    CostUI.createContextMenu(callbacks);
    table.get_blender_id = function () {
      return this.getAttribute("id").split("-")[2];
    };

    return [table, tbody];
  }

  static deleteCostItem(costItemId) {
    const costItemRow = CostUI.getCostItemRow(costItemId);
    let expandedState = JSON.parse(localStorage.getItem("expandedState")) || {};
    expandedState = CostUI.deleteCostItemRow(costItemRow, expandedState);
    localStorage.setItem("expandedState", JSON.stringify(expandedState));
  }

  static createContextMenu(callbacks) {
    const contextMenu = document.createElement("div");
    contextMenu.id = "context-menu";
    contextMenu.classList.add("context-menu");
    contextMenu.innerHTML = `
                    <button id="edit-cost-values-button">Edit Cost Values</button>
                    <button id="add-cost-item-button">Add sub-cost</button>
                    <button id="duplicate-button">Duplicate</button>
                    <button id="delete-cost-item">Delete</button>
                    <button id="assign-selection">Assign Selection</button>
            `;
    document.body.appendChild(contextMenu);

    document.addEventListener("contextmenu", function (event) {
      event.preventDefault();
      const targetRow = event.target.closest("tr");
      const targetCell = event.target.closest("td");
      if (targetRow) {
        const isCostTable = targetRow.parentElement.parentElement
          ? targetRow.parentElement.parentElement.id.includes("cost-items")
          : false;
        if (isCostTable) {
          const contextMenu = document.getElementById("context-menu");
          contextMenu.style.display = "block";
          contextMenu.style.left = `${event.pageX}px`;
          contextMenu.style.top = `${event.pageY}px`;
          contextMenu.targetRow = targetRow;
          contextMenu.targetCell = targetCell;
        } else {
          document.getElementById("context-menu").style.display = "none";
        }
      }
    });

    document.addEventListener("click", function (event) {
      const contextMenu = document.getElementById("context-menu");
      if (!contextMenu.contains(event.target)) {
        contextMenu.style.display = "none";
      }
    });

    const editCostValuesButton = document.getElementById(
      "edit-cost-values-button"
    );
    const addButton = document.getElementById("add-cost-item-button");
    const deleteCostItemButton = document.getElementById("delete-cost-item");
    const duplicateButton = document.getElementById("duplicate-button");
    const getSelectedProducts = document.getElementById("assign-selection");

    function handleButtonClick(button, callback) {
      if (button && !button.hasListener) {
        button.addEventListener("click", function () {
          const targetRow = document.getElementById("context-menu").targetRow;
          if (targetRow) {
            const costItemId = parseInt(targetRow.getAttribute("id"));
            callback(costItemId);
          }
          document.getElementById("context-menu").style.display = "none";
        });
        button.hasListener = true;
      }
    }

    handleButtonClick(deleteCostItemButton, callbacks.deleteCostItem);
    handleButtonClick(duplicateButton, callbacks.duplicateCostItem);
    handleButtonClick(getSelectedProducts, callbacks.enableEditingQuantities);
    handleButtonClick(editCostValuesButton, callbacks.enableEditingCostValues);
    handleButtonClick(addButton, callbacks.addCostItem);
    handleButtonClick(deleteCostItemButton, callbacks.deleteCostItem);

    addTableListeners(callbacks);

    function addTableListeners(callbacks) {
      function getColumnNames(tableId) {
        const table = document.getElementById(tableId);
        const headerRow = table.querySelector("thead tr");
        return Array.from(headerRow.children).map((headerCell) =>
          headerCell.textContent.trim()
        );
      }
      document
        .getElementById("cost-items")
        .addEventListener("click", function (event) {
          const targetRow = event.target.closest("tr");
          const targetCell = event.target.closest("td");
          if (targetRow && targetCell) {
            const columnIndex = Array.from(targetRow.children).indexOf(
              targetCell
            );
            const tableId = targetRow.parentElement.parentElement.id;
            const costItemId = parseInt(targetRow.getAttribute("id"));
            const columnName = getColumnNames(tableId)[columnIndex];
            if (
              (columnName.includes("Cost") || columnName.includes("Rate")) &&
              !columnName.includes("Total")
            ) {
              callbacks.enableEditingCostValues
                ? callbacks.enableEditingCostValues(costItemId)
                : null;
            }
            if (columnName === "Quantity") {
              callbacks.enableEditingQuantities
                ? callbacks.enableEditingQuantities(costItemId)
                : null;
            }
          }
        });
    }
  }

  static deleteCostItemRow(targetRow, expandedState) {
    if (!targetRow) {
      return;
    }
    delete expandedState[targetRow.id];
    targetRow.remove();
    const subRows = document.querySelectorAll(`[parent-id='${targetRow.id}']`);
    subRows.forEach((subRow) => {
      CostUI.deleteCostItemRow(subRow, expandedState);
    });
    return expandedState;
  }

  static addResizer(resizer) {
    let startX, startWidth, th;

    resizer.addEventListener("mousedown", function (e) {
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
      G = ((num >> 8) & 0x00ff) + amt,
      B = (num & 0x0000ff) + amt;
    return `#${(
      0x1000000 +
      (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
      (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
      (B < 255 ? (B < 1 ? 0 : B) : 255)
    )
      .toString(16)
      .slice(1)
      .toUpperCase()}`;
  }

  static applyColorScheme(tableId, colorScheme) {
    const rows = document.querySelectorAll(`#${tableId} tbody tr`);
    rows.forEach((row, index) => {
      const level = index % colorScheme.length;
      row.style.backgroundColor = colorScheme[level];
    });
  }

  static enableAddingCostSchedule(types, addCostSchedule) {
    const addNewSchedule = document.getElementById("add-cost-schedule");

    addNewSchedule.addEventListener("click", function () {
      const name = "Add New Cost Schedule";

      const form = CostUI.Form({
        id: "add-cost-schedule-form",
        name: name,
        icon: "fa-solid fa-money-bill-wave",
      });

      const nameLabel = document.createElement("label");
      nameLabel.textContent = "Name:";
      form.appendChild(nameLabel);
      form.classList.add("column-container");

      const nameInput = document.createElement("input");
      nameInput.type = "text";
      nameInput.name = "name";
      form.appendChild(nameInput);

      const typeLabel = document.createElement("label");
      typeLabel.textContent = "Type:";
      form.appendChild(typeLabel);

      const typeSelect = document.createElement("select");
      typeSelect.name = "Predefined Type";

      types.forEach((type) => {
        const option = document.createElement("option");
        option.value = type.name;
        option.textContent = type.name;
        option.title = type.description;
        typeSelect.appendChild(option);
      });
      form.appendChild(typeSelect);

      const submitButton = document.createElement("button");
      submitButton.textContent = "Add";
      submitButton.classList.add("action-button");
      form.appendChild(submitButton);

      document
        .getElementById("add-cost-schedule-form")
        .addEventListener("submit", function (event) {
          event.preventDefault();
          const formData = new FormData(
            document.getElementById("add-cost-schedule-form")
          );
          const data = {};
          formData.forEach((value, key) => {
            data[key] = value;
          });
          addCostSchedule(data.name, data["Predefined Type"]);
          document.getElementById("add-cost-schedule-form").remove();
        });
    });
  }

  static createColorPicker() {
    const div = document.createElement("div");
    div.classList.add("row-container");
    const colorPicker = document.createElement("input");
    colorPicker.type = "color";
    colorPicker.id = "color-picker";
    colorPicker.value = "#ff0000";
    const colorText = document.createElement("p");
    colorText.textContent = "Select a color to change row color:";
    div.appendChild(colorText);
    div.appendChild(colorPicker);

    colorPicker.addEventListener("input", function () {
      const baseColor = colorPicker.value;
      const colorScheme = CostUI.generateColorScheme(baseColor);
      CostUI.applyColorScheme("cost-items", colorScheme);
    });
    const colorScheme = CostUI.generateColorScheme("#000000");
    CostUI.applyColorScheme("cost-items", colorScheme);
    return div;
  }

  static createCostSchedule({ costSchedule, currency, callbacks = {} }) {
    const [table, tbody] = CostUI.createCostTable({
      costSchedule,
      currency,
      callbacks,
    });
    if (costSchedule["cost_items"].length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.textContent = "No cost items found";
      tr.appendChild(td);
      tbody.appendChild(tr);

      const addSummaryCostItemButton = document.createElement("button");
      addSummaryCostItemButton.textContent = "Add Summary Cost Item";
      addSummaryCostItemButton.addEventListener("click", function () {
        callbacks.addSummaryCostItem
          ? callbacks.addSummaryCostItem(costSchedule.id)
          : null;
      });
      td.appendChild(addSummaryCostItemButton);
      addSummaryCostItemButton.classList.add("action-button");
    } else {
      CostUI.createCostTree({
        costItems: costSchedule["cost_items"],
        container: tbody,
        nestingLevel: 0,
        parentID: null,
        callbacks: callbacks,
        isScheduleOfRates: costSchedule.PredefinedType === "SCHEDULEOFRATES",
      });
      CostUI.applyExpandedState();
    }
  }

  static createCostTree({
    costItems,
    container,
    nestingLevel,
    parentID,
    callbacks,
    isScheduleOfRates = false,
  }) {
    costItems.forEach((costItem) => {
      const row = CostUI.addCostItemRow(
        costItem,
        nestingLevel,
        parentID,
        isScheduleOfRates,
        callbacks
      );
      container.appendChild(row);

      if (costItem.IsNestedBy && costItem.IsNestedBy.length > 0) {
        CostUI.createCostTree({
          costItems: costItem.IsNestedBy,
          container: container,
          nestingLevel: nestingLevel + 1,
          parentID: costItem.id,
          isScheduleOfRates: isScheduleOfRates,
          callbacks: callbacks,
        });
      }
    });
  }

  static format_number(number) {
    return new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      useGrouping: true,
    })
      .format(number)
      .replace(/,/g, " ");
  }

  static addCostItemRow(
    costItem,
    nestingLevel,
    parentID,
    isScheduleOfRates,
    callbacks = {}
  ) {
    const totalQuantity = costItem.TotalCostQuantity
      ? CostUI.format_number(costItem.TotalCostQuantity)
      : "-";
    let appliedValue = costItem.TotalAppliedValue
      ? CostUI.format_number(costItem.TotalAppliedValue)
      : "-";
    const unitBasisValue = costItem.UnitBasisValueComponent
      ? CostUI.format_number(costItem.UnitBasisValueComponent)
      : null;
    if (isScheduleOfRates && unitBasisValue) {
      appliedValue = appliedValue + " / " + unitBasisValue;
    }
    const row = CostUI.createCostItemRow(costItem, nestingLevel, parentID);
    const identification = costItem.Identification
      ? costItem.Identification
      : "XXX";
    const idCell = CostUI.createTableCell(identification);
    row.appendChild(idCell);

    const expandButton = CostUI.createExpandButton(costItem);
    const nameCell = CostUI.createNameCell(
      costItem,
      nestingLevel,
      expandButton,
      callbacks
    );
    row.appendChild(nameCell);

    if (isScheduleOfRates) {
      const unitBasisUnitSymbol = costItem.UnitBasisUnitSymbol
        ? costItem.UnitBasisUnitSymbol
        : "-";
      const unitBasisUnitSymbolCell =
        CostUI.createTableCell(unitBasisUnitSymbol);
      row.appendChild(unitBasisUnitSymbolCell);
    } else {
      const totalCostQuantityCell = CostUI.createTableCell(totalQuantity);
      row.appendChild(totalCostQuantityCell);
      totalCostQuantityCell.classList.add("clickable-cell");
      const unitSymbolCell = CostUI.createTableCell(costItem.UnitSymbol);
      row.appendChild(unitSymbolCell);
    }

    const totalAppliedValueCell = CostUI.createCostCell(appliedValue);
    totalAppliedValueCell.classList.add("clickable-cell");
    row.appendChild(totalAppliedValueCell);

    const totalCostCell = CostUI.createTotalCostCell(
      costItem,
      isScheduleOfRates,
      callbacks.addSumCostValue
    );
    row.appendChild(totalCostCell);

    const actionsCell = CostUI.costItemActions(costItem, callbacks);
    actionsCell.classList.add("actions-column");
    row.appendChild(actionsCell);

    row.get_id = function () {
      return this.getAttribute("id");
    };

    row.isRate = isScheduleOfRates;
    row.get_parent = function () {
      const parentId = this.getAttribute("parent-id");
      return parentId ? document.getElementById(parentId) : null;
    };

    return row;
  }

  static createCostItemRow(costItem, nestingLevel, parentID) {
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

    if (row.IsNestedBy && row.IsNestedBy.length > 0) {
      expandButton.classList.add("fa-angle-right");
    } else {
      expandButton.style.visibility = "hidden";
    }

    expandButton.addEventListener("click", function (event) {
      event.stopPropagation();
      let isExpanded = CostUI.isRowExpanded(row.id);
      if (event.shiftKey) {
        if (isExpanded) {
          CostUI.contractRow(row.id, true);
          CostUI.updateExpandedState(row.id, false, true);
        } else {
          CostUI.expandRow(row.id, true);
          CostUI.updateExpandedState(row.id, true, true);
        }
      } else {
        if (isExpanded) {
          CostUI.contractRow(row.id, true);
          CostUI.updateExpandedState(row.id, false);
        } else {
          CostUI.expandRow(row.id);
          CostUI.updateExpandedState(row.id, true);
        }
      }
    });

    return expandButton;
  }

  static hideRow(id) {
    const row = document.getElementById(id);
    if (row) {
      row.classList.add("nested");
    }
  }

  static contractRow(parentId, recursive = false) {
    CostUI.updateToggleButton(parentId, "contract");
    const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
    rows.forEach((row) => {
      const childId = row.getAttribute("id");
      CostUI.hideRow(childId);
      if (recursive || (childId && CostUI.isRowExpanded(childId))) {
        CostUI.contractRow(childId, recursive);
      }
    });
  }

  static showRow(id) {
    const row = document.getElementById(id);
    if (row) {
      row.classList.remove("nested");
    }
  }

  static updateToggleButton(id, type = "contract") {
    const toggleButton = document.querySelector(`[id='${id}'] .action-button`);
    if (!toggleButton) {
      return;
    }
    if (type === "expand") {
      toggleButton.classList.remove("fa-angle-right");
      toggleButton.classList.add("fa-angle-up");
    } else {
      toggleButton.classList.remove("fa-angle-up");
      toggleButton.classList.add("fa-angle-right");
    }
  }

  static expandRow(parentId, recursive = false) {
    CostUI.updateExpandedState(parentId, true);
    CostUI.updateToggleButton(parentId, "expand");
    const rows = document.querySelectorAll(`[parent-id='${parentId}']`);
    rows.forEach((row) => {
      const childId = row.getAttribute("id");
      CostUI.showRow(childId);
      if (recursive || (childId && CostUI.isRowExpanded(childId))) {
        CostUI.expandRow(childId, recursive);
      }
    });
  }

  static updateExpandedState(id, isExpanded, recursive = false) {
    const expandedState =
      JSON.parse(localStorage.getItem("expandedState")) || {};
    expandedState[id] = isExpanded;
    localStorage.setItem("expandedState", JSON.stringify(expandedState));
    if (recursive) {
      const rows = document.querySelectorAll(`[parent-id='${id}']`);
      rows.forEach((row) => {
        CostUI.updateExpandedState(row.id, isExpanded, recursive);
      });
    }
  }

  static applyExpandedState() {
    const expandedState =
      JSON.parse(localStorage.getItem("expandedState")) ||
      CostUI.getAllCostItemsIds().reduce((acc, id) => {
        acc[id] = true;
        return acc;
      }, {});

    Object.keys(expandedState).forEach((id) => {
      if (expandedState[id]) {
        CostUI.expandRow(id);
      } else {
        CostUI.contractRow(id);
      }
    });
  }

  static isRowExpanded(id) {
    const expandedState =
      JSON.parse(localStorage.getItem("expandedState")) || {};
    return expandedState[id] || false;
  }

  static createNameCell(costItem, nestingLevel, expandButton, callbacks) {
    const nameCell = document.createElement("td");
    const nameInput = document.createElement("input");
    nameInput.value = costItem.Name ? costItem.Name : "Unnamed";

    nameInput.addEventListener("change", function () {
      callbacks.editCostItemName
        ? callbacks.editCostItemName(costItem.id, this.value)
        : null;
    });

    nameInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        callbacks.editCostItemName
          ? callbacks.editCostItemName(costItem.id, this.value)
          : null;
      }
    });

    nameCell.style.paddingLeft = nestingLevel * 20 + "px";
    nameCell.classList.add("row-container");
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

  static createCostCell(appliedValue) {
    return CostUI.createTableCell(appliedValue);
  }

  static createTotalCostCell(costItem, isScheduleOfRates, callback) {
    const totalCostCell = document.createElement("td");
    const totalCost = CostUI.format_number(costItem.TotalCost);
    totalCostCell.textContent = totalCost;
    if (isScheduleOfRates) {
      return totalCostCell;
    }
    if (costItem.IsSum) {
      totalCostCell.textContent = totalCost + " *";
    } else if (!costItem.TotalCost) {
      const button = CostUI.createButton("Sum", "fa-solid fa-calculator");
      button.addEventListener("click", function () {
        const costItemId = parseInt(this.closest("tr").getAttribute("id"));
        callback(costItemId);
      });
      const onHoverElement = CostUI.onHoverElement();
      onHoverElement.appendChild(button);
      totalCostCell.appendChild(onHoverElement);
    }

    return totalCostCell;
  }

  static onHoverElement() {
    const div = document.createElement("div");
    div.classList.add("actions-column");
    div.classList.add("append-right");
    return div;
  }

  static costItemActions(costItem, callbacks) {
    const divFlex = document.createElement("div");
    divFlex.classList.add("row-container");
    const addCostItem = CostUI.addCostItemButton(
      costItem.id,
      callbacks.addCostItem
    );
    const selectButton = CostUI.createSelectButton(
      costItem.id,
      callbacks.selectAssignedElements
    );
    const deleteButton = CostUI.deleteCostItemButton(
      costItem.id,
      callbacks.deleteCostItem
    );
    const duplicateButton = CostUI.duplicateCostItemButton(
      costItem.id,
      callbacks.duplicateCostItem
    );

    [addCostItem, duplicateButton, selectButton, deleteButton].forEach(
      (button) => {
        divFlex.appendChild(button);
      }
    );

    const actionsCell = document.createElement("td");
    actionsCell.appendChild(divFlex);
    return actionsCell;
  }

  static duplicateCostItemButton(costItemId, duplicateCostItem) {
    const duplicateButton = CostUI.createButton(
      "Duplicate",
      "fa-solid fa-copy"
    );
    duplicateButton.addEventListener(
      "click",
      duplicateCostItem.bind(null, costItemId)
    );
    return duplicateButton;
  }

  static addCostItemButton(costItemId, addCostItem) {
    const addCostItemButton = CostUI.createButton(
      "Add Sub-Cost",
      "fa-solid fa-plus"
    );
    addCostItemButton.addEventListener(
      "click",
      addCostItem.bind(null, costItemId)
    );
    return addCostItemButton;
  }

  static createSelectButton(costItemId, selectAssignedElements) {
    const selectButton = CostUI.createButton(
      "Select",
      "fa-solid fa-arrow-pointer"
    );
    selectButton.addEventListener(
      "click",
      selectAssignedElements.bind(null, costItemId)
    );
    return selectButton;
  }

  static deleteCostItemButton(costItemId, deleteCostItem) {
    const deleteButton = CostUI.createButton("Delete", "fa-solid fa-trash");
    deleteButton.addEventListener(
      "click",
      deleteCostItem.bind(null, costItemId)
    );
    return deleteButton;
  }

  static createButton(text, icon) {
    const button = document.createElement("button");
    !icon ? (button.textContent = text) : null;
    icon
      ? button.classList.add("action-button", ...icon.split(" "))
      : button.classList.add("action-button");
    button.dataset.tooltip = text;
    return button;
  }

  static highlightElement(id) {
    const element = document.getElementById(id);
    if (element) {
      element.classList.add("highlighted");
    }
  }

  static unhighlightElement(id) {
    const element = document.getElementById(id);
    if (element) {
      element.classList.remove("highlighted");
    }
  }

  static getAllCostItemsIds() {
    const rows = document.querySelectorAll("#cost-items tr");
    const ids = [];
    rows.forEach((row) => {
      ids.push(row.id);
    });
    return ids;
  }

  static Text(label, icon = null, size = "medium") {
    const text = document.createElement("span");
    text.textContent = label;
    if (icon === null) {
      return text;
    }
    const div = document.createElement("div");
    div.classList.add("row-container");
    const i = document.createElement("i");
    i.className = icon;
    div.appendChild(i);
    div.appendChild(text);
    div.style.fontSize = size;
    return div;
  }

  static createCard(id, title, mainContainer, callback) {
    const card = document.createElement("div");
    card.classList.add("card");
    card.id = "schedule-" + id;

    const cardBody = document.createElement("div");
    cardBody.classList.add("card-body");

    const cardTitle = CostUI.Text(
      title,
      "fa-solid fa-money-bill-wave",
      "large"
    );
    cardTitle.classList.add("card-title");

    const cardButton = CostUI.createButton("Load", "fa-solid fa-repeat");
    cardButton.addEventListener("click", callback);

    cardBody.appendChild(cardTitle);
    cardBody.appendChild(mainContainer);
    cardBody.appendChild(cardButton);
    card.appendChild(cardBody);

    return card;
  }

  static getCostItemRow(costItemId) {
    return document.getElementById(costItemId);
  }

  static getRowNameCell(costItemId) {
    return CostUI.getCostItemRow(costItemId)
      ? CostUI.getCostItemRow(costItemId).querySelector("td input")
      : null;
  }

  static getCostItemName(costItemId) {
    return CostUI.getRowNameCell(costItemId)
      ? CostUI.getRowNameCell(costItemId).value
      : "Unnamed";
  }

  static createCostValuesForm({ costItemId, costValues, callbacks }) {
    const formId = "cost-values-form-" + costItemId;

    const costItemRow = CostUI.getCostItemRow(costItemId);
    const isRate = costItemRow.isRate;

    let existingForm = document.getElementById(formId);
    if (existingForm) {
      existingForm.remove();
    }
    const costItemName = CostUI.getCostItemName(costItemId);

    let formName = "Cost Values: " + costItemName;
    const form = CostUI.Form({
      icon: "fa-dollar-sign",
      id: formId,
      name: formName,
    });
    let headers;
    if (isRate) {
      headers = [
        "Type",
        "Category",
        "Value",
        "Unit Symbol",
        "Unit Component",
        "",
      ];
    } else {
      headers = ["Type", "Category", "Value", ""];
    }

    const { tableContainer, table } = CostUI.addTable({
      headers: headers,
      className: "cost-values-table",
      id: "cost-values-table-" + costItemId,
    });

    costValues.forEach((costValue) => {
      costValue.isRate = isRate;
      const tr = CostUI.createCostvaluesRow({
        costItemId,
        costValue,
        costValueCallbacks: callbacks,
      });
      table.appendChild(tr);
    });
    form.appendChild(tableContainer);
    if (!isRate) {
      //TODO: IMPLEMENT ADDING COST VALUES FOR COST RATES
      const addButton = CostUI.createAddCostValueButton(costItemId, callbacks);
      form.appendChild(addButton);
    }
    return form;
  }

  static getCostValuesTable(costItemId) {
    return document.getElementById("cost-values-table-" + costItemId);
  }

  static addNewCostValueRow(costItemId, costValueId, costValueCallbacks) {
    const table = CostUI.getCostValuesTable(costItemId);
    if (!table) {
      return;
    }
    const costItemRow = CostUI.getCostItemRow(costItemId);
    const isRate = costItemRow.isRate;
    let newData;
    if (isRate) {
      newData = {
        category: "",
        name: "",
        applied_value: 0,
        id: costValueId,
        parent: costItemId,
        unit_data: {
          unit_symbol: "",
          value_component: 0,
        },
      };
    } else {
      newData = {
        category: "",
        name: "",
        applied_value: 0,
        id: costValueId,
        parent: costItemId,
      };
    }
    const tr = CostUI.createCostvaluesRow({
      costItemId,
      costValue: newData,
      costValueCallbacks,
    });
    table.appendChild(tr);
  }

  static addTable({ id, className, headers }) {
    const div = document.createElement("div");
    div.classList.add("table-container");
    const table = document.createElement("table");
    div.appendChild(table);
    if (className !== "") {
      table.classList.add(className);
    }
    table.id = id;

    const headerRow = document.createElement("tr");
    headers.forEach((headerText) => {
      const th = document.createElement("th");
      th.style.position = "relative";
      th.textContent = headerText;
      headerRow.appendChild(th);
    });
    const thead = document.createElement("thead");
    thead.appendChild(headerRow);
    table.appendChild(thead);
    table.get_header_row = function () {
      return headerRow;
    };
    table.get_header_by_name = function (name) {
      const headers = headerRow.querySelectorAll("th");
      return Array.from(headers).find((header) => header.textContent === name);
    };
    return { tableContainer: div, table: table };
  }

  static createCostvaluesRow({ costItemId, costValue, costValueCallbacks }) {
    if (document.getElementById(costValue.id)) {
      return document.getElementById(costValue.id);
    }

    const tr = document.createElement("tr");
    tr.parent = costItemId;
    tr.id = costValue.id;

    const costType = CostUI.determineCostType(costValue);
    const { dropdown, typeCell } = CostUI.createTypeCell(
      tr,
      costType,
      costItemId,
      costValue,
      costValueCallbacks
    );
    tr.appendChild(typeCell);

    const categoryCell = CostUI.createTableInput(
      "text",
      "category",
      costValue.category
    );
    tr.appendChild(categoryCell);

    const value = CostUI.determineValue(costValue);
    const valueCell1 = CostUI.createTableInput("number", "value", value);
    tr.appendChild(valueCell1);
    let unitSymbolCell;
    let unitComponentCell;
    if (costValue.isRate) {
      unitSymbolCell = CostUI.Text(costValue.unit_data.unit_symbol); //TODO CostUI.createTableInput("text", "unit_symbol", costValue.unit_data.unit_symbol);
      tr.appendChild(unitSymbolCell);
      unitComponentCell = CostUI.createTableInput(
        "number",
        "unit_value_component",
        costValue.unit_data.value_component
      );
      tr.appendChild(unitComponentCell);
    }

    CostUI.addValueChangeListeners(
      tr,
      costItemId,
      costValue,
      costValueCallbacks
    );
    dropdown.addEventListener("change", function () {
      const selectedType = this.value;
      CostUI.updateRowBasedOnType(selectedType, categoryCell, valueCell1);

      if (selectedType === "SUM") {
        const costValueId = parseInt(this.closest("tr").getAttribute("id"));
        const appliedValue = parseFloat(
          valueCell1.querySelector("input").value
        );
        const costCategory = categoryCell.querySelector("input").value;

        if (costValueCallbacks.editCostValues) {
          costValueCallbacks.editCostValues(costItemId, [
            {
              costType: selectedType,
              costCategory: costCategory,
              appliedValue: appliedValue,
              id: costValueId,
              costItemId: costItemId,
            },
          ]);
        }
      }
    });

    const deleteCell = CostUI.createDeleteCell(
      costItemId,
      costValue,
      costValueCallbacks,
      tr
    );
    tr.appendChild(deleteCell);

    CostUI.updateRowBasedOnType(costType, categoryCell, valueCell1);
    return tr;
  }

  static determineCostType(costValue) {
    if (costValue.category === "*") {
      return "SUM";
    } else if (costValue.category && costValue.category !== "*") {
      return "CATEGORY";
    } else if (costValue.applied_value) {
      return "FIXED";
    }
    return "FIXED";
  }

  static createTypeCell(costType, costItemId, costValue, costValueCallbacks) {
    const options = ["FIXED", "CATEGORY", "SUM"];
    const typeCell = document.createElement("td");
    const dropdown = CostUI.createTableDropdown({
      name: "type",
      options: options,
      defaultValue: costType,
    });
    typeCell.appendChild(dropdown);

    return { dropdown, typeCell };
  }

  static determineValue(costValue) {
    function cleanLabel(value) {
      return value.replace(/[^0-9.]/g, "");
    }

    if (costValue.category === "*") {
      return cleanLabel(costValue.label);
    } else {
      return costValue.applied_value;
    }
  }

  static getCostValueData({
    typeCell,
    categoryCell,
    valueCell1,
    componentCell,
  }) {
    const costType = typeCell.value;
    const costCategory = categoryCell ? categoryCell.value : null;
    const appliedValue = parseFloat(valueCell1.value);
    const unitBasisValue = componentCell
      ? parseFloat(componentCell.value)
      : null;
    return { costType, costCategory, appliedValue, unitBasisValue };
  }

  static addValueChangeListeners(
    tr,
    costItemId,
    costValue,
    costValueCallbacks
  ) {
    function handleCostValueChange(costItemId) {
      let costValueData = CostUI.getCostValueData({
        typeCell,
        categoryCell,
        valueCell1,
        componentCell,
      });
      costValueData = {
        ...costValueData,
        id: costValue.id,
        costItemId: costItemId,
      };
      if (costValueData.unitBasisValue) {
        costValueData.unitComponent = costValue.unit_data.unit_component;
      }
      if (costValueCallbacks.editCostValues) {
        costValueCallbacks.editCostValues(costItemId, [costValueData]);
      }
    }

    const typeCell = tr.querySelector("td select[name='type']");
    const categoryCell = tr.querySelector("td input[name='category']");
    const valueCell1 = tr.querySelector("td input[name='value']");
    const componentCell = tr.querySelector(
      "td input[name='unit_value_component']"
    );
    valueCell1.addEventListener(
      "change",
      handleCostValueChange.bind(valueCell1, costItemId)
    );

    valueCell1.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        handleCostValueChange.call(this, costItemId);
      }
    });

    if (componentCell) {
      componentCell.addEventListener(
        "change",
        handleCostValueChange.bind(componentCell, costItemId)
      );
      componentCell.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          handleCostValueChange.call(this, costItemId);
        }
      });
    }
  }

  static createDeleteCell(costItemId, costValue, costValueCallbacks, tr) {
    const deleteCell = document.createElement("td");
    const deleteButton = CostUI.createButton("Delete", "fa-solid fa-trash");

    deleteButton.addEventListener("click", function () {
      costValueCallbacks.deleteCostValue(costItemId, costValue.id);
      tr.remove();
    });

    deleteCell.appendChild(deleteButton);
    return deleteCell;
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

  static createTableDropdown({ name, options, defaultValue = "FIXED" }) {
    const dropdown = document.createElement("select");
    dropdown.name = name;
    options.forEach((optionValue) => {
      const option = document.createElement("option");
      option.value = optionValue;
      option.textContent = optionValue;
      if (optionValue === defaultValue) {
        option.selected = true;
      }
      dropdown.appendChild(option);
    });
    return dropdown;
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
    const addButton = CostUI.createButton("Add Cost Value", "fa-solid fa-plus");
    addButton.addEventListener("click", function (e) {
      e.preventDefault();
      callbacks.addCostValue ? callbacks.addCostValue(costItemId) : null;
    });
    return addButton;
  }

  static Form({ id, name, icon = "fa-solid fa-file", shouldHide = false }) {
    function style(form) {
      form.classList.add("floating-form");
      form.style.position = "absolute";
      form.style.top = "50%";
      form.style.left = "50%";
      form.style.transform = "translate(-50%, -50%)";
    }
    if (document.getElementById(id)) {
      const formContainer = document
        .getElementById(id)
        .querySelector(".form-container");
      formContainer.innerHTML = "";
      return formContainer;
    }
    const form = document.createElement("form");
    form.id = id;
    style(form);
    const header = CostUI.createHeader(name, icon);
    let closeButton;

    if (shouldHide) {
      closeButton = CostUI.createHideButton(form);
    } else {
      const callback = () => {
        form.remove();
        const costItemId = form.id.split("-").pop();
        CostUI.unhighlightElement(costItemId);
      };
      closeButton = CostUI.createCloseButton(callback);
    }
    form.appendChild(header);
    form.appendChild(closeButton);
    CostUI.makeFormDraggable(form);

    const formContainer = document.createElement("div");
    formContainer.classList.add("form-container");
    form.appendChild(formContainer);
    document.body.appendChild(form);
    return formContainer;
  }
  static makeFormDraggable(form) {
    let pos1 = 0,
      pos2 = 0,
      pos3 = 0,
      pos4 = 0;
    form.onmousedown = function (e) {
      if (!e.target.closest("input, select, button")) {
        dragMouseDown(e);
      }
    };

    const formElements = form.querySelectorAll("input, select, button");
    formElements.forEach((element) => {
      element.onmousedown = function (e) {
        e.stopImmediatePropagation();
      };
    });

    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;

      let newTop = form.offsetTop - pos2;
      let newLeft = form.offsetLeft - pos1;

      const minTop = form.offsetHeight / 2;
      const minLeft = form.offsetWidth / 2;
      const maxTop = window.innerHeight - form.offsetHeight / 2;
      const maxLeft = window.innerWidth - form.offsetWidth / 2;

      if (newTop < minTop) newTop = minTop;
      if (newTop > maxTop) newTop = maxTop;
      if (newLeft < minLeft) newLeft = minLeft;
      if (newLeft > maxLeft) newLeft = maxLeft;

      form.style.top = newTop + "px";
      form.style.left = newLeft + "px";
    }

    function closeDragElement() {
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }

  static createHeader(text, icon) {
    const header = document.createElement("div");
    const i = document.createElement("i");
    i.className = icon;
    header.classList.add("form-header");
    const span = document.createElement("span");
    span.textContent = text;
    header.appendChild(i);
    header.appendChild(span);
    return header;
  }

  static createHideButton(form) {
    const hideButton = document.createElement("span");
    hideButton.classList.add("close-button");
    hideButton.innerHTML = "&minus;";
    hideButton.addEventListener("click", function () {
      form.style.display = "none";
    });
    return hideButton;
  }

  static createCloseButton(callback) {
    const closeButton = document.createElement("span");
    closeButton.classList.add("close-button");
    closeButton.innerHTML = "&times;";
    closeButton.addEventListener("click", callback);
    return closeButton;
  }

  static createProductRow(product, shouldAddQto = false) {
    const row = document.createElement("tr");

    const cellData = {
      id: product.info.id,
      class: product.info.class,
      name: product.info.name,
      type: product.info.type,
      count: "1",
    };

    for (const [key, value] of Object.entries(cellData)) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }

    if (shouldAddQto) {
      const quantitySets = product.qtos;
      Object.entries(quantitySets).forEach(([qtoName, qto]) => {
        Object.entries(qto).forEach(([key, value]) => {
          if (key !== "id") {
            const cell = document.createElement("td");
            cell.textContent = parseFloat(value).toFixed(2);
            row.appendChild(cell);
          }
        });
      });
    }

    return row;
  }

  static addQuantityHeaders(table, products, shouldAddQto = true) {
    const headerRow = table.get_header_row();
    const countHeader = table.get_header_by_name("Count");
    const quantitySums = { count: 0 };
    const quantityHeaders = { count: countHeader };
    if (!shouldAddQto) return { quantitySums, quantityHeaders };
    if (products.length > 0) {
      const quantitySets = products[0].qtos;
      Object.entries(quantitySets).forEach(([qtoName, qto]) => {
        Object.keys(qto).forEach((key) => {
          if (key !== "id") {
            const qtoHeader = document.createElement("th");
            qtoHeader.textContent = key;
            qtoHeader.style.cursor = "pointer";
            headerRow.appendChild(qtoHeader);
            quantitySums[key] = 0;
            quantityHeaders[key] = qtoHeader;
          }
        });
      });
    }

    return { quantitySums, quantityHeaders };
  }

  static getAssinedQuantity(products, costItemId) {
    let quantityAssigned = null;
    products.forEach((product) => {
      const product_id = product.info.id;
      const assignedQuantities = product.assigned_quantities;
      if (assignedQuantities.length > 0) {
        assignedQuantities.forEach((assignedQuantity) => {
          if (assignedQuantity.cost_item_id === costItemId) {
            product.isProductAssigned = true;
            quantityAssigned = assignedQuantity.name;
          }
        });
      }
    });
    return quantityAssigned;
  }

  static calculateSums(qtos, quantitySums) {
    Object.entries(qtos).forEach(([qtoName, qto]) => {
      Object.entries(qto).forEach(([key, value]) => {
        if (key !== "id") {
          quantitySums[key] += parseFloat(value);
        }
      });
    });
  }

  static countProducts(products, quantitySums) {
    products.forEach((product) => {
      quantitySums.count += 1;
    });
  }

  static addSubTotalRow(quantitySums, shouldAddQto = true) {
    const subtotalRow = document.createElement("tr");

    const cells = [
      { textContent: "", style: { border: "none" } },
      { textContent: "", style: { border: "none" } },
      { textContent: "", style: { border: "none" } },
      { textContent: "Subtotal", colSpan: 1, style: { border: "none" } },
      { textContent: quantitySums.count },
    ];

    cells.forEach((cellData) => {
      const cell = document.createElement("td");
      if (cellData.textContent !== undefined)
        cell.textContent = cellData.textContent;
      if (cellData.colSpan !== undefined) cell.colSpan = cellData.colSpan;
      if (cellData.style !== undefined)
        Object.assign(cell.style, cellData.style);
      subtotalRow.appendChild(cell);
    });

    if (shouldAddQto) {
      Object.keys(quantitySums).forEach((key) => {
        if (key !== "count") {
          const subtotalCell = document.createElement("td");
          subtotalCell.textContent = quantitySums[key].toFixed(2);
          subtotalRow.appendChild(subtotalCell);
        }
      });
    }

    subtotalRow.classList.add("subtotal-row");

    return subtotalRow;
  }

  static createProductTable({
    container,
    products,
    quantityNames,
    costItemId,
    callbacks,
  }) {
    if (products.length === 0) {
      const noProductsMessage = document.createElement("p");
      noProductsMessage.textContent =
        "Your Blender Selection is empty! Select objects first.";
      container.appendChild(noProductsMessage);
      return;
    }
    const { tableContainer, table } = CostUI.addTable({
      headers: ["Step Id", "Class", "Name", "Type", "Count"],
      className: "",
      id: "cost-values-table-" + costItemId,
    });
    container.appendChild(tableContainer);
    const tbody = document.createElement("tbody");
    table.appendChild(tbody);

    const quantityAssigned = CostUI.getAssinedQuantity(products, costItemId);
    const areProductsSameClass = products.every(
      (product) => product.info.class === products[0].info.class
    );

    const shouldAddQto = areProductsSameClass ? true : false;
    const headerRow = table.get_header_row();
    const { quantitySums, quantityHeaders } = CostUI.addQuantityHeaders(
      table,
      products,
      shouldAddQto
    );

    if (shouldAddQto) {
      CostUI.highlightColumn(
        table,
        headerRow,
        quantityHeaders,
        quantityAssigned
      );

      products.forEach((product) => {
        const row = CostUI.createProductRow(product, shouldAddQto);
        tbody.appendChild(row);

        const isProductAssigned = product.assigned_quantities
          ? product.assigned_quantities.some(
              (assignedQuantity) => assignedQuantity.cost_item_id === costItemId
            )
          : false;
        isProductAssigned ? row.classList.add("highlighted") : null;

        CostUI.calculateSums(product.qtos, quantitySums);
      });
    } else {
      products.forEach((product) => {
        const row = CostUI.createProductRow(product, shouldAddQto);
        tbody.appendChild(row);
      });
    }

    CostUI.countProducts(products, quantitySums);

    const subtotalRow = CostUI.addSubTotalRow(quantitySums, shouldAddQto);
    tbody.appendChild(subtotalRow);

    const quantitySelect = document.createElement("select");

    if (shouldAddQto) {
      quantityNames.forEach((name) => {
        const option = document.createElement("option");
        option.value = name;
        option.text = name;
        quantitySelect.appendChild(option);
      });
    }

    const option = document.createElement("option");
    option.value = "count";
    option.text = "count";
    quantitySelect.appendChild(option);

    quantitySelect.addEventListener("change", (event) => {
      const selectedQuantity = event.target.value;

      Object.values(quantityHeaders).forEach((header) => {
        header.classList.remove("highlighted");
      });
      table.querySelectorAll("td").forEach((cell) => {
        cell.classList.remove("highlighted");
      });

      if (quantityHeaders[selectedQuantity]) {
        quantityHeaders[selectedQuantity].classList.add("highlighted");
        const columnIndex = Array.from(headerRow.children).indexOf(
          quantityHeaders[selectedQuantity]
        );
        table.querySelectorAll(`tr`).forEach((row) => {
          row.children[columnIndex].classList.add("highlighted");
        });
      }
    });

    Object.entries(quantityHeaders).forEach(([key, header]) => {
      header.addEventListener("click", () => {
        quantitySelect.value = key;
        const event = new Event("change");
        quantitySelect.dispatchEvent(event);
      });
    });

    quantityAssigned
      ? CostUI.highlightColumn(
          table,
          headerRow,
          quantityHeaders,
          quantityAssigned
        )
      : null;

    quantitySelect.value = quantityAssigned ? quantityAssigned : "count";

    const productIds = products.map((product) => product.info.id);
    callbacks.emptyForm = () => {
      container.innerHTML = "";
    };
    const addProductAssignmentsButton = CostUI.addProductAssignmentsButton(
      costItemId,
      productIds,
      quantitySelect,
      callbacks
    );

    container.appendChild(quantitySelect);
    container.appendChild(addProductAssignmentsButton);
    return table;
  }

  static createAssignmentsTable({
    container,
    products,
    costItemId,
    quantityNames,
    callbacks,
  }) {
    const { tableContainer, table } = CostUI.addTable({
      headers: ["Step Id", "Class", "Name", "Type", "Count"],
      className: "",
      id: "cost-values-table-" + costItemId,
    });

    container.appendChild(tableContainer);
    const tbody = document.createElement("tbody");
    table.appendChild(tbody);

    let quantityAssigned = CostUI.getAssinedQuantity(products, costItemId);
    const shouldAddQto = quantityAssigned ? true : false;
    const headerRow = table.get_header_row();
    const { quantitySums, quantityHeaders } = CostUI.addQuantityHeaders(
      table,
      products,
      shouldAddQto
    );

    shouldAddQto
      ? CostUI.highlightColumn(
          table,
          headerRow,
          quantityHeaders,
          quantityAssigned
        )
      : null;

    products.forEach((product) => {
      const row = CostUI.createProductRow(product, shouldAddQto);
      tbody.appendChild(row);
      shouldAddQto ? CostUI.calculateSums(product.qtos, quantitySums) : null;
    });

    CostUI.countProducts(products, quantitySums);

    const subtotalRow = CostUI.addSubTotalRow(quantitySums, shouldAddQto);
    tbody.appendChild(subtotalRow);
  }

  static highlightColumn(table, headerRow, quantityHeaders, quantityAssigned) {
    if (quantityAssigned) {
      if (quantityHeaders[quantityAssigned]) {
        quantityHeaders[quantityAssigned].classList.add("highlighted");
        const columnIndex = Array.from(headerRow.children).indexOf(
          quantityHeaders[quantityAssigned]
        );
        table.querySelectorAll(`tr`).forEach((row) => {
          row.children[columnIndex].classList.add("highlighted");
        });
      }
    }
  }
  static addProductAssignmentsButton(
    costItemId,
    productIds,
    quantitySelect,
    callbacks
  ) {
    const addProductAssignmentsButton = CostUI.createButton(
      "Add Product Assignments",
      "fa-solid fa-plus"
    );
    addProductAssignmentsButton.addEventListener("click", (event) => {
      event.preventDefault();
      let propName = quantitySelect.value;
      if (propName === "count") {
        propName = "";
      }
      callbacks.addProductAssignments
        ? callbacks.addProductAssignments({
            costItemId,
            selectedQuantity: propName,
            productIds,
          })
        : null;
      callbacks.emptyForm ? callbacks.emptyForm() : null;
      callbacks.enableEditingQuantities(costItemId);
    });
    addProductAssignmentsButton.classList.add("action-button");
    return addProductAssignmentsButton;
  }

  static addSettingsMenu() {
    const settingsMenu = CostUI.Form({
      id: "settings-menu",
      name: "Settings",
      icon: "fa-solid fa-gear",
      shouldHide: true,
    });

    const picker = CostUI.createColorPicker();
    const tableFontSize = CostUI.createFontSizePicker();
    const currencyPicker = CostUI.createCurrencyPicker();
    settingsMenu.appendChild(picker);
    settingsMenu.appendChild(tableFontSize);
    document.getElementById("settings-menu").style.display = "none";
    CostUI.applySavedSettings();
  }

  static createFontSizePicker() {
    const div = document.createElement("div");
    const fontSizeText = document.createElement("p");
    fontSizeText.textContent = "Select a font size for the table:";
    div.appendChild(fontSizeText);
    const fontSizePicker = document.createElement("input");
    fontSizePicker.type = "number";
    fontSizePicker.id = "font-size-picker";
    fontSizePicker.value = localStorage.getItem("tableFontSize") || 14;
    div.appendChild(fontSizePicker);
    fontSizePicker.addEventListener("input", function () {
      const fontSize = fontSizePicker.value + "px";
      CostUI.saveFontSize(fontSize);
      CostUI.applyFontSizeToAllTables(fontSize);
    });
    return div;
  }

  static createColorPicker() {
    const div = document.createElement("div");
    const colorText = document.createElement("p");
    colorText.textContent = "Select a color for the table:";
    div.appendChild(colorText);
    const colorPicker = document.createElement("input");
    colorPicker.type = "color";
    colorPicker.id = "color-picker";
    colorPicker.value = localStorage.getItem("tableColor") || "#ffffff";
    div.appendChild(colorPicker);
    colorPicker.addEventListener("input", function () {
      const color = colorPicker.value;
      CostUI.saveColor(color);
      CostUI.applyColorToAllTables(color);
    });
    return div;
  }

  static createCurrencyPicker() {
    const currency = CostUI.getCurrency();
    const div = document.createElement("div");
    const currencyText = document.createElement("p");
    currencyText.textContent = "Select a currency for the table:";
    div.appendChild(currencyText);
    const currencyPicker = document.createElement("input");
    currencyPicker.type = "text";
    currencyPicker.id = "currency-picker";
    currencyPicker.value = currency;
    div.appendChild(currencyPicker);
    currencyPicker.addEventListener("input", function () {
      const currency = currencyPicker.value;
      CostUI.saveCurrency(currency);
    });
    return div;
  }

  static saveCurrency(currency) {
    localStorage.setItem("tableCurrency", currency);
  }

  static getCurrency() {
    return localStorage.getItem("tableCurrency");
  }

  static saveFontSize(fontSize) {
    localStorage.setItem("tableFontSize", fontSize);
  }

  static saveColor(color) {
    localStorage.setItem("tableColor", color);
  }

  static applyFontSizeToAllTables(fontSize) {
    document.documentElement.style.setProperty("--fontSize", fontSize);
  }

  static applyColorToAllTables(color) {
    const tables = document.querySelectorAll("table");
    tables.forEach((table) => {
      table.style.backgroundColor = color;
    });
  }

  static applySavedSettings() {
    const savedFontSize = localStorage.getItem("tableFontSize");
    if (savedFontSize) {
      CostUI.applyFontSizeToAllTables(savedFontSize);
      const fontSizePicker = document.getElementById("font-size-picker");
      if (fontSizePicker) {
        fontSizePicker.value = parseInt(savedFontSize, 10);
      }
    }

    const savedColor = localStorage.getItem("tableColor");
    if (savedColor) {
      CostUI.applyColorToAllTables(savedColor);
      const colorPicker = document.getElementById("color-picker");
      if (colorPicker) {
        colorPicker.value = savedColor;
      }
    }
  }

  static getRibbonBar() {
    return document.getElementById("ribbon-bar");
  }

  static addRibbonButton({ text, icon, callback }) {
    const ribbonBar = CostUI.getRibbonBar();

    const button = document.createElement("button");
    button.classList.add("action-button", ...icon.split(" "));
    button.dataset.tooltip = text;

    button.addEventListener("click", () => callback(button));

    ribbonBar.appendChild(button);
  }

  static toggleSchedulesContainer(button) {
    const schedulesContainer = CostUI.getSchedulesContainer();
    const isHidden = schedulesContainer.style.display === "none";

    if (isHidden) {
      CostUI.displaySchedulesContainer();
      button.classList.remove("fa-eye");
      button.classList.add("fa-eye-slash");
      button.dataset.tooltip = "Hide Schedules";
    } else {
      CostUI.hideSchedulesContainer();
      button.classList.remove("fa-eye-slash");
      button.classList.add("fa-eye");
      button.dataset.tooltip = "Display Schedules";
    }
  }

  static getSchedulesContainer() {
    return document.getElementById("cost-schedules");
  }

  static displaySchedulesContainer() {
    const schedulesContainer = CostUI.getSchedulesContainer();
    schedulesContainer.style.display = "flex";
  }

  static hideSchedulesContainer() {
    const schedulesContainer = CostUI.getSchedulesContainer();
    schedulesContainer.style.display = "none";
  }

  static getSettingsMenu() {
    return document.getElementById("settings-menu");
  }

  static toggleSettingsMenu() {
    const settingsMenu = CostUI.getSettingsMenu();
    if (settingsMenu.style.display === "none") {
      settingsMenu.style.display = "block";
    } else {
      settingsMenu.style.display = "none";
    }
  }

  static createRibbon() {
    CostUI.addSettingsMenu();
    CostUI.addRibbonButton({
      text: "Hide Schedules",
      icon: "fa-regular fa-eye-slash",
      callback: (button) => {
        CostUI.toggleSchedulesContainer(button);
      },
    });
    CostUI.addRibbonButton({
      text: "Settings",
      icon: "fas fa-cog",
      callback: () => {
        CostUI.toggleSettingsMenu();
      },
    });
  }

  static enableEditingQuantities({
    costItemId,
    selectedProducts,
    assignedProducts,
    quantityNames,
    costQuantities,
    callbacks,
  }) {
    CostUI.highlightElement(costItemId);
    const form = CostUI.Form({
      id: "enable-editing-quantities-" + costItemId,
      name: "Editing Quantities for: " + CostUI.getCostItemName(costItemId),
      icon: "fa-solid fa-box",
    });

    const ribbonBar = CostUI.createRibbonBar();
    form.appendChild(ribbonBar);

    const selectedProductsSection = CostUI.selectedProductsSection({
      products: selectedProducts,
      quantityNames,
      costItemId,
      callbacks,
    });

    const assignedProductsSection = CostUI.assignedProductsSection({
      products: assignedProducts,
      quantityNames,
      costItemId,
      callbacks,
    });

    const manualQuantitiesSection = CostUI.manualQuantitiesSection({
      costItemId,
      costQuantities,
      has_assigned_products: assignedProducts.length > 0,
      callbacks,
    });

    form.appendChild(selectedProductsSection);
    form.appendChild(assignedProductsSection);
    form.appendChild(manualQuantitiesSection);

    const summarySection = CostUI.createSummarySection({
      selectedProducts,
      assignedProducts,
      costQuantities,
    });
    form.appendChild(summarySection);

    CostUI.addEventListeners({
      switchBar: ribbonBar,
      costItemId,
      selectedProductsSection,
      assignedProductsSection,
      manualQuantitiesSection,
    });

    const lastActiveSection =
      localStorage.getItem("lastActiveSection") || "selected-products";
    const lastActiveButton = document.getElementById(
      `${lastActiveSection}-btn`
    );
    if (lastActiveButton) {
      lastActiveButton.click();
    }
  }

  static createRibbonBar() {
    const ribbonBar = document.createElement("div");
    ribbonBar.className = "switch-bar";
    ribbonBar.innerHTML = `
      <button class="action-button" id="selected-products-btn">Selected Products</button>
      <button class="action-button" id="assigned-products-btn">Assigned Products</button>
      <button class="action-button" id="manual-quantities-btn">Manual Quantities</button>
    `;
    return ribbonBar;
  }

  static createSummarySection({
    selectedProducts,
    assignedProducts,
    costQuantities,
  }) {
    const summarySection = document.createElement("div");
    summarySection.classList.add("summary-section");

    const manualQuantities = costQuantities.quantities.filter(
      (quantity) => !quantity.fromProduct
    );
    const paramaterQuantities = costQuantities.quantities.filter(
      (quantity) => quantity.fromProduct
    );

    const table = document.createElement("table");
    table.classList.add("summary-table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const headers = ["Category", "Count"];
    headers.forEach((headerText) => {
      const th = document.createElement("th");
      th.textContent = headerText;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");

    const data = [
      { category: "Assigned Products", count: assignedProducts.length },
      { category: "Manual Quantities", count: manualQuantities.length },
      {
        category: "Product derived Quantities",
        count: paramaterQuantities.length,
      },
    ];

    data.forEach((item) => {
      const row = document.createElement("tr");
      const categoryCell = document.createElement("td");
      categoryCell.textContent = item.category;
      const countCell = document.createElement("td");
      countCell.textContent = item.count;
      row.appendChild(categoryCell);
      row.appendChild(countCell);
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    summarySection.appendChild(table);

    return summarySection;
  }

  static addEventListeners({
    switchBar,
    costItemId,
    selectedProductsSection,
    assignedProductsSection,
    manualQuantitiesSection,
  }) {
    const buttons = switchBar.querySelectorAll(".action-button");

    buttons.forEach((button) => {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        const sectionName = button.id.replace("-btn", "");
        const sectionId = sectionName + "-section-" + costItemId;

        if (selectedProductsSection)
          selectedProductsSection.style.display = "none";
        if (assignedProductsSection)
          assignedProductsSection.style.display = "none";
        if (manualQuantitiesSection)
          manualQuantitiesSection.style.display = "none";

        const section = document.getElementById(sectionId);
        if (section) {
          section.style.display = "block";
        }
        buttons.forEach((btn) => btn.classList.remove("active-btn"));
        button.classList.add("active-btn");

        localStorage.setItem("lastActiveSection", sectionName);
      });
    });
  }

  static getSection(costItemId, sectionName) {
    return document.getElementById(`${sectionName}-${costItemId}`);
  }

  static selectedProductsSection({
    products,
    quantityNames,
    costItemId,
    callbacks,
  }) {
    const selectedProductsSection = document.createElement("div");
    selectedProductsSection.id = "selected-products-section-" + costItemId;
    selectedProductsSection.classList.add("form-section");
    const numberOfProducts = CostUI.Text(
      "Selection basket : " + products.length + " products",
      "fa-solid fa-cart-shopping",
      "medium"
    );
    selectedProductsSection.appendChild(numberOfProducts);

    const selectedProductsTable = CostUI.createProductTable({
      container: selectedProductsSection,
      products: products,
      quantityNames,
      costItemId,
      callbacks,
    });
    return selectedProductsSection;
  }

  static assignedProductsSection({
    products,
    quantityNames,
    costItemId,
    callbacks,
  }) {
    const assignedProductsSection = document.createElement("div");
    assignedProductsSection.id = "assigned-products-section-" + costItemId;
    assignedProductsSection.style.display = "none";
    assignedProductsSection.classList.add("form-section");
    if (products.length > 0) {
      let text = " Assigned Products : " + products.length;
      const assignedProductsText = CostUI.Text(
        text,
        "fa-solid fa-solid fa-paperclip",
        "medium"
      );
      assignedProductsSection.appendChild(assignedProductsText);
      const assignmentsTable = CostUI.createAssignmentsTable({
        container: assignedProductsSection,
        products: products,
        quantityNames,
        costItemId,
        callbacks,
      });
    }

    return assignedProductsSection;
  }

  static manualQuantitiesSection({
    costItemId,
    costQuantities,
    has_assigned_products,
    callbacks,
  }) {
    const manualQuantitiesSection = document.createElement("div");
    manualQuantitiesSection.classList.add("form-section");
    manualQuantitiesSection.id = "manual-quantities-section-" + costItemId;
    manualQuantitiesSection.style.display = "none";

    const title = CostUI.Text(
      "Manual Quantities",
      "fa-solid fa-ruler",
      "medium"
    );
    manualQuantitiesSection.appendChild(title);
    const unitSymbol = costQuantities.unit_symbol;

    let quantityType = costQuantities.quantity_type;

    if (quantityType) {
      const text = CostUI.Text(
        quantityType + " (" + unitSymbol + " )",
        "fa-solid fa-ruler",
        "small"
      );
      manualQuantitiesSection.appendChild(text);
    } else {
      const quantityTypes = [
        "IfcQuantityArea",
        "IfcQuantityLength",
        "IfcQuantityVolume",
        "IfcQuantityCount",
        "IfcQuantityWeight",
      ];
      const dropdown = CostUI.createTableDropdown({
        name: "type",
        options: quantityTypes,
        defaultValue: "IfcQuantityArea",
      });
      dropdown.id = "quantity-type-dropdown-" + costItemId;
      manualQuantitiesSection.appendChild(dropdown);
    }
    if (quantityType === "IfcQuantityCount" && has_assigned_products) {
      const text = CostUI.Text(
        " One of the quantities is assigned to the product selection",
        "fa-solid fa-warning",
        "small"
      );
      manualQuantitiesSection.appendChild(text);
    }

    let paramaterQuantities = costQuantities.quantities.filter(
      (quantity) => quantity.fromProduct
    );
    let manualQuantities = costQuantities.quantities.filter(
      (quantity) => !quantity.fromProduct
    );

    let headerNames = ["Name", "Value" + " (" + unitSymbol + " )", "Actions"];

    if (manualQuantities.length > 0) {
      headerNames = [];
      Object.entries(manualQuantities[0]).forEach(([key, value]) => {
        if (key !== "id" && key !== "fromProduct") {
          headerNames.push(key);
        }
      });
      headerNames.push("Actions");
    }

    const { tableContainer, table } = CostUI.addTable({
      headers: headerNames,
      className: "manual-quantities-table",
      id: "manual-quantities-table-" + costItemId,
    });

    manualQuantities.forEach((quantity) => {
      const tr = CostUI.createManualQuantityRow(
        costItemId,
        quantity,
        callbacks
      );
      table.appendChild(tr);
    });
    const addButton = CostUI.createAddManualQuantityButton(
      costItemId,
      quantityType,
      callbacks
    );

    manualQuantitiesSection.appendChild(tableContainer);
    manualQuantitiesSection.appendChild(addButton);
    return manualQuantitiesSection;
  }

  static createManualQuantityRow(costItemId, quantity, callbacks) {
    const tr = document.createElement("tr");
    tr.id = quantity.id;
    Object.entries(quantity).forEach(([key, value]) => {
      if (key !== "id" && key !== "fromProduct") {
        if (key === "Name") {
          const cell = document.createElement("td");
          const input = document.createElement("input");
          input.type = "text";
          input.value = value;
          cell.appendChild(input);
          tr.appendChild(cell);

          input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
              e.preventDefault();
              callbacks.editQuantity(costItemId, quantity.id, {
                [key]: input.value,
              });
            }
          });
        } else if (key.toLowerCase().includes("value")) {
          const cell = document.createElement("td");
          const input = document.createElement("input");
          input.type = "number";
          input.value = value;
          cell.appendChild(input);

          input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
              e.preventDefault();
              callbacks.editQuantity(costItemId, quantity.id, {
                [key]: parseFloat(input.value),
              });
            }
          });
          tr.appendChild(cell);
        } else {
          const cell = document.createElement("td");
          cell.textContent = value;
          tr.appendChild(cell);
        }
      }
    });

    const deleteButton = CostUI.createButton("Delete", "fa-solid fa-trash");
    const deleteCell = document.createElement("td");
    deleteButton.addEventListener("click", function (e) {
      e.preventDefault();
      callbacks.deleteQuantity(costItemId, quantity.id);
      tr.remove();
    });
    deleteCell.appendChild(deleteButton);
    tr.appendChild(deleteCell);

    return tr;
  }

  static createAddManualQuantityButton(costItemId, quantityType, callbacks) {
    const addButton = CostUI.createButton(
      "Add Manual Quantity",
      "fa-solid fa-plus"
    );

    addButton.addEventListener("click", function (e) {
      e.preventDefault();
      let type = quantityType;
      if (!type) {
        const qtoSection = document.getElementById(
          "manual-quantities-section-" + costItemId
        );
        const dropdown = qtoSection.querySelector("select");
        type = dropdown ? dropdown.value : null;
      }
      callbacks.addQuantity(costItemId, type);
    });

    return addButton;
  }
}
