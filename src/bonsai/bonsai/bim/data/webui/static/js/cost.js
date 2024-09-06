import { CostUI } from "./utilities/costui.js";

const connectedClients = {};
let socket;

let isScheduleLoad = {};

$(document).ready(function () {
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

  connectSocket();
  CostUI.createColorPicker();
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
}

function handlePredefinedTypes(data) {
  CostUI.enableAddingCostSchedule(
    data.data["predefined_types"],
    addCostSchedule
  );
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

  CostUI.highlightCostItem(data.data["cost_values"]["cost_item_id"]);
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
  executeOperator({ type: "deleteCostItem", costItemId: costItemId });
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

function handleCostSchedulesData(data) {
  const blenderId = data.blenderId;
  const costSchedules = data.data["cost_schedules"]["cost_schedules"];
  if (costSchedules.length === 0) {
    return;
  }
  const currency = data.data["cost_schedules"]["currency"]
    ? data.data["cost_schedules"]["currency"]["name"]
    : "Undefined";
  const costScheduleDiv = document.getElementById("cost-schedules");
  costScheduleDiv.innerHTML = "";
  costSchedules.forEach((costSchedule) => {
    costSchedule.UpdateDate = new Date(costSchedule.UpdateDate);
    const predefinedType = CostUI.text("Predefined Type: " + costSchedule.PredefinedType)
    const updatedOn = CostUI.text("Updated On: " + costSchedule.UpdateDate);
    const div = document.createElement("div");
    
    div.appendChild(predefinedType);
    div.appendChild(updatedOn);
    const callback = () => loadCostSchedule(costSchedule.id, blenderId);

    const card = CostUI.createCard(costSchedule.Name, div, callback);
    costScheduleDiv.append(card);
  });
}

function handleCostItemsData(data) {
  CostUI.createCostSchedule({
    data: data.data["cost_items"]["cost_items"],
    costScheduleId: data.data["cost_items"]["cost_schedule_id"],
    blenderID: data.blenderId,
    callbacks: {
      addCostItem: addCostItem,
      deleteCostItem: deleteCostItem,
      duplicateCostItem: duplicateCostItem,
      selectAssignedElements: selectAssignedElements,
      editCostItemName: editCostItemName,
      enableEditingCostValues: enableEditingCostValues,
      addSummaryCostItem: addSummaryCostItem,
    },
  });
}

function duplicateCostItem(costItemId) {
  executeOperator({ type: "duplicateCostItem", costItemId: costItemId });
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
