import { CostUI } from "./utilities/costui.js";

const connectedClients = {};
let socket;

$(document).ready(function () {
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

  connectSocket();
  CostUI.createRibbon();
  CostUI.addShortcuts();
});

function connectSocket() {
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  socket = io(url);

  socket.on("blender_connect", handleBlenderConnect);
  socket.on("blender_disconnect", handleBlenderDisconnect);
  socket.on("connected_clients", handleConnectedClients);
  socket.on("theme_data", handleThemeData);
  socket.on("connect", handleWebConnect);
  socket.on("predefined_types", handlePredefinedTypes);
  socket.on("cost_schedules", handleCostSchedulesData);
  socket.on("cost_items", handleCostItemsData);
  socket.on("cost_values", handleCostValuesData);
  socket.on("cost_value", handleCostValueData);
  socket.on("quantities", handleEditQuantities);
  socket.on("classification", handleClassificationData);
  socket.on("message", handleMessage);
}

function handleEditQuantities(data) {
  const costItemId = data.data["quantities"]["cost_item_id"];
  const products = data.data["quantities"]["selected_products"];
  const assigned_products = data.data["quantities"]["assigned_products"];
  const quantityNames = data.data["quantities"]["product_quantity_names"];
  const costQuantities = data.data["quantities"]["cost_quantities"];

  CostUI.enableEditingQuantities({
    costItemId: costItemId,
    selectedProducts: products,
    assignedProducts: assigned_products,
    quantityNames: quantityNames,
    costQuantities: costQuantities,
    callbacks: {
      addProductAssignments: addProductAssignments,
      enableEditingQuantities: enableEditingQuantities,
      addQuantity: addQuantity,
      editQuantity: editQuantity,
      deleteQuantity: deleteQuantity,
      assignFromQuery: assignFromQuery,
    },
  });
}

function assignCostValues(costRateId, callback){
  const selectedCostItems = CostUI.getSelectedCostItems();
  if (selectedCostItems.length === 0) {
    return;
  }
  executeOperator({
    type: "assignCostValues",
    costRateId: costRateId,
    costItemIds: selectedCostItems,
  });
}


function addSumCostValue(costItemId) {
  executeOperator({ type: "addSumCostValue", costItemId: costItemId });
}

function assignFromQuery(costItemId, query, propName) {
  executeOperator({
    type: "assignFromQuery",
    costItemId: costItemId,
    query: query,
    propName: propName,
  });
}

function addQuantity(costItemId, ifcClass) {
  executeOperator({
    type: "AddCostItemQuantity",
    costItemId: costItemId,
    ifcClass: ifcClass,
  });
}

function editQuantity(costItemId, quantityId, attributes) {
  executeOperator({
    type: "editCostItemQuantity",
    costItemId: costItemId,
    quantityId: quantityId,
    attributes: attributes,
  });
}

function deleteQuantity(costItemId, quantityId) {
  executeOperator({
    type: "deleteCostItemQuantity",
    costItemId: costItemId,
    quantityId: quantityId,
  });
}

function handlePredefinedTypes(data) {
  CostUI.enableAddingCostSchedule(
    data.data["predefined_types"],
    addCostSchedule
  );
}

function addProductAssignments({ costItemId, selectedQuantity, productIds }) {
  executeOperator({
    type: "addProductAssignments",
    costItemId: costItemId,
    propName: selectedQuantity,
    productIds: productIds,
  });
}

function addCostSchedule(name, predefinedType) {
  executeOperator({
    type: "addCostSchedule",
    name: name,
    predefinedType: predefinedType,
  });
}

function handleBlenderConnect(blenderId) {
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = { shown: false, ifc_file: "" };
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) + 1;
  });
}

function handleBlenderDisconnect(blenderId) {
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeTableElement(blenderId);
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) - 1;
  });
}

function removeTableElement(blenderId) {
  $("#cost-items-" + blenderId).remove();
}

const costValueCallbacks = {
  editCostValues: editCostValues,
  addCostValue: addCostValue,
  deleteCostValue: deleteCostValue,
};

function handleCostValueData(data) {
  const costItemId = data.data["cost_value"]["cost_item_id"];
  const costValueId = data.data["cost_value"]["cost_value_id"];
  CostUI.addNewCostValueRow(costItemId, costValueId, costValueCallbacks);
}

function deleteCostValue(costItemId, costValueId) {
  executeOperator({
    type: "deleteCostValue",
    costItemId: costItemId,
    costValueId: costValueId,
  });
}

function handleConnectedClients(data) {
  $("#blender-count").text(data.length);

  data.forEach(function (id) {
    connectedClients[id] = { shown: false, ifc_file: "" };
  });
}

function handleThemeData(themeData) {
  function arrayToRgbString(arr) {
    const [r, g, b, a] = arr.map((num) => Math.round(num * 255));
    if (a !== undefined) {
      return `rgba(${r}, ${g}, ${b}, ${a})`;
    }
    return `rgb(${r}, ${g}, ${b})`;
  }

  function generateCssVariableRule(theme) {
    let cssVariables = ":root.blender {\n";
    for (const key in theme) {
      const cssVariableName = `--blender-${key.replace(/_/g, "-")}`;
      const cssVariableValue = arrayToRgbString(theme[key]);
      cssVariables += `    ${cssVariableName}: ${cssVariableValue};\n`;
    }
    cssVariables += "}";
    return cssVariables;
  }

  const cssRule = generateCssVariableRule(themeData.theme);

  var styleElement = $("#index-stylesheet")[0];
  if (styleElement) {
    var sheet = styleElement.sheet || styleElement.styleSheet;
    sheet.insertRule(cssRule, sheet.cssRules.length);
  }
}

function setTheme(theme) {
  $("html").removeClass("light dark blender").addClass(theme);
  $(":root").css("color-scheme", theme);
  if (theme === "light") {
    $("#toggle-theme").html('<i class="fas fa-sun"></i>');
  } else if (theme === "dark") {
    $("#toggle-theme").html('<i class="fas fa-moon"></i>');
  } else if (theme === "blender") {
    $("#toggle-theme").html('<i class="fas fa-adjust"></i>');
  }
  localStorage.setItem("theme", theme);
}

function toggleClientList() {
  var clientList = $("#client-list");

  if (clientList.hasClass("show")) {
    clientList.removeClass("show");
    return;
  }

  clientList.empty();
  var counter = 0;

  $.each(connectedClients, function (id, client) {
    counter++;

    const dropdownIcon = $("<i>")
      .addClass("fas fa-chevron-down")
      .css("margin-left", "0.5rem");

    const clientDiv = $("<div>")
      .addClass("client")
      .text(client.ifc_file || "Blender " + counter);

    clientDiv.append(dropdownIcon);

    const clientDetailsDiv = $("<div>").addClass("client-details");

    if (id) {
      const clientId = $("<div>")
        .addClass("client-detail")
        .text(`Blender ID: ${id}`);
      clientDetailsDiv.append(clientId);
    }

    if (!client.has_drawings) {
      const clientShown = $("<div>")
        .addClass("client-detail")
        .text("No drawings exist for this IFC File yet");
      clientDetailsDiv.append(clientShown);
    } else {
      const clientNumbers = $("<div>")
        .addClass("client-detail")
        .text(
          `${allDrawings[client.ifc_file].drawings.length} Drawing(s), 
          ${allDrawings[client.ifc_file].sheets.length} Sheet(s)`
        );
      clientDetailsDiv.append(clientNumbers);
    }

    clientDiv.append(clientDetailsDiv);

    clientDiv.on("click", function () {
      clientDetailsDiv.toggleClass("show");
    });

    clientList.append(clientDiv);
  });
  clientList.addClass("show");
}

function handleCostSchedulesData(data) {
  const blenderId = data.blenderId;
  const costSchedules = data.data["cost_schedules"]["cost_schedules"];
  if (costSchedules.length === 0) {
    return;
  }
  const costScheduleDiv = document.getElementById("cost-schedules");
  costScheduleDiv.innerHTML = "";
  costSchedules.forEach((costSchedule) => {
    const predefinedType = CostUI.Text(
      "Predefined Type: " + costSchedule.PredefinedType,
      "fa-solid fa-paperclip"
    );
    const updatedDate = new Date(costSchedule.UpdateDate).toLocaleDateString();
    const updatedOn = CostUI.Text(
      "Updated On: " + updatedDate,
      "fa-solid fa-pen-nib"
    );
    const div = document.createElement("div");

    div.appendChild(predefinedType);
    div.appendChild(updatedOn);
    const callback = () => loadCostSchedule(costSchedule.id, blenderId);

    const card = CostUI.createCard(
      costSchedule.id,
      costSchedule.Name,
      div,
      callback
    );
    costScheduleDiv.append(card);
  });
}

function handleCostItemsData(data) {
  const costScheduleId = data.data["cost_items"]["schedule_data"][0]["id"];
  const currency = data.data["cost_items"]["currency"]
    ? data.data["cost_items"]["currency"]["name"]
    : "Undefined";
  const costSchedule = data.data["cost_items"]["schedule_data"][0];
  CostUI.createCostSchedule({
    costSchedule: costSchedule,
    currency: currency,
    callbacks: {
      addCostItem: addCostItem,
      deleteCostItem: deleteCostItem,
      duplicateCostItem: duplicateCostItem,
      selectAssignedElements: selectAssignedElements,
      editCostItemName: editCostItemName,
      enableEditingCostValues: enableEditingCostValues,
      addSummaryCostItem: addSummaryCostItem,
      enableEditingQuantities: enableEditingQuantities,
      addSumCostValue: addSumCostValue,
      enableEditingClassification: enableEditingClassification,
      assignCostValues: assignCostValues,
    },
  });
}

function addCostItem(costItemId) {
  executeOperator({ type: "addCostItem", costItemId: costItemId });
}

function editCostItemName(costItemId, name) {
  executeOperator({
    type: "editCostItemName",
    costItemId: costItemId,
    name: name,
  });
}

function selectAssignedElements(costItemId) {
  executeOperator({ type: "selectAssignedElements", costItemId: costItemId });
}

function handleWebConnect() {
  executeOperator({ type: "getPredefinedTypes" });
  getCostSchedules();
}

function addSummaryCostItem(costScheduleId) {
  executeOperator({
    type: "addSummaryCostItem",
    costScheduleId: costScheduleId,
  });
}

function loadCostSchedule(costScheduleId, blenderId) {
  executeOperator(
    { type: "loadCostSchedule", costScheduleId: costScheduleId },
    blenderId
  );
}

function getCostSchedules(blenderId) {
  executeOperator({ type: "getCostSchedules" }, blenderId);
}

function enableEditingCostValues(costItemId) {
  executeOperator({ type: "enableEditingCostValues", costItemId: costItemId });
}

function enableEditingClassification(costItemId) {
  executeOperator({
    type: "enableEditingClassification",
    costItemId: costItemId,
  });
}

function removeClassificationReference(costItemId, classificationId) {
  executeOperator({
    type: "removeClassificationReference",
    costItemId: costItemId,
    classificationId: classificationId,
  });
}

function addClassificationReference(
  costItemId,
  classificationName,
  classificationId
) {
  executeOperator({
    type: "addClassificationReference",
    costItemId: costItemId,
    classificationName: classificationName,
    classificationId: classificationId,
  });
}

function handleClassificationData(data) {
  const costClassifications =
    data.data["classification"]["cost_classifications"];
  const classificationElements =
    data.data["classification"]["classification_data"];
  const classificationName = data.data["classification"]["classification_name"];
  const costItemId = data.data["classification"]["cost_item_id"];

  CostUI.createCostClassificationWindow({
    classificationName,
    classificationElements,
    costClassifications,
    costItemId,
    callbacks: {
      enableEditingClassification: enableEditingClassification,
      removeClassificationReference: removeClassificationReference,
      addClassificationReference: addClassificationReference,
    },
  });
}

function enableEditingQuantities(costItemId) {
  executeOperator({ type: "enableEditingQuantities", costItemId: costItemId });
}

function duplicateCostItem(costItemId) {
  executeOperator({ type: "duplicateCostItem", costItemId: costItemId });
}

function handleCostValuesData(data) {
  CostUI.createCostValuesForm({
    costValues: data.data["cost_values"]["cost_values"],
    costItemId: data.data["cost_values"]["cost_item_id"],
    callbacks: {
      editCostValues: editCostValues,
      addCostValue: addCostValue,
      deleteCostValue: deleteCostValue,
    },
  });

  CostUI.highlightElement(data.data["cost_values"]["cost_item_id"]);
}

function addCostValue(costItemId) {
  executeOperator({ type: "addCostValue", costItemId: costItemId });
}

function editCostValues(costItemId, costValues) {
  executeOperator({
    type: "editCostValues",
    costItemId: costItemId,
    costValues: costValues,
  });
}

function deleteCostItem(costItemId) {
  CostUI.deleteCostItem(costItemId);
  executeOperator({ type: "deleteCostItem", costItemId: costItemId });
}

function handleMessage(data) {
  if (data.data["message"].hasOwnProperty("error")) {
    handleError(data);
  } else {
    handleSuccess(data);
  }
}

function handleError(data) {
  const errorMessage = data.data["message"]["error"];
  const containerId = data.data["message"]["container"];
  const container = document.getElementById(containerId);
  CostUI.Error(container, errorMessage);
}

function handleSuccess(data) {
  const successMessage = data.data["message"]["success"];
  const containerId = data.data["message"]["container"];
  const container = document.getElementById(containerId);
  CostUI.Success(container, successMessage);
}

function executeOperator(operator, blenderId) {
  const msg = {
    sourcePage: "cost",
    operator: operator,
  };
  if (blenderId !== undefined) {
    msg.BlenderId = blenderId;
  }
  socket.emit("web_operator", msg);
}
